import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


# mGear Utiliyies
def addOffsetGroups(objs=None, *args):
    """为选中对象添加偏移组，偏移组会提取对象的所有变换，使对象属性归零

    Args:
        objs (list, optional): 要添加偏移组的对象列表.

    Returns:
        list: 偏移组列表
    """
    osgList = []

    if not objs:
        objs = pm.selected()
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        oParent = obj.getParent()
        osg = pm.createNode(
            "transform", name=obj.name() + "_osg", parent=oParent, skipSelect=True
        )
        pm.matchTransform(osg, obj)
        # osg.setTransformation(obj.getMatrix())
        pm.parent(obj, osg)
        osgList.append(osg)
    return osgList


def selectDeformers(*args):
    """选择模型蒙皮受影响的骨骼"""

    oSel = pm.selected()[0]
    oColl = pm.skinCluster(oSel, query=True, influence=True)
    pm.select(oColl)


def replaceShape(source=None, targets=None, *args):
    """将源对象的形节点替换目标对象的形节点,常用语替换控制器形状.
    Args:
        source (None, PyNode): 源节点
        targets (None, list of pyNode): 目标节点或列表
        *args: Maya 占位符
    Returns:
        None
    """
    # 验证参数
    if not source and not targets:
        oSel = pm.selected()
        if len(oSel) < 2:
            pm.displayWarning("At less 2 objects must be selected")
            return None
        else:
            source = oSel[0]  # 第一个选择对象为源节点
            targets = oSel[1:]  # 第二个和后面的为目标节点
    # 遍历目标对象
    for target in targets:
        # 复制一份源节点用于替换
        source2 = pm.duplicate(source)[0]
        # 获取目标对象的形节点
        shape = target.getShapes()
        # 用于储存目标对象形节点属性连接列表
        cnx = []
        if shape:
            # 列出连接的属性，TODO：有空再次检查代码，貌似属性链接有问题
            # plugs参数：列出连接的节点和属性（Attribute('skinCluster3.outputGeometry[0]')），
            # 不添加此参数只会列出连接的节点名称（  nt.SkinCluster('skinCluster3'),）
            # connections：会返回一个配对列表。列表中的每一项元组，存储了所有连接的“来源”和“去向”。
            # 格式为：(Attribute('mesh_bodyShape.inMesh'),Attribute('skinCluster3.outputGeometry[0]'))。
            cnx = shape[0].listConnections(plugs=True, connections=True)
            # c[1]为连接的源头（Attribute('skinCluster3.outputGeometry[0]')），
            # c[0].shortName()提取出不带节点名的纯属性名（"inMesh"）,
            # 因为我们断开连接之后要删除该形节点，所以我们只获取属性名即可重新连接新的形节点
            cnx = [[c[1], c[0].shortName()] for c in cnx]
            # 断开连接
            for s in shape:
                for c in s.listConnections(plugs=True, connections=True):
                    pm.disconnectAttr(c[0])
        # 删除目标对象的形节点
        pm.delete(shape)
        # 将复制出来的源节点的形节点作为目标节点的子对象，
        # relative保持相对变换，shape将一个形状节点“过继”给一个新的变换节点
        pm.parent(source2.getShapes(), target, relative=True, shape=True)
        # 重新连接属性
        for i, sh in enumerate(target.getShapes()):
            # Restore shapes connections
            for c in cnx:
                pm.connectAttr(c[0], sh.attr(c[1]))
            pm.rename(sh, f"{target.name()}_{i}_shape")
        # 删除复制出来的变换节点
        pm.delete(source2)


