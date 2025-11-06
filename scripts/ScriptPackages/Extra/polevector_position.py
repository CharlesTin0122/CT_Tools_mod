import pymel.core as pm


def set_polevector_position(jnt1, jnt2, jnt3, pv_ctrl, ctrl_distance=50.0):
    """
    利用向量来计算极向量约束控制器的位置
    Args:
        jnt1 (nt.Joint): 第一节骨骼名称
        jnt2 (nt.Joint): 第二节骨骼名称
        jnt3 (nt.Joint): 第三节骨骼名称
        pv_ctrl (nt.Transform): 极向量控制器名称
        ctrl_length_scale (float): 极向量控制器和骨骼距离的缩放值

    Returns: Vector

    """
    # 获取参数，并转换为Pymel对象
    jnt1_pos = jnt1.getTranslation(ws=True)
    jnt2_pos = jnt2.getTranslation(ws=True)
    jnt3_pos = jnt3.getTranslation(ws=True)
    # 获取胯骨指向脚的向量
    thigh_foot_vec = jnt3_pos - jnt1_pos
    # 获取胯骨指向膝盖的向量的向量
    thigh_knee_vec = jnt2_pos - jnt1_pos
    # 将胯膝向量向腿脚向量投影，获得该投影位置
    knee_projection_vec = thigh_knee_vec.projectionOnto(thigh_foot_vec)
    # 将投影向量移动到腿上，之前向量起点为原点
    mid_pos = jnt1_pos + knee_projection_vec
    # 获得投影点指向膝盖点的向量，再乘以一个缩放系数，得到极向量，再讲极向量移动到膝盖点
    knee_ctrl_vector = (jnt2_pos - mid_pos).normal()
    distance_vec = knee_ctrl_vector * ctrl_distance
    ctrl_pos = jnt2_pos + distance_vec
    # 设置控制器位置
    pv_ctrl.setTranslation(ctrl_pos)
    return ctrl_pos


if __name__ == "__main__":
    """依次选择三个骨骼对象和一个控制器对象，然后执行脚本，
    控制器就被摆放在正确的位置上,通过ctrl_length_scale数值来调整控制器和骨骼距离。
    """
    jnt_1, jnt_2, jnt_3, ctrl_pv = pm.selected()
    set_polevector_position(jnt_1, jnt_2, jnt_3, ctrl_pv, 20)
