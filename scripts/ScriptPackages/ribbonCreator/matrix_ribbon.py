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
    """ """

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

        self.inner_curve = None
        self.outer_curve = None
        self.is_flip_normal = False
        self.is_ring_plane = False

        self.ribbon_pin_num = 5
        self.ribbon_ctrl_num = 3

        self.nurbs_plane = None

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # main settings
        self.name_line = QtWidgets.QLineEdit()
        self.name_line.setText("Ribbon")
        self.name_line.setFixedWidth(80)
        self.ctrl_cb = QtWidgets.QCheckBox("Add Ctrl")
        # Nurbs arguments
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

        # create nurbs btn
        self.nurbs_btn = QtWidgets.QPushButton("Create Nurbs")

        # poly to nurbs arguments
        self.inner_edges_btn = QtWidgets.QPushButton("Inner egdes")
        self.inner_edges_btn.setFixedWidth(120)
        self.outer_edges_btn = QtWidgets.QPushButton("Outer egdes")
        self.outer_edges_btn.setFixedWidth(120)
        self.flip_normal_cb = QtWidgets.QCheckBox("Flip Normals")
        self.closed_loop_cb = QtWidgets.QCheckBox("Circular Plane")

        self.p2n_btn = QtWidgets.QPushButton("Polygon To Nurbs")

        # ribbon arguments
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
        # ribbon button
        self.ribbon_button = QtWidgets.QPushButton("Create Ribbon")

    def create_layouts(self):
        # mian settings layout
        settings_layout = QtWidgets.QHBoxLayout()
        settings_layout.addWidget(QtWidgets.QLabel("name: "))
        settings_layout.addWidget(self.name_line)
        settings_layout.addStretch()
        settings_layout.addWidget(self.ctrl_cb)

        settings_grp = QtWidgets.QGroupBox("Main Settings")
        settings_grp.setLayout(settings_layout)
        # nurbs layout
        nurbs_layout = QtWidgets.QGridLayout()
        nurbs_layout.setSpacing(3)
        # 设置伸缩，参数1：列索引，参数2：缩放比例
        nurbs_layout.setColumnStretch(0, 0)  # 左 label列，不伸缩
        nurbs_layout.setColumnStretch(1, 0)  # 左输入列，不伸缩
        nurbs_layout.setColumnStretch(2, 1)  # 中间空隙，伸缩
        nurbs_layout.setColumnStretch(3, 0)  # 右 label列，不伸缩
        nurbs_layout.setColumnStretch(4, 0)  # 右输入列，不伸缩

        nurbs_layout.addWidget(QtWidgets.QLabel("orient: "), 0, 0)
        nurbs_layout.addWidget(self.orient_comb, 0, 1)
        nurbs_layout.addWidget(QtWidgets.QLabel("segment: "), 0, 3)
        nurbs_layout.addWidget(self.segment_spin, 0, 4)
        nurbs_layout.addWidget(QtWidgets.QLabel("width: "), 1, 0)
        nurbs_layout.addWidget(self.width_double_spin, 1, 1)
        nurbs_layout.addWidget(QtWidgets.QLabel("length: "), 1, 3)
        nurbs_layout.addWidget(self.length_double_spin, 1, 4)

        nurbs_grp = QtWidgets.QGroupBox("Create NURBS")
        nurbs_grp.setLayout(nurbs_layout)

        # poly to nurbs layout
        p2n_layout = QtWidgets.QGridLayout()
        p2n_layout.setSpacing(3)
        p2n_layout.setColumnStretch(0, 0)
        p2n_layout.setColumnStretch(1, 1)
        p2n_layout.setColumnStretch(2, 0)

        p2n_layout.addWidget(self.inner_edges_btn, 0, 0)
        p2n_layout.addWidget(self.outer_edges_btn, 0, 2)
        p2n_layout.addWidget(self.flip_normal_cb, 1, 0)
        p2n_layout.addWidget(self.closed_loop_cb, 1, 2)

        p2n_grp = QtWidgets.QGroupBox("Polygon To Nurbs")
        p2n_grp.setLayout(p2n_layout)

        # Ribbon layout
        ribbon_layout = QtWidgets.QHBoxLayout()
        ribbon_layout.addWidget(self.pin_label)
        ribbon_layout.addWidget(self.pin_spin)
        ribbon_layout.addStretch()
        ribbon_layout.addWidget(self.ctrl_label)
        ribbon_layout.addWidget(self.ctrl_spin)
        # GroupBox包裹layout
        ribbon_grp = QtWidgets.QGroupBox("Create Ribbon ")
        ribbon_grp.setLayout(ribbon_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(settings_grp)
        main_layout.addWidget(nurbs_grp)
        main_layout.addWidget(self.nurbs_btn)

        main_layout.addWidget(p2n_grp)
        main_layout.addWidget(self.p2n_btn)

        main_layout.addWidget(ribbon_grp)
        main_layout.addWidget(self.ribbon_button)

    def create_connections(self):
        # nurbs arguments
        self.orient_comb.currentTextChanged.connect(self.on_orient_comb_changed)
        self.width_double_spin.valueChanged.connect(self.on_width_spin_changed)
        self.length_double_spin.valueChanged.connect(self.on_length_spin_changed)
        self.segment_spin.valueChanged.connect(self.on_segment_spin_changed)
        self.ctrl_cb.toggled.connect(self.on_ctrl_cb_toggled)
        self.nurbs_btn.clicked.connect(self.on_nurbs_btn_clicked)

        # poly to nurbs
        self.inner_edges_btn.clicked.connect(self.on_inner_btn_clicked)
        self.outer_edges_btn.clicked.connect(self.on_outer_btn_clicked)
        self.flip_normal_cb.toggled.connect(self.on_flip_normal_cb_toggled)
        self.closed_loop_cb.toggled.connect(self.on_closed_loop_cb_toggled)
        self.p2n_btn.clicked.connect(self.on_p2n_btn_clicked)

        # ribbon arguments
        self.pin_spin.valueChanged.connect(self.on_pin_spin_changed)
        self.ctrl_spin.valueChanged.connect(self.on_ctrl_spin_changed)
        # ribbon btn
        self.ribbon_button.clicked.connect(self.on_ribbon_button_clicked)

    """----------------------------槽函数------------------------------"""

    @QtCore.Slot()
    def on_orient_comb_changed(self, text):
        """Ribbon朝向下拉菜单槽函数"""
        self.ribbon_axis = self.orient_comb.currentData()

    @QtCore.Slot()
    def on_width_spin_changed(self, value):
        """Ribbon宽度数值控件槽函数"""
        self.ribbon_width = value

    @QtCore.Slot()
    def on_length_spin_changed(self, value):
        """Ribbon长度数值控件槽函数"""
        self.ribbon_length = value

    @QtCore.Slot()
    def on_segment_spin_changed(self, value):
        """Ribbon段数数值控件槽函数"""
        self.ribbon_segment_count = value

    @QtCore.Slot()
    def on_ctrl_cb_toggled(self, check):
        """是否创建控制器复选框"""
        self.create_ctrl = check

    @QtCore.Slot()
    def on_nurbs_btn_clicked(self):
        """创建NURBS平面槽函数"""
        self.ribbon_name = self.name_line.text()
        try:
            self.nurbs_plane = self.create_nurbs_plane(
                self.ribbon_name,
                self.ribbon_axis,
                self.ribbon_width,
                self.ribbon_length,
                self.ribbon_segment_count,
            )
        except Exception as e:
            traceback.print_exc()
            QtWidgets.QMessageBox.warning(self, "Warning", f"{e}")

    @QtCore.Slot()
    def on_inner_btn_clicked(self):
        """创建NURBS曲线槽函数"""
        self.inner_curve = self.polygon_to_curve(
            curve_name=f"{self.ribbon_name}_iner_cuv",
        )
        return self.inner_curve

    @QtCore.Slot()
    def on_outer_btn_clicked(self):
        """创建NURBS曲线槽函数"""
        self.outer_curve = self.polygon_to_curve(
            curve_name=f"{self.ribbon_name}_outer_cuv",
        )
        return self.outer_curve

    @QtCore.Slot()
    def on_flip_normal_cb_toggled(self, check):
        """是否反转法线"""
        self.is_flip_normal = check

    @QtCore.Slot()
    def on_closed_loop_cb_toggled(self, check):
        """是否闭合曲面"""
        self.is_ring_plane = check

    @QtCore.Slot()
    def on_p2n_btn_clicked(self):
        """polygon to nurbs"""
        self.nurbs_plane = self.polygon_to_nurbs(
            self.ribbon_name,
            self.inner_curve,
            self.outer_curve,
            self.is_flip_normal,  # 是否反转曲面法线
        )
        pm.delete(self.inner_curve)
        pm.delete(self.outer_curve)

    @QtCore.Slot()
    def on_pin_spin_changed(self, value):
        """pin骨骼数量"""
        self.ribbon_pin_num = value

    @QtCore.Slot()
    def on_ctrl_spin_changed(self, value):
        """控制骨骼数量"""
        self.ribbon_ctrl_num = value

    @QtCore.Slot()
    def on_ribbon_button_clicked(self):
        """创建Ribbon"""
        self.ribbon_name = self.name_line.text()
        try:
            self.create_ribbon(
                self.nurbs_plane,
                self.ribbon_name,
                self.ribbon_pin_num,
                self.ribbon_ctrl_num,
                self.create_ctrl,
            )
        except Exception as e:
            traceback.print_exc()
            QtWidgets.QMessageBox.warning(self, "Warning", f"{e}")

    """---------------------静态方法和类方法------------------------"""

    @staticmethod
    def get_maya_main_window():
        """获取maya主界面"""
        app = QtWidgets.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    @classmethod
    def show_dialog(cls):
        """显示窗口"""
        if not cls._ui_instance:
            cls._ui_instance = RibbonCreator()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()

    """----------------------------------逻辑核心-----------------------------"""

    def create_nurbs_plane(
        self, ribbon_name, axis, width, length, segment_count
    ) -> pm.nodetypes.Transform:
        """创建NURBS平面，用于制作Ribbon
        Args:
            ribbon_name(str):ribbon名称
            axis (tuple): 平面朝向：(0,0,1)
            width (float): 宽度
            length (float):长度
            segment_count (ont): 段数

        returns:
            nt.Transform
        """
        length_ratio = length / width  # 长宽比
        nurbs_plane = pm.nurbsPlane(
            name=f"{ribbon_name}_plane",
            pivot=(0, 0, 0),  # 枢轴位置
            axis=axis,  # 朝向
            width=width,  # 宽度
            lengthRatio=length_ratio,  # 长宽比
            degree=3,  # 度
            u=1,  # u方向段数
            v=segment_count - 1,  # V方向段数
            constructionHistory=0,  # 是否保留历史
        )
        pm.select(clear=True)
        return nurbs_plane[0]

    def polygon_to_curve(self, curve_name):
        """将选中的多边形边转换为NURBS曲线
        Args:
            curve_name (str): 曲线名称
        Returns:
            nt.Transform: NURBS曲线
        """

        nirbs_curve = pm.polyToCurve(
            form=2,  # 曲线的形式: 0: 开放曲线 (Open)1: 闭合曲线 (Closed)2: 周期性曲线 (Periodic)，适合生成无缝闭合的曲线。
            degree=3,  # 曲线的度:1（线性）或 3（三次样条曲线，平滑）
            conformToSmoothMeshPreview=0,  # 是否使用均匀间距: 0: 非均匀间距 1:强制均匀间距。
            name="curve_name",
        )
        pm.select(clear=True)
        # pm.rebuildCurve("temp2", rpo=1, rt=0, s=20, ch=1)
        return nirbs_curve[0]

    def polygon_to_nurbs(self, ribbon_name, inner_curve, outer_curve, is_flip_nornal):
        """
        通过Loft命令将两个NURBS曲线 Loft 成一个NURBS曲面

        Args:
            ribbon_name (str): ribbon名称
            inner_curve (nt.Transform): 内侧NURBS曲线
            outer_curve (nt.Transform): 外侧NURBS曲线
            is_flip_nornal (bool): 是否反转曲面法线

        Returns:
            nt.Transform: 生成的NURBS曲面
        """
        nurbs_plane = pm.loft(
            inner_curve,
            outer_curve,
            reverse=0,  # 是否反转曲线的方向
            constructionHistory=0,  # 是否保留构造历史
            uniform=1,  # 是否使用均匀参数化。
            close=0,  # 是否闭合曲面，如果设置为true,则生成的表面将是封闭的(周期性)的,起点(终点)都在第一条曲线处。
            autoReverse=1,  # 自动调整曲面方向
            degree=3,  # 生成曲面的度数
            sectionSpans=1,  # 曲面的跨度数
            range=0,  # 是否使用完整曲线范围
            polygon=0,  # 是否生成多边形曲面。
            reverseSurfaceNormals=is_flip_nornal,  # 是否反转曲面法线，通过UV交换来实现
            name=f"{ribbon_name}_plane",
        )
        pm.select(clear=True)
        return nurbs_plane[0]

    def create_ribbon(
        self, nurbs_plane, ribbon_name, pin_num, ctrl_num, create_ctrl=False
    ):
        """使用矩阵节点实现Ribbon，
        使用"uvPin"节点将pin骨骼附加的nurbs平面
        使用"pointOnSurfaceInfo"节点获取控制骨骼和控制器位置
        控制骨骼蒙皮到nurbs平面
        控制器约束控制骨骼
        Args:
            nurbs_plane (pm.nodetypes.Transform): 要创建Ribbon的nurbsPlane
            ribbon_name（str）：ribbon名称
            pin_num (int): pin骨骼数量
            ctrl_num (int): 控制骨骼数量
            create_ctrl（bool）:是否创建控制器
        Returns:
            tuple[list, list]: 返回控制骨骼列表和pin骨骼列表
        """
        # 检查变量
        if pm.selected():
            nurbs_plane = pm.selected()[0]
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
        # 删除历史冻结变换
        pm.delete(nurbs_plane, constructionHistory=True)
        pm.makeIdentity(
            nurbs_plane,
            apply=True,
            translate=True,
            rotate=True,
            scale=True,
            normal=False,
        )
        # 获取nurbs plane 的形状节点
        nurbs_shape = nurbs_plane.getShape()
        # 创建pin骨骼
        pin_jnt_list = []
        pin_osg_list = []
        for i in range(pin_num):
            # 根据pin_num计算位置比例，uvPin默认以百分比计算UV位置，并且防止除0
            # 要创建5个pin骨骼，第0个骨骼在v方向0位置，第1个骨骼在v方向1/4位置
            v_pose = 0.0 if pin_num == 1 else (i / float(pin_num - 1))
            # 如果是闭合曲面（首尾相接），则多计算一个段数，防止首尾骨骼重合
            # 要创建5个pin骨骼，第0个骨骼在v方向0位置，第1个骨骼在v方向1/5位置，第4个骨骼在v方向4/5位置
            if self.is_ring_plane:
                v_pose = i / float(pin_num)
            # 创建 uvPin 节点
            uvPin_node = pm.createNode("uvPin", name=f"{ribbon_name}_uvPin_{i}")
            # 创建pin骨骼
            pin_jnt = pm.joint(name=f"{ribbon_name}_pin_{i}", radius=1)
            pin_osg = pm.createNode(
                "transform", name=f"{ribbon_name}_pin_{i}_osg", skipSelect=True
            )
            pm.parent(pin_jnt, pin_osg)
            # 设置和连接节点属性
            uvPin_node.coordinate[0].coordinateU.set(0.5)
            uvPin_node.coordinate[0].coordinateV.set(v_pose)

            nurbs_shape.worldSpace[0].connect(uvPin_node.deformedGeometry)
            # 连接骨骼偏移父对象矩阵,因为我们不会将pin骨骼直接用于蒙皮(游戏中骨骼不支持偏移父对象矩阵)
            uvPin_node.outputMatrix[0].connect(pin_osg.offsetParentMatrix)
            # 如果要将pin骨骼直接用于蒙皮,使用一下代码代替
            # decomposeMatrix_node = pm.createNode(
            #     "decomposeMatrix", name=f"decomposeMatrix{i}"
            # )
            # uvPin_node.outputMatrix[0].connect(decomposeMatrix_node.inputMatrix)
            # decomposeMatrix_node.outputTranslate.connect(pin_osg.translate)
            # decomposeMatrix_node.outputRotate.connect(pin_osg.rotate)

            # 添加列表
            pin_jnt_list.append(pin_jnt)
            pin_osg_list.append(pin_osg)
        # 创建控制骨骼和控制器
        ctrl_jnt_list = []
        ctrl_grp_list = []
        for i in range(ctrl_num):
            v_pose = 0 if ctrl_num == 1 else (i / float(ctrl_num - 1))
            # 如果是环形曲面（首尾相接），则多计算一个段数，防止首尾骨骼重合
            if self.is_ring_plane:
                v_pose = i / float(ctrl_num)

            # 创建 uvPin 节点
            ctrl_uvPin_node = pm.createNode(
                "uvPin", name=f"{ribbon_name}_ctrluvPin_{i}"
            )
            # 创建pin骨骼
            ctrl_pin_jnt = pm.joint(name=f"{ribbon_name}_ctrljnt_{i}", radius=3)
            # 设置和连接节点属性
            ctrl_uvPin_node.coordinate[0].coordinateU.set(0.5)
            ctrl_uvPin_node.coordinate[0].coordinateV.set(v_pose)

            nurbs_shape.worldSpace[0].connect(ctrl_uvPin_node.deformedGeometry)
            ctrl_decomposeMatrix_node = pm.createNode(
                "decomposeMatrix", name=f"ctrl_decomposeMatrix{i}"
            )
            ctrl_uvPin_node.outputMatrix[0].connect(
                ctrl_decomposeMatrix_node.inputMatrix
            )
            ctrljnt_translate = ctrl_decomposeMatrix_node.outputTranslate.get()
            ctrljnt_rotate = ctrl_decomposeMatrix_node.outputRotate.get()
            ctrljnt_scale = ctrl_decomposeMatrix_node.outputScale.get()
            ctrl_pin_jnt.translate.set(ctrljnt_translate)
            ctrl_pin_jnt.rotate.set(ctrljnt_rotate)
            ctrl_pin_jnt.scale.set(ctrljnt_scale)
            # 断开连接， 移除节点
            pm.delete(ctrl_decomposeMatrix_node, ctrl_uvPin_node)
            # 设置控制骨骼位置创建控制器
            if create_ctrl:
                ctrl_name = f"{ribbon_name}_ctrl_{i}"
                ctrl = pm.circle(
                    name=ctrl_name,
                    constructionHistory=False,
                    normal=self.ribbon_axis,
                    radius=8,
                )[0]
                # 创建控制骨骼偏移组
                ctrl_offset_grp = pm.group(ctrl, name=f"{ctrl_name}_offset")
                # 控制器对齐控制骨骼并约束
                pm.matchTransform(ctrl_offset_grp, ctrl_pin_jnt)
                pm.parentConstraint(ctrl, ctrl_pin_jnt, maintainOffset=True)
                pm.scaleConstraint(ctrl, ctrl_pin_jnt, maintainOffset=True)
                ctrl_grp_list.append(ctrl_offset_grp)
            ctrl_jnt_list.append(ctrl_pin_jnt)

        # 控制骨骼蒙皮到nur平面
        pm.skinCluster(nurbs_plane, ctrl_jnt_list)
        # 打组，整理场景
        pin_jnt_grp = pm.group(pin_osg_list, name=f"{ribbon_name}_pin_Jnt_grp")
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
