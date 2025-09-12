from PySide2 import QtCore, QtWidgets, QtGui


class CollapsibleHeader(QtWidgets.QWidget):
    """可折叠标题"""

    # Icon常量
    COLLAPSED_PIXMAP = QtGui.QPixmap(":teRightArrow.png")
    EXPANDED_PIXMAP = QtGui.QPixmap(":teDownArrow.png")
    # 鼠标点击标题信号
    clicked = QtCore.Signal()

    def __init__(self, text, parent=None):
        super().__init__(parent)
        # 设置控件背景颜色
        self.setAutoFillBackground(True)
        self.set_background_color()
        # 设置图标标签
        self.icon_label = QtWidgets.QLabel()
        self.icon_label.setFixedWidth(CollapsibleHeader.COLLAPSED_PIXMAP.width())
        # 设置文本标签
        self.text_label = QtWidgets.QLabel()
        # 文本标签会捕获鼠标事件，使父对象QWidget接收不到鼠标点击事件
        # 使文本标签对鼠标事件透明，点击事件会“穿透”它，作用于它的父对象（QWidget）上。WA: 代表 Window Attribute
        # 这意味着 self.text_label 将对所有鼠标事件（如点击、悬停、拖动等）透明，鼠标事件会直接传递给它下方的控件，而不会被 QLabel 本身捕获或处理。
        self.text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
        # 主布局
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(4, 4, 4, 4)
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.text_label)
        # 设置文本和折叠控件
        self.set_text(text)
        self.set_expanded(False)

    def set_text(self, text):
        """设置标签文本"""
        self.text_label.setText(f"<b>{text}</b>")  # 粗体显示

    def set_background_color(self, color=None):
        """设置背景颜色"""
        # 默认为按钮颜色
        if not color:
            color = (
                QtWidgets.QPushButton().palette().color(QtGui.QPalette.ColorRole.Button)
            )
        print(color)
        palette = self.palette()  # 获取当前控件调色板
        palette.setColor(QtGui.QPalette.ColorRole.Window, color)
        self.setPalette(palette)

    def is_expanded(self):
        """是否已展开"""
        return self._is_expanded

    def set_expanded(self, expanded):
        """设置折叠icon"""
        self._is_expanded = expanded
        if self._is_expanded:
            self.icon_label.setPixmap(self.EXPANDED_PIXMAP)
        else:
            self.icon_label.setPixmap(self.COLLAPSED_PIXMAP)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        """鼠标点击释放后发射信号"""
        self.clicked.emit()


class CollapsibleWidget(QtWidgets.QWidget):
    """可折叠控件"""

    def __init__(self, text, parent=None):
        super().__init__(parent)
        # 可折叠标题
        self.header_wdg = CollapsibleHeader(text)
        self.header_wdg.clicked.connect(self.on_header_clicked)
        # 可折叠主体
        self.body_wdg = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(3)
        # 主布局
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.header_wdg)
        self.main_layout.addWidget(self.body_wdg)

        self.set_expanded(False)  # 全部折叠

    def add_widget(self, widget):
        """折叠主体添加控件"""
        self.body_layout.addWidget(widget)

    def add_layout(self, layout):
        """折叠主体添加布局"""
        self.body_layout.addLayout(layout)

    def set_expanded(self, expanded):
        """设置控件折叠展开"""
        self.header_wdg.set_expanded(expanded)  # 设置可折叠标题Icon
        self.body_wdg.setVisible(expanded)  # 设置当前控件可见性

    def set_header_background_color(self, color):
        """设置折叠标题背景色"""
        self.header_wdg.set_background_color(color)

    @QtCore.Slot()
    def on_header_clicked(self):
        """折叠标题被点击槽函数"""
        # 每次取反，达到切换效果
        self.set_expanded(not self.header_wdg.is_expanded())


class MainWidget(QtWidgets.QDialog):
    """主控件"""

    _ui_instance = None
    WINDOW_TITLE = "Main Dialog"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(MainWidget.WINDOW_TITLE)
        self.setMinimumSize(300, 120)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        """创建控件"""
        # 可折叠控件1：6个按钮
        self.collapsible_wdg_1 = CollapsibleWidget("Section A")
        for i in range(6):
            self.collapsible_wdg_1.add_widget(QtWidgets.QPushButton(f"Button{i}"))
        # # 可折叠控件2：6个复选框
        self.collapsible_wdg_2 = CollapsibleWidget("Section B")
        layout = QtWidgets.QFormLayout()
        for i in range(6):
            layout.addRow(f"Row{i}", QtWidgets.QCheckBox())
        self.collapsible_wdg_2.add_layout(layout)

    def create_layout(self):
        """创建布局"""
        # 创建主体控件和主体布局
        self.body_wdg = QtWidgets.QWidget()
        self.body_layout = QtWidgets.QVBoxLayout(self.body_wdg)
        self.body_layout.setContentsMargins(4, 2, 4, 2)
        self.body_layout.setSpacing(3)
        self.body_layout.setAlignment(QtCore.Qt.AlignTop)

        self.body_layout.addWidget(self.collapsible_wdg_1)
        self.body_layout.addWidget(self.collapsible_wdg_2)
        # 创建滚动区
        self.body_scroll_area = QtWidgets.QScrollArea()
        # 去除滚动区域淡蓝色边框
        self.body_scroll_area.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.body_scroll_area.setWidgetResizable(True)
        self.body_scroll_area.setWidget(self.body_wdg)
        # 创建主布局：main_layout->body_scroll_area->body_wdg->body_layout->collapsible_wdgs
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.body_scroll_area)

    def create_connections(self):
        pass

    @QtCore.Slot()
    def template_slot(self):
        pass

    @staticmethod
    def get_maya_main_window():
        """通过 QApplication 获取 Maya 主窗口的 PySide 实例"""
        # 用于获取当前运行的 maya QApplication 实例
        app = QtWidgets.QApplication.instance()
        # 如果当前没有运行的实例，返回None
        if not app:
            return None
        # app.topLevelWidgets() 返回当前 QApplication 管理的所有顶层窗口（没有父窗口）列表
        for widget in app.topLevelWidgets():
            # 如果窗口的 Qt 对象名称为"MayaWindow"，返回这个窗口实例
            if widget.objectName() == "MayaWindow":
                return widget
        return None

    @classmethod
    def show_ui(cls):
        """单例模式显示UI"""
        if cls._ui_instance is None:
            cls._ui_instance = MainWidget()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


if __name__ == "__main__":
    MainWidget.show_ui()
