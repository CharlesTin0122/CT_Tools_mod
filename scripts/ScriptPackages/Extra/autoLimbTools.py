# -*- encoding: utf-8 -*-
"""
@File    :   main.py
@Time    :   2025/05/23 10:47:19
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

import pymel.core as pc


def auto_limb_tools():
    """
    自动化肢体工具
    """
    is_rear_leg = 1  # 是否是后腿
    limb_joints = 4  # 关节数量

    # 用于生成名称的信息
    if is_rear_leg:
        front_rear = "rear"
        print("This is a rear leg.")
    else:
        front_rear = "front"
        print("This is a front leg.")

    # 检查选中的关节
    select_check = pc.ls(sl=True, type="joint")
    if not select_check:
        pc.error("No joints selected.")
    else:
        jnt_root = select_check[0]

    # 获取关节名称后缀
    left_right = jnt_root.getName()[-2:]
    # 确保后缀可用
    if left_right not in ["_l", "_r"]:
        pc.error("The joint name should end with _l or _r.")
    # 创建名称
    limb_name = f"{front_rear}_leg{left_right}"
    paw_ctrl_name = f"{limb_name}_ik_ctrl"
    pv_ctrl_name = f"{limb_name}_pv_ctrl"
    hock_ctrl_name = f"{limb_name}_hock_ctrl"
    root_ctrl_name = f"{limb_name}_root_ctrl"

    # -----------------------------创建辅助骨骼---------------------------------
    jnt_hierarchy = []
    jnt_hierarchy = jnt_root.listRelatives(
        children=True,
        allDescendents=True,  # 所有后代
        type="joint",
    )
    jnt_hierarchy.append(jnt_root)  # 添加根关节
    jnt_hierarchy.reverse()  # 反转列表
    pc.select(clear=True)  # 清除选择

    # 创建骨骼"ik", "fk", "stretch"骨骼链,如果是后腿，增加"driver"骨骼链，每个骨骼链四节骨骼
    new_jnt_list = ["ik", "fk", "stretch"]
    if is_rear_leg:
        new_jnt_list.append("driver")
    # 创建关节
    for new_jnt in new_jnt_list:  # 遍历新关节列表
        for i in range(limb_joints):  # 遍历关节数量
            # 生成骨骼名称
            new_jnt_name = f"{jnt_hierarchy[i]}_{new_jnt}"
            # 创建新关节
            jnt = pc.joint(name=new_jnt_name)
            # 对齐新关节
            pc.matchTransform(jnt, jnt_hierarchy[i])
            # 冻结变换
            pc.makeIdentity(jnt, apply=True, translate=False, rotate=True, scale=False)
        # 清除选择，不再连接父子关系
        pc.select(clear=True)

    # FKIK骨骼约束主骨骼
    for i in range(limb_joints):
        pc.parentConstraint(
            f"{jnt_hierarchy[i]}_ik", f"{jnt_hierarchy[i]}_fk", jnt_hierarchy[i]
        )
    # FK控制器控制FK骨骼
    for i in range(limb_joints):
        pc.parentConstraint(f"{jnt_hierarchy[i]}_fk_ctrl", f"{jnt_hierarchy[i]}_fk")
    # IK控制器控制IK骨骼
    if is_rear_leg:
        # 为驱动骨骼添加IK,四节骨骼IK
        driver_ikHandle = pc.ikHandle(
            name=f"{limb_name}_driver_ikHandle",
            solver="ikRPsolver",
            startJoint=f"{jnt_hierarchy[0]}_driver",
            endEffector=f"{jnt_hierarchy[3]}_driver",
        )[0]

    # 为IK骨骼创建IK效应器
    # 为上三节骨骼创建旋转平面IK
    knee_ikHandle = pc.ikHandle(
        name=f"{limb_name}_knee_ikHandle",
        solver="ikRPsolver",  # RotatePlaneSolver（旋转平面IK）
        startJoint=f"{jnt_hierarchy[0]}_ik",
        endEffector=f"{jnt_hierarchy[2]}_ik",
    )[0]
    # 为下两节骨骼创建单链IK
    hock_ikHandle = pc.ikHandle(
        name=f"{limb_name}_hock_ikHandle",
        solver="ikSCsolver",  # SingleChainSolver（单链IK）
        startJoint=f"{jnt_hierarchy[2]}_ik",
        endEffector=f"{jnt_hierarchy[3]}_ik",
    )[0]
    # 给上两节骨骼IK句柄打组创建一个膝盖控制组
    knee_ctrl_grp = pc.group(
        knee_ikHandle,  # 创建IK会返回一个列表[ikHandle，IkEffector]
        name=f"{limb_name}_knee_ctrl",
    )
    # 为膝盖控制组再打组成为偏移组
    knee_ctrl_grp_offset = pc.group(
        knee_ctrl_grp,
        name=f"{limb_name}_knee_ctrl_offset",
    )
    # 获取脚踝骨骼的枢轴点,返回两个三位向量：选转轴和缩放轴
    ankle_pivot = pc.nodetypes.Joint(f"{jnt_hierarchy[3]}_ik").getPivots(
        worldSpace=True
    )
    # 将组的枢轴对齐到脚踝枢轴，IK句柄的位置在脚踝，IK组的位置在脚掌
    knee_ctrl_grp.setPivots(ankle_pivot[0], worldSpace=True)
    knee_ctrl_grp_offset.setPivots(ankle_pivot[0], worldSpace=True)

    # 将脚踝IK句柄作为脚掌控制器的子物体
    pc.parent(hock_ikHandle, paw_ctrl_name)
    """    
    其基本原理是：
    1. 使用drive骨骼添加四节骨骼的IK用于控制腿部的全局运动
    2. 使用ik骨骼添加上三节骨骼的旋转平面IK和下两节骨骼的单链IK，用于控制腿部运动细节调整
    3. 使用drive骨骼作为ik骨骼ik效应器的父对象来控制ik骨骼
    4. 而IK骨骼直接父子约束主骨骼，从而实现了对主骨骼的控制
    """
    # 如果是后腿，调整层级使得drive骨骼控制IK手柄，
    if is_rear_leg:
        # 将膝盖IK控制偏移组作为metatarsus_l_driver骨骼的子对象
        pc.parent(knee_ctrl_grp_offset, f"{jnt_hierarchy[2]}_driver")
        # 将脚踝IK句柄作为backcarpus_l_driver的子对象
        pc.parent(hock_ikHandle, f"{jnt_hierarchy[3]}_driver")
        # 将驱动骨骼IK句柄（四节骨骼IK）作为脚掌控制器的子对象
        pc.parent(driver_ikHandle, paw_ctrl_name)
    # 如果是前腿，则将膝盖IK控制偏移组作为根控制器的子集，并用脚部IK控制器点约束
    else:
        pc.parent(knee_ctrl_grp_offset, "local_ctrl")
        pc.pointConstraint(paw_ctrl_name, knee_ctrl_grp_offset)
    # 使用控制器控制IK骨骼脚掌骨转
    pc.orientConstraint(paw_ctrl_name, f"{jnt_hierarchy[3]}_ik")
    # 添加极向量约束
    if is_rear_leg:
        # 如果是后腿，则使用极向量控制器约束驱动骨骼IK句柄
        pc.poleVectorConstraint(pv_ctrl_name, driver_ikHandle)
    else:
        # 如果是前腿，则使用极向量控制器约束IK骨骼膝盖IK句柄
        pc.poleVectorConstraint(pv_ctrl_name, knee_ikHandle)

    # ------------------------添加 hock_ctrl--------------------------------
    # 使用控制器hock_ctrl的位移驱动骨骼IK效应器偏移组的旋转，跳过Y轴，因为Y轴要被极向量约束控制
    # pc.orientConstraint(hock_ctrl_name, knee_ctrl_grp, skip="y", maintainOffset=True)
    hock_multi = pc.createNode("multiplyDivide", name=f"{limb_name}_hock_multi")
    pc.PyNode(hock_ctrl_name).translate.connect(hock_multi.input1)
    hock_multi.outputZ.connect(knee_ctrl_grp.rotateX)
    hock_multi.outputX.connect(knee_ctrl_grp.rotateZ)
    hock_multi.input2X.set(-5)
    hock_multi.input2Z.set(5)
    # ------------------------------FK IK SWitch------------------------------
    for i in range(limb_joints):
        # 找到约束节点，位于骨骼层级下第一个父子约束节点
        constraint = pc.listConnections(jnt_hierarchy[i], type="parentConstraint")[0]
        # 找到IKFK骨骼的约束权重属性
        weight_attr = pc.parentConstraint(constraint, query=True, weightAliasList=True)
        # 创建一个reverse节点，用于属性链接
        reverse_node = pc.createNode("reverse", name=f"{limb_name}_fkik_reverse")
        # 链接属性
        pc.PyNode(root_ctrl_name).FK_IK_Switch.connect(weight_attr[0])
        pc.PyNode(root_ctrl_name).FK_IK_Switch.connect(reverse_node.inputX)
        reverse_node.outputX.connect(weight_attr[1])
    # -------------------------------------更新层级-----------------------------------
    # 创建一个组用于储存生成的辅助骨骼，位置在腿部根关节位置
    helper_jnt_grp = pc.group(name=f"{limb_name}_grp", empty=True)
    pc.matchTransform(helper_jnt_grp, jnt_root)
    pc.makeIdentity(helper_jnt_grp, apply=True, translate=True, rotate=True)
    helper_jnt_grp.visibility.set(0)  # 隐藏组
    # 将所有生成的辅助骨骼作为子对象
    pc.parent(
        f"{jnt_root}_ik",
        f"{jnt_root}_fk",
        f"{jnt_root}_stretch",
        helper_jnt_grp,
    )
    # 只有后腿才有driver骨骼
    if is_rear_leg:
        pc.parent(f"{jnt_root}_driver", helper_jnt_grp)
    # 使用根控制器父子约束辅助骨骼组
    pc.parentConstraint(
        root_ctrl_name,
        helper_jnt_grp,
        maintainOffset=True,
    )
    # 将组放入大纲rig_system层级之下
    pc.parent(helper_jnt_grp, "rig_system")
    pc.select(clear=True)  # 清除选择

    # -------------------------------------肢体的缩放-----------------------------------
    # 获取骨骼位置
    jnt0_position = jnt_hierarchy[0].getTranslation(space="world")
    jnt1_position = jnt_hierarchy[1].getTranslation(space="world")
    jnt2_position = jnt_hierarchy[2].getTranslation(space="world")
    jnt3_position = jnt_hierarchy[3].getTranslation(space="world")
    # 计算单个骨骼长度
    distance_0_1 = (jnt0_position - jnt1_position).length()
    distance_1_2 = (jnt1_position - jnt2_position).length()
    distance_2_3 = (jnt2_position - jnt3_position).length()
    # 计算腿部骨骼静态骨骼长度和
    static_length = distance_0_1 + distance_1_2 + distance_2_3
    # 计算腿部根骨骼到脚部IK控制器动态长度
    distance_node = pc.createNode(
        "distanceBetween",
        name=f"{limb_name}_length_dynamic",
    )
    pc.PyNode(paw_ctrl_name).worldMatrix[0].connect(distance_node.inMatrix1)
    pc.PyNode(f"{jnt_hierarchy[0]}_fk").worldMatrix[0].connect(distance_node.inMatrix2)
    # 计算静态长度和动态长度的比值
    divide_node_ratio = pc.createNode(
        "multiplyDivide",
        name=f"{limb_name}_length_ratio",
    )
    divide_node_ratio.operation.set(2)  # 除法
    # 使用动态骨骼长度除以静态骨骼长度得到比值
    distance_node.distance.connect(divide_node_ratio.input1X)
    divide_node_ratio.input2X.set(static_length)
    # 使用条件节点计算IK骨骼长度
    condition_node_stretch_type = pc.createNode(
        "condition",
        name=f"{limb_name}_length_condition",
    )
    condition_node_stretch_type.operation.set(2)  # 大于
    # 如果动态骨骼长度与静态骨骼长度的比值大于1，则使用比值作为IK骨骼的X轴缩放系数
    divide_node_ratio.outputX.connect(condition_node_stretch_type.firstTerm)
    condition_node_stretch_type.secondTerm.set(1)
    divide_node_ratio.outputX.connect(condition_node_stretch_type.colorIfTrueR)
    # 缩放IK骨骼
    condition_node_stretch_type.outColorR.connect(f"{jnt_hierarchy[0]}_ik.scaleX")
    condition_node_stretch_type.outColorR.connect(f"{jnt_hierarchy[1]}_ik.scaleX")
    condition_node_stretch_type.outColorR.connect(f"{jnt_hierarchy[2]}_ik.scaleX")
    # 如果是后腿，则还需要缩放驱动骨骼，因为IK骨骼的IK效应器是由驱动骨骼控制的。
    if is_rear_leg:
        condition_node_stretch_type.outColorR.connect(
            f"{jnt_hierarchy[0]}_driver.scaleX"
        )
        condition_node_stretch_type.outColorR.connect(
            f"{jnt_hierarchy[1]}_driver.scaleX"
        )
        condition_node_stretch_type.outColorR.connect(
            f"{jnt_hierarchy[2]}_driver.scaleX"
        )

    # -------------------------------------控制器属性控制肢体的缩放-----------------------------------
    # 创建一个blendColors节点用于控制肢体的缩放
    blend_node_stretch = pc.createNode("blendColors", name=f"{limb_name}_blendColors")
    # color2X设置为1，表示当Stretchiness属性为0时，骨骼的缩放系数为1，double3 表示一个三维浮点数向量
    blend_node_stretch.color2.set(1, 0, 0, type="double3")
    # 将除法节点的输出（骨骼比例）连接到blendColors节点的color1R属性
    divide_node_ratio.outputX.connect(blend_node_stretch.color1R, force=True)
    # 将混合的输出连接到条件节点的colorIfTrueR属性
    blend_node_stretch.outputR.connect(
        condition_node_stretch_type.colorIfTrueR, force=True
    )
    # 连接控制器的Stretchiness属性到blendColors节点的blender属性
    pc.PyNode(paw_ctrl_name).Stretchiness.connect(
        blend_node_stretch.blender, force=True
    )

    # 我们使用驱动关键帧来控制缩放类型
    # 设置控制器属性，0伸长缩短，1只伸长，2只缩短
    pc.PyNode(paw_ctrl_name).Stretch_Type.set(0)  # 伸长缩短
    # 设置条件节点的操作类型，0等于，1不等于，2大于，3大于等于，4小于，5小于等于
    condition_node_stretch_type.operation.set(1)  # 不等于
    # 设置驱动关键帧
    pc.setDrivenKeyframe(
        condition_node_stretch_type.operation,
        currentDriver=pc.PyNode(paw_ctrl_name).Stretch_Type,
        value=1,  # 不等于
        driverValue=0,  # 伸长缩短
    )
    pc.setDrivenKeyframe(
        condition_node_stretch_type.operation,
        currentDriver=pc.PyNode(paw_ctrl_name).Stretch_Type,
        value=3,  # 大于等于
        driverValue=1,  # 只伸长
    )
    pc.setDrivenKeyframe(
        condition_node_stretch_type.operation,
        currentDriver=pc.PyNode(paw_ctrl_name).Stretch_Type,
        value=5,  # 小于等于
        driverValue=2,  # 只缩短
    )
    pc.PyNode(paw_ctrl_name).Stretch_Type.set(1)  # 只伸长
    # 清除选择
    pc.select(clear=True)

    # ----------------------------为骨骼缩放添加体积守恒---------------------------
    # 创建一个multiplyDivide节点用于计算体积守恒
    power_node_volume = pc.createNode("multiplyDivide", name=f"{limb_name}_volume")
    # 设置multiplyDivide节点的操作类型为幂计算
    power_node_volume.operation.set(3)
    # 将肢体长度比值连接到multiplyDivide节点的input1X属性
    blend_node_stretch.outputR.connect(power_node_volume.input1X, force=True)
    # 将幂计算的结果链接到条件节点的colorIfTrueG属性
    power_node_volume.outputX.connect(
        condition_node_stretch_type.colorIfTrueG, force=True
    )
    # 条件节点的outColorG链接到骨骼缩放YZ轴
    condition_node_stretch_type.outColorG.connect(
        f"{jnt_hierarchy[1]}.scaleY", force=True
    )
    condition_node_stretch_type.outColorG.connect(
        f"{jnt_hierarchy[1]}.scaleZ", force=True
    )
    condition_node_stretch_type.outColorG.connect(
        f"{jnt_hierarchy[2]}.scaleY", force=True
    )
    condition_node_stretch_type.outColorG.connect(
        f"{jnt_hierarchy[2]}.scaleZ", force=True
    )
    # 链接控制器的Volume_Offset属性到multiplyDivide节点的input2X属性
    pc.PyNode(root_ctrl_name).Volume_Offset.connect(
        power_node_volume.input2X, force=True
    )
    # 设置默认体积守恒值为-0.5
    pc.PyNode(root_ctrl_name).Volume_Offset.set(-0.5)

    # -------------------------------------添加扭曲关节-----------------------------------
    # 设置左右翻转变量，用于镜像左右数值
    if left_right == "_l":
        flip_side = 1
    else:
        flip_side = -1
    # 创建扭曲关节
    roll_jnt_list = [
        jnt_hierarchy[0],
        jnt_hierarchy[3],
        jnt_hierarchy[0],
        jnt_hierarchy[0],
    ]
    for i in range(len(roll_jnt_list)):
        # 生成骨骼名称，roll骨骼是扭曲骨骼，Follow骨骼用于控制扭曲骨骼旋转
        if i > 2:
            roll_jnt_name = f"{roll_jnt_list[i]}_follow_tip"
        elif i > 1:
            roll_jnt_name = f"{roll_jnt_list[i]}_follow"
        else:
            roll_jnt_name = f"{roll_jnt_list[i]}_roll"
        # 创建扭曲关节
        roll_jnt = pc.joint(name=roll_jnt_name, radius=5)
        # 对齐扭曲关节
        pc.matchTransform(roll_jnt, roll_jnt_list[i])
        # 冻结变换
        pc.makeIdentity(roll_jnt, apply=True, translate=False, rotate=True, scale=False)

        # 处理父子关系
        if i < 2:
            pc.parent(roll_jnt, roll_jnt_list[i])
        elif i > 2:
            pc.parent(roll_jnt, f"{roll_jnt_list[2]}_follow")
        # 取消选择
        pc.select(clear=True)
        # 显示局部旋转轴
        # pc.toggle(roll_jnt, localAxis=True)
    # 调整follow_tip骨骼位置
    jnt0_position = jnt_hierarchy[0].getTranslation(space="world")
    jnt1_position = jnt_hierarchy[1].getTranslation(space="world")
    follow_tip_position = (jnt0_position + jnt1_position) / 2
    pc.PyNode(f"{roll_jnt_list[2]}_follow_tip").setTranslation(
        follow_tip_position, space="world"
    )
    # 设置follow骨骼的位置,如果是右侧 数值 * -1
    pc.move(
        f"{roll_jnt_list[2]}_follow",
        0,
        0,
        -5 * flip_side,
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )

    # 创建瞄准约束所使用的定位器
    loc_roll_aim = pc.spaceLocator(name=f"{roll_jnt_list[0]}_roll_aim")
    pc.parent(loc_roll_aim, f"{roll_jnt_list[2]}_follow")
    pc.matchTransform(loc_roll_aim, f"{roll_jnt_list[2]}_follow")
    # 移动定位器
    pc.move(
        loc_roll_aim,
        0,
        0,
        -5 * flip_side,
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )

    # 添加瞄准约束
    pc.aimConstraint(
        jnt_hierarchy[1],
        f"{roll_jnt_list[0]}_roll",
        weight=1,
        aimVector=(1 * flip_side, 0, 0),
        worldUpType="object",
        worldUpObject=loc_roll_aim,
        upVector=(0, 0, -1 * flip_side),
        maintainOffset=True,
    )

    # 为follow骨骼添加旋转平面IK
    follow_ikHandle = pc.ikHandle(
        name=f"{limb_name}_follow_ikHandle",
        solver="ikRPsolver",
        startJoint=f"{roll_jnt_list[2]}_follow",
        endEffector=f"{roll_jnt_list[2]}_follow_tip",
    )[0]
    # 将follow_ikHandle作为膝盖骨骼的子对象
    pc.parent(follow_ikHandle, jnt_hierarchy[1])
    # 对齐follow_ikHandle
    pc.matchTransform(follow_ikHandle, jnt_hierarchy[1])

    follow_ikHandle.poleVector.set(0, 0, 0)  # 设置极向量为0

    # -------------------------------------添加脚踝扭曲关节-----------------------------------
    loc_roll_lower_aim = pc.spaceLocator(name=f"{roll_jnt_list[1]}_roll_aim")
    pc.matchTransform(loc_roll_lower_aim, f"{roll_jnt_list[1]}_roll")
    pc.parent(loc_roll_lower_aim, jnt_hierarchy[3])
    # 移动定位器
    pc.move(
        loc_roll_lower_aim,
        5 * flip_side,
        0,
        0,
        relative=True,
        objectSpace=True,
        worldSpaceDistance=True,
    )

    # 添加瞄准约束
    pc.aimConstraint(
        jnt_hierarchy[2],
        f"{roll_jnt_list[1]}_roll",
        weight=1,
        aimVector=(0, 1 * flip_side, 0),
        worldUpType="object",
        worldUpObject=loc_roll_lower_aim,
        upVector=(1 * flip_side, 0, 0),
        maintainOffset=True,
    )

    # 整理大纲
    pc.parent(f"{roll_jnt_list[0]}_follow", helper_jnt_grp)
    # 清除选择
    pc.select(clear=True)
