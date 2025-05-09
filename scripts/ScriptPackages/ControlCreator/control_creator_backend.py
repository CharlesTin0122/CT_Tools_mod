import json
from pathlib import Path
import pymel.core as pc
import maya.cmds as cmds  # 使用 maya.cmds 获取组件的旋转轴心点


def get_script_directory():
    """获取脚本所在的目录，优先使用__file__，否则使用用户脚本目录"""
    try:
        # 如果是通过文件执行
        script_path = Path(__file__).resolve()
        return script_path.parent
    except NameError:
        # 如果是在Maya脚本编辑器中粘贴执行 (没有 __file__)
        # 使用Maya的用户脚本目录作为备选
        # 注意：这要求 control_shapes 文件夹在该用户脚本目录下
        user_script_dir = Path(cmds.internalVar(userScriptDir=True))
        return user_script_dir


def get_control_shapes_dir():
    return get_script_directory() / "control_shapes"


# 获取曲线信息 (与你提供的版本基本一致)
def get_curve_info(curve_transform):
    curve_shape = curve_transform.getShape()
    if not curve_shape or not isinstance(curve_shape, pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 不是一个有效的NURBS曲线，已跳过。")
        return None
    shape_name = curve_shape.name()  # 使用 .name() 以确保获取正确的长/短名称
    curve_data = {}
    curve_data["cvs"] = [
        list(cv) for cv in curve_shape.getCVs(space="object")
    ]  # 获取对象空间的CV点
    curve_data["knots"] = list(curve_shape.getKnots())
    curve_data["degree"] = curve_shape.degree()
    curve_data["form"] = curve_shape.form().index
    curve_data["overrideEnabled"] = curve_shape.overrideEnabled.get()
    curve_data["overrideRGBColors"] = curve_shape.overrideRGBColors.get()
    curve_data["overrideColorRGB"] = list(curve_shape.overrideColorRGB.get())
    curve_data["useOutlinerColor"] = curve_shape.useOutlinerColor.get()
    curve_data["outlinerColor"] = list(curve_shape.outlinerColor.get())
    return {shape_name: curve_data}


# 创建曲线 (修改: 返回offset group, 并处理颜色)
def create_curve_from_data(
    data, base_name="newCurve", new_color_index=None, new_rgb_color=None
):
    created_curves_info = []
    for shape_data_name, curve_data in data.items():
        # 如果 base_name 包含Maya不允许的字符，或者想用shape_data_name
        # 你可能需要一个更复杂的命名策略
        # 这里我们简单使用 base_name 作为前缀

        actual_shape_name = f"{base_name}Shape"  # 确保形状名和变换名有一定关联但不同
        transform_name = base_name

        cvs = [point[:3] for point in curve_data["cvs"]]
        knots = curve_data["knots"]
        degree = curve_data["degree"]
        form = curve_data["form"]

        # 创建曲线的变换节点，确保名称唯一
        temp_curve_transform = pc.curve(
            point=cvs,
            knot=knots,
            degree=degree,
            periodic=(form == 2),
            # name=transform_name # 先不指定名字，PyMel会自动处理，之后重命名
        )
        # 重命名变换节点和形状节点
        curve_transform = pc.rename(temp_curve_transform, transform_name)
        curve_shape = curve_transform.getShape()
        pc.rename(curve_shape, actual_shape_name)

        # 恢复保存的颜色属性
        if new_color_index is not None:  # 优先使用新指定的索引颜色
            curve_shape.overrideEnabled.set(True)
            curve_shape.overrideRGBColors.set(False)
            curve_shape.overrideColor.set(new_color_index)
        elif new_rgb_color is not None:  # 其次使用新指定的RGB颜色
            curve_shape.overrideEnabled.set(True)
            curve_shape.overrideRGBColors.set(True)
            curve_shape.overrideColorRGB.set(new_rgb_color)
        elif curve_data.get("overrideEnabled"):  # 否则尝试恢复保存的颜色
            curve_shape.overrideEnabled.set(curve_data["overrideEnabled"])
            curve_shape.overrideRGBColors.set(curve_data["overrideRGBColors"])
            if curve_data["overrideRGBColors"]:
                curve_shape.overrideColorRGB.set(curve_data["overrideColorRGB"])
            else:
                # 注意：原始get_curve_info没有保存overrideColor的索引值
                # 如果需要恢复索引颜色，需要在get_curve_info中添加 pc.getAttr(curve_shape + ".overrideColor")
                # 这里我们仅作演示，如果不是RGB，则不特别设置颜色索引，除非有新传入
                pass

        # 创建并返回 offset group
        offset_group_name = f"{curve_transform.name()}_offset"
        offset_group = pc.group(empty=True, name=offset_group_name)
        pc.parent(curve_transform, offset_group)

        # 清理曲线自身的变换 (使其相对于offset group是归零的)
        curve_transform.translate.set(0, 0, 0)
        curve_transform.rotate.set(0, 0, 0)
        curve_transform.scale.set(1, 1, 1)

        created_curves_info.append(
            {"offset_group": offset_group, "curve_transform": curve_transform}
        )

    # 如果只有一个曲线被创建，直接返回其信息，否则返回列表
    return (
        created_curves_info[0] if len(created_curves_info) == 1 else created_curves_info
    )


# 写入JSON (与你提供的版本一致)
def write_json_data(json_data: dict, json_name: str, subfolder="control_shapes"):
    module_path = (
        Path(__file__).resolve()
        if "__file__" in globals()
        else Path(cmds.internalVar(userScriptDir=True))
    )
    module_dir = (
        module_path.parent if "__file__" in globals() else module_path
    )  # 如果在脚本编辑器运行，可能没有parent

    target_dir = module_dir / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)  # 确保目录存在

    control_shapes_path = target_dir / (
        json_name if json_name.endswith(".json") else f"{json_name}.json"
    )

    try:
        with open(control_shapes_path, "w") as d:
            json.dump(json_data, d, indent=4)
        print(f"控制器形状已保存到: {control_shapes_path}")
    except IOError as e:
        pc.error(f"写入JSON文件失败: {e}")


