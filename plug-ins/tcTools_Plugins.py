# -*- coding: utf-8 -*-
# @FileName :  fbx_importer.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/19 10:35
# @Software : PyCharm
# Description:

import pymel.core as pc
from importlib import reload
import tcTools_MenuUI

reload(tcTools_MenuUI)


def load_tcTools():
    tcTools_MenuUI.createMenu()


def unLoad_tcTools():
    tcTools_MenuUI.deleteMenu()


def initializePlugin(mobject):
    load_tcTools()


def uninitializePlugin(mobject):
    unLoad_tcTools()
