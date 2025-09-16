import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


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


if __name__ == "__main__":
    objs = pm.selected()
    if len(objs) == 5:
        root_controller = [0]
        ik_controller = objs[1]
        root_jnt = objs[2]
        mid_jnt = objs[3]
        end_jnt = objs[4]

        limb_stretch(
            root_ctrl=objs[0],
            ik_ctrl=objs[1],
            ik_jnt_01=objs[2],
            ik_jnt_02=objs[3],
            ik_jnt_03=objs[4],
            stretch_axis="x",
        )
    else:
        pm.warning("请按顺序选择4个物体：IK控制器, 根关节, 中间关节, 末端关节。")
