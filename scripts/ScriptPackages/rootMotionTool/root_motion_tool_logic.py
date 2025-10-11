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
import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


def pin_ctrl_anim(ctrl_list=None) -> list:
    """钉住选定控制器使其父对象的变换不会影响到选定控制器
    原理：
    1. 为每个控制器创建一个空间定位器.
    2. 控制器约束定位器，并烘焙定位器动画，便将控制器的动画传递到定位器上.
    3. 删除约束节点.
    4. 反过来,定位器约束控制器,控制器便被Pin住了.
    5. 这样便可以在不破坏控制器动画的前提下修改其父对象控制器,一般用来处理根骨骼动画
    """
    # 验证参数
    if ctrl_list is None:
        ctrl_list = pm.selected()
    # 遍历控制器列表，生成定位器，并将动画烘焙到定位器
    with pm.UndoChunk():
        ctrl_loc_list = []
        ctrl_con_list = []
        for ctrl in ctrl_list:
            ctrl_loc = pm.spaceLocator(n=f"{ctrl}_loc")
            ctrl_loc_list.append(ctrl_loc)
            ctrl_cons = pm.parentConstraint(ctrl, ctrl_loc, mo=False)
            ctrl_con_list.append(ctrl_cons)
        pm.bakeResults(
            ctrl_loc_list,
            simulation=True,
            t=(pm.env.getMinTime(), pm.env.getMaxTime()),
            sampleBy=1,
        )
        # 删除约束节点
        pm.delete(ctrl_con_list)
        # 使用定位器约束控制器以到达钉住控制器的效果
        for i, ctrl in enumerate(ctrl_list):
            pm.parentConstraint(ctrl_loc_list[i], ctrl, mo=True)
    # 返回定位器列表
    return ctrl_loc_list


def bake_pined_anim(
    ctrl_list: list, ctrl_loc_list: list, start_frame: int, end_frame: int
):
    """烘焙控制器动画，并删除空间定位器"""
    # 烘焙控制器动画
    pm.bakeResults(
        ctrl_list,
        simulation=True,
        t=(start_frame, end_frame),
        sampleBy=1,
    )
    # 删除定位器列表
    pm.delete(ctrl_loc_list)


