from Qt import QtCore, QtWidgets


class TemplateDialog(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "Template Window"
    OBJECT_NAME = "myTemplateDialog"  # 建议给对象命名，方便在 Maya 中追踪

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)
        self.setObjectName(self.OBJECT_NAME)
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
        # 通常 Maya 启动后，其主窗口就是 topLevelWidgets 中的 QMainWindow
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == "MayaWindow":
                return widget
        return None

    @classmethod
    def show_ui(cls):
        """单例显示 UI"""
        # 如果旧窗口已存在，先关闭它
        if cls._ui_instance is not None:
            cls._ui_instance.close()
            cls._ui_instance.deleteLater()

        cls._ui_instance = TemplateDialog()
        cls._ui_instance.show()
        return cls._ui_instance


# 执行代码
def run():
    return TemplateDialog.show_ui()
