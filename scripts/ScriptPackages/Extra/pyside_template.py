from Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui


class TemplateDialog(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "Template"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(TemplateDialog.WINDOW_TITLE)
        self.setMinimumSize(300, 120)
        # 窗口在关闭时自动彻底销毁对象
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        pass

    def create_layout(self):
        pass

    def create_connections(self):
        pass

    @QtCore.Slot()
    def template_slot(self):
        pass

    def closeEvent(self, event):
        """关闭窗口时清空实例"""
        TemplateDialog._ui_instance = None
        super().closeEvent(event)

    @staticmethod
    def get_maya_main_window():
        """返回 Maya 主窗口的 PySide 实例"""
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrapInstance(int(ptr), QtWidgets.QMainWindow)
        return None

    @classmethod
    def show_ui(cls):
        """单例显示 UI"""
        # 如果没有单例或者实例不显示，则创建并显示实例
        if cls._ui_instance is None or not cls._ui_instance.isVisible():
            cls._ui_instance = TemplateDialog()
            cls._ui_instance.show()
        # 其他情况实例抬起并激活
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# 执行代码
def run():
    TemplateDialog.show_ui()