def addBlendedJoint(
    oSel=None, compScale=True, blend=0.5, name=None, select=True, *args
):
    """创建混合骨骼
    在选中骨骼同层级创建一个混合骨骼他的旋转是选中骨骼的一半. 使用 pairBlend 节点.

    Args:
        oSel (None or joint, optional): 如果未提供，使用选中骨骼.
        compScale (bool, optional): 骨骼的segmentScaleCompensate属性. 默认为 True.
        blend (float, optional): 旋转混合值
        name (None, optional): 混合骨骼的名称
        *args: Maya's dummy

    Returns:
        list: blended joints list

    """
    # 验证参数
    if not oSel:
        oSel = pm.selected()
    elif not isinstance(oSel, list):
        oSel = [oSel]
    # 用于储存混合骨骼
    jnt_list = []
    # 遍历所选骨骼
    for x in oSel:
        # 获取骨骼父对象和混合骨骼名称
        if isinstance(x, pm.nodetypes.Joint):
            parent = x.getParent()
            if name:
                bname = "blend_" + name
            else:
                bname = "blend_" + x.name()
            # 创建骨骼，添加到列表，设置半径，设置父对象
            jnt = pm.createNode("joint", n=bname, p=x)
            jnt_list.append(jnt)
            jnt.attr("radius").set(1.5)
            pm.parent(jnt, parent)
            # 创建pairBlend节点
            o_node = pm.createNode("pairBlend")
            # 设置节点旋转差值为四元数（Quaternion）
            o_node.attr("rotInterpolation").set(1)
            # 设置节点混合权重
            pm.setAttr(o_node + ".weight", blend)
            # 链接属性
            pm.connectAttr(x + ".translate", o_node + ".inTranslate1")
            pm.connectAttr(x + ".translate", o_node + ".inTranslate2")
            pm.connectAttr(x + ".rotate", o_node + ".inRotate1")

            pm.connectAttr(o_node + ".outRotateX", jnt + ".rotateX")
            pm.connectAttr(o_node + ".outRotateY", jnt + ".rotateY")
            pm.connectAttr(o_node + ".outRotateZ", jnt + ".rotateZ")

            pm.connectAttr(o_node + ".outTranslateX", jnt + ".translateX")
            pm.connectAttr(o_node + ".outTranslateY", jnt + ".translateY")
            pm.connectAttr(o_node + ".outTranslateZ", jnt + ".translateZ")

            pm.connectAttr(x + ".scale", jnt + ".scale")
            # 设置混合骨骼颜色为黄色
            jnt.attr("overrideEnabled").set(1)
            jnt.attr("overrideColor").set(17)
            # 设置混合骨骼 分段缩放补偿
            jnt.attr("segmentScaleCompensate").set(compScale)

            try:
                defSet = pm.PyNode("rig_deformers_grp")

            except TypeError:
                pm.sets(n="rig_deformers_grp")
                defSet = pm.PyNode("rig_deformers_grp")

            pm.sets(defSet, add=jnt)
        else:
            pm.displayWarning(
                "Blended Joint can't be added to: %s. Because "
                "is not ot type Joint" % x.name()
            )

    if jnt_list and select:
        pm.select(jnt_list)

    return jnt_list


def addSupportJoint(oSel=None, select=True, *args):
    """为混合骨骼添加修形骨骼.
    修形骨骼用于蒙皮到模型，被RBF算法或驱动关键帧驱动用来修形
    Args:
        oSel (None or blended joint, optional): 混合骨骼如果未提供则使用选中骨骼.
        *args: Mays's dummy

    Returns:
        list: blended joints list

    """
    # 验证参数
    if not oSel:
        oSel = pm.selected()
    elif not isinstance(oSel, list):
        oSel = [oSel]
    # 列表用于添加修形骨骼
    jnt_list = []
    # 遍历所选对象
    for x in oSel:
        if x.name().split("_")[0] == "blend":
            # 获取所有子骨骼
            children = [
                item
                for item in pm.selected()[0].listRelatives(
                    allDescendents=True, type="joint"
                )
            ]
            # 获取子骨骼数量
            i = len(children)
            # 获取修形骨骼唯一命名
            name = x.name().replace("blend", "blendSupport_%s" % str(i))
            # 创建骨骼，添加列表，设置属性
            jnt = pm.createNode("joint", n=name, p=x)
            jnt_list.append(jnt)
            jnt.attr("radius").set(1.5)
            jnt.attr("overrideEnabled").set(1)
            jnt.attr("overrideColor").set(17)
            try:
                defSet = pm.PyNode("rig_deformers_grp")

            except pm.MayaNodeError:
                pm.sets(n="rig_deformers_grp")
                defSet = pm.PyNode("rig_deformers_grp")

            pm.sets(defSet, add=jnt)

        else:
            pm.displayWarning(
                "Support Joint can't be added to: %s. Because "
                "is not blend joint" % x.name()
            )

    if jnt_list and select:
        pm.select(jnt_list)

    return jnt_list


