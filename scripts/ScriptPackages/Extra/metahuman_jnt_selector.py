import maya.cmds as cmds
import maya.OpenMayaUI as omui
import pymel.core as pm
from Qt import QtCore, QtWidgets

# --- 动态处理 Maya 版本兼容性 (PySide2 vs PySide6) ---
try:
    # Maya 2025+ 使用 PySide6 / shiboken6
    from shiboken6 import wrapInstance
except ImportError:
    try:
        # Maya 2017-2024 使用 PySide2 / shiboken2
        from shiboken2 import wrapInstance
    except ImportError:
        # 极老版本 fallback
        from shiboken import wrapInstance


# --- 骨骼选择组数据 ---
JOINT_GROUPS = {
    "头骨": ["FACIAL_C_Skull"],
    "眼球": [
        "FACIAL_L_EyelidUpperA",
        "FACIAL_L_EyelidUpperB",
        "FACIAL_L_EyelidLowerA",
        "FACIAL_L_EyelidLowerB",
        "FACIAL_L_Eye",
    ],
    "瞳孔": ["FACIAL_L_Pupil"],
    "鼻子": [
        "FACIAL_C_Nose",
        "FACIAL_C_NoseTip",
        "FACIAL_L_Nostril",
        "FACIAL_C_NoseLower",
    ],
    "鼻梁": ["FACIAL_C_Nose"],
    "鼻尖": ["FACIAL_C_NoseTip"],
    "鼻翼": ["FACIAL_L_Nostril"],
    "鼻底": ["FACIAL_C_NoseLower"],
    "下颌": [
        "FACIAL_C_Jaw",
        "FACIAL_C_LowerLipRotation",
    ],
    "下巴": ["FACIAL_C_Chin"],
    "上牙": ["FACIAL_C_TeethUpper"],
    "下牙": ["FACIAL_C_TeethLower"],
    "舌头": ["FACIAL_C_Tongue1"],
    "嘴部": ["FACIAL_C_MouthUpper", "FACIAL_C_MouthLower"],
}