# 读取JSON (与你提供的版本一致)
def read_json_data(json_name: str, subfolder="control_shapes"):
    module_path = (
        Path(__file__).resolve()
        if "__file__" in globals()
        else Path(cmds.internalVar(userScriptDir=True))
    )
    module_dir = module_path.parent if "__file__" in globals() else module_path

    control_shapes_path = (
        module_dir
        / subfolder
        / (json_name if json_name.endswith(".json") else f"{json_name}.json")
    )

    if not control_shapes_path.exists():
        pc.warning(f"JSON文件未找到: {control_shapes_path}")
        return None
    try:
        with open(control_shapes_path, "r") as r:
            json_data = json.load(r)
        return json_data
    except (IOError, json.JSONDecodeError) as e:
        pc.error(f"读取或解析JSON文件失败: {e}")
        return None


# -----------------------------------------------------------------------------
# 新增功能函数
# -----------------------------------------------------------------------------


def adjust_controller_size(controller_info_or_node, scale_factor):
    """
    调整控制器的大小。可以直接修改CV点。
    :param controller_info_or_node: create_curve_from_data返回的字典，或控制器的offset group/transform节点。
    :param scale_factor: 缩放因子，可以是单个浮点数或三元组/列表 [sx, sy, sz]。
    """
    curve_transform = None
    if (
        isinstance(controller_info_or_node, dict)
        and "curve_transform" in controller_info_or_node
    ):
        curve_transform = controller_info_or_node["curve_transform"]
    elif isinstance(controller_info_or_node, pc.nodetypes.Transform):
        # 如果是offset group，找到其下的curve transform
        children_shapes = controller_info_or_node.getShapes(type="nurbsCurve")
        if children_shapes:  # 输入是曲线变换节点本身
            curve_transform = controller_info_or_node
        else:  # 输入可能是offset group
            children_transforms = controller_info_or_node.getChildren(type="transform")
            for child in children_transforms:
                if child.getShape(type="nurbsCurve"):
                    curve_transform = child
                    break
        if not curve_transform:
            pc.warning("未能从输入中找到有效的曲线变换节点进行缩放。")
            return
    else:
        pc.warning("adjust_controller_size需要控制器信息字典或PyNode变换节点。")
        return

    curve_shape = curve_transform.getShape()
    if not curve_shape or not isinstance(curve_shape, pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 没有有效的NURBS曲线形状。")
        return

    if isinstance(scale_factor, (int, float)):
        s = [scale_factor, scale_factor, scale_factor]
    elif isinstance(scale_factor, (list, tuple)) and len(scale_factor) == 3:
        s = list(scale_factor)
    else:
        pc.warning("scale_factor 必须是一个数字或包含三个数字的列表/元组。")
        return

    # 获取CV点，在对象空间进行缩放，然后设置回去
    # 这种方式会保持曲线的枢轴点(pivot)在原位进行缩放
    cvs = curve_shape.getCVs(space="object")
    scaled_cvs = [pc.dt.Point(cv[0] * s[0], cv[1] * s[1], cv[2] * s[2]) for cv in cvs]
    curve_shape.setCVs(scaled_cvs, space="object")
    curve_shape.updateCurve()  # 更新曲线显示
    print(f"控制器 {curve_transform.name()} 的大小已调整。")


def match_to_joint(controller_info_or_offset_group, joint_node):
    """
    将控制器的offset group匹配到骨骼的位置和旋转。
    :param controller_info_or_offset_group: create_curve_from_data返回的字典，或控制器的offset group节点。
    :param joint_node: 目标骨骼 (PyNode)。
    """
    offset_group = None
    if (
        isinstance(controller_info_or_offset_group, dict)
        and "offset_group" in controller_info_or_offset_group
    ):
        offset_group = controller_info_or_offset_group["offset_group"]
    elif isinstance(controller_info_or_offset_group, pc.nodetypes.Transform):
        offset_group = controller_info_or_offset_group  # 假设直接传入了offset group
    else:
        pc.warning("match_to_joint需要控制器信息字典或PyNode offset group节点。")
        return

    if not isinstance(joint_node, pc.nodetypes.Joint):
        pc.warning(f"{joint_node.name()} 不是一个骨骼节点。")
        return

    # 使用pc.matchTransform进行匹配，更简洁且能处理父子约束等复杂情况下的匹配
    pc.matchTransform(
        offset_group, joint_node, position=True, rotation=True, scale=False
    )  # 通常不匹配骨骼的缩放给控制器

    # 或者手动获取和设置：
    # world_pos = joint_node.getTranslation(space='world')
    # world_rot = joint_node.getRotation(space='world', quaternion=False) # 获取欧拉角
    # offset_group.setTranslation(world_pos, space='world')
    # offset_group.setRotation(world_rot, space='world')

    print(f"控制器 {offset_group.name()} 已匹配到骨骼 {joint_node.name()}。")


def orient_controller_cvs(controller_info_or_node, rotation_xyz_degrees):
    """
    通过旋转CV点来调整控制器的局部朝向。
    旋转是相对于曲线对象空间的轴心进行的。
    :param controller_info_or_node: create_curve_from_data返回的字典，或控制器的offset group/transform节点。
    :param rotation_xyz_degrees: 包含X, Y, Z轴旋转角度（度数）的列表/元组。
    """
    curve_transform = None
    if (
        isinstance(controller_info_or_node, dict)
        and "curve_transform" in controller_info_or_node
    ):
        curve_transform = controller_info_or_node["curve_transform"]
    elif isinstance(controller_info_or_node, pc.nodetypes.Transform):
        children_shapes = controller_info_or_node.getShapes(type="nurbsCurve")
        if children_shapes:
            curve_transform = controller_info_or_node
        else:
            children_transforms = controller_info_or_node.getChildren(type="transform")
            for child in children_transforms:
                if child.getShape(type="nurbsCurve"):
                    curve_transform = child
                    break
        if not curve_transform:
            pc.warning("未能从输入中找到有效的曲线变换节点进行定向。")
            return
    else:
        pc.warning("orient_controller_cvs需要控制器信息字典或PyNode变换节点。")
        return

    curve_shape = curve_transform.getShape()
    if not curve_shape or not isinstance(curve_shape, pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 没有有效的NURBS曲线形状。")
        return

    if not (
        isinstance(rotation_xyz_degrees, (list, tuple))
        and len(rotation_xyz_degrees) == 3
    ):
        pc.warning("rotation_xyz_degrees 必须是一个包含三个数字的列表/元组。")
        return

    # 获取曲线的旋转轴心点 (通常是 (0,0,0) 在对象空间，因为我们已经清理过变换)
    # 注意: pc.rotate() 的 objectCenterPivot 参数在某些PyMel版本中可能不直接作用于组件。
    # 我们需要在对象空间旋转CV点，而曲线的变换节点的translate/rotate应该是0。
    # 因此，在对象空间中，旋转中心就是(0,0,0)。
    pivot_point = (0, 0, 0)

    # PyMel的 pc.rotate 在组件模式下有时行为不符合预期，特别是pivot。
    # 使用 maya.cmds 来旋转组件通常更可靠。
    cv_components = [
        f"{curve_shape.name()}.cv[{i}]" for i in range(curve_shape.numCVs())
    ]
    if cv_components:
        cmds.rotate(
            rotation_xyz_degrees[0],
            rotation_xyz_degrees[1],
            rotation_xyz_degrees[2],
            cv_components,
            objectSpace=True,  # 在对象空间旋转
            pivot=pivot_point,
            relative=True,
        )  # 相对旋转
        curve_shape.updateCurve()
        print(f"控制器 {curve_transform.name()} 的CV点已旋转。")
    else:
        print(f"控制器 {curve_transform.name()} 没有CV点可旋转。")


# -----------------------------------------------------------------------------
# 主函数/示例用法
# -----------------------------------------------------------------------------
def main_tool_example():
    # --- 1. 保存一个选定的曲线作为预设 (可选步骤) ---
    # 首先在Maya中手动创建一个NURBS曲线并选中它
    # selection = pc.selected()
    # if selection and isinstance(selection[0], pc.nodetypes.Transform) and selection[0].getShape(type="nurbsCurve"):
    #     selected_curve_transform = selection[0]
    #     curve_info_dict = get_curve_info(selected_curve_transform)
    #     if curve_info_dict:
    #         # 使用曲线变换节点的名称作为文件名 (移除非法字符)
    #         base_filename = selected_curve_transform.name().replace(":", "_").replace("|", "_")
    #         write_json_data(curve_info_dict, f"{base_filename}_shape")
    # else:
    #     print("请先选择一个NURBS曲线以保存其形状。")

    # --- 2. 从JSON文件加载并创建控制器 ---
    # 假设我们有一个名为 "circle_shape.json" 的预设文件在 "control_shapes" 文件夹中
    # 你可以先运行上面的保存部分，例如创建一个圆并命名为 "circle"，它会保存为 "circle_shape.json"

    json_to_load = (
        "circle.json"  # 替换为你实际的JSON文件名 (例如之前保存的 "myCube_shape.json")
    )
    # 你提供的原始列表里有 "circle.json"

    loaded_data = read_json_data(json_to_load)

    if loaded_data:
        # 创建控制器，可以指定基础名称和颜色
        # Maya 颜色索引: 6=蓝色, 13=红色, 17=黄色, 14=绿色 等
        controller_creation_info = create_curve_from_data(
            loaded_data, base_name="myNewCtrl", new_color_index=17
        )  # 黄色

        if not controller_creation_info:
            print(f"从 {json_to_load} 创建控制器失败。")
            return

        # controller_creation_info 现在是 {"offset_group": offset_group_node, "curve_transform": curve_node}
        offset_grp = controller_creation_info["offset_group"]
        # curve_trans = controller_creation_info["curve_transform"] # 如果需要直接操作曲线变换节点

        print(f"控制器 {offset_grp.name()} 已创建。")

        # --- 3. 调整控制器大小 ---
        # 将控制器放大到原来的1.5倍
        adjust_controller_size(offset_grp, 1.5)
        # 或者分别调整X, Y, Z轴的大小
        # adjust_controller_size(offset_grp, [2.0, 1.0, 1.0])

        # --- 4. 将控制器匹配到骨骼 ---
        # 假设场景中有一个名为 "joint1" 的骨骼
        # 在实际使用中，你可能需要让用户选择骨骼
        try:
            target_joint = pc.PyNode("joint1")  # 尝试获取场景中的joint1
            if pc.objExists(target_joint) and isinstance(
                target_joint, pc.nodetypes.Joint
            ):
                match_to_joint(offset_grp, target_joint)
            else:
                print(
                    "场景中未找到名为 'joint1' 的骨骼，跳过匹配步骤。请创建一个骨骼或修改脚本中的骨骼名称。"
                )
        except pc.MayaNodeError:
            print(
                "场景中未找到名为 'joint1' 的骨骼，跳过匹配步骤。请创建一个骨骼或修改脚本中的骨骼名称。"
            )

        # --- 5. 调整控制器朝向 (旋转CV点) ---
        # 例如，将控制器的CV点沿其局部X轴旋转90度
        orient_controller_cvs(offset_grp, [90, 0, 0])
        # 再沿其局部Y轴旋转45度
        # orient_controller_cvs(offset_grp, [0, 45, 0])

        print(f"控制器工具示例操作完成: {offset_grp.name()}")
        pc.select(offset_grp)  # 选中最终的控制器组以便查看
    else:
        print(
            f"未能从 {json_to_load} 加载数据。请确保文件存在于 'control_shapes' 子目录中。"
        )


if __name__ == "__main__":
    # 清理场景以便测试 (可选)
    # pc.select(all=True)
    # pc.delete()
    # pc.joint(name="joint1", p=(2,3,0)) # 创建一个示例骨骼

    # 运行示例
    main_tool_example()