def transform_to_offsetParentMatrix(objs=None):
    """将对象变换转移到偏移父矩阵,变换置零

    Args:
        objs (nt.Transform): 对象列表
    """
    if not objs:
        objs = pm.selected()
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        # 获取对象局部矩阵
        obj_matrix = obj.getMatrix(objectSpace=True)
        # 获取对象偏移父矩阵
        obj_offsetParentMatrix = obj.offsetParentMatrix.get()
        # 设置对象偏移父矩阵为 局部矩阵 * 偏移父矩阵,顺序不能反
        obj.offsetParentMatrix.set(obj_matrix * obj_offsetParentMatrix)
        # 设置对象局部矩阵为单位矩阵,变换置零
        obj.setMatrix(dt.Matrix())


def offsetParentMatrix_to_transform(objs=None):
    """将对象偏移父矩阵转移到变换,偏移父矩阵置零

    Args:
        objs (nt.Transform): 对象列表
    """
    if not objs:
        objs = pm.selected()
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        # 获取对象偏移父矩阵
        obj_offsetParentMatrix = obj.offsetParentMatrix.get()
        # 获取对象局部矩阵
        obj_matrix = obj.getMatrix(objectSpace=True)
        # 设置对象矩阵为 局部矩阵 * 偏移父矩阵 ,顺序不能反
        obj.setMatrix(obj_matrix * obj_offsetParentMatrix)
        # 设置对象偏移父矩阵为单位矩阵,变换置零
        obj.offsetParentMatrix.set(dt.Matrix())


# Rig Utilities
def match_bind_jnt_to_ikfk_jnt(
    limb_setting_ctrl: nt.Transform,
    bind_jnt_list: list[nt.Joint],
    fk_jnt_list: list[nt.Joint],
    ik_jnt_list: list[nt.Joint],
    fk_ctrl_grp: nt.Transform,
    ik_ctrl_grp: nt.Transform,
):
    """轻量级IKFK骨骼约束主骨骼，使用blendColor节点代替ParentConstrain节点，ikfkSwitch属性：0为IK模式，1为FK模式

    Args:
        limb_setting_ctrl (nt.Transform): IKFK设置控制器
        bind_jnt_list (list[nt.Joint]): 主骨骼列表
        fk_jnt_list (list[nt.Joint]): FK骨骼列表
        ik_jnt_list (list[nt.Joint]): IK骨骼列表
        fk_ctrl_grp: nt.Transform,:FK控制器组
        ik_ctrl_grp: nt.Transform:IK控制器组
    """
    # 添加属性
    if not limb_setting_ctrl.hasAttr("ikfkSwitch"):
        limb_setting_ctrl.addAttr(
            "ikfkSwitch",
            type="float",
            maxValue=1.0,
            minValue=0.0,
            defaultValue=0.0,
            keyable=True,
        )
    for i in range(len(bind_jnt_list)):
        # 连接位移
        translate_blender_node = pm.createNode(
            "blendColors", name=f"translate_blender{i}"
        )
        fk_jnt_list[i].translate.connect(translate_blender_node.color1)
        ik_jnt_list[i].translate.connect(translate_blender_node.color2)
        limb_setting_ctrl.ikfkSwitch.connect(translate_blender_node.blender)
        translate_blender_node.output.connect(bind_jnt_list[i].translate)
        # 连接旋转
        rotate_blender_node = pm.createNode("blendColors", name=f"rotate_blender{i}")
        fk_jnt_list[i].rotate.connect(rotate_blender_node.color1)
        ik_jnt_list[i].rotate.connect(rotate_blender_node.color2)
        limb_setting_ctrl.ikfkSwitch.connect(rotate_blender_node.blender)
        rotate_blender_node.output.connect(bind_jnt_list[i].rotate)
        # 连接缩放
        scale_blender_node = pm.createNode("blendColors", name=f"scale_blender{i}")
        fk_jnt_list[i].scale.connect(scale_blender_node.color1)
        ik_jnt_list[i].scale.connect(scale_blender_node.color2)
        limb_setting_ctrl.ikfkSwitch.connect(scale_blender_node.blender)
        scale_blender_node.output.connect(bind_jnt_list[i].scale)
        # 连接控制器显示
        limb_setting_ctrl.ikfkSwitch.connect(fk_ctrl_grp.visibility)
        reverse_visibility_node = pm.createNode("reverse", name="reverse_visibility")
        limb_setting_ctrl.ikfkSwitch.connect(reverse_visibility_node.inputX)
        reverse_visibility_node.outputX.connect(ik_ctrl_grp.visibility)


