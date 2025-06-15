import pymel.core as pc
import maya.cmds as cmds  # 导入 maya.cmds 以便在某些 UI 回调中可能需要
from pathlib import Path
import functools  # 用于 partial，方便传递参数给回调函数
from ControlCreator.control_creator_backend import (
    get_control_shapes_dir,
    create_curve_from_data,
    read_json_data,
    adjust_controller_size,
    match_to_joint,
    orient_controller_cvs,
)


class ControlCreatorUI:
    def __init__(self):
        self.window_name = "ControlCreatorToolWindow"
        self.window_title = "控制器创建工具 (Control Creator)"

        self.control_shapes_path = get_control_shapes_dir()
        self.available_shapes = []
        self.selected_shape_file = None
        self.created_controllers = []  # 存储创建的控制器信息

        # 默认颜色 (Maya 索引颜色, 17是黄色)
        self.default_color_index = 17
        self.current_rgb_color = pc.colorIndex(self.default_color_index, q=True)

        if pc.window(self.window_name, exists=True):
            try:
                pc.deleteUI(self.window_name)
            except Exception as e:
                print(e)

        self.window = pc.window(
            self.window_name, title=self.window_title, sizeable=True, menuBar=True
        )

        # --- 菜单 ---
        pc.menu(label="文件", tearOff=False)
        pc.menuItem(label="刷新控制器列表", command=self.populate_shapes_grid)
        pc.menuItem(label="设置控制器形状文件夹...", command=self.set_shapes_folder_cmd)
        pc.menuItem(divider=True)
        pc.menuItem(label="关闭", command=lambda *args: pc.deleteUI(self.window_name))

        # --- 主布局 ---
        self.main_layout = pc.columnLayout(adj=True, rs=5, cal="center")

        # --- 搜索栏 (简化) ---
        pc.text(label="搜索（暂未实现动态过滤）：")
        self.search_field = pc.textField(placeholderText="搜索控制器形状...")

        # --- 控制器形状网格 ---
        pc.separator(h=10, style="in")
        pc.text(label="选择控制器形状:")
        self.shapes_scroll_layout = pc.scrollLayout(
            h=200, childResizable=True, borderVisible=True
        )  # 固定高度，可滚动
        self.shapes_grid_layout = pc.gridLayout(
            numberOfColumns=3, cellWidthHeight=(100, 100), ag=True
        )  # 3列，单元格大小
        self.populate_shapes_grid()
        pc.setParent("..")  # 返回到 shapes_scroll_layout 的父级 (main_layout)
        pc.setParent("..")  # 返回到 main_layout 的父级

        pc.separator(h=10, style="in")

        # --- 选项区域 ---
        with pc.frameLayout(
            label="控制器选项",
            collapsable=True,
            collapse=False,
            borderVisible=True,
            width=320,
        ):
            with pc.columnLayout(adj=True, rs=3):
                self.ctrl_name_field = pc.textFieldGrp(
                    label="控制器名称: ", text="myNewCtrl", cw=[(1, 80), (2, 200)]
                )

                # 颜色选择
                with pc.rowLayout(
                    nc=3, adj=3, rat=[(1, "both", 0), (2, "both", 0), (3, "both", 0)]
                ):
                    pc.text(label="颜色:")
                    self.color_swatch = pc.canvas(
                        width=50,
                        height=20,
                        rgbValue=self.current_rgb_color,
                        pressCommand=self.pick_color_cmd,
                    )
                    self.color_mode_radio = pc.radioButtonGrp(
                        label="",
                        labelArray2=["索引", "RGB"],
                        numberOfRadioButtons=2,
                        sl=1,  # 默认索引
                        onCommand1=self.update_color_mode,
                        onCommand2=self.update_color_mode,
                        cw2=[50, 50],
                        ct2=["left", "left"],
                    )

                self.scale_field = pc.floatFieldGrp(
                    label="大小 (缩放): ",
                    value1=1.0,
                    numberOfFields=1,
                    cw=[(1, 80), (2, 50)],
                )

                # 旋转 (简化为三个轴向的输入)
                self.rotate_x_field = pc.floatFieldGrp(
                    label="旋转 X: ",
                    value1=0.0,
                    numberOfFields=1,
                    cw=[(1, 80), (2, 50)],
                )
                self.rotate_y_field = pc.floatFieldGrp(
                    label="旋转 Y: ",
                    value1=0.0,
                    numberOfFields=1,
                    cw=[(1, 80), (2, 50)],
                )
                self.rotate_z_field = pc.floatFieldGrp(
                    label="旋转 Z: ",
                    value1=0.0,
                    numberOfFields=1,
                    cw=[(1, 80), (2, 50)],
                )

        pc.separator(h=10, style="in")

        # --- 操作按钮 ---
        self.match_to_selection_cb = pc.checkBox(
            label="匹配到选中的骨骼/对象", value=True
        )

        pc.button(
            label="创建控制器 (Create Controls)",
            h=40,
            bgc=(0.2, 0.6, 0.2),
            command=self.create_controls_cmd,
        )
        pc.button(
            label="对选中的控制器应用后处理",
            h=30,
            command=self.apply_post_process_to_selected_cmd,
            annotation="对场景中选中的控制器（或其offset group）应用上方的大小和旋转设置",
        )

        pc.setParent("..")  # 返回到 main_layout
        self.window.show()

    def set_shapes_folder_cmd(self, *args):
        result = pc.fileDialog2(
            fileMode=3,  # 文件夹选择
            dialogStyle=2,  # Maya 风格
            caption="选择控制器形状 (.json) 文件夹",
        )
        if result and len(result) > 0:
            new_path = Path(result[0])
            if new_path.is_dir():
                self.control_shapes_path = new_path
                self.populate_shapes_grid()
                pc.displayInfo(f"控制器形状文件夹已更新为: {new_path}")
            else:
                pc.warning("选择的路径不是一个有效的文件夹。")

    def update_color_mode(self, *args):
        # 如果切换到索引模式，尝试从RGB近似找到一个索引颜色
        # 如果切换到RGB模式，color_swatch已经显示RGB了
        # 这里只是简单地让用户知道模式变了，实际颜色拾取在 pick_color_cmd
        mode = self.color_mode_radio.getSelect()
        if mode == 1:  # 索引
            pc.displayInfo("颜色模式: 索引 (下次拾取颜色将设置索引)")
        else:  # RGB
            pc.displayInfo("颜色模式: RGB (下次拾取颜色将直接使用RGB)")

    def pick_color_cmd(self, *args):
        current_mode_is_index = self.color_mode_radio.getSelect() == 1

        # 获取当前 swatch 的颜色作为颜色编辑器的初始颜色
        initial_color = (
            self.color_swatch.getBackgroundColor()
        )  # 使用 getBackgroundColor for canvas

        # 打开 Maya 颜色编辑器
        pc.colorEditor(rgb=initial_color)  # 用之前swatch的颜色初始化

        if pc.colorEditor(query=True, result=True):  # 如果用户点击了 "OK"
            rgb_color = pc.colorEditor(query=True, rgb=True)  # 获取 RGB 值 (0-1范围)
            self.current_rgb_color = rgb_color  # 存储RGB

            if current_mode_is_index:
                # 如果是索引模式，我们尝试找到最接近的Maya索引颜色
                # 这只是一个简单的近似，Maya内部有更复杂的映射
                closest_index = 0
                min_dist = float("inf")
                for i in range(32):  # Maya有32个标准索引颜色
                    index_rgb = pc.colorIndex(i, q=True)
                    dist = sum([(rgb_color[j] - index_rgb[j]) ** 2 for j in range(3)])
                    if dist < min_dist:
                        min_dist = dist
                        closest_index = i
                self.default_color_index = closest_index
                # 更新swatch为索引颜色对应的RGB
                self.color_swatch.setBackgroundColor(
                    pc.colorIndex(self.default_color_index, q=True)
                )
                pc.displayInfo(f"选择了索引颜色: {self.default_color_index}")
            else:  # RGB 模式
                self.color_swatch.setBackgroundColor(rgb_color)
                pc.displayInfo(f"选择了RGB颜色: {rgb_color}")
        else:  # 用户取消
            pc.displayInfo("颜色选择已取消。")

    def populate_shapes_grid(self, *args):
        # 清理旧的按钮
        for child in self.shapes_grid_layout.getChildArray() or []:
            pc.deleteUI(child)

        self.available_shapes = []
        if (
            not self.control_shapes_path.exists()
            or not self.control_shapes_path.is_dir()
        ):
            pc.warning(f"控制器形状文件夹未找到或不是目录: {self.control_shapes_path}")
            pc.text(
                label="错误: 控制器形状文件夹无效。", parent=self.shapes_grid_layout
            )
            return

        json_files = sorted(list(self.control_shapes_path.glob("*.json")))

        if not json_files:
            pc.text(
                label="未找到控制器形状 (.json) 文件。", parent=self.shapes_grid_layout
            )
            return

        for json_file in json_files:
            shape_name = json_file.stem  # 获取文件名（不含扩展名）
            self.available_shapes.append({"name": shape_name, "path": json_file})

            # 创建一个iconTextButton 并使用图标
            icon_path = self.control_shapes_path / f"{shape_name}.png"  # 图标路径
            btn_label = shape_name[:15] + (
                "..." if len(shape_name) > 15 else ""
            )  # 截断长名称
            if icon_path.exists():
                btn = pc.iconTextButton(
                    style="iconAndTextVertical",
                    image1=str(icon_path),
                    label=btn_label,
                    parent=self.shapes_grid_layout,
                    width=80,
                    height=80,
                    command=functools.partial(self.select_shape_cmd, json_file),
                )
            else:
                btn = pc.button(
                    label=btn_label,
                    parent=self.shapes_grid_layout,
                    width=80,
                    height=80,
                    command=functools.partial(self.select_shape_cmd, json_file),
                )
                # 使用 functools.partial 来传递 json_file 给回调函数

    def select_shape_cmd(self, shape_file_path, *args):
        self.selected_shape_file = shape_file_path
        # 可选：高亮选中的按钮或在UI某处显示已选形状
        pc.displayInfo(f"已选择形状: {shape_file_path.name}")
        # 更新控制器名称字段为选定形状的名称（可选）
        self.ctrl_name_field.setText(shape_file_path.stem + "_ctrl")

    def create_controls_cmd(self, *args):
        if not self.selected_shape_file:
            pc.warning("请先从列表中选择一个控制器形状。")
            return

        ctrl_name = self.ctrl_name_field.getText()
        if not ctrl_name:
            pc.warning("请输入控制器名称。")
            return

        loaded_data = read_json_data(
            self.selected_shape_file.name, subfolder=self.control_shapes_path.name
        )
        if not loaded_data:
            pc.error(f"无法加载形状数据: {self.selected_shape_file.name}")
            return

        # 处理颜色
        use_index_color = self.color_mode_radio.getSelect() == 1
        color_idx = None
        rgb_col = None
        if use_index_color:
            color_idx = self.default_color_index
        else:
            rgb_col = self.current_rgb_color

        # 执行创建控制器
        is_checked = pc.checkBox(self.match_to_selection_cb, query=True, value=True)
        jnts = pc.selected()
        # 如果勾选了匹配选定对象，且有选定的骨骼
        if is_checked and jnts:
            # 遍历选定的骨骼创建控制器
            for jnt in jnts:
                created_info = create_curve_from_data(
                    loaded_data,
                    base_name=jnt.getName(),
                    new_color_index=color_idx,
                    new_rgb_color=rgb_col,
                )
                if not created_info:
                    pc.error("创建控制器失败。")
                    return
                self.apply_post_process(created_info)
                match_to_joint(created_info, jnt)
                self.created_controllers.append(created_info)
                pc.displayInfo(
                    f"控制器 '{created_info['offset_group'].name()}' 已创建。"
                )
            # 父子关系控制器
            # self.created_controllers 的结构是：
            # [
            #   {"offset_group": offset_grp_0_node, "curve_transform": curve_0_node}, # 索引 0
            #   {"offset_group": offset_grp_1_node, "curve_transform": curve_1_node}, # 索引 1
            #   {"offset_group": offset_grp_2_node, "curve_transform": curve_2_node}, # 索引 2
            #   ...
            # ]

            # 获取控制器数量
            # num_controllers = len(self.created_controllers)

            # if num_controllers > 1:  # 至少需要两个控制器才能形成父子关系
            #     # 循环到倒数第二个控制器，因为我们要访问 i 和 i+1
            #     for i in range(num_controllers - 1):
            #         # 将成为父级的控制器信息
            #         parent_controller_info = self.created_controllers[i]
            #         # 将成为子级的控制器信息
            #         child_controller_info = self.created_controllers[i + 1]

            #         # 通常，我们将下一个控制器的 "offset_group" 作为子对象
            #         child_to_be_parented = child_controller_info["offset_group"]

            #         # 而当前控制器的 "curve_transform" 作为父对象
            #         parent_object = parent_controller_info["curve_transform"]
            #         # 如果父子对象皆存在
            #         if child_to_be_parented and parent_object:
            #             try:
            #                 pc.parent(child_to_be_parented, parent_object)
            #                 print(
            #                     f"成功将 '{child_to_be_parented.name()}' 设置为 '{parent_object.name()}' 的子对象。"
            #                 )
            #             except Exception as e:
            #                 pc.warning(
            #                     f"设置父子关系时出错：将 '{child_to_be_parented.name()}' 设置为 '{parent_object.name()}' 的子对象失败。错误: {e}"
            #                 )
            #         else:
            #             pc.warning(
            #                 f"在索引 {i} 或 {i + 1} 处缺少有效的控制器节点信息。"
            #             )
            # else:
            #     print("控制器数量不足以创建父子关系。")

        # 如果没有勾选匹配选定对象，或者勾选但没有选中骨骼
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

            self.created_controllers.append(created_info)  # 存储引用
            pc.displayInfo(f"控制器 '{created_info['offset_group'].name()}' 已创建。")

            # 应用后处理 (大小、旋转、匹配)
            self.apply_post_process(created_info)

            pc.select(created_info["offset_group"])

    def apply_post_process(self, controller_info):
        """对给定的控制器应用UI中设置的大小、旋转和匹配"""
        if not controller_info or "offset_group" not in controller_info:
            return

        offset_grp = controller_info["offset_group"]
        curve_shapes = controller_info["curve_transform"].getShapes()

        # 1. 大小
        scale_val = self.scale_field.getValue1()
        if scale_val != 1.0:  # 只有当不是默认值1时才调整
            adjust_controller_size(controller_info, scale_val)

        # 2. 旋转 (CVs)
        rot_x = self.rotate_x_field.getValue1()
        rot_y = self.rotate_y_field.getValue1()
        rot_z = self.rotate_z_field.getValue1()
        if rot_x != 0.0 or rot_y != 0.0 or rot_z != 0.0:
            orient_controller_cvs(controller_info, [rot_x, rot_y, rot_z])

        # TODO 3.颜色
        use_index_color = self.color_mode_radio.getSelect() == 1
        new_color_index = None
        new_rgb_color = None
        if use_index_color:
            new_color_index = self.default_color_index
        else:
            new_rgb_color = self.current_rgb_color

        # 颜色属性
        for curve_shape in curve_shapes:
            if new_color_index is not None:  # 优先使用新指定的索引颜色
                curve_shape.overrideEnabled.set(True)
                curve_shape.overrideRGBColors.set(False)
                curve_shape.overrideColor.set(new_color_index)
            elif new_rgb_color is not None:  # 其次使用新指定的RGB颜色
                curve_shape.overrideEnabled.set(True)
                curve_shape.overrideRGBColors.set(True)
                curve_shape.overrideColorRGB.set(new_rgb_color)

    def apply_post_process_to_selected_cmd(self, *args):
        """对场景中选中的控制器（或其offset group）应用UI中的大小和旋转设置"""
        selected_nodes = pc.selected(type="transform")
        if not selected_nodes:
            pc.warning(
                "请先在场景中选择一个或多个控制器（的offset group或transform节点）。"
            )
            return

        for node in selected_nodes:
            # 尝试构建 controller_info 字典，以便与后端函数兼容
            # 这部分需要根据你的控制器层级结构来确定如何找到 curve_transform 和 offset_group
            temp_info = {}
            if node.name().endswith("_offset"):  # 假设选中了offset group
                temp_info["offset_group"] = node
                children_curves = [
                    child
                    for child in node.getChildren(type="transform")
                    if child.getShape(type="nurbsCurve")
                ]
                if children_curves:
                    temp_info["curve_transform"] = children_curves[0]
            elif node.getShape(type="nurbsCurve"):  # 假设选中了曲线的transform
                temp_info["curve_transform"] = node
                parent = node.getParent()
                if parent and parent.name().endswith("_offset"):  # 尝试找到offset group
                    temp_info["offset_group"] = parent
            else:
                pc.warning(f"跳过节点 {node.name()}：无法确定其为控制器结构。")
                continue

            if (
                "curve_transform" not in temp_info and "offset_group" not in temp_info
            ):  # 确保至少有一个有效
                pc.warning(f"跳过节点 {node.name()}：无法识别为有效控制器组件。")
                continue

            pc.displayInfo(f"对选中的 {node.name()} 应用后处理...")
            self.apply_post_process(temp_info)


# --- 用于启动UI的函数 ---
def show_control_creator_ui():
    ControlCreatorUI()


# --- 如果直接运行此脚本，显示UI ---
if __name__ == "__main__":
    show_control_creator_ui()
