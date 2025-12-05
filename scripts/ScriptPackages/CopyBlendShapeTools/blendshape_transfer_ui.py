from Qt import QtCore, QtWidgets


# 自定义控件类用于填充TabWidget
class bs_transfer_sameTopo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.source_mesh_label = QtWidgets.QLabel("Source Mesh: ")
        self.source_mesh_line = QtWidgets.QLineEdit()
        self.source_mesh_btn = QtWidgets.QPushButton("<<")

        self.target_mesh_label = QtWidgets.QLabel("Source Mesh: ")
        self.target_mesh_line = QtWidgets.QLineEdit()
        self.target_mesh_btn = QtWidgets.QPushButton("<<")

        self.load_targets_btn = QtWidgets.QPushButton("Load Targets")
        self.target_list = QtWidgets.QListWidget()

        self.transfer_btn = QtWidgets.QPushButton("transfer Blendshapes")

    def create_layouts(self):
        source_mesh_lo = QtWidgets.QHBoxLayout()
        source_mesh_lo.addWidget(self.source_mesh_label)
        source_mesh_lo.addWidget(self.source_mesh_line)
        source_mesh_lo.addWidget(self.source_mesh_btn)

        target_mesh_lo = QtWidgets.QHBoxLayout()
        target_mesh_lo.addWidget(self.target_mesh_label)
        target_mesh_lo.addWidget(self.target_mesh_line)
        target_mesh_lo.addWidget(self.target_mesh_btn)

        main_lo = QtWidgets.QHBoxLayout(self)
        main_lo.addLayout(source_mesh_lo)
        main_lo.addLayout(target_mesh_lo)

        main_lo.addWidget(self.load_targets_btn)
        main_lo.addWidget(self.target_list)
        main_lo.addWidget(self.transfer_btn)

    def create_connections(self):
        self.source_mesh_btn.clicked.connect(self.load_source_mesh)
        self.target_mesh_btn.clicked.connect(self.load_target_mesh)
        self.load_targets_btn.clicked.connect(self.load_targets)
        self.transfer_btn.clicked.connect(self.transfer)

    # ------------------------------槽函数--------------------------------------
    def load_source_mesh(self):
        pass

    def load_target_mesh(self):
        pass

    def load_targets(self):
        pass

    def transfer(self):
        pass