def spline_ik_stretch(
    ik_ctrl: nt.Transform,
    spline_curve: nt.Transform,
    spline_jnt_list: list[nt.Joint],
    stretch_axis: str = "x",
):
    """为SplineIK添加缩放功能

    Args:
        ik_ctrl (nt.Transform): SplineIK控制器
        spline_curve (nt.Transform): SplineIK曲线
        spline_jnt_list (list[nt.Joint]): SplineIK骨骼链
        stretch_axis (str, optional): 骨骼链的主拉伸轴 ('x', 'y', or 'z')。默认为 "x"。
    """
    # 添加IK控制器属性
    if not ik_ctrl.hasAttr("AutoStretch"):
        ik_ctrl.addAttr(
            "AutoStretch",
            type="float",
            maxValue=1.0,
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )
    if not ik_ctrl.hasAttr("MaxStretch"):
        ik_ctrl.addAttr(
            "MaxStretch", type="float", minValue=1.0, defaultValue=1.2, keyable=True
        )
    if not ik_ctrl.hasAttr("AutoVolume"):
        ik_ctrl.addAttr(
            "AutoVolume",
            type="float",
            maxValue=1.0,
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )
    # 获取曲线形节点
    curve_shape = spline_curve.getShape()
    # 计算静态长度
    curve_info_node = pm.createNode("curveInfo", name="spline_curve_info")
    curve_shape.worldSpace[0].connect(curve_info_node.inputCurve)
    static_length = curve_info_node.arcLength.get()

    # 获取曲线动态长度和静态长度之比
    distance_ratio_node = pm.createNode("multiplyDivide", name="distance_ratio")
    distance_ratio_node.operation.set(2)  # divide
    curve_info_node.arcLength.connect(distance_ratio_node.input1X)
    distance_ratio_node.input2X.set(static_length)
    # 设置缩放开关
    stretch_switch_node = pm.createNode("blendColors", name="stretch_switch")
    ik_ctrl.AutoStretch.connect(stretch_switch_node.blender)
    stretch_switch_node.color2R.set(1)
    distance_ratio_node.outputX.connect(stretch_switch_node.color1R)
    # 限制缩放
    clamp_stretch_node = pm.createNode("clampRange", name="clamp_stretch")
    stretch_switch_node.outputR.connect(clamp_stretch_node.input)
    ik_ctrl.MaxStretch.connect(clamp_stretch_node.maximum)
    clamp_stretch_node.minimum.set(1)
    # 计算体积保持
    calculate_volume_node = pm.createNode("multiplyDivide", name="calculate_volume")
    calculate_volume_node.operation.set(3)  # power
    clamp_stretch_node.output.connect(calculate_volume_node.input1X)
    calculate_volume_node.input2X.set(-0.5)
    # 体积保持开关
    volume_switch_node = pm.createNode("blendColors", name="volume_switch")
    ik_ctrl.AutoVolume.connect(volume_switch_node.blender)
    calculate_volume_node.outputX.connect(volume_switch_node.color1R)
    volume_switch_node.color2R.set(1)
    # 连接缩放属性
    other_axis = [axis for axis in "xyz" if axis != stretch_axis.lower()]
    for jnt in spline_jnt_list:
        clamp_stretch_node.output.connect(jnt.attr(f"scale{stretch_axis.upper()}"))
        volume_switch_node.outputR.connect(jnt.attr(f"scale{other_axis[0].upper()}"))
        volume_switch_node.outputR.connect(jnt.attr(f"scale{other_axis[1].upper()}"))


