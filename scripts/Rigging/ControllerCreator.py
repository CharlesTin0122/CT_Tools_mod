# -*- encoding: utf-8 -*-
"""
@File    :   ControllerCreator.py
@Time    :   2025/05/09 09:58:21
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

from importlib import reload
from ControlCreator import control_creator_ui

reload(control_creator_ui)
control_creator_ui.show_control_creator_ui()
