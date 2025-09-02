from pathlib import Path
import importlib
import traceback
from Qt.QtWidgets import (
    QApplication,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QToolBox,
    QListWidget,
    QListWidgetItem,
    QFrame,
    QMenuBar,
)

from Qt.QtCore import Qt, QSize
from Qt.QtGui import QColor


# --- 主窗口类 ---
class TcToolsUI(QDialog):
    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = TcToolsUI.maya_main_window()
        super().__init__(parent)
        self.setWindowTitle("Tc Tools V1.0")
        self.setGeometry(300, 300, 350, 600)
        self.init_ui()

    def init_ui(self):
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 菜单栏和搜索栏

        self.menu_bar = QMenuBar()
        edit_menu = self.menu_bar.addMenu("Edit")
        help_menu = self.menu_bar.addMenu("Help")
        main_layout.addWidget(self.menu_bar)
        # 搜索栏
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(10, 5, 10, 5)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索...")
        self.search_bar.textChanged.connect(self.filter_tools)
        search_layout.addWidget(self.search_bar)
        main_layout.addLayout(search_layout)
        # 分割线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("background-color: #444;")
        main_layout.addWidget(line)

        # 功能区域 (使用 QToolBox)
        self.tool_box = QToolBox()
        self.tool_box.setContentsMargins(5, 10, 5, 10)

        self.populate_tool_box()
        main_layout.addWidget(self.tool_box)

        self.setLayout(main_layout)

    def populate_tool_box(self):
        """填充 QToolBox 的内容"""
        # 确定菜单分类
        category_list = ["modeling", "Rigging", "Animation", "TD"]
        # 获取当前脚本所在路径：scripts/
        current_file_path = Path(__file__).parent
        # 根据分类和类别下的脚本
        for category in category_list:
            item_list = []
            # 拼接路径：scripts/Rigging
            item_path = Path(current_file_path, category)
            # 获取路径下所有py文件
            item_list = [
                str(f.stem) for f in Path(item_path).glob("*.py") if Path(f).is_file()
            ]
            # 创建工具列表控件
            list_widget = self._create_tool_list_widget(category, item_list)
            # tool_box添加项目
            self.tool_box.addItem(list_widget, category)

    def _create_tool_list_widget(self, category, item_list):
        """一个辅助函数，用于创建并填充一个 QListWidget"""
        # 创建列表控件
        list_widget = QListWidget()
        list_widget.setSpacing(2)
        list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        list_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # 遍历分类下的脚本列表，创建列表控件项目
        for item in item_list:
            item = QListWidgetItem(item)
            item.setSizeHint(QSize(100, 25))
            item.setBackgroundColor(QColor(96, 96, 96))
            # 设置列表控件项目数据
            item.setData(Qt.UserRole, [category, item])
            list_widget.addItem(item)
        return list_widget

    def filter_tools(self, text):
        """实现搜索框功能"""
        search_text = text.lower().strip()
        # 遍历工具盒项
        for index in range(self.tool_box.count()):
            list_widget = self.tool_box.widget(index)
            if not isinstance(list_widget, QListWidget):
                continue
            # 遍历工具盒列表项
            for row in range(list_widget.count()):
                item = list_widget.item(row)
                item_text = item.text().lower()
                # 如果搜索关键测存在 且不包含在列表项名称内，隐藏项
                if search_text and search_text not in item_text:
                    item.setHidden(True)
                # 否则显示
                else:
                    item.setHidden(False)

    def on_item_double_clicked(self, item):
        category_name, list_item = item.data(Qt.UserRole)
        try:
            # 动态导入，执行脚本
            module_name = f"{category_name}.{list_item.text()}"
            module = importlib.import_module(module_name)
            importlib.reload(module)

        except Exception as e:
            print(f"Error running {item.text()}.py: {e}")
            traceback.print_exc()

    @staticmethod
    def maya_main_window():
        """获取maya主界面的pyside实例"""
        app = QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    # 创建单例窗口
    @classmethod
    def show_ui(cls):
        """显示单例窗口"""
        # 如果窗口单例为空，则创建窗口单例
        if not cls._ui_instance:
            cls._ui_instance = cls()
        # 如果窗口单例被隐藏，则显示
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        # 其他情况，抬升窗口并激活
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# --- 程序入口 ---
if __name__ == "__main__":
    TcToolsUI.show_ui()
