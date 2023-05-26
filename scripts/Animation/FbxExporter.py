# -*- coding: utf-8 -*-
# @FileName :  FbxExporter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/26 10:58
# @Software : PyCharm
# Description:
from importlib import reload
from fbxExporter import fbx_exporter
reload(fbx_exporter)

ui = fbx_exporter.FbxExporterUI()
ui.show()