def limb_stretch(
    root_ctrl: nt.Transform,
    ik_ctrl: nt.Transform,
    ik_jnt_01: nt.Joint,
    ik_jnt_02: nt.Joint,
    ik_jnt_03: nt.Joint,
    stretch_axis: str = "x",
):
    """为三关节肢体创建可拉伸的IK系统。

    Args:
        root_ctrl (nt.Transform):  肢体根控制器
        ik_ctrl (nt.Transform):  肢体末端控制器
        ik_jnt_01 (nt.Joint): 肢体的根关节。
        ik_jnt_02 (nt.Joint): 肢体的中间关节。
        ik_jnt_03 (nt.Joint): 肢体的末端关节。
        stretch_axis (str, optional): 关节的主拉伸轴 ('x', 'y', or 'z')。默认为 "x"。
    """
    # 添加IK控制器属性
    if not ik_ctrl.hasAttr("AutoStretch"):
        ik_ctrl.addAttr(
            "AutoStretch",
            type="float",
            maxValue=1.0,
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )
    if not ik_ctrl.hasAttr("MaxStretch"):
        ik_ctrl.addAttr(
            "MaxStretch", type="float", minValue=1.0, defaultValue=1.2, keyable=True
        )
    if not ik_ctrl.hasAttr("AutoVolume"):
        ik_ctrl.addAttr(
            "AutoVolume",
            type="float",
            maxValue=1.0,
            minValue=0.0,
            defaultValue=1.0,
            keyable=True,
        )
    # # 添加拉伸模式的枚举属性
    # if not ik_ctrl.hasAttr("StretchMode"):
    #     ik_ctrl.addAttr(
    #         "StretchMode",
    #         attributeType="enum",
    #         enumName="None:Both:Stretch:----:Squash",  # 枚举选项
    #         defaultValue=0,
    #         keyable=True,
    #     )
    # 计算静态长度
    jnt01_world_position: dt.Vector = ik_jnt_01.getTranslation(space="world")
    jnt02_world_position: dt.Vector = ik_jnt_02.getTranslation(space="world")
    jnt03_world_position: dt.Vector = ik_jnt_03.getTranslation(space="world")
    distance1 = jnt01_world_position.distanceTo(jnt02_world_position)
    distance2 = jnt02_world_position.distanceTo(jnt03_world_position)
    jnt_static_distance = distance1 + distance2
    # 核心逻辑
    ## 计算动态距离
    dynamic_distance_node = pm.createNode("distanceBetween", name="dynamic_distance")
    root_ctrl.worldMatrix[0].connect(dynamic_distance_node.inMatrix1)
    ik_ctrl.worldMatrix[0].connect(dynamic_distance_node.inMatrix2)
    ## 计算动态距离和静态距离之间的比例
    distance_ratio_node = pm.createNode("multiplyDivide", name="distance_ratio")
    distance_ratio_node.operation.set(2)
    distance_ratio_node.input2X.set(jnt_static_distance)
    dynamic_distance_node.distance.connect(distance_ratio_node.input1X)
    ## 设置缩放开关
    stretch_switch_node = pm.createNode("blendColors", name="stretch_switch")
    stretch_switch_node.color2R.set(1)
    ik_ctrl.AutoStretch.connect(stretch_switch_node.blender)
    distance_ratio_node.outputX.connect(stretch_switch_node.color1R)
    ## 仅支持拉伸，不支持缩短,TODO:支持None，Both，Stretch，----，Squash。
    stretch_operation_node = pm.createNode("condition", name="stretch_operation")
    stretch_operation_node.operation.set(2)  # CreaterThan
    stretch_operation_node.colorIfFalseR.set(1)
    stretch_switch_node.outputR.connect(stretch_operation_node.colorIfTrueR)
    dynamic_distance_node.distance.connect(stretch_operation_node.firstTerm)
    stretch_operation_node.secondTerm.set(jnt_static_distance)
    ## 限制最大缩放，使用condition节点，也可以使用clampRange节点
    max_stretch_node = pm.createNode("condition", name="max_stretch")
    max_stretch_node.operation.set(5)  # less or equal
    stretch_operation_node.outColorR.connect(max_stretch_node.firstTerm)
    ik_ctrl.MaxStretch.connect(max_stretch_node.secondTerm)
    stretch_operation_node.outColorR.connect(max_stretch_node.colorIfTrueR)
    ik_ctrl.MaxStretch.connect(max_stretch_node.colorIfFalseR)
    ## 保持体积计算
    calculate_volume_node = pm.createNode("multiplyDivide", name="calculate_volume")
    calculate_volume_node.operation.set(3)  # power
    max_stretch_node.outColorR.connect(calculate_volume_node.input1X)
    calculate_volume_node.input2X.set(-0.5)
    ## 保持体积开关
    maintain_volume_node = pm.createNode("blendColors", name="maintain_volume")
    ik_ctrl.AutoVolume.connect(maintain_volume_node.blender)
    calculate_volume_node.outputX.connect(maintain_volume_node.color1R)
    maintain_volume_node.color2R.set(1)
    ## 连接IK骨骼缩放属性
    jnt_list = [ik_jnt_01, ik_jnt_02, ik_jnt_03]
    other_axes = [axis for axis in "xyz" if axis != stretch_axis.lower()]
    for jnt in jnt_list:
        max_stretch_node.outColorR.connect(jnt.attr(f"scale{stretch_axis.upper()}"))

        maintain_volume_node.outputR.connect(jnt.attr(f"scale{other_axes[0].upper()}"))
        maintain_volume_node.outputR.connect(jnt.attr(f"scale{other_axes[1].upper()}"))