class MhJntSelector(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "MetaHuman Joint Selector"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(MhJntSelector.WINDOW_TITLE)
        self.resize(350, 400)  # 给一个初始大小
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # 尝试自动填充 Mesh 名称（如果有选中的话）
        self.auto_fill_mesh_name()

    def create_widgets(self):
        self.central_widget = QtWidgets.QWidget()

        # 1. Mesh 载入/隔离区域
        self.mesh_label = QtWidgets.QLabel("Mesh 模型名称:")
        self.mesh_line_edit = QtWidgets.QLineEdit()
        self.mesh_line_edit.setPlaceholderText("例如: Face_Mesh (留空只选骨骼)")
        self.load_button = QtWidgets.QPushButton("载入 Mesh")
        self.load_button.setToolTip("将当前选中的物体名称填入输入框")

        # 2. 骨骼选择按钮区域
        self.joint_buttons = {}
        for name, joints in JOINT_GROUPS.items():
            button = QtWidgets.QPushButton(name)
            button.joint_list = joints
            button.setSizePolicy(
                QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred
            )
            button.setMinimumHeight(30)
            self.joint_buttons[name] = button

        # 3. 镜像骨骼按钮
        self.mirror_button = QtWidgets.QPushButton("执行 L -> R 镜像骨骼")
        self.mirror_button.setStyleSheet(
            "QPushButton { background-color: #3498DB; color: white; font-weight: bold; padding: 10px; } QPushButton:hover { background-color: #5DADE2; }"
        )
        self.mirror_button.setToolTip("将左侧骨骼位置镜像到右侧")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)  # 直接设置给 self (QDialog)

        # 1. Mesh 载入布局
        mesh_layout = QtWidgets.QHBoxLayout()
        mesh_layout.addWidget(self.mesh_label)
        mesh_layout.addWidget(self.mesh_line_edit)
        mesh_layout.addWidget(self.load_button)

        # 2. 骨骼选择网格布局
        joint_group = QtWidgets.QGroupBox("骨骼快速选择与隔离")
        joint_layout = QtWidgets.QGridLayout(joint_group)
        joint_layout.setSpacing(5)

        row, col = 0, 0
        for name, button in self.joint_buttons.items():
            joint_layout.addWidget(button, row, col)
            col += 1
            if col > 1:  # 每行 2 个
                col = 0
                row += 1

        # 3. 组合
        main_layout.addLayout(mesh_layout)
        main_layout.addSpacing(10)
        main_layout.addWidget(joint_group)
        main_layout.addSpacing(10)
        main_layout.addWidget(self.mirror_button)
        main_layout.addStretch()

    def create_connections(self):
        # 这里的载入按钮我改为了“获取当前选择的物体名”，这样更方便
        self.load_button.clicked.connect(self.on_get_selected_mesh)

        for name, button in self.joint_buttons.items():
            button.clicked.connect(
                lambda checked=False,
                j_list=button.joint_list: self.on_joint_select_clicked(j_list)
            )

        self.mirror_button.clicked.connect(MhJntSelector.mirror_joints_L_to_R)

    def auto_fill_mesh_name(self):
        """如果用户当前已经选中了模型，自动填入"""
        sel = pm.selected(type="transform")
        if sel:
            # 简单判断是否可能是头部 Mesh
            self.mesh_line_edit.setText(sel[0].name())

    # --- Callbacks ---

    def on_get_selected_mesh(self):
        """获取当前选中的物体填入输入框，并尝试隔离"""
        sel = pm.selected()
        if sel:
            name = sel[0].name()
            self.mesh_line_edit.setText(name)

            # 尝试直接隔离选中的这个 Mesh
            model_panel = MhJntSelector.get_active_model_panel()
            if model_panel:
                pm.isolateSelect(model_panel, state=1)
                pm.isolateSelect(model_panel, addSelected=True)
                pm.isolateSelect(model_panel, update=True)
        else:
            pm.warning("请先在场景中选择 Mesh 模型。")

    def on_joint_select_clicked(self, joint_list):
        mesh_name = self.mesh_line_edit.text()
        MhJntSelector.select_and_isolate(mesh_name, joint_list)

    # --- 骨骼选择逻辑函数 ---

    @staticmethod
    def get_active_model_panel():
        """
        智能获取当前激活的模型视口 (Viewport)。
        优先级:
        1. 拥有焦点的 ModelPanel
        2. 鼠标指针下的 ModelPanel
        3. 场景中可见的第一个 ModelPanel
        """
        # 1. 尝试获取带焦点的面板
        panel = cmds.getPanel(withFocus=True)
        if panel and cmds.getPanel(typeOf=panel) == "modelPanel":
            return panel

        # 2. 尝试获取鼠标下的面板
        panel = cmds.getPanel(underPointer=True)
        if panel and cmds.getPanel(typeOf=panel) == "modelPanel":
            return panel

        # 3. 都不行，遍历所有可见的 modelPanel，返回第一个
        vis_panels = cmds.getPanel(visiblePanels=True)
        for p in vis_panels:
            if cmds.getPanel(typeOf=p) == "modelPanel":
                return p

        return None

    @staticmethod
    def select_and_isolate(mesh_name, joint_names):
        """
        选择指定的骨骼，并将指定的 Mesh 模型和选中的骨骼一起隔离显示。
        """
        try:
            # 1. 选择骨骼
            valid_joints = [j for j in joint_names if cmds.objExists(j)]

            if not valid_joints:
                pm.warning("场景中找不到列表中指定的任何骨骼。")
                return

            pm.select(clear=True)
            pm.select(valid_joints, replace=True)
            print("已选择骨骼: " + ", ".join(valid_joints))

            selected_joints = pm.ls(selection=True, type="joint")

            # 2. 隔离显示逻辑
            # 即使没有 Mesh，也应该允许选择骨骼，所以这里不做强制 return，只是标记是否隔离
            isolate_objects = list(selected_joints)

            if mesh_name and pm.objExists(mesh_name):
                mesh_obj = pm.ls(mesh_name)
                isolate_objects.extend(mesh_obj)
            elif mesh_name:
                pm.warning(f"Mesh '{mesh_name}' 不存在，将仅隔离显示骨骼。")
            else:
                pm.warning("未输入 Mesh 名称，将仅隔离显示骨骼。")

            # 获取视口
            model_panel_name = MhJntSelector.get_active_model_panel()
            if not model_panel_name:
                pm.warning("未找到活动的视口 (Viewport)，无法执行隔离显示。")
                return

            # 执行隔离显示 (先开启隔离状态，再加载选定对象，这样最稳)
            # 方法 A: 暴力重置
            pm.isolateSelect(model_panel_name, state=0)  # 先关
            pm.isolateSelect(model_panel_name, state=1)  # 再开

            # 清空当前隔离列表并添加新对象
            # 注意：addSelected 往往比 addItems 稳定，但我们需要精确控制
            for obj in isolate_objects:
                pm.isolateSelect(model_panel_name, addDagObject=obj)

            # 强制刷新视图
            pm.isolateSelect(model_panel_name, update=True)
            print(f"✅ 在视口 '{model_panel_name}' 执行隔离显示。")

        except Exception as e:
            pm.error(f"执行选择/隔离显示时发生错误: {e}")

    @staticmethod
    def mirror_joints_L_to_R():
        """执行镜像体积骨骼逻辑：将 '_L_' 骨骼的位置镜像到 '_R_' 骨骼。"""
        # 查找所有以 'FACIAL_L_' 开头且类型为 'joint' 的对象
        l_joints = pm.ls("FACIAL_L_*", type="joint")
        mirrored_count = 0

        if not l_joints:
            pm.warning("场景中未找到 'FACIAL_L_*' 骨骼。")
            return

        try:
            for jnt in l_joints:
                # 确保名称中包含 "_L_" 且能正确替换
                if "_L_" in jnt.name():
                    r_joint_name = jnt.name().replace("_L_", "_R_")

                    if pm.objExists(r_joint_name):
                        r_joint = pm.ls(r_joint_name)[0]

                        # 1. 查询 L 骨骼的世界空间位置
                        pos = pm.xform(
                            jnt, query=True, translation=True, worldSpace=True
                        )

                        # 2. 计算镜像位置（X 轴取反）
                        mirror_pos = [-pos[0], pos[1], pos[2]]

                        # 3. 设置 R 骨骼的世界空间位置
                        pm.xform(r_joint, translation=mirror_pos, worldSpace=True)
                        mirrored_count += 1

            print(f"骨骼镜像完成。共镜像了 {mirrored_count} 对骨骼。")

        except Exception as e:
            pm.error(f"执行镜像骨骼时发生错误: {e}")

    def closeEvent(self, event):
        MhJntSelector._ui_instance = None
        super(MhJntSelector, self).closeEvent(event)

    @staticmethod
    def get_maya_main_window():
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrapInstance(int(ptr), QtWidgets.QMainWindow)
        return None

    @classmethod
    def show_ui(cls):
        if cls._ui_instance is None or not cls._ui_instance.isVisible():
            cls._ui_instance = MhJntSelector()
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# 执行代码
def run():
    MhJntSelector.show_ui()


# 执行代码
if __name__ == "__main__":
    run()
