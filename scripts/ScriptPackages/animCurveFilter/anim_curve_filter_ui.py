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
```
from animCurveFilter import anim_curve_filter_ui as ui
ui.show_ui
```
"""

from importlib import reload
import traceback
from Qt import QtWidgets, QtCore
# from animCurveFilter.constant import FILTER_MODES
# from animCurveFilter.anim_curve_filter_logic import AnimCurveFilterLogic

from animCurveFilter import constant
from animCurveFilter import anim_curve_filter_logic

reload(constant)
reload(anim_curve_filter_logic)
FILTER_MODES = constant.FILTER_MODES
AnimCurveFilterLogic = anim_curve_filter_logic.AnimCurveFilterLogic


class AnimCurveFilterUI(QtWidgets.QDialog):
    """
    动画曲线过滤器UI类,使用 PySide 构建。
    """

    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = AnimCurveFilterUI.maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("动画曲线过滤器")
        self.setObjectName("AnimCurveFilter")
        self.setMinimumWidth(350)

        # 核心逻辑处理器
        self.filter_logic = AnimCurveFilterLogic()
        self.file_modes = FILTER_MODES

        # UI控件
        self.filter_combo = None
        self.value_slider = None
        self.tip_label = None
        self.reverse_button = None
        # 构建控件
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
        main_layout.addStretch()
        main_layout.addWidget(self.tip_label)
        main_layout.addWidget(self.reverse_button)

    def _create_connections(self):
        """连接信号与槽。"""
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)

        self.value_slider.sliderPressed.connect(self.filter_logic.cache_current_curves)
        self.value_slider.valueChanged.connect(self._on_slider_value_changed)
        self.value_slider.sliderReleased.connect(self.reset_slider)

        self.reverse_button.clicked.connect(self.filter_logic.restore_cached_curves)
        self.reverse_button.clicked.connect(self.reset_slider)

    def _on_filter_changed(self):
        """当ComboBox选项改变时，更新UI和滑条。"""
        # 获取数据
        current_filter = self.filter_combo.currentText()
        settings = FILTER_MODES[current_filter]
        # 设置 tips
        self.tip_label.setText(settings["tip"])

        # 设置滑条，阻止信号触发，以避免在设置值时执行过滤逻辑
        self.value_slider.blockSignals(True)
        self.value_slider.setRange(
            settings["slider_range"][0], settings["slider_range"][1]
        )
        self.value_slider.setValue(settings["default_value"])
        self.value_slider.setSingleStep(settings["single_step"])
        self.value_slider.blockSignals(False)
        # 设置滑条数值标签
        self.value_label.setText(f"当前值： {settings['default_value']}")

    def _on_slider_value_changed(self, value):
        """当滑条值改变时，执行对应的过滤器逻辑。"""
        # 获取数据
        current_filter = self.filter_combo.currentText()
        settings = FILTER_MODES[current_filter]
        # 更新滑条数值标签显示
        self.value_label.setText(f"当前值： {value}")

        # 如果需要remap，则计算remap后的值，否则直接使用滑条值
        if settings["remap_range"]:
            i_min, i_max = self.value_slider.minimum(), self.value_slider.maximum()
            o_min, o_max = settings["remap_range"]
            # remap(0, 100, 0, 1, 50) = 0.5
            processed_value = self.filter_logic.remap_value(
                i_min, i_max, o_min, o_max, value
            )
        else:
            processed_value = value

        # 根据选择的过滤器调用对应的逻辑函数
        filter_function_name = f"apply_{current_filter.lower()}_filter"
        # 从对象中获取命名属性; getattr(x, 'y')等同于x.y。如果找不到，返回None
        filter_function = getattr(self.filter_logic, filter_function_name)
        if not filter_function:
            raise ValueError(f"Filter function {filter_function_name} not found.")
        # 如果函数存在，执行函数
        else:
            try:
                filter_function(processed_value)
            except Exception as e:
                traceback.print_exc()
                print(e)

    def reset_slider(self):
        current_filter = self.filter_combo.currentText()
        settings = FILTER_MODES[current_filter]
        try:
            self.value_slider.setValue(settings["default_value"])
            self.value_label.setText(f"当前值： {settings['default_value']}")
        except Exception as e:
            print(e)

    # --- 静态和类方法 (无需修改) ---
    @staticmethod
    def maya_main_window():
        app = QtWidgets.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    @classmethod
    def show_ui(cls):
        if not cls._ui_instance:
            cls._ui_instance = cls()

        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# --- 主程序入口 ---
if __name__ == "__main__":
    AnimCurveFilterUI.show_ui()
