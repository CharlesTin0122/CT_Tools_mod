from Qt import QtWidgets
from CopyBlendShapeTools.blendshape_transfer_logic import (
    find_blendshape_info,
    transfer_blendshape_targets_sameTopo,
    transfer_blendshape_targets_diffTopo,
    copy_blendshapes,
)
import pymel.core as pm


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

        self.target_mesh_label = QtWidgets.QLabel("Target Mesh: ")
        self.target_mesh_line = QtWidgets.QLineEdit()
        self.target_mesh_btn = QtWidgets.QPushButton("<<")

        self.load_targets_btn = QtWidgets.QPushButton("Load Targets")
        self.target_list_wgt = QtWidgets.QListWidget()

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

        main_lo = QtWidgets.QVBoxLayout(self)
        main_lo.addLayout(source_mesh_lo)
        main_lo.addLayout(target_mesh_lo)

        main_lo.addWidget(self.load_targets_btn)
        main_lo.addWidget(self.target_list_wgt)
        main_lo.addWidget(self.transfer_btn)

    def create_connections(self):
        self.source_mesh_btn.clicked.connect(self.load_source_mesh)
        self.target_mesh_btn.clicked.connect(self.load_target_mesh)
        self.load_targets_btn.clicked.connect(self.load_targets)
        self.transfer_btn.clicked.connect(self.transfer)

    # ------------------------------槽函数--------------------------------------
    def load_source_mesh(self):
        self.source_mesh = pm.selected()[0]
        if self.source_mesh:
            sel_name = self.source_mesh.name()
            self.source_mesh_line.setText(sel_name)

    def load_target_mesh(self):
        self.target_mesh = pm.selected()[0]
        if self.target_mesh:
            sel_name = self.target_mesh.name()
            self.target_mesh_line.setText(sel_name)

    def load_targets(self):
        self.target_list = pm.selected()
        for obj in self.target_list:
            obj_name = obj.name()
            self.target_list_wgt.addItem(obj_name)

    def transfer(self):
        transfer_blendshape_targets_sameTopo(
            self.source_mesh, self.target_mesh, self.target_list
        )


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
        self.target_list_wgt = QtWidgets.QListWidget()

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

        main_lo = QtWidgets.QVBoxLayout(self)
        main_lo.addLayout(source_mesh_lo)
        main_lo.addLayout(source_mesh_trans_lo)
        main_lo.addLayout(target_mesh_lo)
        main_lo.addLayout(target_mesh_trans_lo)

        main_lo.addWidget(self.load_targets_btn)
        main_lo.addWidget(self.target_list_wgt)
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
        self.source_mesh = pm.selected()[0]
        if self.source_mesh:
            sel_name = self.source_mesh.name()
            self.source_mesh_line.setText(sel_name)

    def load_source_mesh_trans(self):
        self.source_mesh_trans = pm.selected()[0]
        if self.source_mesh_trans:
            sel_name = self.source_mesh_trans.name()
            self.source_mesh_trans_line.setText(sel_name)

    def load_target_mesh(self):
        self.target_mesh = pm.selected()[0]
        if self.target_mesh:
            sel_name = self.target_mesh.name()
            self.target_mesh_line.setText(sel_name)

    def load_target_mesh_trans(self):
        self.target_mesh_trans = pm.selected()[0]
        if self.target_mesh_trans:
            sel_name = self.target_mesh_trans.name()
            self.target_mesh_trans_line.setText(sel_name)

    def load_targets(self):
        self.target_list = pm.selected()
        for obj in self.target_list:
            obj_name = obj.name()
            self.target_list_wgt.addItem(obj_name)

    def transfer(self):
        transfer_blendshape_targets_diffTopo(
            self.source_mesh,
            self.source_mesh_trans,
            self.target_mesh,
            self.target_mesh_trans,
            self.target_list,
        )


class force_wrap(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.source_mesh_label = QtWidgets.QLabel("Source Mesh: ")
        self.source_mesh_line = QtWidgets.QLineEdit()
        self.source_mesh_btn = QtWidgets.QPushButton("<<")

        self.blendshapse_label = QtWidgets.QLabel("Blendshapes: ")
        self.blendshapse_list_wgt = QtWidgets.QListWidget()
        self.blendshapse_list_wgt.setSelectionMode(QtWidgets.QListWidget.MultiSelection)

        self.load_targets_btn = QtWidgets.QPushButton("Load Targets")
        self.target_list_wgt = QtWidgets.QListWidget()

        self.transfer_btn = QtWidgets.QPushButton("Copy Blendshapes")

    def create_layouts(self):
        source_mesh_lo = QtWidgets.QHBoxLayout()
        source_mesh_lo.addWidget(self.source_mesh_label)
        source_mesh_lo.addWidget(self.source_mesh_line)
        source_mesh_lo.addWidget(self.source_mesh_btn)

        main_lo = QtWidgets.QVBoxLayout(self)
        main_lo.addLayout(source_mesh_lo)

        main_lo.addWidget(self.blendshapse_label)
        main_lo.addWidget(self.blendshapse_list_wgt)
        main_lo.addWidget(self.load_targets_btn)
        main_lo.addWidget(self.target_list_wgt)
        main_lo.addWidget(self.transfer_btn)

    def create_connections(self):
        self.source_mesh_btn.clicked.connect(self.load_source_mesh)
        self.load_targets_btn.clicked.connect(self.load_targets)
        self.transfer_btn.clicked.connect(self.transfer)

    # ------------------------------槽函数--------------------------------------
    def load_source_mesh(self):
        self.source_mesh = pm.selected()[0]
        if self.source_mesh:
            sel_name = self.source_mesh.name()
            self.source_mesh_line.setText(sel_name)

            bs_info_list = find_blendshape_info(self.source_mesh)

            bs_name_list = []
            for bs_info in bs_info_list:
                bs_name = bs_info[0]
                bs_name_list.append(bs_name)

            self.blendshapse_list_wgt.clear()
            self.blendshapse_list_wgt.addItems(bs_name_list)

    def load_targets(self):
        self.target_list_wgt.clear()
        self.target_list = pm.selected()
        self.target_list_wgt.addItems([obj.name() for obj in self.target_list])

    def transfer(self):
        self.selected_blendshapes = [
            item.text() for item in self.blendshapse_list_wgt.selectedItems()
        ]
        copy_blendshapes(self.source_mesh, self.target_list, self.selected_blendshapes)


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

    def create_widgets(self):
        """创建控件"""
        # 创建自定义控件实例
        self.custom_widget_01 = bs_transfer_sameTopo()
        self.custom_widget_02 = bs_transfer_diffTopo()
        self.custom_widget_03 = force_wrap()
        # 创建TabWidget，并将QWidget添加到Tab
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.custom_widget_01, "Same Topo")
        self.tab_widget.addTab(self.custom_widget_02, "Diff Topo")
        self.tab_widget.addTab(self.custom_widget_03, "Froce Wrap")

    def create_layouts(self):
        """创建布局"""

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)  # 添加 tab_widget

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
