import pymel.core as pc
from PySide2 import QtWidgets, QtGui, QtCore
from pathlib import Path
import functools
from ..utils.path_manager import PathManager
from ..utils.color_manager import ColorManager
from ..utils.constants import UIConstants
from ..backend.control_creator_backend import (
    create_curve_from_data,
    read_json_data,
    adjust_controller_size,
    match_to_joint,
    orient_controller_cvs,
)


class ControlCreatorUI(QtWidgets.QMainWindow):
    """控制器创建工具的 PySide2 UI 界面"""

    def __init__(self, parent=None):
        super(ControlCreatorUI, self).__init__(parent)
        self.setWindowTitle("控制器创建工具 (Control Creator)")
        self.setMinimumWidth(UIConstants.WINDOW_WIDTH)
        self.control_shapes_path = PathManager.get_control_shapes_dir()
        self.available_shapes = []
        self.selected_shape_file = None
        self.created_controllers = []
        self.color_manager = ColorManager(UIConstants.DEFAULT_COLOR_INDEX)
        self._build_ui()

    def _build_ui(self):
        """构建主 UI"""
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.main_layout.setSpacing(10)

        self._build_menu()
        self._build_search_bar()
        self._build_shapes_grid()
        self._build_options_frame()
        self._build_action_buttons()

    def _build_menu(self):
        """构建菜单栏"""
        menubar = self.menuBar()
        file_menu = menubar.addMenu("文件")
        file_menu.addAction("刷新控制器列表", self.populate_shapes_grid)
        file_menu.addAction("设置控制器形状文件夹...", self.set_shapes_folder_cmd)
        file_menu.addSeparator()
        file_menu.addAction("关闭", self.close)

    def _build_search_bar(self):
        """构建搜索栏"""
        search_layout = QtWidgets.QHBoxLayout()
        search_label = QtWidgets.QLabel("搜索控制器形状：")
        self.search_field = QtWidgets.QLineEdit()
        self.search_field.setPlaceholderText("输入形状名称...")
        self.search_field.textChanged.connect(self._filter_shapes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_field)
        self.main_layout.addLayout(search_layout)

    def _build_shapes_grid(self):
        """构建形状选择网格"""
        self.shapes_scroll = QtWidgets.QScrollArea()
        self.shapes_scroll.setWidgetResizable(True)
        self.shapes_scroll.setMinimumHeight(UIConstants.SCROLL_HEIGHT)
        self.shapes_widget = QtWidgets.QWidget()
        self.shapes_grid = QtWidgets.QGridLayout(self.shapes_widget)
        self.shapes_grid.setSpacing(5)
        self.shapes_scroll.setWidget(self.shapes_widget)
        self.main_layout.addWidget(self.shapes_scroll)
        self.populate_shapes_grid()

    def _build_options_frame(self):
        """构建控制器选项区域"""
        options_frame = QtWidgets.QGroupBox("控制器选项")
        options_layout = QtWidgets.QVBoxLayout(options_frame)
        options_layout.setSpacing(5)

        # 控制器名称
        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("控制器名称：")
        self.ctrl_name_field = QtWidgets.QLineEdit("myNewCtrl")
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.ctrl_name_field)
        options_layout.addLayout(name_layout)

        # 颜色选择
        color_layout = QtWidgets.QHBoxLayout()
        color_label = QtWidgets.QLabel("颜色：")
        self.color_swatch = QtWidgets.QPushButton()
        self.color_swatch.setFixedSize(50, 20)
        self.update_color_swatch()
        self.color_swatch.clicked.connect(self._pick_color_cmd)
        self.color_mode_radio = QtWidgets.QButtonGroup()
        index_radio = QtWidgets.QRadioButton("索引")
        rgb_radio = QtWidgets.QRadioButton("RGB")
        self.color_mode_radio.addButton(index_radio, 1)
        self.color_mode_radio.addButton(rgb_radio, 2)
        index_radio.setChecked(True)
        index_radio.toggled.connect(lambda: self.color_manager.toggle_mode(True))
        rgb_radio.toggled.connect(lambda: self.color_manager.toggle_mode(False))
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_swatch)
        color_layout.addWidget(index_radio)
        color_layout.addWidget(rgb_radio)
        color_layout.addStretch()
        options_layout.addLayout(color_layout)

        # 大小
        scale_layout = QtWidgets.QHBoxLayout()
        scale_label = QtWidgets.QLabel("大小 (缩放)：")
        self.scale_field = QtWidgets.QDoubleSpinBox()
        self.scale_field.setValue(1.0)
        self.scale_field.setSingleStep(0.1)
        self.scale_field.setMinimum(0.1)
        scale_layout.addWidget(scale_label)
        scale_layout.addWidget(self.scale_field)
        scale_layout.addStretch()
        options_layout.addLayout(scale_layout)

        # 旋转
        rotate_layout = QtWidgets.QVBoxLayout()
        for axis in ["X", "Y", "Z"]:
            layout = QtWidgets.QHBoxLayout()
            label = QtWidgets.QLabel(f"旋转 {axis}：")
            spinbox = QtWidgets.QDoubleSpinBox()
            spinbox.setObjectName(f"rotate_{axis.lower()}_field")
            spinbox.setSingleStep(5.0)
            spinbox.setMinimum(-360.0)
            spinbox.setMaximum(360.0)
            layout.addWidget(label)
            layout.addWidget(spinbox)
            layout.addStretch()
            rotate_layout.addLayout(layout)
        options_layout.addLayout(rotate_layout)

        self.main_layout.addWidget(options_frame)

    def _build_action_buttons(self):
        """构建操作按钮"""
        self.match_to_selection_cb = QtWidgets.QCheckBox("匹配到选中的骨骼/对象")
        self.match_to_selection_cb.setChecked(True)
        self.hierarchy_cb = QtWidgets.QCheckBox("Hierarchy (控制器跟随骨骼层级)")
        create_button = QtWidgets.QPushButton("创建控制器 (Create Controls)")
        create_button.setStyleSheet(
            f"background-color: rgb({UIConstants.BUTTON_COLOR[0] * 255}, {UIConstants.BUTTON_COLOR[1] * 255}, {UIConstants.BUTTON_COLOR[2] * 255});"
        )
        create_button.setFixedHeight(40)
        create_button.clicked.connect(self.create_controls_cmd)
        post_process_button = QtWidgets.QPushButton("对选中的控制器应用后处理")
        post_process_button.setFixedHeight(30)
        post_process_button.clicked.connect(self.apply_post_process_to_selected_cmd)
        post_process_button.setToolTip(
            "对选中的控制器（或其 offset group）应用大小和旋转设置"
        )
        self.main_layout.addWidget(self.match_to_selection_cb)
        self.main_layout.addWidget(self.hierarchy_cb)
        self.main_layout.addWidget(create_button)
        self.main_layout.addWidget(post_process_button)
        self.main_layout.addStretch()

    def update_color_swatch(self):
        """更新颜色样本显示"""
        rgb = self.color_manager.current_rgb_color
        self.color_swatch.setStyleSheet(
            f"background-color: rgb({rgb[0] * 255}, {rgb[1] * 255}, {rgb[2] * 255});"
        )

    def set_shapes_folder_cmd(self):
        """设置控制器形状文件夹"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择控制器形状 (.json) 文件夹", str(self.control_shapes_path)
        )
        if folder:
            new_path = Path(folder)
            if PathManager.set_control_shapes_dir(new_path):
                self.control_shapes_path = new_path
                self.populate_shapes_grid()
                pc.displayInfo(f"控制器形状文件夹已更新为: {new_path}")
            else:
                pc.warning("选择的路径不是一个有效的文件夹。")

    def _filter_shapes(self, text):
        """根据搜索文本过滤形状网格"""
        self.populate_shapes_grid(text.lower())

    def populate_shapes_grid(self, search_filter=""):
        """填充形状选择网格"""
        for i in reversed(range(self.shapes_grid.count())):
            widget = self.shapes_grid.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.available_shapes = []
        if (
            not self.control_shapes_path.exists()
            or not self.control_shapes_path.is_dir()
        ):
            pc.warning(f"控制器形状文件夹无效: {self.control_shapes_path}")
            label = QtWidgets.QLabel("错误: 控制器形状文件夹无效。")
            self.shapes_grid.addWidget(label, 0, 0)
            return
        json_files = sorted(self.control_shapes_path.glob("*.json"))
        if not json_files:
            label = QtWidgets.QLabel("未找到控制器形状 (.json) 文件。")
            self.shapes_grid.addWidget(label, 0, 0)
            return
        row, col = 0, 0
        for json_file in json_files:
            shape_name = json_file.stem
            if search_filter and search_filter not in shape_name.lower():
                continue
            self.available_shapes.append({"name": shape_name, "path": json_file})
            btn_label = shape_name[:15] + ("..." if len(shape_name) > 15 else "")
            button = QtWidgets.QPushButton(btn_label)
            button.setFixedSize(*UIConstants.GRID_CELL_SIZE)
            icon_path = self.control_shapes_path / f"{shape_name}.png"
            if icon_path.exists():
                button.setIcon(QtGui.QIcon(str(icon_path)))
                button.setIconSize(QtCore.QSize(80, 80))
            button.clicked.connect(functools.partial(self.select_shape_cmd, json_file))
            self.shapes_grid.addWidget(button, row, col)
            col += 1
            if col >= UIConstants.GRID_COLUMNS:
                col = 0
                row += 1

    def select_shape_cmd(self, shape_file_path):
        """选择控制器形状"""
        self.selected_shape_file = shape_file_path
        self.ctrl_name_field.setText(shape_file_path.stem + "_ctrl")
        pc.displayInfo(f"已选择形状: {shape_file_path.name}")

    def _pick_color_cmd(self):
        """选择颜色"""
        if self.color_manager.pick_color(self.color_swatch):
            self.update_color_swatch()

    def create_controls_cmd(self):
        """创建控制器"""
        if not self.selected_shape_file:
            pc.warning("请先选择一个控制器形状。")
            return
        ctrl_name = self.ctrl_name_field.text()
        if not ctrl_name:
            pc.warning("请输入控制器名称。")
            return
        loaded_data = read_json_data(
            self.selected_shape_file.name, subfolder=self.control_shapes_path.name
        )
        if not loaded_data:
            pc.error(f"无法加载形状数据: {self.selected_shape_file.name}")
            return
        color_idx = (
            self.color_manager.default_color_index
            if self.color_manager.use_index_mode
            else None
        )
        rgb_col = (
            self.color_manager.current_rgb_color
            if not self.color_manager.use_index_mode
            else None
        )
        is_checked = self.match_to_selection_cb.isChecked()
        is_hierarchy_mode = self.hierarchy_cb.isChecked()
        jnts = pc.selected()
        if is_hierarchy_mode and jnts:
            progress = pc.progressWindow(
                title="创建控制器", maxValue=len(jnts), isInterruptable=True
            )
            try:
                self._create_hierarchy_controllers(
                    jnts, loaded_data, color_idx, rgb_col
                )
            finally:
                pc.progressWindow(endProgress=True)
        elif is_checked and jnts:
            progress = pc.progressWindow(
                title="创建控制器", maxValue=len(jnts), isInterruptable=True
            )
            try:
                for i, jnt in enumerate(jnts):
                    if pc.progressWindow(query=True, isCancelled=True):
                        break
                    pc.progressWindow(
                        edit=True, progress=i, status=f"创建控制器: {jnt.name()}"
                    )
                    created_info = create_curve_from_data(
                        loaded_data,
                        base_name=jnt.nodeName(),
                        new_color_index=color_idx,
                        new_rgb_color=rgb_col,
                    )
                    if not created_info:
                        pc.warning(f"跳过 {jnt.name()}：控制器创建失败。")
                        continue
                    self.apply_post_process(created_info)
                    match_to_joint(created_info, jnt)
                    self.created_controllers.append(created_info)
                    pc.displayInfo(
                        f"控制器 '{created_info['offset_group'].name()}' 已创建。"
                    )
            finally:
                pc.progressWindow(endProgress=True)
        else:
            created_info = create_curve_from_data(
                loaded_data,
                base_name=ctrl_name,
                new_color_index=color_idx,
                new_rgb_color=rgb_col,
            )
            if not created_info:
                pc.error("创建控制器失败。")
                return
            self.created_controllers.append(created_info)
            self.apply_post_process(created_info)
            pc.select(created_info["offset_group"])
            pc.displayInfo(f"控制器 '{created_info['offset_group'].name()}' 已创建。")

    def _create_hierarchy_controllers(self, joints, loaded_data, color_idx, rgb_col):
        """递归创建控制器并跟随骨骼层级"""
        self.created_controllers = []
        jnt_to_controller = {}

        def create_recursive(joint):
            if not isinstance(joint, pc.nodetypes.Joint):
                pc.warning(f"跳过 {joint.name()}：不是骨骼节点。")
                return None
            created_info = create_curve_from_data(
                loaded_data,
                base_name=joint.nodeName(),
                new_color_index=color_idx,
                new_rgb_color=rgb_col,
            )
            if not created_info:
                pc.warning(f"骨骼 {joint.name()} 的控制器创建失败。")
                return None
            self.apply_post_process(created_info)
            match_to_joint(created_info, joint)
            self.created_controllers.append(created_info)
            jnt_to_controller[joint] = created_info["offset_group"]
            for child in joint.getChildren(type="joint"):
                child_ctrl_group = create_recursive(child)
                if child_ctrl_group:
                    pc.parent(child_ctrl_group, created_info["curve_transform"])
            return created_info["offset_group"]

        for i, root_joint in enumerate(joints):
            if pc.progressWindow(query=True, isCancelled=True):
                break
            pc.progressWindow(
                edit=True, progress=i, status=f"创建控制器: {root_joint.name()}"
            )
            create_recursive(root_joint)
        if self.created_controllers:
            pc.select([c["offset_group"] for c in self.created_controllers])
            pc.displayInfo(f"共创建控制器: {len(self.created_controllers)}")

    def apply_post_process(self, controller_info):
        """应用大小、旋转和颜色设置"""
        if not controller_info or "offset_group" not in controller_info:
            return
        scale_val = self.scale_field.value()
        if scale_val != 1.0:
            adjust_controller_size(controller_info, scale_val)
        rot_x = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_x_field").value()
        rot_y = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_y_field").value()
        rot_z = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_z_field").value()
        if rot_x != 0.0 or rot_y != 0.0 or rot_z != 0.0:
            orient_controller_cvs(controller_info, [rot_x, rot_y, rot_z])
        curve_shapes = controller_info["curve_transform"].getShapes()
        for curve_shape in curve_shapes:
            self.color_manager.apply_color_to_curve(
                curve_shape,
                {},
                self.color_manager.default_color_index
                if self.color_manager.use_index_mode
                else None,
                self.color_manager.current_rgb_color
                if not self.color_manager.use_index_mode
                else None,
            )

    def apply_post_process_to_selected_cmd(self):
        """对选中的控制器应用后处理"""
        selected_nodes = pc.selected(type="transform")
        if not selected_nodes:
            pc.warning("请先选择控制器（offset group 或 transform 节点）。")
            return
        progress = pc.progressWindow(
            title="应用后处理", maxValue=len(selected_nodes), isInterruptable=True
        )
        try:
            # 保存 UI 输入值
            scale_val = self.scale_field.value()
            rot_x = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_x_field").value()
            rot_y = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_y_field").value()
            rot_z = self.findChild(QtWidgets.QDoubleSpinBox, "rotate_z_field").value()
            for i, node in enumerate(selected_nodes):
                if pc.progressWindow(query=True, isCancelled=True):
                    break
                pc.progressWindow(
                    edit=True, progress=i, status=f"处理控制器: {node.name()}"
                )
                controller_info = self._get_controller_info_from_node(node)
                if not controller_info:
                    pc.warning(f"跳过 {node.name()}：不是有效的控制器结构。")
                    continue
                pc.displayInfo(f"对 {node.name()} 应用后处理...")
                self.apply_post_process(controller_info)
            # 在所有控制器处理后再重置 UI
            self.scale_field.setValue(1.0)
            self.findChild(QtWidgets.QDoubleSpinBox, "rotate_x_field").setValue(0.0)
            self.findChild(QtWidgets.QDoubleSpinBox, "rotate_y_field").setValue(0.0)
            self.findChild(QtWidgets.QDoubleSpinBox, "rotate_z_field").setValue(0.0)
        finally:
            pc.progressWindow(endProgress=True)

    def _get_controller_info_from_node(self, node):
        """从节点获取控制器信息"""
        if not isinstance(node, pc.nodetypes.Transform):
            return None
        temp_info = {}
        if node.name().endswith("_offset"):
            temp_info["offset_group"] = node
            children_curves = [
                c
                for c in node.getChildren(type="transform")
                if c.getShape(type="nurbsCurve")
            ]
            if children_curves:
                temp_info["curve_transform"] = children_curves[0]
        elif node.getShape(type="nurbsCurve"):
            temp_info["curve_transform"] = node
            parent = node.getParent()
            if parent and parent.name().endswith("_offset"):
                temp_info["offset_group"] = parent
        return temp_info if temp_info.get("curve_transform") else None


def show_control_creator_ui():
    """启动 UI"""
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication([])
    from shiboken2 import wrapInstance
    import maya.OpenMayaUI as omui

    main_window_ptr = omui.MQtUtil.mainWindow()
    main_window = wrapInstance(int(main_window_ptr), QtWidgets.QMainWindow)
    ui = ControlCreatorUI(parent=main_window)
    ui.show()
    return ui


if __name__ == "__main__":
    show_control_creator_ui()
