# -*- coding: utf-8 -*-
# @FileName :  FbxImporter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/26 10:56
# @Software : PyCharm
# Description:
from importlib import reload
from fbxImporter import fbx_importer_ue4

reload(fbx_importer_ue4)
advAnimToolsUI = fbx_importer_ue4.AdvAnimToolsUI()
advAnimToolsUI.create_ui()
