# -*- encoding: utf-8 -*-
"""
@File    :   root_motion_tool_01.py
@Time    :   2025/04/27 18:01:03
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   根动画工具UI
"""

from Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt
from rootMotionTool.root_motion_tool_logic import (
    Inplace_to_RootMotion,
    RootMotion_to_Inplace,
)


class RootMotionTool(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "RootMotionTool"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(RootMotionTool.WINDOW_TITLE)
        self.setMinimumSize(300, 120)
        # 窗口在关闭时自动彻底销毁对象
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.root_obj_label = QtWidgets.QLabel("Root Obj: ")
        self.root_obj_line = QtWidgets.QLineEdit()
        self.root_obj_btn = QtWidgets.QPushButton("<<")

        self.pelvis_obj_label = QtWidgets.QLabel("Pelvis Obj: ")
        self.pelvis_obj_line = QtWidgets.QLineEdit()
        self.pelvis_obj_btn = QtWidgets.QPushButton("<<")

        self.ik_ctrls_label = QtWidgets.QLabel("Ik Ctrls: ")
        self.ik_ctrls_btn = QtWidgets.QPushButton("Load Ik Ctrls")
        self.ik_ctrls_list = QtWidgets.QListWidget()

        self.tx_label = QtWidgets.QLabel("Translate X: ")
        self.tx_checkBox = QtWidgets.QCheckBox()
        self.ty_label = QtWidgets.QLabel("Translate Y: ")
        self.ty_checkBox = QtWidgets.QCheckBox()
        self.tz_label = QtWidgets.QLabel("Translate Z: ")
        self.tz_checkBox = QtWidgets.QCheckBox()
        self.rx_label = QtWidgets.QLabel("Rotate X: ")
        self.rx_checkBox = QtWidgets.QCheckBox()
        self.ry_label = QtWidgets.QLabel("Rotate Y: ")
        self.ry_checkBox = QtWidgets.QCheckBox()
        self.rz_label = QtWidgets.QLabel("Rotate Z: ")
        self.rz_checkBox = QtWidgets.QCheckBox()

        self.inplace_to_rootmotion_btn = QtWidgets.QPushButton("Inplace To Rootmotion")
        self.rootmotion_to_inplace_btn = QtWidgets.QPushButton("Rootmotion To Inplace")

    def create_layout(self):
        root_obj_layout = QtWidgets.QHBoxLayout()
        root_obj_layout.addWidget(self.root_obj_label)
        root_obj_layout.addWidget(self.root_obj_line)
        root_obj_layout.addWidget(self.root_obj_btn)

        pelvis_obj_layout = QtWidgets.QHBoxLayout()
        pelvis_obj_layout.addWidget(self.pelvis_obj_label)
        pelvis_obj_layout.addWidget(self.pelvis_obj_line)
        pelvis_obj_layout.addWidget(self.pelvis_obj_btn)

        ik_ctrls_layout = QtWidgets.QVBoxLayout()
        ik_ctrls_layout.addWidget(self.ik_ctrls_label)
        ik_ctrls_layout.addWidget(self.ik_ctrls_list)
        ik_ctrls_layout.addWidget(self.ik_ctrls_btn)

        translate_layout = QtWidgets.QHBoxLayout()
        translate_layout.addWidget(self.tx_label)
        translate_layout.addWidget(self.tx_checkBox)
        translate_layout.addWidget(self.ty_label)
        translate_layout.addWidget(self.ty_checkBox)
        translate_layout.addWidget(self.tz_label)
        translate_layout.addWidget(self.tz_checkBox)

        rotate_layout = QtWidgets.QHBoxLayout()
        rotate_layout.addWidget(self.rx_label)
        rotate_layout.addWidget(self.rx_checkBox)
        rotate_layout.addWidget(self.ry_label)
        rotate_layout.addWidget(self.ry_checkBox)
        rotate_layout.addWidget(self.rz_label)
        rotate_layout.addWidget(self.rz_checkBox)

        axis_layout = QtWidgets.QVBoxLayout()
        axis_layout.addLayout(translate_layout)
        axis_layout.addLayout(rotate_layout)

        axis_grp = QtWidgets.QGroupBox("Root Motion Axis")
        axis_grp.setLayout(axis_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(root_obj_layout)
        main_layout.addLayout(pelvis_obj_layout)
        main_layout.addLayout(ik_ctrls_layout)
        main_layout.addWidget(axis_grp)
        main_layout.addWidget(self.inplace_to_rootmotion_btn)
        main_layout.addWidget(self.rootmotion_to_inplace_btn)

    def create_connections(self):
        self.root_obj_btn.clicked.connect(self.on_root_obj_btn)
        self.pelvis_obj_btn.clicked.connect(self.on_pelvis_obj_btn)
        self.ik_ctrls_btn.clicked.connect(self.on_ik_ctrls_list)
        self.inplace_to_rootmotion_btn.clicked.connect(
            self.on_inplace_to_rootmotion_btn
        )
        self.rootmotion_to_inplace_btn.clicked.connect(
            self.on_rootmotion_to_inplace_btn
        )

    @QtCore.Slot()
    def on_root_obj_btn(self):
        select_obj = pm.selected()
        if not select_obj:
            pm.warning("Please select root obj")
        obj_name = select_obj[0].name()
        self.root_obj_line.setText(obj_name)

    @QtCore.Slot()
    def on_pelvis_obj_btn(self):
        select_obj = pm.selected()
        if not select_obj:
            pm.warning("Please select pelvis obj")
        obj_name = select_obj[0].name()
        self.pelvis_obj_line.setText(obj_name)

    @QtCore.Slot()
    def on_ik_ctrls_list(self):
        self.ik_ctrls_list.clear()
        select_obj = pm.selected()
        if not select_obj:
            pm.warning("Please select pelvis obj")
        obj_name_List = [obj.name() for obj in select_obj]
        self.ik_ctrls_list.addItems(obj_name_List)

    @QtCore.Slot()
    def on_inplace_to_rootmotion_btn(self):
        root_ctrl = nt.Transform(self.root_obj_line.text())
        pelvis_ctrl = nt.Transform(self.pelvis_obj_line.text())
        tx = self.tx_checkBox.isChecked()
        ty = self.ty_checkBox.isChecked()
        tz = self.tz_checkBox.isChecked()
        rx = self.rx_checkBox.isChecked()
        ry = self.ry_checkBox.isChecked()
        rz = self.rz_checkBox.isChecked()
        ik_ctrl_list = [
            pm.PyNode(self.ik_ctrls_list.item(i).text())
            for i in range(self.ik_ctrls_list.count())
            if self.ik_ctrls_list.item(i) is not None
        ]
        Inplace_to_RootMotion(
            root_ctrl, pelvis_ctrl, tx, ty, tz, rx, ry, rz, ik_ctrl_list
        )

    @QtCore.Slot()
    def on_rootmotion_to_inplace_btn(self):
        root_obj = nt.Transform(self.root_obj_line.text())
        pelvis_obj = nt.Transform(self.pelvis_obj_line.text())
        ik_ctrl_list = [
            pm.PyNode(self.ik_ctrls_list.item(i).text())
            for i in range(self.ik_ctrls_list.count())
            if self.ik_ctrls_list.item(i) is not None
        ]
        RootMotion_to_Inplace(root_obj, pelvis_obj, ik_ctrl_list)

    def closeEvent(self, event):
        """关闭窗口时清空实例"""
        RootMotionTool._ui_instance = None
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
            cls._ui_instance = RootMotionTool()
            cls._ui_instance.show()
        # 其他情况实例抬起并激活
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# 执行代码
def run():
    RootMotionTool.show_ui()