def reverse_foot(
    foot_ik_ctrl: nt.Transform,
    toe_ik_ctrl: nt.Transform,
    foot_ik_handle: nt.IkHandle,
    ball_ik_handle: nt.IkHandle,
    toe_ik_handle: nt.IkHandle,
    heel_rev_ctrl: nt.Transform,
    tip_rev_ctrl: nt.Transform,
    out_rev_ctrl: nt.Transform,
    in_rev_ctrl: nt.Transform,
    ball_rev_ctrl: nt.Transform,
):
    """设置反转脚
    TODO:设置脚掌Pivot，将其完善为一个插件，包含界面，先摆放locater位置再生成反转脚

    Args:
        foot_ik_ctrl (nt.Transform): 脚部IK控制器,控制脚部变换
        toe_ik_ctrl (nt.Transform): 脚趾IK控制器,控制脚趾的旋转
        foot_ik_handle (nt.IkHandle): 脚部IK句柄
        ball_ik_handle (nt.IkHandle): 脚趾根IK句柄
        toe_ik_handle (nt.IkHandle): 脚尖IK句柄
        heel_rev_ctrl (nt.Transform): 脚跟反转控制器
        tip_rev_ctrl (nt.Transform): 脚尖反转控制器
        out_rev_ctrl (nt.Transform): 脚外侧反转控制器
        in_rev_ctrl (nt.Transform): 脚内侧反转控制器
        ball_rev_ctrl (nt.Transform): 脚趾根反转控制器
    """
    # 创建控制器列表
    foot_ctrls = [
        toe_ik_ctrl,
        heel_rev_ctrl,
        tip_rev_ctrl,
        out_rev_ctrl,
        in_rev_ctrl,
        ball_rev_ctrl,
    ]
    # 为控制器创建偏移组
    (
        toe_ik_ctrl_osg,
        heel_ctrl_osg,
        tip_ctrl_osg,
        out_ctrl_osg,
        in_ctrl_osg,
        ball_ctrl_osg,
    ) = addOffsetGroups(foot_ctrls)
    # 创建反转脚
    pm.parent(heel_ctrl_osg, foot_ik_ctrl)
    pm.parent(tip_ctrl_osg, heel_rev_ctrl)
    pm.parent(out_ctrl_osg, tip_rev_ctrl)
    pm.parent(in_ctrl_osg, out_rev_ctrl)
    pm.parent(toe_ik_ctrl_osg, in_rev_ctrl)
    pm.parent(ball_ctrl_osg, in_rev_ctrl)

    pm.parent(toe_ik_handle, toe_ik_ctrl)
    pm.parent(foot_ik_handle, ball_ik_handle, ball_rev_ctrl)
    pm.select(clear=True)


