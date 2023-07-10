# -*- coding: utf-8 -*-
# @FileName :  batch_mayafile_execute.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/6/1 14:58
# @Software : PyCharm
# Description:
from importlib import reload
from Batch_File import batch_file_excute as bfe
reload(bfe)

batch_tool = bfe.BatchMayaFile()
batch_tool.create_ui()
