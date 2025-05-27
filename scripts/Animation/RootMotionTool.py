# -*- coding: utf-8 -*-
"""
@FileName    :   RootMotionTool.py
@DateTime    :   2023/06/08 17:52:58
@Author  :   Tian Chao
@Contact :   tianchao0533@163.com
"""

from importlib import reload
from rootMotionTool import root_motion_tool_01

reload(root_motion_tool_01)
root_motion_tool_01.Inplace_to_RootMotion(
    "root_main_C0_ctl", "body_C0_ctl", ik_ctrls=["leg_R0_ik_ctl", "leg_L0_ik_ctl"]
)
