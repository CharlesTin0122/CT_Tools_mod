from Qt import QtCore, QtWidgets
import pymel.core as pm
from connectTwistSwing.connect_twist_swing_logic import connect_twist_swing


class ConnectTwistSwing(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "ConnectTwistSwing"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(ConnectTwistSwing.WINDOW_TITLE)
        self.setMinimumSize(300, 120)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lab_twist = QtWidgets.QLabel("Twist Weight: ")
        self.dsb_twist = QtWidgets.QDoubleSpinBox()
        self.dsb_twist.setFixedWidth(60)
        self.dsb_twist.setMinimum(-1.0)
        self.dsb_twist.setMaximum(1.0)
        self.dsb_twist.setSingleStep(0.1)

        self.lab_swing = QtWidgets.QLabel("Swing Weight: ")
        self.dsb_swing = QtWidgets.QDoubleSpinBox()
        self.dsb_swing.setFixedWidth(60)
        self.dsb_swing.setMinimum(-1.0)
        self.dsb_swing.setMaximum(1.0)
        self.dsb_swing.setSingleStep(0.1)

        self.lab_axis = QtWidgets.QLabel("Twist Axis: ")
        self.comB_axis = QtWidgets.QComboBox()
        self.comB_axis.addItem("X", "X")
        self.comB_axis.addItem("Y", "Y")
        self.comB_axis.addItem("Z", "Z")

        self.btn_apply = QtWidgets.QPushButton("Apply")

    def create_layout(self):
        twist_layout = QtWidgets.QHBoxLayout()
        twist_layout.addWidget(self.lab_twist)
        twist_layout.addWidget(self.dsb_twist)

        swing_layout = QtWidgets.QHBoxLayout()
        swing_layout.addWidget(self.lab_swing)
        swing_layout.addWidget(self.dsb_swing)

        axis_layout = QtWidgets.QHBoxLayout()
        axis_layout.addWidget(self.lab_axis)
        axis_layout.addWidget(self.comB_axis)

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.btn_apply)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(twist_layout)
        main_layout.addLayout(swing_layout)
        main_layout.addLayout(axis_layout)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.btn_apply.clicked.connect(self.on_btn_apply_clicked)

    @QtCore.Slot()
    def on_btn_apply_clicked(self):
        selection = pm.selected()
        if len(selection) < 2:
            pm.warning("请选择至少两个对象：第一个是源对象，第二个是目标对象。")
            return None
        driver, driven = selection[0], selection[1]
        twist_weight = self.dsb_twist.value()
        swing_weight = self.dsb_swing.value()
        twist_axis = self.comB_axis.currentData()
        try:
            connect_twist_swing(driver, driven, twist_weight, swing_weight, twist_axis)
        except Exception as e:
            print(e)

    @staticmethod
    def get_maya_main_window():
        """通过 QApplication 获取 Maya 主窗口的 PySide 实例"""
        # app.topLevelWidgets() 返回当前 QApplication 管理的所有顶层窗口（没有父窗口）列表
        for widget in QtWidgets.QApplication.topLevelWidgets():
            # 如果窗口的 Qt 对象名称为"MayaWindow"，返回这个窗口实例
            if widget.objectName() == "MayaWindow":
                return widget
        return None

    def closeEvent(self, event):
        ConnectTwistSwing._ui_instance = None
        super().closeEvent(event)

    @classmethod
    def show_ui(cls):
        """单例模式显示UI"""
        if cls._ui_instance is None:
            cls._ui_instance = ConnectTwistSwing()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


if __name__ == "__main__":
    ConnectTwistSwing.show_ui()
