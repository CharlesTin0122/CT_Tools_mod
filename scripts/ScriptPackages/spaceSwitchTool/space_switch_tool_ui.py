from Qt import QtCore, QtWidgets
import pymel.core as pm
from spaceSwitchTool.space_switch_tool_matrix import (
    addSpaceSwitching,
    seamless_space_switch,
    bake_space,
)


class space_item(QtWidgets.QWidget):
    def __init__(self, node_name, parent=None):
        super().__init__(parent)
        self.node_name = node_name
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.driver_node_label = QtWidgets.QLabel("Driver Node:")

        self.driver_node_line = QtWidgets.QLineEdit()
        self.driver_node_line.setMinimumWidth(60)
        self.driver_node_line.setText(self.node_name)

        self.driver_node_btn = QtWidgets.QPushButton("<<")
        self.driver_node_btn.setFixedWidth(60)

        self.display_name_label = QtWidgets.QLabel("Display Name:")

        self.display_name_line = QtWidgets.QLineEdit()
        self.display_name_line.setMinimumWidth(60)
        self.display_name_line.setText(self.node_name)

        self.remove_widget_btn = QtWidgets.QPushButton("Remove")
        self.remove_widget_btn.setFixedWidth(60)

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addWidget(self.driver_node_label)
        main_layout.addWidget(self.driver_node_line)
        main_layout.addWidget(self.driver_node_btn)
        main_layout.addWidget(self.display_name_label)
        main_layout.addWidget(self.display_name_line)
        main_layout.addWidget(self.remove_widget_btn)

    def create_connections(self):
        self.driver_node_btn.clicked.connect(self.on_driver_node_btn_clicked)
        self.remove_widget_btn.clicked.connect(self.on_remove_widget_btn_clicked)

    @QtCore.Slot()
    def on_driver_node_btn_clicked(self):
        selected_obj = pm.selected()[0]
        if not selected_obj:
            pm.warning("Please select node")
        node_name = selected_obj.name()
        self.driver_node_line.setText(node_name)

    @QtCore.Slot()
    def on_remove_widget_btn_clicked(self):
        self.deleteLater()


