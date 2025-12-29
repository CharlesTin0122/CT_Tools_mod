from Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from RigUtils.rig_utils import (
    addOffsetGroups,
    addBlendedJoint,
    addSupportJoint,
    transform_to_offsetParentMatrix,
    offsetParentMatrix_to_transform,
    matrix_constraint,
    create_export_joints,
)
from RigUtils.polevector_position import set_polevector_position
from RigUtils.joint_on_vertexes_or_objs import create_joints


class RigToolKit(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "RigToolKit"

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
        self.add_offset_group_btn.setToolTip("为对象添加偏移组来归零对象变换")
        self.matrix_constraint_btn = QtWidgets.QPushButton("Matrix Constraint")
        self.matrix_constraint_btn.setToolTip(
            "先选择驱动对象，后选择被驱动对象，添加矩阵约束"
        )

        self.joint_on_vertexes_or_objs_btn = QtWidgets.QPushButton("joint On Objs")
        self.joint_on_vertexes_or_objs_btn.setToolTip(
            "在选中的对象中心位置创建骨骼，如果选中的对象是模型顶点，则在所有选中顶点中心位置创建骨骼"
        )
        self.polevector_position = QtWidgets.QPushButton("Calculate PoleVector")
        self.polevector_position.setToolTip(
            "选中三个骨骼和一个控制器，计算并设置极向量控制器位置"
        )

        self.add_blended_joint_btn = QtWidgets.QPushButton("Add Blended Joint")
        self.add_blended_joint_btn.setToolTip(
            "为当前选中骨骼创建混合骨骼，混合骨骼的旋转是选中骨骼的一半"
        )
        self.add_support_joint_btn = QtWidgets.QPushButton("Add Support Joint")
        self.add_support_joint_btn.setToolTip(
            "为当前选中骨骼创建支持骨骼，支持骨骼常用于RBF修形"
        )

        self.transform_to_OPM_btn = QtWidgets.QPushButton("Transform To OPM")
        self.transform_to_OPM_btn.setToolTip(
            "将选中对象的变换置零并将数值转移到偏移父矩阵（OffsetParentMatrix）"
        )
        self.OPM_to_transform_btn = QtWidgets.QPushButton("OPM To Transform")
        self.OPM_to_transform_btn.setToolTip(
            "将选中对象的偏移父矩阵（OffsetParentMatrix）置零并将数值转移到变换"
        )

        self.create_export_joints = QtWidgets.QPushButton("Create Export Joints")
        self.create_export_joints.setToolTip(
            "为当前选中的骨骼创建导出骨骼，导出骨骼位移旋转被原骨骼矩阵约束"
        )

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
        self.add_offset_group_btn.clicked.connect(addOffsetGroups)
        self.matrix_constraint_btn.clicked.connect(matrix_constraint)

        self.joint_on_vertexes_or_objs_btn.clicked.connect(create_joints)
        self.polevector_position.clicked.connect(set_polevector_position)

        self.add_blended_joint_btn.clicked.connect(addBlendedJoint)
        self.add_support_joint_btn.clicked.connect(addSupportJoint)

        self.transform_to_OPM_btn.clicked.connect(transform_to_offsetParentMatrix)
        self.OPM_to_transform_btn.clicked.connect(offsetParentMatrix_to_transform)

        self.create_export_joints.clicked.connect(create_export_joints)

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
