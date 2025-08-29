from pathlib import Path
from Qt import QtCore, QtWidgets
import pymel.core as pm


class AssetsViewDialog(QtWidgets.QDialog):
    WINDOW_TITLE = "Assets view dialog"
    _ui_instance = None

    def __init__(self, parent=None):
        """构造函数"""
        if not parent:
            parent = AssetsViewDialog.get_maya_main_win()
        super().__init__(parent)

        self.setWindowTitle(AssetsViewDialog.WINDOW_TITLE)
        self.setMinimumSize(800, 500)

        self.root_path = pm.internalVar(userAppDir=True)

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # 设置上下文菜单
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        self.open_action = QtWidgets.QAction("Open", self)
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)

    def create_widgets(self):
        # 获取跟路径：当前场景所在的路径，
        self.root_path = AssetsViewDialog.get_root_path()
        # 如果获取失败（当前为空场景），则使用 userAppDir：Documents/maya/
        if not self.root_path:
            self.root_path = pm.internalVar(userAppDir=True)
        # 设置树视图模型，用于表示文件系统的层次结构（如目录和文件）
        self.model = QtWidgets.QFileSystemModel()  # 创建模型
        self.model.setRootPath(self.root_path)  # 设置模型根路径
        self.model.setNameFilters(["*.ma", "*.mb", "*.fbx"])  # 过滤
        self.model.setNameFilterDisables(False)  # 隐藏过滤文件
        # 设置树视图控件
        self.tree_view = QtWidgets.QTreeView()  # 创建树视图控件
        self.tree_view.setModel(self.model)  # 设置模型
        self.tree_view.setRootIndex(self.model.index(self.root_path))  # 设置根索引
        # self.tree_view.hideColumn(1)  # 隐藏size列
        self.tree_view.setColumnWidth(0, 250)  # 设置name列宽度为250

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.go_up_btn = QtWidgets.QPushButton("Go Up")

    def create_layout(self):
        btn_layou = QtWidgets.QHBoxLayout()
        btn_layou.addWidget(self.refresh_btn)
        btn_layou.addWidget(self.go_up_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.tree_view)
        main_layout.addLayout(btn_layou)

    def create_connections(self):
        # 视图没对象双击信号连接槽函数，传递树视图对象索引
        self.tree_view.doubleClicked.connect(self.on_double_clicked)
        self.refresh_btn.clicked.connect(self.on_refresh_btn_clicked)
        self.go_up_btn.clicked.connect(self.on_go_up_btn_clicked)
        self.open_action.triggered.connect(self.open_file)
        self.import_action.triggered.connect(self.import_file)
        self.reference_action.triggered.connect(self.reference_file)

    @QtCore.Slot()
    def on_double_clicked(self, index):
        """双击槽函数"""
        path = self.model.filePath(index)  # 获取双击的树视图对象路径
        # 如果对象是文件夹路径
        if self.model.isDir(index):
            print(f"Directory selected: {path}")
        # 如果对象是文件路径
        else:
            try:
                pm.openFile(path, force=True)
            except Exception as e:
                print(e)

    @QtCore.Slot()
    def on_refresh_btn_clicked(self):
        # 获取跟路径：当前场景所在的路径，
        self.root_path = AssetsViewDialog.get_root_path()
        # 如果获取失败（当前为空场景），则使用 userAppDir：Documents/maya/
        if not self.root_path:
            self.root_path = pm.internalVar(userAppDir=True)
        current_index = self.model.index(self.root_path)
        self.model.setRootPath(self.root_path)
        self.tree_view.setRootIndex(current_index)

    @QtCore.Slot()
    def on_go_up_btn_clicked(self):
        current_index = self.model.index(self.model.rootPath())
        parent_index = self.model.parent(current_index)
        if parent_index.isValid():
            self.root_path = self.model.filePath(parent_index)
            self.model.setRootPath(self.root_path)
            self.tree_view.setRootIndex(parent_index)
        else:
            pm.warning("已在文件系统根目录，无法再向上！")

    @QtCore.Slot()
    def show_context_menu(self, position):
        selected_indexes = self.tree_view.selectedIndexes()
        if selected_indexes and not self.model.isDir(selected_indexes[0]):
            context_menu = QtWidgets.QMenu()
            context_menu.addActions(
                [self.open_action, self.import_action, self.reference_action]
            )
            context_menu.exec_(self.mapToGlobal(position))

    @QtCore.Slot()
    def open_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.model.filePath(file_index)
        try:
            pm.openFile(file_path, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to open file: {str(e)}"
            )

    @QtCore.Slot()
    def import_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.model.filePath(file_index)
        file_name = Path(file_path).stem
        try:
            pm.importFile(file_path, namespace=file_name, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to open file: {str(e)}"
            )

    @QtCore.Slot()
    def reference_file(self):
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.model.filePath(file_index)
        file_name = Path(file_path).stem
        try:
            pm.createReference(file_path, namespace=file_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to open file: {str(e)}"
            )

    @staticmethod
    def get_root_path() -> str:
        scene_path = pm.sceneName()
        return (
            str(Path(scene_path).parent)
            if scene_path
            else pm.internalVar(userAppDir=True)
        )

    @staticmethod
    def get_maya_main_win():
        """获取maya主界面"""
        return pm.ui.Window("MayaWindow").asQtObject()

    @classmethod
    def show_ui(cls):
        """显示界面"""
        if not cls._ui_instance:
            cls._ui_instance = cls()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()

    def closeEvent(self, event):
        AssetsViewDialog._ui_instance = None
        super().closeEvent(event)


if __name__ == "__main__":
    AssetsViewDialog.show_ui()
