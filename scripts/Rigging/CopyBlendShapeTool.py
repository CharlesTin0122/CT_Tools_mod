# -*- coding: utf-8 -*-
# @FileName :  GenerateDeformer.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/26 11:02
# @Software : PyCharm
# Description:
from importlib import reload
from copyBlendShapeTool import copy_blendshape_tool
reload(copy_blendshape_tool)
cbt = copy_blendshape_tool.CopyBlendShapeTool()
cbt.create_ui()
