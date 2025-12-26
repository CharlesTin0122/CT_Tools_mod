from Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


class RigToolKit(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "Template"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(RigToolKit.WINDOW_TITLE)
        self.setMinimumSize(300, 120)
        # 窗口在关闭时自动彻底销毁对象
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.add_offset_group_btn = QtWidgets.QPushButton("Add Offset Group")
        self.matrix_constraint_btn = QtWidgets.QPushButton("Matrix Constraint")

        self.joint_on_vertexes_or_objs_btn = QtWidgets.QPushButton("joint On Objs")
        self.polevector_position = QtWidgets.QPushButton("Calculate PoleVector")

        self.add_blended_joint_btn = QtWidgets.QPushButton("Add Blended Joint")
        self.add_support_joint_btn = QtWidgets.QPushButton("Add Support Joint")

        self.transform_to_OPM_btn = QtWidgets.QPushButton("Transform To OPM")
        self.OPM_to_transform_btn = QtWidgets.QPushButton("OPM To Transform")

        self.create_export_joints = QtWidgets.QPushButton("Create Export Joints")

    def create_layout(self):
        layout_1 = QtWidgets.QHBoxLayout()
        layout_1.addWidget(self.add_offset_group_btn)
        layout_1.addWidget(self.matrix_constraint_btn)

        layout_2 = QtWidgets.QHBoxLayout()
        layout_2.addWidget(self.joint_on_vertexes_or_objs_btn)
        layout_2.addWidget(self.polevector_position)

        layout_3 = QtWidgets.QHBoxLayout()
        layout_3.addWidget(self.add_blended_joint_btn)
        layout_3.addWidget(self.add_support_joint_btn)

        layout_4 = QtWidgets.QHBoxLayout()
        layout_4.addWidget(self.transform_to_OPM_btn)
        layout_4.addWidget(self.OPM_to_transform_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(layout_1)
        main_layout.addLayout(layout_2)
        main_layout.addLayout(layout_3)
        main_layout.addLayout(layout_4)
        main_layout.addWidget(self.create_export_joints)

    def create_connections(self):
        pass

    @QtCore.Slot()
    def template_slot(self):
        pass

    def closeEvent(self, event):
        """关闭窗口时清空实例"""
        RigToolKit._ui_instance = None
        super().closeEvent(event)

    @staticmethod
    def get_maya_main_window():
        """返回 Maya 主窗口的 PySide 实例"""
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrapInstance(int(ptr), QtWidgets.QMainWindow)
        return None

    @classmethod
    def show_ui(cls):
        """单例显示 UI"""
        # 如果没有单例或者实例不显示，则创建并显示实例
        if cls._ui_instance is None or not cls._ui_instance.isVisible():
            cls._ui_instance = RigToolKit()
            cls._ui_instance.show()
        # 其他情况实例抬起并激活
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# 执行代码
def run():
    RigToolKit.show_ui()
