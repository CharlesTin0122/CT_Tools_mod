from PySide2 import QtCore, QtWidgets
from PySide2 import QtUiTools
from Qt import QtCompat


class DesignerUI(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "Template"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(DesignerUI.WINDOW_TITLE)

        self.init_ui()
        self.create_layout()
        self.create_connections()

    def init_ui(self):
        # Qt.py 库的用法
        # self.ui = QtCompat.loadUi(
        #     r"D:\CT_Tools_mod\scripts\ScriptPackages\Extra\quick_start.ui",
        #     baseinstance=self,
        # )

        # PySide2的用法
        f = QtCore.QFile(r"D:\CT_Tools_mod\scripts\ScriptPackages\Extra\quick_start.ui")
        f.open(QtCore.QFile.ReadOnly)

        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(f, parentWidget=self)

        f.close()

    def create_layout(self):
        self.ui.layout().setContentsMargins(6, 6, 6, 6)

    def create_connections(self):
        btn_ok = self.ui.findChild(QtWidgets.QPushButton, "btn_ok")
        btn_ok.clicked.connect(self.on_btn_ok_clicked)

        self.ui.btn_cancel.clicked.connect(self.close)

    @QtCore.Slot()
    def template_slot(self):
        pass

    @QtCore.Slot()
    def on_btn_ok_clicked(self):
        print("clicked OK")

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
            cls._ui_instance = DesignerUI()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


if __name__ == "__main__":
    DesignerUI.show_ui()
