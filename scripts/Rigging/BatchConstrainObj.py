# -*- coding: utf-8 -*-
# @FileName :  ConstrainNearestJoint.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/26 13:09
# @Software : PyCharm
# Description:
from importlib import reload
from batchConstrNearestObj import batch_constrain_obj as bco
reload(bco)
ui = bco.BatchConstrNearestObj()
ui.create_ui()