class CreateSpaces(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.target_node_lable = QtWidgets.QLabel("Target Node:")
        self.target_node_line = QtWidgets.QLineEdit()
        self.target_node_line.setMinimumWidth(120)
        self.target_node_btn = QtWidgets.QPushButton("<<")
        self.target_node_btn.setFixedWidth(20)

        self.attribute_lable = QtWidgets.QLabel("Switch Attribute:")
        self.attribute_line = QtWidgets.QLineEdit()
        self.attribute_line.setMinimumWidth(120)

        self.clear_info_btn = QtWidgets.QPushButton("Clear Info")

        self.add_space_btn = QtWidgets.QPushButton("Add Spases")
        self.add_space_btn.setStyleSheet("background-color: darkgray;")

        self.spaces_area = QtWidgets.QScrollArea()
        self.spaces_area.setWidgetResizable(True)
        self.content_widget = QtWidgets.QWidget()
        self.spaces_area.setWidget(self.content_widget)
        self.content_layout = QtWidgets.QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(QtCore.Qt.AlignTop)

        self.clear_spaces_btn = QtWidgets.QPushButton("Clear Spaces")

        self.generate_spaces_btn = QtWidgets.QPushButton("Generate Spaces")
        self.generate_spaces_btn.setStyleSheet("background-color: darkgray;")

    def create_layout(self):
        target_node_layout = QtWidgets.QHBoxLayout()
        target_node_layout.setSpacing(5)
        target_node_layout.setStretch(1, 1)
        target_node_layout.addWidget(self.target_node_lable)
        target_node_layout.addWidget(self.target_node_line)
        target_node_layout.addWidget(self.target_node_btn)

        attribute_layout = QtWidgets.QHBoxLayout()
        attribute_layout.setSpacing(5)
        attribute_layout.addWidget(self.attribute_lable)
        attribute_layout.addWidget(self.attribute_line)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addLayout(target_node_layout)
        info_layout.addLayout(attribute_layout)
        info_layout.addWidget(self.clear_info_btn)
        info_group = QtWidgets.QGroupBox("Info")
        info_group.setLayout(info_layout)

        spaces_layout = QtWidgets.QVBoxLayout()
        spaces_layout.addWidget(self.add_space_btn)
        spaces_layout.addWidget(self.spaces_area)
        spaces_layout.addWidget(self.clear_spaces_btn)

        spaces_group = QtWidgets.QGroupBox("Spaces")
        spaces_group.setLayout(spaces_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(info_group)
        main_layout.addWidget(spaces_group)
        main_layout.addWidget(self.generate_spaces_btn)

    def create_connections(self):
        self.target_node_btn.clicked.connect(self.on_target_node_btn_clicked)
        self.clear_info_btn.clicked.connect(self.on_clear_info_btn_clicked)
        self.clear_spaces_btn.clicked.connect(self.on_clear_spaces_btn_clicked)
        self.add_space_btn.clicked.connect(self.on_add_space_btn_clicked)
        self.generate_spaces_btn.clicked.connect(self.on_generate_spaces_btn_clicked)

    @QtCore.Slot()
    def on_target_node_btn_clicked(self):
        selected_obj = pm.selected()[0]
        if not selected_obj:
            pm.warning("Please select node")
        node_name = selected_obj.name()
        self.target_node_line.setText(node_name)

    @QtCore.Slot()
    def on_clear_info_btn_clicked(self):
        self.target_node_line.clear()
        self.attribute_line.clear()

    @QtCore.Slot()
    def on_clear_spaces_btn_clicked(self):
        if not self.item_list:
            pass
        for item in self.item_list:
            item.deleteLater()

    @QtCore.Slot()
    def on_add_space_btn_clicked(self):
        selected_obj = pm.selected()
        if not selected_obj:
            pm.warning("Please select node")
        self.item_list = []
        for obj in selected_obj:
            obj_name = obj.name()
            space_item_widget = space_item(node_name=obj_name)
            self.content_layout.addWidget(space_item_widget)
            self.item_list.append(space_item_widget)

    @QtCore.Slot()
    def on_generate_spaces_btn_clicked(self):
        target_node = pm.PyNode(self.target_node_line.text())
        switch_attributre = self.attribute_line.text()
        driver_list = [
            pm.PyNode(item.driver_node_line.text()) for item in self.item_list
        ]
        enum_item_list = [item.display_name_line.text() for item in self.item_list]
        addSpaceSwitching(
            target_node,
            switch_attributre,
            driver_list,
            enum_item_list,
        )


# 自定义控件类用于填充TabWidget
class SwitchSpases(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.target_node_lable = QtWidgets.QLabel("Target Node:")
        self.target_node_line = QtWidgets.QLineEdit()
        self.target_node_line.setMinimumWidth(120)
        self.target_node_btn = QtWidgets.QPushButton("<<")
        self.target_node_btn.setFixedWidth(20)

        self.attribute_lable = QtWidgets.QLabel("Switch Attribute:")
        self.attribute_line = QtWidgets.QLineEdit()
        self.attribute_line.setMinimumWidth(120)

        self.clear_info_btn = QtWidgets.QPushButton("Clear Info")

        self.load_spaces_btn = QtWidgets.QPushButton("Load Spaces")
        self.spaces_list = QtWidgets.QListWidget()
        self.spaces_list.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        self.switch_space_btn = QtWidgets.QPushButton("Switch_Space")
        self.switch_space_btn.setStyleSheet("background-color: darkgray;")
        self.start_frame_label = QtWidgets.QLabel("Start Frame:")
        self.start_frame_spin = QtWidgets.QSpinBox()
        self.start_frame_spin.setFixedWidth(60)
        self.start_frame_spin.setMinimum(-10000)
        self.start_frame_spin.setMaximum(10000)
        self.start_frame_spin.setSingleStep(1)
        self.end_frame_label = QtWidgets.QLabel("End Frame:")
        self.end_frame_spin = QtWidgets.QSpinBox()
        self.end_frame_spin.setFixedWidth(60)
        self.end_frame_spin.setMinimum(-10000)
        self.end_frame_spin.setMaximum(10000)
        self.end_frame_spin.setSingleStep(1)
        self.bake_space_btn = QtWidgets.QPushButton("Bake_Space")
        self.bake_space_btn.setStyleSheet("background-color: darkgray;")

    def create_layout(self):
        target_node_layout = QtWidgets.QHBoxLayout()
        target_node_layout.setSpacing(5)
        target_node_layout.setStretch(1, 1)
        target_node_layout.addWidget(self.target_node_lable)
        target_node_layout.addWidget(self.target_node_line)
        target_node_layout.addWidget(self.target_node_btn)

        attribute_layout = QtWidgets.QHBoxLayout()
        attribute_layout.setSpacing(5)
        attribute_layout.addWidget(self.attribute_lable)
        attribute_layout.addWidget(self.attribute_line)

        info_layout = QtWidgets.QVBoxLayout()
        info_layout.addLayout(target_node_layout)
        info_layout.addLayout(attribute_layout)
        info_layout.addWidget(self.clear_info_btn)
        info_group = QtWidgets.QGroupBox("Info")
        info_group.setLayout(info_layout)

        spaces_layout = QtWidgets.QVBoxLayout()
        spaces_layout.addWidget(self.load_spaces_btn)
        spaces_layout.addWidget(self.spaces_list)
        spaces_layout.addWidget(self.switch_space_btn)
        spaces_group = QtWidgets.QGroupBox("Spaces")
        spaces_group.setLayout(spaces_layout)

        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.addWidget(self.start_frame_label)
        frame_layout.addWidget(self.start_frame_spin)
        frame_layout.addWidget(self.end_frame_label)
        frame_layout.addWidget(self.end_frame_spin)
        bake_layout = QtWidgets.QVBoxLayout()
        bake_layout.addLayout(frame_layout)
        bake_layout.addWidget(self.bake_space_btn)
        bake_grp = QtWidgets.QGroupBox("Bake")
        bake_grp.setLayout(bake_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(info_group)
        main_layout.addWidget(spaces_group)
        main_layout.addWidget(bake_grp)

    def create_connections(self):
        self.target_node_btn.clicked.connect(self.on_target_node_btn_clicked)
        self.clear_info_btn.clicked.connect(self.on_clear_info_btn_clicked)
        self.load_spaces_btn.clicked.connect(self.on_load_spaces_btn_clicked)
        self.switch_space_btn.clicked.connect(self.on_switch_space_btn_clicked)
        self.bake_space_btn.clicked.connect(self.on_bake_space_btn_clicked)

    @QtCore.Slot()
    def on_target_node_btn_clicked(self):
        selected_obj = pm.selected()[0]
        if not selected_obj:
            pm.warning("Please select node")
        node_name = selected_obj.name()
        self.target_node_line.setText(node_name)

    @QtCore.Slot()
    def on_clear_info_btn_clicked(self):
        self.target_node_line.clear()
        self.attribute_line.clear()
        self.spaces_list.clear()

    @QtCore.Slot()
    def on_load_spaces_btn_clicked(self):
        obj = pm.PyNode(self.target_node_line.text())
        if not obj:
            pm.warning("Please input target node")
        attr = obj.attr(self.attribute_line.text())
        if not attr:
            pm.warning("Please input right attribute")
        enum_items = attr.getEnums()
        # {'global': 0, 'body': 1, 'spine': 2, 'head': 3, 'clavicle': 4}
        for key, value in enum_items.items():
            self.spaces_list.addItem(key)

    @QtCore.Slot()
    def on_switch_space_btn_clicked(self):
        target_node = pm.PyNode(self.target_node_line.text())
        switch_attribute = self.attribute_line.text()
        new_space_index = self.spaces_list.selectedIndexes()[0].row()
        try:
            seamless_space_switch(target_node, switch_attribute, new_space_index)
        except Exception as e:
            pm.warning(e)

    @QtCore.Slot()
    def on_bake_space_btn_clicked(self):
        target_node = pm.PyNode(self.target_node_line.text())
        switch_attribute = self.attribute_line.text()
        new_space_index = self.spaces_list.selectedIndexes()[0].row()
        start_frame = self.start_frame_spin.value()
        end_frame = self.end_frame_spin.value()

        bake_space(
            target_node, switch_attribute, new_space_index, start_frame, end_frame
        )


class SpaceSwitchingTool(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "SpaceSwitchingTool"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(SpaceSwitchingTool.WINDOW_TITLE)
        self.setMinimumSize(600, 600)

        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.create_spaces_widget = CreateSpaces()
        self.switch_spases_widget = SwitchSpases()

        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(self.create_spaces_widget, "CreateSpaces")
        self.tab_widget.addTab(self.switch_spases_widget, "SwitchSpases")

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.tab_widget)

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
            cls._ui_instance = SpaceSwitchingTool()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


if __name__ == "__main__":
    SpaceSwitchingTool.show_ui()