def addSpaceSwitching(
    target_node: nt.Transform,
    target_group: nt.Transform,
    switch_attributre: str,
    switch_constraint: str,
    driver_list: list[nt.Transform],
    enum_item_list=None,
) -> None:
    """为目标节点添加空间切换功能

    Args:
        target_node (nt.Transform): 要添加空间切换的目标节点
        target_group (nt.Transform): 要添加空间切换的目标节点的父级组
        switch_attributre (str): 要添加到目标节点的枚举属性名称，一般为"Follow"
        switch_constraint (str): 约束类型：parent，orient, point
        driver_list (list[nt.Transform]): 驱动节点列表
        enum_item_list (list[str]):要添加到目标节点的枚举项
    """
    if not enum_item_list:
        enum_item_list = [node.name() for node in driver_list]
    # 添加空间切换空间切换的枚举属性
    if not target_node.hasAttr(switch_attributre):
        target_node.addAttr(
            switch_attributre,
            attributeType="enum",
            enumName=":".join(enum_item_list),  # 枚举选项
            defaultValue=0,
            keyable=True,
        )
    # 创建定位器
    loc_list = []
    for node in driver_list:
        driver_loc = pm.spaceLocator(name=f"{node.name()}_loc")
        pm.hide(driver_loc)
        pm.parent(driver_loc, node)
        pm.matchTransform(driver_loc, target_node)
        loc_list.append(driver_loc)
    # 创建约束
    constraint_node = None
    if switch_constraint == "parent":
        constraint_node = pm.parentConstraint(
            loc_list, target_group, maintainOffset=True
        )
    elif switch_constraint == "orient":
        constraint_node = pm.orientConstraint(
            loc_list, target_group, maintainOffset=True
        )
    elif switch_constraint == "point":
        constraint_node = pm.pointConstraint(
            loc_list, target_group, maintainOffset=True
        )
    # 检查约束是否成功创建
    if not constraint_node:
        pm.warning(f"无效的约束类型: '{switch_constraint}'。空间切换设置失败。")
        return
    # 直接获取权重属性列表，而不是手动拼接字符串
    weight_alias_list = constraint_node.getWeightAliasList()
    # 连接节点
    for i, node in enumerate(driver_list):
        condition_node = pm.createNode(
            "condition", name=f"{enum_item_list[i]}_condition"
        )
        condition_node.operation.set(0)  # Equal
        condition_node.secondTerm.set(i)
        condition_node.colorIfTrueR.set(1)
        condition_node.colorIfFalseR.set(0)

        target_node.attr(switch_attributre).connect(condition_node.firstTerm)
        condition_node.outColorR.connect(weight_alias_list[i])


def seamless_space_switch(
    target_node: nt.Transform,
    target_group: nt.Transform,
    switch_attribute: str,
    new_space_index: int,
) -> None:
    """
    执行无缝的空间切换，确保目标节点在切换时世界空间位置不变。

    Args:
        target_node (nt.Transform): 带有空间切换属性的控制器。
        switch_attribute (str): 控制空间切换的枚举属性的名称 (例如 "Follow")。
        new_space_index (int): 要切换到的新空间的索引值 (枚举的整数值)。
    """
    # 为前一帧设置关键帧
    current_frame = pm.currentTime()
    pre_frame = current_frame - 1
    pm.setKeyframe(target_node.attr(switch_attribute), time=pre_frame)

    # 在切换前，记录下控制器当前的世界矩阵
    original_world_matrix = target_node.getMatrix(worldSpace=True)

    # 执行切换：设置枚举属性为新的值,这会导致 target_group 发生跳变
    try:
        target_node.attr(switch_attribute).set(new_space_index)
    except Exception as e:
        pm.warning(f"无法设置属性 '{switch_attribute}' 为 {new_space_index}。错误: {e}")
        return

    # 计算补偿矩阵
    ## 获取 target_group 在新位置下的世界矩阵及其逆矩阵
    new_parent_world_matrix = target_group.getMatrix(worldSpace=True)
    new_parent_world_inverse_matrix = new_parent_world_matrix.inverse()

    # 计算出控制器新的本地矩阵,新本地矩阵 = 旧世界矩阵 * 新父级逆世界矩阵
    new_local_matrix = original_world_matrix * new_parent_world_inverse_matrix

    # 应用新的本地变换到控制器上,使用TransformationMatrix来方便地提取平移和旋转值
    xform_matrix = dt.TransformationMatrix(new_local_matrix)
    translation = xform_matrix.getTranslation("world")
    # getRotation() 返回弧度(radians)，需要转换为角度(degrees)
    rotation = xform_matrix.getRotation()
    rotation_in_degrees = [dt.degrees(angle) for angle in rotation]
    # 设置位移和旋转
    target_node.translate.set(translation)
    target_node.rotate.set(rotation_in_degrees)

    # 在当前帧K上关键帧
    pm.setKeyframe(target_node, attribute=["translate", "rotate"])
    pm.setKeyframe(target_node.attr(switch_attribute))

    print(f"空间已切换到索引 {new_space_index}，并已自动K帧。")


