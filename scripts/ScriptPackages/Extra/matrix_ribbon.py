# -*- encoding: utf-8 -*-
"""
@File    :   matrix_ribbon.py
@Time    :   2025/08/28 11:30:20
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

import traceback
import pymel.core as pm
from Qt import QtCore, QtWidgets, QtGui


class RibbonCreator(QtWidgets.QDialog):
    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = RibbonCreator.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("Ribbon Creator")
        self.setMinimumSize(100, 200)

        self.ribbon_name = "Ribbon"
        self.ribbon_axis = (0, -1, 0)
        self.ribbon_width = 5
        self.ribbon_length = 20
        self.ribbon_segment_count = 5
        self.ribbon_pin_num = 5
        self.ribbon_ctrl_num = 3

        self.nurbs_plane = None
        self.ctrl_list = []
        self.pin_list = []

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.orient_comb = QtWidgets.QComboBox()
        self.orient_comb.addItem("x", (1, 0, 0))
        self.orient_comb.addItem("y", (0, 1, 0))
        self.orient_comb.addItem("z", (0, 0, 1))
        self.orient_comb.addItem("-x", (-1, 0, 0))
        self.orient_comb.addItem("-y", (0, -1, 0))
        self.orient_comb.addItem("-z", (0, 0, -1))

        self.width_double_spin = QtWidgets.QDoubleSpinBox()
        self.width_double_spin.setFixedWidth(60)
        self.width_double_spin.setMinimum(0.1)
        self.width_double_spin.setMaximum(10000.0)
        self.width_double_spin.setValue(5.0)

        self.length_double_spin = QtWidgets.QDoubleSpinBox()
        self.length_double_spin.setFixedWidth(60)
        self.length_double_spin.setMinimum(0.1)
        self.length_double_spin.setMaximum(10000.0)
        self.length_double_spin.setValue(20.0)

        self.segment_spin = QtWidgets.QSpinBox()
        self.segment_spin.setFixedWidth(60)
        self.segment_spin.setMinimum(1)
        self.segment_spin.setMaximum(10000)
        self.segment_spin.setValue(5)

        self.pin_label = QtWidgets.QLabel("pin_num: ")

        self.pin_spin = QtWidgets.QSpinBox()
        self.pin_spin.setFixedWidth(60)
        self.pin_spin.setMinimum(1)
        self.pin_spin.setMaximum(10000)
        self.pin_spin.setValue(5)

        self.ctrl_label = QtWidgets.QLabel("ctrl_num: ")

        self.ctrl_spin = QtWidgets.QSpinBox()
        self.ctrl_spin.setFixedWidth(60)
        self.ctrl_spin.setMinimum(1)
        self.ctrl_spin.setMaximum(10000)
        self.ctrl_spin.setValue(3)

        self.button = QtWidgets.QPushButton("Create Ribbon")

    def create_layouts(self):
        nurbs_layout = QtWidgets.QFormLayout()
        nurbs_layout.addRow("orient: ", self.orient_comb)
        nurbs_layout.addRow("width: ", self.width_double_spin)
        nurbs_layout.addRow("length: ", self.length_double_spin)
        nurbs_layout.addRow("segment: ", self.segment_spin)

        nurbs_grp = QtWidgets.QGroupBox("NURBS Arguments")
        nurbs_grp.setLayout(nurbs_layout)

        ribbon_layout = QtWidgets.QHBoxLayout()
        ribbon_layout.addWidget(self.pin_label)
        ribbon_layout.addWidget(self.pin_spin)
        ribbon_layout.addStretch()
        ribbon_layout.addWidget(self.ctrl_label)
        ribbon_layout.addWidget(self.ctrl_spin)

        ribbon_grp = QtWidgets.QGroupBox("Ribbon Arguments")
        ribbon_grp.setLayout(ribbon_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(nurbs_grp)
        main_layout.addWidget(ribbon_grp)
        main_layout.addWidget(self.button)

    def create_connections(self):
        self.orient_comb.currentTextChanged.connect(self.on_orient_comb_changed)
        self.width_double_spin.valueChanged.connect(self.on_width_spin_changed)
        self.length_double_spin.valueChanged.connect(self.on_length_spin_changed)
        self.segment_spin.valueChanged.connect(self.on_segment_spin_changed)
        self.pin_spin.valueChanged.connect(self.on_pin_spin_changed)
        self.ctrl_spin.valueChanged.connect(self.on_ctrl_spin_changed)
        self.button.clicked.connect(self.on_button_clicked)

    @QtCore.Slot()
    def on_orient_comb_changed(self, text):
        self.ribbon_axis = self.orient_comb.currentData()

    @QtCore.Slot()
    def on_width_spin_changed(self, value):
        self.ribbon_width = value

    @QtCore.Slot()
    def on_length_spin_changed(self, value):
        self.ribbon_length = value

    @QtCore.Slot()
    def on_segment_spin_changed(self, value):
        self.ribbon_segment_count = value

    @QtCore.Slot()
    def on_pin_spin_changed(self, value):
        self.ribbon_pin_num = value

    @QtCore.Slot()
    def on_ctrl_spin_changed(self, value):
        self.ribbon_ctrl_num = value

    @QtCore.Slot()
    def on_button_clicked(self):
        try:
            self.nurbs_plane = self.create_nurbs_plane(
                self.ribbon_axis,
                self.ribbon_width,
                self.ribbon_length,
                self.ribbon_segment_count,
            )
            self.ctrl_list, self.pin_list = self.create_ribbon(
                self.nurbs_plane, self.ribbon_pin_num, self.ribbon_ctrl_num
            )
        except Exception as e:
            traceback.print_exc()
            pm.displayWarning(e)

    @staticmethod
    def get_maya_main_window():
        app = QtWidgets.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    @classmethod
    def show_dialog(cls):
        if not cls._ui_instance:
            cls._ui_instance = RibbonCreator()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()

    def create_nurbs_plane(
        self, axis, width, length, segment_count
    ) -> pm.nodetypes.Transform:
        """创建NURBS平面，用于制作Ribbon

        Args:
            axis (tuple): 平面朝向：(0,0,1)
            width (float): 宽度
            length (float):长度
            segment_count (ont): 段数

        returns:
            nt.Transform

        """
        length_ratio = length / width
        nurbs_plane = pm.nurbsPlane(
            pivot=(0, 0, 0),
            axis=axis,
            width=width,
            lengthRatio=length_ratio,
            degree=3,
            u=1,
            v=segment_count,
            constructionHistory=0,
        )[0]
        return nurbs_plane

    def create_ribbon(self, nurbs_plane, pin_num, ctrl_num):
        """使用矩阵节点实现Ribbon，主要用到"uvPin"和"pointOnSurfaceInfo"节点

        Args:
            nurbs_plane (pm.nodetypes.Transform): 要创建Ribbon的nurbsPlane
            pin_num (int): pin骨骼数量
            ctrl_num (int): 控制骨骼数量

        Returns:
            tuple[list, list]: 返回控制骨骼列表和pin骨骼列表
        """
        if isinstance(nurbs_plane, str) and pm.objExists(nurbs_plane):
            nurbs_plane = pm.PyNode(nurbs_plane)
        elif isinstance(nurbs_plane, pm.nodetypes.Transform):
            pass
        elif isinstance(nurbs_plane, pm.nodetypes.NurbsSurface):
            nurbs_plane = nurbs_plane.getTransform()
        else:
            raise TypeError("Invalid surface object specified.")

        if not isinstance(pin_num, int) or pin_num <= 0:
            raise ValueError("pin_num must be a positive integer.")
        if not isinstance(ctrl_num, int) or ctrl_num <= 0:
            raise ValueError("ctrl_num must be a positive integer.")

        nurbs_name = nurbs_plane.name()
        nurbs_shape = nurbs_plane.getShape()
        paramLengthV = nurbs_shape.minMaxRangeV.get()  # 一般为0:1

        pin_jnt_list = []
        for i in range(pin_num):
            v_pose = 0.0 if pin_num == 1 else (i / float(pin_num - 1)) * paramLengthV[1]
            uvPin_node = pm.createNode("uvPin", name=f"uvPin_{i}")
            pin_jnt = pm.joint(name=f"{nurbs_name}_pin_{i}", radius=1)

            uvPin_node.coordinate[0].coordinateU.set(0.5)
            uvPin_node.coordinate[0].coordinateV.set(v_pose)

            nurbs_shape.worldSpace[0].connect(uvPin_node.deformedGeometry)
            uvPin_node.outputMatrix[0].connect(pin_jnt.offsetParentMatrix)
            pin_jnt_list.append(pin_jnt)

        ctrl_jnt_list = []
        for i in range(ctrl_num):
            v_pose = 0 if ctrl_num == 1 else (i / float(ctrl_num - 1)) * paramLengthV[1]
            posi_node = pm.createNode("pointOnSurfaceInfo", name=f"posi_{i}")
            ctrl_jnt = pm.joint(name=f"{nurbs_name}_ctrlJnt_{i}", radius=5)
            posi_node.parameterU.set(0.5)
            posi_node.parameterV.set(v_pose)
            nurbs_shape.worldSpace[0].connect(posi_node.inputSurface)
            position = posi_node.result.position.get()
            if position:
                ctrl_jnt.setTranslation(position)
                pm.delete(posi_node)
            ctrl_jnt_list.append(ctrl_jnt)
        pm.skinCluster(nurbs_plane, ctrl_jnt_list)

        pin_jnt_grp = pm.group(pin_jnt_list, name=f"{nurbs_name}_pin_Jnt_grp")
        ctrl_jnt_grp = pm.group(ctrl_jnt_list, name=f"{nurbs_name}_ctrl_Jnt_grp")

        return ctrl_jnt_list, pin_jnt_list


if __name__ == "__main__":
    RibbonCreator.show_dialog()
