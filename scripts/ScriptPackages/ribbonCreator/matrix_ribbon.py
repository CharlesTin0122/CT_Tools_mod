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
from Qt import QtCore, QtWidgets


class RibbonCreator(QtWidgets.QDialog):
    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = RibbonCreator.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("Ribbon Creator")
        self.setMinimumSize(300, 200)

        self.ribbon_name = "Ribbon"
        self.create_ctrl = False
        self.ribbon_axis = (1, 0, 0)
        self.ribbon_width = 5
        self.ribbon_length = 20
        self.ribbon_segment_count = 5
        self.ribbon_pin_num = 5
        self.ribbon_ctrl_num = 3

        self.nurbs_plane = None

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.name_line = QtWidgets.QLineEdit()
        self.name_line.setText("Ribbon")
        self.name_line.setFixedWidth(80)

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

        self.ctrl_cb = QtWidgets.QCheckBox("Add Ctrl")

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
        nurbs_layout = QtWidgets.QGridLayout()
        nurbs_layout.setSpacing(5)
        nurbs_layout.setColumnStretch(0, 0)  # 左 label列，不伸缩
        nurbs_layout.setColumnStretch(1, 0)  # 左输入列，不伸缩
        nurbs_layout.setColumnStretch(2, 1)  # 中间空隙，伸缩
        nurbs_layout.setColumnStretch(3, 0)  # 右 label列，不伸缩
        nurbs_layout.setColumnStretch(4, 0)  # 右输入列，不伸缩

        nurbs_layout.addWidget(QtWidgets.QLabel("name: "), 0, 0)
        nurbs_layout.addWidget(self.name_line, 0, 1)
        nurbs_layout.addWidget(QtWidgets.QLabel("orient: "), 0, 3)
        nurbs_layout.addWidget(self.orient_comb, 0, 4)

        nurbs_layout.addWidget(QtWidgets.QLabel("width: "), 1, 0)
        nurbs_layout.addWidget(self.width_double_spin, 1, 1)
        nurbs_layout.addWidget(QtWidgets.QLabel("length: "), 1, 3)
        nurbs_layout.addWidget(self.length_double_spin, 1, 4)

        nurbs_layout.addWidget(QtWidgets.QLabel("segment: "), 2, 0)
        nurbs_layout.addWidget(self.segment_spin, 2, 1)
        nurbs_layout.addWidget(self.ctrl_cb, 2, 4)

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
        self.ctrl_cb.toggled.connect(self.on_ctrl_cb_toggled)
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
    def on_ctrl_cb_toggled(self, check):
        self.create_ctrl = check

    @QtCore.Slot()
    def on_button_clicked(self):
        self.ribbon_name = self.name_line.text()
        try:
            self.nurbs_plane = self.create_nurbs_plane(
                self.ribbon_name,
                self.ribbon_axis,
                self.ribbon_width,
                self.ribbon_length,
                self.ribbon_segment_count,
            )
            self.create_ribbon(
                self.nurbs_plane,
                self.ribbon_name,
                self.ribbon_pin_num,
                self.ribbon_ctrl_num,
                self.create_ctrl,
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
        self, ribbon_name, axis, width, length, segment_count
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
            name=f"{ribbon_name}_plane",
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

    def create_ribbon(
        self, nurbs_plane, ribbon_name, pin_num, ctrl_num, create_ctrl=False
    ):
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

        nurbs_shape = nurbs_plane.getShape()
        paramLengthV = nurbs_shape.minMaxRangeV.get()  # 一般为0:1

        pin_jnt_list = []
        for i in range(pin_num):
            v_pose = 0.0 if pin_num == 1 else (i / float(pin_num - 1)) * paramLengthV[1]
            uvPin_node = pm.createNode("uvPin", name=f"{ribbon_name}_uvPin_{i}")
            pin_jnt = pm.joint(name=f"{ribbon_name}_pin_{i}", radius=1)

            uvPin_node.coordinate[0].coordinateU.set(0.5)
            uvPin_node.coordinate[0].coordinateV.set(v_pose)

            nurbs_shape.worldSpace[0].connect(uvPin_node.deformedGeometry)
            uvPin_node.outputMatrix[0].connect(pin_jnt.offsetParentMatrix)
            pin_jnt_list.append(pin_jnt)

        ctrl_jnt_list = []
        ctrl_grp_list = []
        for i in range(ctrl_num):
            v_pose = 0 if ctrl_num == 1 else (i / float(ctrl_num - 1)) * paramLengthV[1]
            posi_node = pm.createNode(
                "pointOnSurfaceInfo", name=f"{ribbon_name}_posi_{i}"
            )
            ctrl_jnt = pm.joint(name=f"{ribbon_name}_ctrlJnt_{i}", radius=5)
            posi_node.parameterU.set(0.5)
            posi_node.parameterV.set(v_pose)
            nurbs_shape.worldSpace[0].connect(posi_node.inputSurface)
            position = posi_node.result.position.get()
            if position:
                ctrl_jnt.setTranslation(position)
                if create_ctrl:
                    ctrl_name = f"{ribbon_name}_ctrl_{i}"
                    ctrl = pm.circle(
                        name=ctrl_name,
                        constructionHistory=False,
                        normal=self.ribbon_axis,
                        radius=8,
                    )[0]
                    ctrl_offset_grp = pm.group(ctrl, name=f"{ctrl_name}_offset")
                    pm.matchTransform(ctrl_offset_grp, ctrl_jnt)
                    pm.parentConstraint(ctrl, ctrl_jnt)
                    pm.scaleConstraint(ctrl, ctrl_jnt)
                    ctrl_grp_list.append(ctrl_offset_grp)
            ctrl_jnt_list.append(ctrl_jnt)
            pm.delete(posi_node)

        pm.skinCluster(nurbs_plane, ctrl_jnt_list)

        pin_jnt_grp = pm.group(pin_jnt_list, name=f"{ribbon_name}_pin_Jnt_grp")
        ctrl_jnt_grp = pm.group(ctrl_jnt_list, name=f"{ribbon_name}_ctrl_Jnt_grp")

        if create_ctrl:
            ctrl_grp = pm.group(ctrl_grp_list, name=f"{ribbon_name}_ctrl_grp")
            pm.group(
                nurbs_plane,
                pin_jnt_grp,
                ctrl_jnt_grp,
                ctrl_grp,
                name=f"{ribbon_name}_grp",
            )
        else:
            pm.group(
                nurbs_plane,
                pin_jnt_grp,
                ctrl_jnt_grp,
                name=f"{ribbon_name}_grp",
            )


if __name__ == "__main__":
    RibbonCreator.show_dialog()