def matrix_constraint(
    source_obj=None,
    target_obj=None,
    maintainOffset=True,
    translate=True,
    rotate=True,
    scale=True,
    target_is_joint=True,
):
    """
    矩阵约束.
    Args:
        source_obj (nt.Transform): 源对象.
        target_obj (nt.Transform): 目标对象.
        maintainOffset (bool): 是否保持偏移.
        translate (bool): 是否约束位移.
        rotate (bool): 是否约束旋转.
        scale (bool): 是否约束缩放.
        target_is_joint (bool): 目标对象是否为骨骼，如果是则移除jointOrient的影响.
    Returns:
        None
    """
    if not source_obj or not target_obj:
        selection = pm.selected()
        if len(selection) < 2:
            pm.warning("请选择至少两个对象：第一个是源对象，第二个是目标对象。")
            return None
        source_obj, target_obj = selection[0], selection[1]

    with pm.UndoChunk():
        # 通过目标对象世界矩阵左乘源对象世界逆矩阵获取两者之间的偏移矩阵
        offset_matrix = dt.Matrix()
        if maintainOffset:
            target_world_matrix = target_obj.worldMatrix[0].get()
            source_world_inverse_matrix = source_obj.worldInverseMatrix[0].get()
            offset_matrix = target_world_matrix * source_world_inverse_matrix
        node_sufix = f"{source_obj.name()}_to_{target_obj.name()}"
        # 矩阵乘法
        mult_matrix_node = pm.createNode("multMatrix", name=f"mult_matrix_{node_sufix}")
        mult_matrix_node.matrixIn[0].set(offset_matrix)
        source_obj.worldMatrix[0].connect(mult_matrix_node.matrixIn[1])
        target_obj.parentInverseMatrix[0].connect(mult_matrix_node.matrixIn[2])
        # 分解矩阵
        decompose_matrix_node = pm.createNode(
            "decomposeMatrix", name=f"decompose_matrix_{node_sufix}"
        )
        mult_matrix_node.matrixSum.connect(decompose_matrix_node.inputMatrix)
        # 连接变换
        if translate:
            decompose_matrix_node.outputTranslate.connect(target_obj.translate)
        if rotate:
            # 如果目标对象是骨骼，需要移除jointOrient的影响
            # jointOrient转化为四元数并取逆，被矩阵计算出的四元数相乘，来移除jointOrient的影响
            # if target_is_joint:
            #     # 创建所需的四元数节点
            #     eulerToQuat_node = pm.createNode(
            #         "eulerToQuat", name=f"eulerToQuat_{node_sufix}"
            #     )
            #     quatInvert_node = pm.createNode(
            #         "quatInvert", name=f"quatInvert_{node_sufix}"
            #     )
            #     quatProd_node = pm.createNode("quatProd", name=f"quatProd_{node_sufix}")
            #     quatToEuler_node = pm.createNode(
            #         "quatToEuler", name=f"quatToEuler_{node_sufix}"
            #     )
            #     # 连接节点
            #     target_obj.jointOrient.connect(eulerToQuat_node.inputRotate)
            #     eulerToQuat_node.outputQuat.connect(quatInvert_node.inputQuat)
            #     decompose_matrix_node.outputQuat.connect(quatProd_node.input1Quat)
            #     quatInvert_node.outputQuat.connect(quatProd_node.input2Quat)
            #     quatProd_node.outputQuat.connect(quatToEuler_node.inputQuat)
            #     quatToEuler_node.outputRotate.connect(target_obj.rotate)

            decompose_matrix_node.outputRotate.connect(target_obj.rotate)
            if target_is_joint:
                # 如果目标对象是骨骼，需要移除jointOrient的影响,直接置零，不再使用四元数计算以提高性能
                target_obj.jointOrient.set(dt.Vector())
        if scale:
            decompose_matrix_node.outputScale.connect(target_obj.scale)
        # 收尾
        print(f"成功创建从 '{source_obj.name()}' 到 '{target_obj.name()}' 的矩阵约束。")


def create_export_joints(source_jnts=None, sufix="exp"):
    """为绑定创建游戏引擎用的蒙皮导出骨骼"""
    if not source_jnts:
        source_jnts = pm.selected(type="joint")
    if not isinstance(source_jnts, list):
        source_jnts = [source_jnts]

    exp_jnt_list = []
    for jnt in source_jnts:
        pm.select(clear=True)
        exp_jnt = pm.joint(name=f"{jnt.name()}_{sufix}")
        pm.matchTransform(exp_jnt, jnt, position=True, rotation=True, scale=True)
        pm.makeIdentity(exp_jnt, apply=True)
        matrix_constraint(jnt, exp_jnt, maintainOffset=False, target_is_joint=True)
        exp_jnt_list.append(exp_jnt)
    return exp_jnt_list
