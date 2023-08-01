# -*- coding: utf-8 -*-
# @FileName :  CurveFilter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/26 10:50
# @Software : PyCharm
# Description:
from importlib import reload
import animCurveFilter.anim_curve_filter as Filter
reload(Filter)
curve_filter = Filter.AnimCurveFilter()
curve_filter.create_ui()
