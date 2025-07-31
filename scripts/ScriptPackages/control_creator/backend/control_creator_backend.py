import json
import math
import pymel.core as pc
import pymel.core.datatypes as dt
from pathlib import Path
from ..utils.path_manager import PathManager
from ..utils.color_manager import ColorManager
from ..utils.curve_utils import get_curve_info, validate_nurbs_curve, extract_curve_data


def create_single_curve(curve_data, transform_name):
    """创建单条 NURBS 曲线"""
    cvs = [point[:3] for point in curve_data["cvs"]]
    knots = curve_data["knots"]
    degree = curve_data["degree"]
    form = curve_data["form"]
    return pc.curve(
        point=cvs,
        knot=knots,
        degree=degree,
        periodic=(form == 2),
    )


def merge_curves(temp_curve_transforms, transform_name):
    """合并多条曲线到一个变换节点"""
    parent_transform = temp_curve_transforms[0]
    if len(temp_curve_transforms) > 1:
        for transform in temp_curve_transforms[1:]:
            child_shape = transform.getShape()
            try:
                pc.parent(child_shape, parent_transform, shape=True, relative=True)
                pc.delete(transform)
            except Exception as e:
                pc.warning(f"合并曲线失败: {e}")
    return pc.rename(parent_transform, transform_name)


def create_curve_from_data(
    data, base_name="newCurve", new_color_index=None, new_rgb_color=None
):
    """根据曲线数据创建控制器"""
    temp_curve_transforms = []
    transform_name = f"{base_name}_ctrl"
    actual_shape_name = f"{transform_name}Shape"
    color_manager = ColorManager()

    for shape_data_name, curve_data in data.items():
        temp_curve_transform = create_single_curve(curve_data, transform_name)
        temp_curve_transforms.append(temp_curve_transform)

    curve_transform = merge_curves(temp_curve_transforms, transform_name)
    curve_shapes = curve_transform.getShapes()
    for i, curve_shape in enumerate(curve_shapes):
        pc.rename(curve_shape, f"{actual_shape_name}_{i}")
        color_manager.apply_color_to_curve(
            curve_shape, curve_data, new_color_index, new_rgb_color
        )

    offset_group_name = f"{curve_transform.name()}_offset"
    offset_group = pc.group(empty=True, name=offset_group_name)
    pc.parent(curve_transform, offset_group)
    curve_transform.translate.set(0, 0, 0)
    curve_transform.rotate.set(0, 0, 0)
    curve_transform.scale.set(1, 1, 1)

    return {"offset_group": offset_group, "curve_transform": curve_transform}


