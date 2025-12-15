# -*- encoding: utf-8 -*-
"""
@File    :   rig_utils.py
@Time    :   2025/10/10 06:45:03
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   绑定常用函数
"""

import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt
from connectTwistSwing.connect_twist_swing_logic import connect_twist_swing


# Rig Utilities
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


def addBlendedJoint(
    base_joint=None, compScale=True, blend=0.5, name=None, select=True, *args
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
    if not base_joint:
        base_joint = pm.selected()
    elif not isinstance(base_joint, list):
        base_joint = [base_joint]
    # 用于储存混合骨骼
    jnt_list = []
    # 遍历所选骨骼
    for jnt in base_joint:
        # 获取骨骼父对象和混合骨骼名称
        if isinstance(jnt, pm.nodetypes.Joint):
            parent = jnt.getParent()
            if name:
                bname = f"{name}_blend"
            else:
                bname = f"{jnt.name()}_blend"
            # 创建骨骼，添加到列表，设置半径，设置父对象
            blend_jnt = pm.createNode("joint", n=bname, p=jnt)
            jnt_list.append(blend_jnt)
            blend_jnt.attr("radius").set(0.5)
            pm.parent(blend_jnt, parent)
            # 连接变换
            connect_twist_swing(
                driver=jnt,
                driven=blend_jnt,
                twist=0.5,
                swing=0.5,
                twist_axis="X",
            )
            jnt.translate.connect(blend_jnt.translate)
            jnt.scale.connect(blend_jnt.scale)
            # 设置混合骨骼颜色为黄色
            blend_jnt.attr("overrideEnabled").set(1)
            blend_jnt.attr("overrideColor").set(17)
            # 设置混合骨骼 分段缩放补偿
            blend_jnt.attr("segmentScaleCompensate").set(compScale)
            # 设置set以方便选择管理
            try:
                defSet = pm.PyNode("rig_deformers_grp")

            except TypeError:
                pm.sets(n="rig_deformers_grp")
                defSet = pm.PyNode("rig_deformers_grp")

            pm.sets(defSet, add=blend_jnt)
        else:
            pm.displayWarning(
                f"Blended Joint can't be added to: {jnt.name()}. Because is not type Joint"
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
        if "blend" in x.name():
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
            name = x.name().replace("blend", f"support_{i}")
            # 创建骨骼，添加列表，设置属性
            jnt = pm.createNode("joint", n=name, p=x)
            jnt_list.append(jnt)
            jnt.attr("radius").set(0.1)
            jnt.attr("overrideEnabled").set(1)
            jnt.attr("overrideColor").set(17)
            try:
                defSet = pm.PyNode("rig_deformers_grp")

            except pm.MayaNodeError:
                pm.sets(n="rig_deformers_grp")
                defSet = pm.PyNode("rig_deformers_grp")

            pm.sets(defSet, add=jnt)

        # 不需要blend_joint的情况
        else:
            # 获取所有子骨骼
            children = [
                item
                for item in pm.selected()[0].listRelatives(
                    allDescendents=True, type="joint"
                )
            ]
            # 获取子骨骼数量
            i = 0
            for obj in children:
                if "_support" in obj.name():
                    i += 1
            # 获取修形骨骼唯一命名
            name = f"{x.name()}_support_{i}"
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


def zero_joint_orient(jnts=None):
    """将骨骼的jointOrient属性置零"""
    if jnts is None:
        jnts = pm.selected()
    for jnt in jnts:
        if not isinstance(jnt, nt.Joint):
            pm.warning(f"{jnt} is not joint ,do not have jointOrient attribute.")
            continue
        jnt.jointOrient.set(dt.Vector())


def matrix_constraint(
    source_obj=None,
    target_obj=None,
    maintainOffset=True,
    translate=True,
    rotate=True,
    scale=True,
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
    Returns:
        None
    """
    # 验证参数
    if not source_obj or not target_obj:
        selection = pm.selected()
        if len(selection) < 2:
            pm.warning("请选择至少两个对象,最后一个对象为目标对象")
            return None
        source_obj, target_obj = selection[0], selection[1]

    with pm.UndoChunk():
        # 通过目标对象世界矩阵左乘源对象世界逆矩阵获取两者之间的偏移矩阵
        offset_matrix = dt.Matrix()
        if maintainOffset:
            target_world_matrix = target_obj.worldMatrix[0].get()
            source_world_inverse_matrix = source_obj.worldInverseMatrix[0].get()
            offset_matrix = target_world_matrix * source_world_inverse_matrix
        node_sufix = f"{source_obj}_to_{target_obj}"
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
            decompose_matrix_node.outputRotate.connect(target_obj.rotate)
            if isinstance(target_obj, nt.Joint):
                # 如果目标对象是骨骼，需要移除jointOrient的影响,直接置零以提高性能，不再使用四元数计算。
                target_obj.jointOrient.set(dt.Vector())
        if scale:
            decompose_matrix_node.outputScale.connect(target_obj.scale)
        # 收尾
        print(f"成功创建从 '{source_obj.name()}' 到 '{target_obj.name()}' 的矩阵约束。")


def create_export_joints(source_jnts=None, namespace="exp"):
    """为绑定创建游戏引擎用的蒙皮导出骨骼"""
    if not pm.namespace(exists=namespace):
        pm.namespace(addNamespace=namespace)
    if not source_jnts:
        source_jnts = pm.selected(type="joint")
    if not isinstance(source_jnts, list):
        source_jnts = [source_jnts]

    exp_jnt_list = []
    for jnt in source_jnts:
        pm.select(clear=True)
        exp_jnt = pm.joint(name=f"{namespace}:{jnt}")
        # 对齐变换，冻结变换
        pm.matchTransform(exp_jnt, jnt, position=True, rotation=True, scale=False)
        pm.makeIdentity(exp_jnt, apply=True)
        # 使用矩阵约束位移和旋转，缩放采用属性直连的方式，因为导出骨骼生成后还要进行骨骼父子连接，会导致缩放混乱
        matrix_constraint(
            jnt, exp_jnt, translate=True, rotate=True, scale=False, maintainOffset=True
        )
        jnt.scale.connect(exp_jnt.scale)
        exp_jnt_list.append(exp_jnt)
    return exp_jnt_list


# Rig Function
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
    ik_jnt_list: list[nt.Joint],
    stretch_axis: str = "x",
):
    """为三关节肢体创建可拉伸的IK系统。

    Args:
        root_ctrl (nt.Transform):  肢体根控制器
        ik_ctrl (nt.Transform):  肢体末端控制器
        ik_jnt_list (list[nt.Joint]): IK骨骼列表
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
    jnt_static_distance = 0
    for i in range(len(ik_jnt_list) - 1):
        pre_jnt_position = ik_jnt_list[i].getTranslation(space="world")
        post_jnt_position = ik_jnt_list[i + 1].getTranslation(space="world")
        distance = pre_jnt_position.distanceTo(post_jnt_position)
        jnt_static_distance += distance

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
    other_axes = [axis for axis in "xyz" if axis != stretch_axis.lower()]
    for jnt in ik_jnt_list:
        max_stretch_node.outColorR.connect(jnt.attr(f"scale{stretch_axis.upper()}"))

        maintain_volume_node.outputR.connect(jnt.attr(f"scale{other_axes[0].upper()}"))
        maintain_volume_node.outputR.connect(jnt.attr(f"scale{other_axes[1].upper()}"))
