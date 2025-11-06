# -*- coding: utf-8 -*-
"""
@FileName      : joint_on_selected_vertexes.py
@DateTime      : 2024/06/12 19:34:10
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2024.2
@PythonVersion : python 3.10.8
@librarys      : pymel 1.4.0
@Description   :
"""

import math
import maya.api.OpenMaya as om
import pymel.core as pm
import pymel.core.datatypes as dt
import pymel.core.nodetypes as nt


def vector_to_euler(source_vector, target_vector, rotate_order=om.MEulerRotation.kXYZ):
    """计算从向量 A 旋转到向量 B 的欧拉角（度）
    1. 计算旋转轴和旋转角度
        1.旋转轴:用单位向量 u 和参考向量 ref (通常是一个全局轴，如(1,0,0))之间的叉积来计算旋转轴 rotation_axis
        2.旋转角度:用单位向量 u 和参考向量之间的点积和大小来计算旋转角度。
    2.将旋转轴和角度转化为欧拉角
        1.利用旋转轴和角度，可以构造旋转矩阵或四元数，然后从旋转矩阵或四元数中提取欧拉角。
    Args:
        source_vector (tuple): 源向量.
        target_vector (tuple): 目标向量.

    Returns:
        tuple: 欧拉角,单位为度
    """
    # 将输入向量和参考向量转换为MVector
    vector_a = om.MVector(source_vector).normalize()
    vector_b = om.MVector(target_vector).normalize()
    # 叉积求旋转轴
    axis = vector_a ^ vector_b
    # 点积求夹角
    dot = max(-1.0, min(1.0, vector_a * vector_b))  # 求点积：限制在-1:1
    angle = math.acos(dot)  # 求夹角：cos(x) = dot
    # 平行/反向处理
    if axis.length() < 1e-8:  # 当 A 和 B 几乎平行或几乎反向时
        if dot > 0:  # 如果点积大于零则说明同向
            return (0.0, 0.0, 0.0)  # 向量相同，无旋转
        else:
            # 反向：任选一个与 A 垂直方向作旋转轴。找 A 的任意正交向量。
            ortho = (
                om.MVector(1, 0, 0) if abs(vector_a.x) < 0.9 else om.MVector(0, 1, 0)
            )
            axis = (vector_a ^ ortho).normalize()
            angle = math.pi  # 180°
    else:
        axis.normalize()
    # 轴角 → 四元数
    quat = om.MQuaternion(angle, axis)
    # 四元数 → 欧拉
    euler = quat.asEulerRotation()
    # 确定旋转顺序，maya默认旋转顺序为：kXYZ,unreal为：kZXY，Unity：kYZX
    euler.reorder(rotate_order)
    # 返回欧拉旋转
    return (math.degrees(euler.x), math.degrees(euler.y), math.degrees(euler.z))


def joint_at_selected_vertexes(vertexes: list):
    """此函数计算所选顶点的中心点和中心法线并在中心点位置创建一个朝向中心法线的骨骼。

    Raises:
        RuntimeError: 未选择目标

    Returns:
        nt.Joint: 创建的骨骼对象
    """

    # 获取所选的定点数量
    vertexes_num = len(vertexes)
    # 创建两个变量用于接收顶点的位置和法线的和
    sum_pos = dt.Point([0, 0, 0])
    sum_normal = dt.Vector([0, 0, 0])
    # 遍历顶点
    for vertex in vertexes:
        vertex_pos = vertex.getPosition(space="world")  # 获取顶点的位置
        vertex_normal = vertex.getNormal()  # 获取顶点的法线
        sum_pos += vertex_pos  # 将顶点的位置加到总和中
        sum_normal += vertex_normal  # 将顶点的法线加到总和中

    # 计算顶点中心点和顶点法线的平均值向量
    center_point = sum_pos / vertexes_num
    center_normal = sum_normal / vertexes_num

    # 法线的平均值向量 转化为 欧拉角旋转，即法线的平均值向量和(1, 0, 0)向量之间的欧拉角(x,y,z)
    center_rotate = vector_to_euler(center_normal, target_vector=(1, 0, 0))
    pm.select(clear=True)  # 清除选择
    # 在 顶点中心点位置 创建 朝向顶点法线平均值向量 的骨骼
    creat_joint = pm.joint(position=center_point, orientation=center_rotate)
    # 返回该骨骼
    return creat_joint


def create_joint_per_mesh(sel_obj: list):
    """为每个选中的模型在边界框(bounding box)中心创建一个骨骼

    Args:
        sel_obj (list): 模型列表

    Returns:
        list: 骨骼列表
    """

    jnt_list = []  # 用于接收骨骼列表
    # 遍历选中的对象
    for obj in sel_obj:
        pm.select(cl=True)  # 清除选择
        center_position = obj.c.get()  # 获取对象中心位置
        jnt = pm.joint(
            name=f"jnt_{obj}", position=center_position
        )  # 在选中的对象的中心创建一个骨骼
        jnt_list.append(jnt)  # 将创建的骨骼添加到骨骼列表
    return jnt_list  # 返回骨骼列表


def create_joints():
    """创建骨骼

    Raises:
        RuntimeError: 未选择目标

    Returns:
        list: 骨骼列表
    """
    # 获取选中的对象
    select_objs = pm.ls(sl=True, flatten=True)
    # 判断是否有选中的对象
    if not select_objs:
        raise RuntimeError("请至少选择一个对象")
    # 如果所选对象为模型，则执行create_joint_per_mesh函数
    if isinstance(select_objs[0], nt.Transform):
        joint_list = create_joint_per_mesh(select_objs)
        return joint_list
    # 如果所选对象为顶点，则执行joint_at_selected_vertexes函数
    if isinstance(select_objs[0], pm.general.MeshVertex):
        creat_joint = joint_at_selected_vertexes(select_objs)
        return creat_joint


if __name__ == "__main__":
    create_joints()
