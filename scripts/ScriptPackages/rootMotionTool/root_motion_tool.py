# -*- encoding: utf-8 -*-
"""
@File    :   root_motion_tool_01.py
@Time    :   2025/04/27 18:01:03
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

import math
import pymel.core as pc

root_name = "bone_0"
pelvis_name = "bone_1"

root_motion_tx = False
root_motion_ty = True
root_motion_tz = False

root_motion_rx = False
root_motion_ry = False
root_motion_rz = True


def get_unique_name(base_name):
    """在场景中生成一个唯一的名称."""
    name = base_name
    counter = 1
    while pc.objExists(name):
        name = f"{base_name}_{counter}"
        counter += 1
    return name


def Inplace_to_RootMotion(root_name, pelvis_name):
    """
    在maya中转换原地动画为根动画.

    Args:
                    root_name (str): 根骨骼名称.
                    pelvis_name (str): 胯骨骼名称

    Raises:
                    ValueError: 如果对象不存在.
    """
    # 验证输入参数
    if not pc.objExists(root_name):
        raise ValueError(f"Root bone '{root_name}' does not exist in the scene.")
    if not pc.objExists(pelvis_name):
        raise ValueError(f"Pelvis bone '{pelvis_name}' does not exist in the scene.")

    # 获取动画时间范围
    firstFrame = math.floor(pc.findKeyframe(pelvis_name, which="first"))
    lastFrame = math.ceil(pc.findKeyframe(pelvis_name, which="last"))
    pc.currentTime(firstFrame)
    # 用唯一的名称创建定位器
    loc_root = pc.spaceLocator(name=get_unique_name("loc_root"))
    loc_pelvis = pc.spaceLocator(name=get_unique_name("loc_pelvis"))

    try:
        # 骨骼约束定位器
        loc_root_constr = pc.parentConstraint(root_name, loc_root)
        loc_pelvis_constr = pc.parentConstraint(pelvis_name, loc_pelvis)

        # 烘焙定位器动画
        pc.bakeResults(
            loc_root, loc_pelvis, time=(firstFrame, lastFrame), sparseAnimCurveBake=True
        )

        # 删除约束节点
        pc.delete(loc_root_constr, loc_pelvis_constr)

        # 胯定位器分别用点约束和方向约束约束根定位器
        loc_point_contr = pc.pointConstraint(loc_pelvis, loc_root, maintainOffset=True)
        loc_orient_contr = pc.orientConstraint(
            loc_pelvis, loc_root, maintainOffset=True
        )

        # 烘焙动画
        pc.bakeResults(
            loc_root,
            time=(firstFrame, lastFrame),
            sparseAnimCurveBake=True,
            minimizeRotation=True,
        )
        # 删除约束节点
        pc.delete(loc_point_contr, loc_orient_contr)

        # 执行欧拉过滤器防止跳变
        pc.filterCurve(loc_root, filter="euler")
        # 根据根动画所需属性修改跟定位器动画
        if not root_motion_tx:
            loc_root.translateX.disconnect()
            pc.setKeyframe(loc_root.translateX)
        if not root_motion_ty:
            loc_root.translateY.disconnect()
            pc.setKeyframe(loc_root.translateY)
        if not root_motion_tz:
            loc_root.translateZ.disconnect()
            pc.setKeyframe(loc_root.translateZ)
        if not root_motion_rx:
            loc_root.rotateX.disconnect()
            pc.setKeyframe(loc_root.rotateX)
        if not root_motion_ry:
            loc_root.rotateY.disconnect()
            pc.setKeyframe(loc_root.rotateY)
        if not root_motion_rz:
            loc_root.rotateZ.disconnect()
            pc.setKeyframe(loc_root.rotateZ)

        # 定位器约束骨骼
        jnt_root_constr = pc.parentConstraint(loc_root, root_name)
        jnt_pelvis_constr = pc.parentConstraint(loc_pelvis, pelvis_name)

        # 烘焙最终动画到骨骼
        pc.bakeResults(
            root_name,
            pelvis_name,
            time=(firstFrame, lastFrame),
            sparseAnimCurveBake=True,
        )
        # 删除约束节点
        pc.delete(jnt_root_constr, jnt_pelvis_constr)
        # 执行欧拉过滤器
        pc.filterCurve(root_name, pelvis_name, filter="euler")
    finally:
        # 清理定位器
        pc.delete([obj for obj in [loc_root, loc_pelvis] if pc.objExists(obj)])


# TODO : 根动画转换为原地动画
def RootMotion_to_Inplace(root_name, pelvis_name, foot_l_name=None, foot_r_name=None):
    # 验证输入参数
    if not pc.objExists(root_name):
        raise ValueError(f"Root bone '{root_name}' does not exist in the scene.")
    if not pc.objExists(pelvis_name):
        raise ValueError(f"Pelvis bone '{pelvis_name}' does not exist in the scene.")
    # 获取动画时间范围
    firstFrame = math.floor(pc.findKeyframe(pelvis_name, which="first"))
    lastFrame = math.ceil(pc.findKeyframe(pelvis_name, which="last"))
    pc.currentTime(firstFrame)
    # 用唯一的名称创建定位器
    locPelvis = pc.spaceLocator(name=get_unique_name("locPelvis"))
    locLFoot = pc.spaceLocator(name=get_unique_name("locLFoot"))
    locRFoot = pc.spaceLocator(name=get_unique_name("locRFoot"))
    # 控制器约束定位器
    pelvis_constr = pc.parentConstraint(pelvis_name, locPelvis)
    foot_l_constr = pc.parentConstraint(foot_l_name, locLFoot)
    foot_r_constr = pc.parentConstraint(foot_r_name, locRFoot)
    # 烘焙定位器动画
    pc.bakeResults(locPelvis, locLFoot, locRFoot, time=(firstFrame, lastFrame))
    pc.delete(pelvis_constr, foot_l_constr, foot_r_constr)
    # 定位器约束控制器
    pelvis_constr = pc.parentConstraint(locPelvis, root_name)
    foot_l_constr = pc.parentConstraint(locLFoot, foot_l_name)
    foot_r_constr = pc.parentConstraint(locRFoot, foot_r_name)
    # 列出需要断开连接的根骨骼属性
    Attrs = [
        f"{root_name}.tx",
        f"{root_name}.ty",
        f"{root_name}.tz",
        f"{root_name}.rx",
        f"{root_name}.ry",
        f"{root_name}.rz",
    ]
    # 断开连接并设置为0
    for attr in Attrs:
        attr.disconnect()
        attr.set(0)
        pc.setKeyframe(attr)
    # 烘焙动画到控制器
    pc.bakeResults(pelvis_name, foot_l_name, foot_r_name, time=(firstFrame, lastFrame))
    # 清理场景
    pc.delete(
        pelvis_constr, foot_l_constr, foot_r_constr, locPelvis, locLFoot, locRFoot
    )


# 运行脚本
if __name__ == "__main__":
    Inplace_to_RootMotion(root_name, pelvis_name)