def write_json_data(json_data: dict, json_name: str, subfolder="control_shapes"):
    """写入控制器形状到 JSON 文件"""
    target_path = PathManager.get_control_shapes_dir(subfolder) / (
        json_name if json_name.endswith(".json") else f"{json_name}.json"
    )
    target_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(target_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
        pc.displayInfo(f"控制器形状已保存到: {target_path}")
    except PermissionError:
        pc.error(f"无权限写入文件: {target_path}")
    except json.JSONEncodeError:
        pc.error(f"JSON 数据编码失败: {json_data}")
    except Exception as e:
        pc.error(f"写入 JSON 文件时发生未知错误: {e}")


def read_json_data(json_name: str, subfolder="control_shapes"):
    """从 JSON 文件读取控制器形状"""
    target_path = PathManager.get_control_shapes_dir(subfolder) / (
        json_name if json_name.endswith(".json") else f"{json_name}.json"
    )
    if not target_path.exists():
        pc.warning(f"JSON 文件未找到: {target_path}")
        return None
    try:
        with open(target_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        pc.error(f"JSON 文件格式错误: {target_path}")
    except PermissionError:
        pc.error(f"无权限读取文件: {target_path}")
    except Exception as e:
        pc.error(f"读取 JSON 文件时发生未知错误: {e}")
    return None


def adjust_controller_size(controller_info_or_node, scale_factor):
    """调整控制器大小"""
    curve_transform = _get_curve_transform(controller_info_or_node)
    if not curve_transform:
        return
    curve_shapes = curve_transform.getShapes()
    if not curve_shapes or not isinstance(curve_shapes[0], pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 没有有效的 NURBS 曲线形状。")
        return
    s = (
        [float(scale_factor)] * 3
        if isinstance(scale_factor, (int, float))
        else list(scale_factor)
    )
    if len(s) != 3:
        pc.warning("scale_factor 必须是数字或三元组。")
        return
    # 使用 pc.xform 调整 CV 点，支持撤销
    for curve_shape in curve_shapes:
        for i in range(curve_shape.numCVs()):
            pc.xform(curve_shape.cv[i], scale=s, relative=True)
        curve_shape.updateCurve()
    pc.displayInfo(f"控制器 {curve_transform.name()} 的大小已调整。")


def match_to_joint(controller_info_or_node, joint_node):
    """将控制器匹配到骨骼位置和旋转"""
    offset_group = None
    if (
        isinstance(controller_info_or_node, dict)
        and "offset_group" in controller_info_or_node
    ):
        offset_group = controller_info_or_node["offset_group"]
    elif isinstance(controller_info_or_node, pc.nodetypes.Transform):
        offset_group = controller_info_or_node
    else:
        pc.warning("需要控制器信息字典或 offset group 节点。")
        return
    if not isinstance(joint_node, pc.nodetypes.Joint):
        pc.warning(f"{joint_node.name()} 不是骨骼节点。")
        return
    pc.matchTransform(
        offset_group, joint_node, position=True, rotation=True, scale=False
    )
    pc.displayInfo(f"控制器 {offset_group.name()} 已匹配到骨骼 {joint_node.name()}。")


def orient_controller_cvs(controller_info_or_node, rotation_xyz_degrees):
    """通过旋转 CV 点调整控制器朝向"""
    curve_transform = _get_curve_transform(controller_info_or_node)
    if not curve_transform:
        return
    curve_shapes = curve_transform.getShapes()
    if not curve_shapes or not isinstance(curve_shapes[0], pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 没有有效的 NURBS 曲线形状。")
        return
    if (
        not isinstance(rotation_xyz_degrees, (list, tuple))
        or len(rotation_xyz_degrees) != 3
    ):
        pc.warning("rotation_xyz_degrees 必须是包含三个数字的列表/元组。")
        return
    # 开启撤销块
    pc.undoInfo(openChunk=True, chunkName="OrientControllerCVs")
    try:
        # 构建旋转矩阵
        rot_rad = [math.radians(deg) for deg in rotation_xyz_degrees]
        rot_matrix = dt.Matrix(dt.EulerRotation(rot_rad, unit="radians").asMatrix())
        pivot_point = curve_transform.getRotatePivot(space="object")
        for curve_shape in curve_shapes:
            cvs = curve_shape.getCVs(space="object")
            transformed_cvs = []
            for cv in cvs:
                # 相对于 pivot_point 旋转
                cv_vec = dt.Vector(cv) - pivot_point
                rotated_vec = cv_vec * rot_matrix + pivot_point
                transformed_cvs.append(rotated_vec)
            # 使用 setCVs 更新 CV 点，支持撤销
            curve_shape.setCVs(transformed_cvs, space="object")
            curve_shape.updateCurve()
            pc.displayInfo(f"控制器 {curve_shape.name()} 的 CV 点已旋转。")
    finally:
        pc.undoInfo(closeChunk=True)


def _get_curve_transform(controller_info_or_node):
    """从控制器信息或节点获取曲线变换节点"""
    if (
        isinstance(controller_info_or_node, dict)
        and "curve_transform" in controller_info_or_node
    ):
        return controller_info_or_node["curve_transform"]
    elif isinstance(controller_info_or_node, pc.nodetypes.Transform):
        children_shapes = controller_info_or_node.getShapes(type="nurbsCurve")
        if children_shapes:
            return controller_info_or_node
        children_transforms = controller_info_or_node.getChildren(type="transform")
        for child in children_transforms:
            if child.getShape(type="nurbsCurve"):
                return child
    pc.warning("无法找到有效的曲线变换节点。")
    return None


def run_control_creator_example():
    """示例：创建并调整控制器"""
    json_to_load = "circle.json"
    loaded_data = read_json_data(json_to_load)
    if not loaded_data:
        pc.warning(f"无法加载 {json_to_load}，请确保文件存在。")
        return
    controller_info = create_curve_from_data(
        loaded_data, base_name="myNewCtrl", new_color_index=17
    )
    if not controller_info:
        pc.error("创建控制器失败。")
        return
    adjust_controller_size(controller_info, 1.5)
    try:
        target_joint = pc.PyNode("joint1")
        if pc.objExists(target_joint) and isinstance(target_joint, pc.nodetypes.Joint):
            match_to_joint(controller_info, target_joint)
        else:
            pc.displayInfo("未找到 'joint1'，跳过匹配。")
    except pc.MayaNodeError:
        pc.displayInfo("未找到 'joint1'，跳过匹配。")
    orient_controller_cvs(controller_info, [90, 0, 0])
    pc.select(controller_info["offset_group"])
    pc.displayInfo(f"控制器工具示例完成: {controller_info['offset_group'].name()}")


if __name__ == "__main__":
    run_control_creator_example()
