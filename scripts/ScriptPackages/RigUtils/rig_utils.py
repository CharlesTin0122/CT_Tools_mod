import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


# mGear Utiliyies
def addNPO(objs=None, *args):
    """Add a transform node as a neutral pose

    Add a transform node as a parent and in the same pose of each of the
    selected objects. This way neutralize the local transfromation
    values.
    NPO stands for "neutral position" terminology from the all mighty
    Softimage ;)

    """
    npoList = []

    if not objs:
        objs = pm.selected()
    if not isinstance(objs, list):
        objs = [objs]
    for obj in objs:
        oParent = obj.getParent()
        oTra = pm.createNode("transform", n=obj.name() + "_npo", p=oParent, ss=True)
        oTra.setTransformation(obj.getMatrix())
        pm.parent(obj, oTra)
        npoList.append(oTra)

    return npoList


def selectDeformers(*args):
    """Select the deformers from the object skinCluster"""

    oSel = pm.selected()[0]
    oColl = pm.skinCluster(oSel, query=True, influence=True)
    pm.select(oColl)


def replaceShape(source=None, targets=None, *args):
    """Replace the shape of one object by another.

    Args:
        source (None, PyNode): Source object with the original shape.
        targets (None, list of pyNode): Targets object to apply the
            source shape.
        *args: Maya's dummy

    Returns:

        None: Return non if nothing is selected or the source and targets
        are none

    """
    if not source and not targets:
        oSel = pm.selected()
        if len(oSel) < 2:
            pm.displayWarning("At less 2 objects must be selected")
            return None
        else:
            source = oSel[0]
            targets = oSel[1:]

    for target in targets:
        source2 = pm.duplicate(source)[0]
        shape = target.getShapes()
        cnx = []
        if shape:
            cnx = shape[0].listConnections(plugs=True, c=True)
            cnx = [[c[1], c[0].shortName()] for c in cnx]
            # Disconnect the conexion before delete the old shape
            for s in shape:
                for c in s.listConnections(plugs=True, c=True):
                    pm.disconnectAttr(c[0])
        pm.delete(shape)
        pm.parent(source2.getShapes(), target, r=True, s=True)

        for i, sh in enumerate(target.getShapes()):
            # Restore shapes connections
            for c in cnx:
                pm.connectAttr(c[0], sh.attr(c[1]))
            pm.rename(sh, target.name() + "_%s_Shape" % str(i))

        pm.delete(source2)


def addBlendedJoint(
    oSel=None, compScale=True, blend=0.5, name=None, select=True, *args
):
    """Create and gimmick blended joint

    Create a joint that rotate 50% of the selected joint. This operation is
    done using a pairBlend node.

    Args:
        oSel (None or joint, optional): If None will use the selected joints.
        compScale (bool, optional): Set the compScale option of the blended
            joint. Default is True.
        blend (float, optional): blend rotation value
        name (None, optional): Name for the blended o_node
        *args: Maya's dummy

    Returns:
        list: blended joints list

    """
    if not oSel:
        oSel = pm.selected()
    elif not isinstance(oSel, list):
        oSel = [oSel]
    jnt_list = []
    for x in oSel:
        if isinstance(x, pm.nodetypes.Joint):
            parent = x.getParent()
            if name:
                bname = "blend_" + name
            else:
                bname = "blend_" + x.name()

            jnt = pm.createNode("joint", n=bname, p=x)
            jnt_list.append(jnt)
            jnt.attr("radius").set(1.5)
            pm.parent(jnt, parent)
            o_node = pm.createNode("pairBlend")
            o_node.attr("rotInterpolation").set(1)
            pm.setAttr(o_node + ".weight", blend)
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

            jnt.attr("overrideEnabled").set(1)
            jnt.attr("overrideColor").set(17)

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
    """Add an extra joint to the blended joint.

    This is meant to be use with SDK for game style deformation.

    Args:
        oSel (None or blended joint, optional): If None will use the current
            selection.
        *args: Mays's dummy

    Returns:
        list: blended joints list

    """
    if not oSel:
        oSel = pm.selected()
    elif not isinstance(oSel, list):
        oSel = [oSel]

    jnt_list = []
    for x in oSel:
        if x.name().split("_")[0] == "blend":
            children = [
                item for item in pm.selected()[0].listRelatives(ad=True, type="joint")
            ]
            i = len(children)
            name = x.name().replace("blend", "blendSupport_%s" % str(i))
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


# Rig Utilities
def match_bind_jnt_to_ikfk_jnt(
    limb_setting_ctrl: nt.Transform,
    bind_jnt_list: list[nt.Joint],
    fk_jnt_list: list[nt.Joint],
    ik_jnt_list: list[nt.Joint],
):
    """轻量级IKFK骨骼约束主骨骼，使用blendColor节点代替ParentConstrain节点，ikfkSwitch属性：0为IK模式，1为FK模式

    Args:
        limb_setting_ctrl (nt.Transform): IKFK设置控制器
        bind_jnt_list (list[nt.Joint]): 主骨骼列表
        fk_jnt_list (list[nt.Joint]): FK骨骼列表
        ik_jnt_list (list[nt.Joint]): IK骨骼列表
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
