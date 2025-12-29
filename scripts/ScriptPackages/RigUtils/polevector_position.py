import pymel.core as pm
import pymel.core.datatypes as dt


def calculate_polevector(jnt1, jnt2, jnt3, pv_ctrl, ctrl_distance=50.0):
    """
    利用向量投影计算极向量控制器的位置。

    Args:
        jnt1, jnt2, jnt3 (nt.Joint): 链式骨骼的三个节点（如 胯、膝、脚）
        pv_ctrl (nt.Transform): 需要定位的控制器
        ctrl_distance (float): 控制器远离膝盖的距离
    """
    # 1. 获取世界坐标位置
    pos1 = dt.Vector(pm.xform(jnt1, q=True, ws=True, t=True))
    pos2 = dt.Vector(pm.xform(jnt2, q=True, ws=True, t=True))
    pos3 = dt.Vector(pm.xform(jnt3, q=True, ws=True, t=True))

    # 2. 计算向量
    line_vec = pos3 - pos1  # 起点到末端的向量
    knee_vec = pos2 - pos1  # 起点到中间点的向量

    # 3. 计算中间点在连线上的投影位置
    # projectionOnto 会返回膝盖点在 line_vec 上的投影分量
    projection = knee_vec.projectionOnto(line_vec)
    mid_point = pos1 + projection

    # 4. 计算从投影点指向膝盖的方向向量（即极向量方向）
    pv_direction = pos2 - mid_point

    # 安全检查：如果骨骼是完全笔直的，pv_direction 长度为 0
    if pv_direction.length() < 0.001:
        pm.warning("骨骼处于完全笔直状态，无法准确计算极向量平面。")
        # 此时可以默认给一个轴向，或者提示用户稍微弯曲骨骼
        return None

    # 5. 归一化并计算最终位置
    final_pos = pos2 + (pv_direction.normal() * ctrl_distance)

    # 6. 设置控制器位置
    pm.xform(pv_ctrl, ws=True, t=final_pos)

    return final_pos


def set_polevector_position():
    sel = pm.selected()
    if len(sel) == 4:
        # 解包选择：前三个为骨骼，最后一个为控制器
        j1, j2, j3, ctrl = sel
        calculate_polevector(j1, j2, j3, ctrl, ctrl_distance=50.0)
    else:
        pm.error("请依次选择三个骨骼（父->子）和一个控制器对象。")