# 自定义控件类用于填充TabWidget
class bs_transfer_diffTopo(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.source_mesh_label = QtWidgets.QLabel("Source Mesh: ")
        self.source_mesh_line = QtWidgets.QLineEdit()
        self.source_mesh_btn = QtWidgets.QPushButton("<<")

        self.source_mesh_trans_label = QtWidgets.QLabel("Source Trans Target: ")
        self.source_mesh_trans_line = QtWidgets.QLineEdit()
        self.source_mesh_trans_btn = QtWidgets.QPushButton("<<")

        self.target_mesh_label = QtWidgets.QLabel("Target Mesh: ")
        self.target_mesh_line = QtWidgets.QLineEdit()
        self.target_mesh_btn = QtWidgets.QPushButton("<<")

        self.target_mesh_trans_label = QtWidgets.QLabel("Target Trans Target: ")
        self.target_mesh_trans_line = QtWidgets.QLineEdit()
        self.target_mesh_trans_btn = QtWidgets.QPushButton("<<")

        self.load_targets_btn = QtWidgets.QPushButton("Load Targets")
        self.target_list = QtWidgets.QListWidget()

        self.transfer_btn = QtWidgets.QPushButton("transfer Blendshapes")

    def create_layouts(self):
        source_mesh_lo = QtWidgets.QHBoxLayout()
        source_mesh_lo.addWidget(self.source_mesh_label)
        source_mesh_lo.addWidget(self.source_mesh_line)
        source_mesh_lo.addWidget(self.source_mesh_btn)

        source_mesh_trans_lo = QtWidgets.QHBoxLayout()
        source_mesh_trans_lo.addWidget(self.source_mesh_trans_label)
        source_mesh_trans_lo.addWidget(self.source_mesh_trans_line)
        source_mesh_trans_lo.addWidget(self.source_mesh_trans_btn)

        target_mesh_lo = QtWidgets.QHBoxLayout()
        target_mesh_lo.addWidget(self.target_mesh_label)
        target_mesh_lo.addWidget(self.target_mesh_line)
        target_mesh_lo.addWidget(self.target_mesh_btn)

        target_mesh_trans_lo = QtWidgets.QHBoxLayout()
        target_mesh_trans_lo.addWidget(self.target_mesh_trans_label)
        target_mesh_trans_lo.addWidget(self.target_mesh_trans_line)
        target_mesh_trans_lo.addWidget(self.target_mesh_trans_btn)

        main_lo = QtWidgets.QHBoxLayout(self)
        main_lo.addLayout(source_mesh_lo)
        main_lo.addLayout(source_mesh_trans_lo)
        main_lo.addLayout(target_mesh_lo)
        main_lo.addLayout(target_mesh_trans_lo)

        main_lo.addWidget(self.load_targets_btn)
        main_lo.addWidget(self.target_list)
        main_lo.addWidget(self.transfer_btn)

    def create_connections(self):
        self.source_mesh_btn.clicked.connect(self.load_source_mesh)
        self.source_mesh_trans_btn.clicked.connect(self.load_source_mesh_trans)
        self.target_mesh_btn.clicked.connect(self.load_target_mesh)
        self.target_mesh_trans_btn.clicked.connect(self.load_target_mesh_trans)
        self.load_targets_btn.clicked.connect(self.load_targets)
        self.transfer_btn.clicked.connect(self.transfer)

    # ------------------------------槽函数--------------------------------------
    def load_source_mesh(self):
        pass

    def load_source_mesh_trans(self):
        pass

    def load_target_mesh(self):
        pass

    def load_target_mesh_trans(self):
        pass

    def load_targets(self):
        pass

    def transfer(self):
        pass


class bs_transfer(QtWidgets.QDialog):
    """工具UI类"""

    # 用于保存窗口实例，实现窗口单例化
    _ui_instance = None

    def __init__(self, parent=None):
        """构造函数"""
        # 如果没有传入父窗口，则maya主窗口为父窗口
        if parent is None:
            parent = bs_transfer.maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("Common Widgets")
        self.setMinimumSize(400, 200)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        """创建控件"""
        # 创建自定义控件实例
        self.custom_widget_01 = bs_transfer_sameTopo()
        self.custom_widget_02 = bs_transfer_diffTopo()
        # 创建TabWidget，并将QWidget添加到Tab
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.custom_widget_01, "Tab 01")
        self.tab_widget.addTab(self.custom_widget_02, "Tab 02")
        self.tab_widget.addTab(QtWidgets.QPushButton("My Button"), "Tab 03")
        # OK and Cancel Button
        self.ok_btn = QtWidgets.QPushButton("OK")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

    def create_layouts(self):
        """创建布局"""

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)  # 添加 tab_widget
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        """创建连接"""
        self.tab_widget.currentChanged.connect(self.on_current_index_changed)

    # 槽函数
    @QtCore.Slot(int)
    def on_current_index_changed(self, index):
        """当TabWidget控件切换Tab时调用,信号传入参数为Tab的索引"""
        print(f"Current Index: {index}")  # 打印当前选项卡索引

    def keyPressEvent(self, event):
        """重写keyPressEvent函数，在使用该工具时避免误操作maya
        比如按下键盘“s”键导致剋帧
        """
        pass

    @staticmethod
    def maya_main_window():
        """获取maya主界面的pyside实例"""
        app = QtWidgets.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    # 创建单例窗口
    @classmethod
    def show_singleton_dialog(cls):
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


if __name__ == "__main__":
    bs_transfer.show_singleton_dialog()
