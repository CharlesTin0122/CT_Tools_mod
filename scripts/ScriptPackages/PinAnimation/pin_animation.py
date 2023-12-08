# -*- coding: UTF-8 -*-
"""
@FileName      : pin_animation.py
@DateTime      : 2023/11/29 17:36:21
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
@Description   :
"""
import pymel.core as pm

sel_ctrls = []
ctrl_loc_list = []
ctrl_con_list = []


def pin_ctrl_anim():
    """为选定的控制器生成pin控制动画
    原理：
    1. 为每个控制器创建一个空间定位器.
    2. 控制器约束定位器，并烘焙定位器动画，便将控制器的动画传递到定位器上.
    3. 删除约束节点.
    4. 反过来,定位器约束控制器,控制器便被Pin住了.
    5. 这样便可以在不破坏身体动画的前提下修改main和root控制器,一般用来处理根骨骼动画
    """
    global sel_ctrls, ctrl_loc_list, ctrl_con_list
    sel_ctrls = pm.selected()
    ctrl_loc_list = []
    ctrl_con_list = []
    for ctrl in sel_ctrls:
        ctrl_loc = pm.spaceLocator(n=f"{ctrl}_loc")
        ctrl_loc_list.append(ctrl_loc)
        ctrl_cons = pm.parentConstraint(ctrl, ctrl_loc, mo=False)
        ctrl_con_list.append(ctrl_cons)
    pm.bakeResults(ctrl_loc_list, simulation=True, t=(pm.env.getMinTime(), pm.env.getMaxTime()), sampleBy=1)
    pm.delete(ctrl_con_list)
    for i, ctrl in enumerate(sel_ctrls):
        pm.parentConstraint(ctrl_loc_list[i], ctrl, mo=True)


def bake_pined_anim():
    """烘焙控制器动画，并删除空间定位器
    """
    pm.bakeResults(sel_ctrls, simulation=True, t=(pm.env.getMinTime(), pm.env.getMaxTime()), sampleBy=1)
    pm.delete(ctrl_loc_list)


if __name__ == "__main__":
    pin_ctrl_anim()
    bake_pined_anim()