def Inplace_to_RootMotion(
    root_ctrl: nt.Transform,
    pelvis_ctrl: nt.Transform,
    tx: bool = False,
    ty: bool = False,
    tz: bool = False,
    rx: bool = False,
    ry: bool = False,
    rz: bool = False,
    ik_ctrl_list=None,
):
    """
    在maya中转换原地动画为根动画.

    Args:
                    root_name (str): 根骨骼名称.
                    pelvis_name (str): 胯骨骼名称

    Raises:
                    ValueError: 如果对象不存在.
    """
    # 验证输入参数
    if not pm.objExists(root_ctrl):
        raise ValueError(f"Root bone '{root_ctrl}' does not exist in the scene.")
    if not pm.objExists(pelvis_ctrl):
        raise ValueError(f"Pelvis bone '{pelvis_ctrl}' does not exist in the scene.")

    # 获取动画时间范围
    first_frame = math.floor(pm.findKeyframe(pelvis_ctrl, which="first"))
    last_frame = math.ceil(pm.findKeyframe(pelvis_ctrl, which="last"))
    pm.currentTime(first_frame)
    with pm.UndoChunk():
        # 创建定位器
        loc_root = pm.spaceLocator(name="loc_root")
        loc_pelvis = pm.spaceLocator(name="loc_pelvis")

        try:
            # 控制器约束定位器
            loc_root_constr = pm.parentConstraint(root_ctrl, loc_root)
            loc_pelvis_constr = pm.parentConstraint(pelvis_ctrl, loc_pelvis)

            # 烘焙定位器动画
            pm.bakeResults(
                loc_root,
                loc_pelvis,
                time=(first_frame, last_frame),
                sparseAnimCurveBake=True,
            )

            # 删除约束节点
            pm.delete(loc_root_constr, loc_pelvis_constr)
            # 钉住pelvis控制器和IK控制器
            loc_list = pin_ctrl_anim([pelvis_ctrl] + (ik_ctrl_list or []))

            # 胯定位器分别用点约束和方向约束约束根定位器
            loc_point_contr = pm.pointConstraint(
                loc_pelvis, loc_root, maintainOffset=True
            )
            loc_orient_contr = pm.orientConstraint(
                loc_pelvis, loc_root, maintainOffset=True
            )

            # 烘焙动画
            pm.bakeResults(
                loc_root,
                time=(first_frame, last_frame),
                sparseAnimCurveBake=True,
                minimizeRotation=True,
            )
            # 删除约束节点
            pm.delete(loc_point_contr, loc_orient_contr)

            # 执行欧拉过滤器防止跳变
            pm.filterCurve(loc_root, filter="euler")
            # 根据根动画所需属性修改跟定位器动画
            if not tx:
                loc_root.translateX.disconnect()
                pm.setKeyframe(loc_root.translateX)
            if not ty:
                loc_root.translateY.disconnect()
                pm.setKeyframe(loc_root.translateY)
            if not tz:
                loc_root.translateZ.disconnect()
                pm.setKeyframe(loc_root.translateZ)
            if not rx:
                loc_root.rotateX.disconnect()
                pm.setKeyframe(loc_root.rotateX)
            if not ry:
                loc_root.rotateY.disconnect()
                pm.setKeyframe(loc_root.rotateY)
            if not rz:
                loc_root.rotateZ.disconnect()
                pm.setKeyframe(loc_root.rotateZ)

            # 定位器约束骨骼
            jnt_root_constr = pm.parentConstraint(loc_root, root_ctrl)

            # 烘焙最终动画到骨骼
            pm.bakeResults(
                root_ctrl,
                time=(first_frame, last_frame),
                sparseAnimCurveBake=True,
            )
            # 删除约束节点
            pm.delete(jnt_root_constr)
            ctrl_list = [pelvis_ctrl] + (ik_ctrl_list or [])

            bake_pined_anim(ctrl_list, loc_list, first_frame, last_frame)
            # 执行欧拉过滤器
            pm.filterCurve(root_ctrl, filter="euler")
        finally:
            # 清理定位器
            pm.delete([obj for obj in [loc_root, loc_pelvis] if pm.objExists(obj)])


def RootMotion_to_Inplace(
    root_obj: nt.Transform, pelvis_obj: nt.Transform, ik_ctrl_list=None
):
    # 验证输入参数
    if not pm.objExists(root_obj):
        raise ValueError(f"Root Obj '{root_obj}' does not exist in the scene.")
    if not pm.objExists(pelvis_obj):
        raise ValueError(f"Pelvis Obj '{pelvis_obj}' does not exist in the scene.")
    # 获取动画时间范围
    firstFrame = math.floor(pm.findKeyframe(pelvis_obj, which="first"))
    lastFrame = math.ceil(pm.findKeyframe(pelvis_obj, which="last"))
    pm.currentTime(firstFrame)
    # 钉住控制器动画
    with pm.UndoChunk():
        try:
            ctrl_list = [pelvis_obj] + (ik_ctrl_list or [])
            loc_list = pin_ctrl_anim(ctrl_list)
            # 列出需要断开连接的根骨骼属性
            attrs = ["tx", "ty", "tz", "rx", "ry", "rz"]
            for attr in attrs:
                root_obj.attr(attr).disconnect()
            root_obj.translate.set(dt.Vector())
            root_obj.rotate.set(dt.Vector())
            pm.setKeyframe(root_obj)
            # 烘焙动画到控制器
            bake_pined_anim(ctrl_list, loc_list, firstFrame, lastFrame)
        except Exception as e:
            pm.warning(f"RootMotion to Inplace Faild:{e}")
