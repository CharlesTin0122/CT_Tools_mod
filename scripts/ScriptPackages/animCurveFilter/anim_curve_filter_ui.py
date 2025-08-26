# -*- encoding: utf-8 -*-

"""
@File    :   anim_curve_filter_logic.py
@Time    :   2025/08/25 17:49:07
@Author  :   Charles Tian
@Version :   2.0.0
@Contact :   tianchao0533@gmail.com
@Desc    :   动画曲线过滤器

使用方法：
    1. 将此文件放入 Maya 脚本路径下，例如："\\Documents\\maya\\20xx\\scripts"
    2. 在 Maya 的脚本编辑器中执行以下 Python 代码:
       import anim_curve_filter_refactored
       anim_curve_filter_refactored.show_ui()
"""

import maya.cmds as cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

from Qt import QtWidgets, QtCore
from animCurveFilter.constant import FILTER_MODES
from animCurveFilter.anim_curve_filter_logic import AnimCurveFilterLogic


def maya_main_window():
    """获取maya主界面"""
    app = QtWidgets.QApplication.instance()
    if app:
        for widget in app.topLevelWidgets():
            if widget.objectName() == "MayaWindow":
                return widget
    return None


MAYA_MAIN_WINDOW = maya_main_window()
# 全局变量来存储UI实例，防止被垃圾回收
ui_instance = None


def show_ui():
    """显示UI界面的函数，确保只有一个实例存在。"""
    global ui_instance
    if ui_instance:
        ui_instance.close()
        ui_instance.deleteLater()
    ui_instance = AnimCurveFilterUI(parent=MAYA_MAIN_WINDOW)
    ui_instance.show()


class AnimCurveFilterUI(QtWidgets.QDialog):
    """
    动画曲线过滤器UI类。
    使用 PySide2 构建，并继承 MayaQWidgetDockableMixin 以便可以停靠在Maya界面中。
    """

    def __init__(self, parent=None):
        super(AnimCurveFilterUI, self).__init__(parent)
        self.setWindowTitle("动画曲线过滤器")
        self.setObjectName("AnimCurveFilter")
        self.setMinimumWidth(350)

        # 核心逻辑处理器
        self.filter_logic = AnimCurveFilterLogic()

        # UI控件
        self.filter_combo = None
        self.value_slider = None
        self.tip_label = None
        self.reverse_button = None

        self._create_widgets()
        self._create_layouts()
        self._create_connections()

        # 初始化UI状态
        self._on_filter_changed()

    def _create_widgets(self):
        """创建UI控件。"""
        self.filter_combo = QtWidgets.QComboBox()
        self.filter_combo.addItems(FILTER_MODES.keys())

        self.value_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.value_slider.setRange(0, 100)
        self.value_slider.setValue(0)
        self.value_slider.setSingleStep(1)
        self.value_slider.setPageStep(10)
        self.value_slider.setTickPosition(QtWidgets.QSlider.TicksAbove)

        self.reverse_button = QtWidgets.QPushButton("恢复 (revert)")
        self.reverse_button.setToolTip("将曲线恢复到本次修改前的状态")

        self.value_label = QtWidgets.QLabel(f"当前值：{self.value_slider.value()}")

        self.tip_label = QtWidgets.QLabel()
        self.tip_label.setWordWrap(True)
        self.tip_label.setStyleSheet("color: #999;")

    def _create_layouts(self):
        """创建UI布局。"""
        main_layout = QtWidgets.QVBoxLayout(self)

        filter_layout = QtWidgets.QHBoxLayout()
        filter_layout.addWidget(QtWidgets.QLabel("过滤器:"))
        filter_layout.addWidget(self.filter_combo)

        slider_layout = QtWidgets.QHBoxLayout()
        slider_layout.addWidget(QtWidgets.QLabel("强度:"))
        slider_layout.addWidget(self.value_slider)

        value_layout = QtWidgets.QHBoxLayout()
        value_layout.addStretch()
        value_layout.addWidget(self.value_label)
        value_layout.addStretch()

        main_layout.addLayout(filter_layout)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(value_layout)
        main_layout.addWidget(self.tip_label)
        main_layout.addWidget(self.reverse_button)
        main_layout.addStretch()

    def _create_connections(self):
        """连接信号与槽。"""
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        self.value_slider.sliderPressed.connect(self.filter_logic.cache_current_curves)
        self.value_slider.valueChanged.connect(self._on_slider_value_changed)
        self.reverse_button.clicked.connect(self.filter_logic.restore_cached_curves)

    def _on_filter_changed(self):
        """当ComboBox选项改变时，更新UI和滑条。"""
        current_filter = self.filter_combo.currentText()
        settings = FILTER_MODES[current_filter]

        self.tip_label.setText(settings["tip"])

        # 阻止信号触发，以避免在设置值时执行过滤逻辑
        self.value_slider.blockSignals(True)

        self.value_slider.setRange(
            settings["slider_range"][0], settings["slider_range"][1]
        )
        self.value_slider.setValue(settings["default_value"])
        self.value_slider.setSingleStep(settings["SingleStep"])
        self.value_slider.setPageStep(settings["PageStep"])

        self.value_slider.blockSignals(False)

    def _on_slider_value_changed(self, value):
        """当滑条值改变时，执行对应的过滤器逻辑。"""

        self.value_label.setText(f"当前值： {value}")
        current_filter = self.filter_combo.currentText()
        settings = FILTER_MODES[current_filter]

        # 如果需要remap，则计算remap后的值，否则直接使用滑条值
        if settings["remap_range"]:
            i_min, i_max = self.value_slider.minimum(), self.value_slider.maximum()
            o_min, o_max = settings["remap_range"]
            processed_value = self.filter_logic.remap(i_min, i_max, o_min, o_max, value)
        else:
            processed_value = value

        # 根据选择的过滤器调用对应的逻辑函数
        filter_function_name = f"apply_{current_filter.lower()}_filter"
        filter_function = getattr(self.filter_logic, filter_function_name, None)

        if filter_function:
            # 将操作包装在 undo chunk 中，以便可以撤销
            cmds.undoInfo(openChunk=True)
            try:
                filter_function(processed_value)
            finally:
                cmds.undoInfo(closeChunk=True)


# --- 主程序入口 ---
if __name__ == "__main__":
    # 在Maya中，最好通过一个独立的函数来调用UI，以避免多重实例问题
    try:
        if ui_instance:
            ui_instance.close()
            ui_instance.deleteLater()
    except:
        pass

    show_ui()
