import math
import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt


def unit_vector_to_euler_angles(unit_vector, reference_vector=(1, 0, 0)):
    """将方向向量转换为欧拉角"""
    u = dt.Vector(unit_vector).normal()
    ref = dt.Vector(reference_vector).normal()

    # 处理向量平行的情况
    dot = ref.dot(u)
    if abs(dot) > 0.9999:
        return (0, 0, 180.0) if dot < 0 else (0, 0, 0)

    rotation_axis = ref ^ u
    rotation_axis.normalize()
    angle = ref.angle(u)

    quaternion = dt.Quaternion(angle, rotation_axis)
    euler_rotation = quaternion.asEulerRotation()
    return [math.degrees(x) for x in euler_rotation.asVector()]


def joint_at_selected_vertexes(vertexes):
    """计算顶点中心点和平均法线方向并创建骨骼"""
    vertexes_num = len(vertexes)
    sum_pos = dt.Point([0, 0, 0])
    sum_normal = dt.Vector([0, 0, 0])

    for vertex in vertexes:
        # 统一使用世界坐标空间
        sum_pos += vertex.getPosition(space="world")
        sum_normal += vertex.getNormal(space="world")

    center_point = sum_pos / vertexes_num
    # 归一化平均法线，确保向量转换准确
    center_normal = sum_normal.normal()

    center_rotate = unit_vector_to_euler_angles(center_normal)

    pm.select(clear=True)
    # 使用 orientation 设置初始朝向
    new_joint = pm.joint(p=center_point, o=center_rotate, name="vtx_joint_1")
    return new_joint


def create_joints():
    """主入口函数"""
    selection = pm.ls(sl=True, flatten=True)
    if not selection:
        pm.warning("未选择任何对象，请选择顶点或模型。")
        return

    # 按照选择类型分流
    if isinstance(selection[0], pm.general.MeshVertex):
        return joint_at_selected_vertexes(selection)

    elif isinstance(selection[0], nt.Transform):
        jnt_list = []
        for obj in selection:
            pm.select(cl=True)
            # 获取世界坐标下的边界框中心
            center = obj.getBoundingBox(space="world").center()
            jnt = pm.joint(name=f"jnt_{obj.nodeName()}", p=center)
            jnt_list.append(jnt)
        return jnt_list


if __name__ == "__main__":
    create_joints()
