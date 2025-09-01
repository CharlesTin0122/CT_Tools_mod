import sys
from Qt.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QFrame,
    QToolButton,
)
from Qt.QtGui import QFont
from Qt.QtCore import Qt


# --- 主窗口类 ---
class TcToolsUI(QWidget):
    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = TcToolsUI.maya_main_window()
        super().__init__(parent)
        self.setWindowTitle("Tc TOOLS V1.0")
        self.setGeometry(300, 300, 350, 600)

        # 初始化UI
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- 1. 顶部栏 (与之前相同) ---
        top_bar_widget = self._create_top_bar()
        main_layout.addWidget(top_bar_widget)

        # --- 2. 搜索栏 (与之前相同) ---
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 5, 10, 5)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索...")
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        main_layout.addWidget(line)

        # --- 3. 功能列表 (关键改动) ---
        # 使用 QTreeWidget 替换 QListWidget
        self.tool_tree = QTreeWidget()
        self.tool_tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tool_tree.setHeaderHidden(True)  # 隐藏默认的表头
        self.tool_tree.setIndentation(10)  # 设置子项的缩进
        self.populate_tool_tree()  # 调用新的填充函数
        main_layout.addWidget(self.tool_tree)

        self.setLayout(main_layout)

    def _create_top_bar(self):
        """创建一个自定义的顶部栏Widget (与之前相同)"""
        top_bar_widget = QWidget()
        top_bar_layout = QHBoxLayout(top_bar_widget)
        top_bar_layout.setContentsMargins(10, 5, 10, 5)
        top_bar_layout.setSpacing(10)

        profile_label = QLabel()

        profile_label.setFixedSize(40, 40)

        btn_edit = QToolButton()

        btn_settings = QToolButton()

        btn_office = QToolButton()

        btn_help = QToolButton()

        btn_power = QToolButton()
        btn_power.setObjectName("PowerButton")

        for btn in [btn_edit, btn_settings, btn_office, btn_help, btn_power]:
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        top_bar_layout.addWidget(profile_label)
        top_bar_layout.addWidget(btn_edit)
        top_bar_layout.addWidget(btn_settings)
        top_bar_layout.addWidget(btn_office)
        top_bar_layout.addWidget(btn_help)
        top_bar_layout.addStretch()
        top_bar_layout.addWidget(btn_power)

        return top_bar_widget

    def populate_tool_tree(self):
        """填充功能树 (关键改动)"""
        # --- 收藏夹 分类 ---
        fav_category = self.add_category_item(self.tool_tree, "收藏夹")
        self.add_tool_item(fav_category, "全部")
        # 添加“绑定”并保存为变量，以便后续添加子项
        binding_item = self.add_tool_item(fav_category, "绑定")
        self.add_tool_item(binding_item, "JT_Controller_Tools_Ver_2.0")
        self.add_tool_item(binding_item, "blendDivider_ver_1.0")

        # 默认展开“收藏夹”和“绑定”
        fav_category.setExpanded(True)
        binding_item.setExpanded(True)

        # 选中“绑定”的子项，使其父项高亮
        self.tool_tree.setCurrentItem(binding_item.child(0))

        # --- 动画 分类 ---
        anim_category = self.add_category_item(self.tool_tree, "动画")
        # 可以在这里为“动画”分类添加子项
        # self.add_tool_item(anim_category, "工具A", "icons/some_icon.png")

        # --- 模型 分类 ---
        model_category = self.add_category_item(self.tool_tree, "模型")

        # --- 渲染 分类 ---
        render_category = self.add_category_item(
            self.tool_tree,
            "渲染",
        )

    def add_category_item(self, parent, text):
        """添加一个分类标题项"""
        item = QTreeWidgetItem(parent, [text])
        font = QFont()
        font.setBold(True)
        item.setFont(0, font)
        return item

    def add_tool_item(self, parent, text):
        """添加一个工具项"""
        item = QTreeWidgetItem(parent, [text])
        return item

    @staticmethod
    def maya_main_window():
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    @classmethod
    def show_singleton_dialog(cls):
        if not cls._ui_instance:
            cls._ui_instance = cls()

        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# --- 程序入口 ---
if __name__ == "__main__":
    TcToolsUI().show_singleton_dialog()
