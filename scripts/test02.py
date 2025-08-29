from pathlib import Path
from Qt import QtCore, QtWidgets
import pymel.core as pm
import re


class AssetsViewDialog(QtWidgets.QDialog):
    WINDOW_TITLE = "Assets View Dialog"
    FILE_FILTERS = ["*.ma", "*.mb", "*.fbx", "*.obj"]
    _ui_instance = None

    def __init__(self, parent=None):
        if not parent:
            parent = self.get_maya_main_win()
        super().__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(800, 500)

        self.root_path = self.get_root_path() or pm.internalVar(userAppDir=True)
        print(f"Initial root path: {self.root_path}")  # 调试

        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        self.open_action = QtWidgets.QAction("Open", self)
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)

    def create_widgets(self):
        self.dir_model = QtWidgets.QFileSystemModel()
        self.dir_model.setRootPath(self.root_path)
        self.dir_model.setFilter(QtCore.QDir.Dirs | QtCore.QDir.NoDotAndDotDot)

        self.file_model = QtWidgets.QFileSystemModel()
        self.file_model.setRootPath(self.root_path)
        self.file_model.setNameFilters(self.FILE_FILTERS)
        self.file_model.setNameFilterDisables(False)
        self.file_model.setFilter(QtCore.QDir.Files)

        self.tree_view = QtWidgets.QTreeView()
        self.tree_view.setModel(self.dir_model)
        self.tree_view.setRootIndex(self.dir_model.index(self.root_path))
        self.tree_view.setColumnWidth(0, 250)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)

        self.list_view = QtWidgets.QListView()
        self.list_view.setModel(self.file_model)
        self.list_view.setRootIndex(self.file_model.index(self.root_path))

        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.go_up_btn = QtWidgets.QPushButton("Go Up")

    def create_layout(self):
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        splitter.addWidget(self.tree_view)
        splitter.addWidget(self.list_view)
        splitter.setSizes([400, 400])

        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.go_up_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(splitter)
        main_layout.addLayout(btn_layout)

    def create_connections(self):
        self.tree_view.clicked.connect(self.on_tree_view_clicked)
        self.tree_view.selectionModel().selectionChanged.connect(
            self.on_tree_view_selection_changed
        )
        self.list_view.doubleClicked.connect(self.on_list_view_double_clicked)
        self.refresh_btn.clicked.connect(self.on_refresh_btn_clicked)
        self.go_up_btn.clicked.connect(self.on_go_up_btn_clicked)
        self.open_action.triggered.connect(self.open_file)
        self.import_action.triggered.connect(self.import_file)
        self.reference_action.triggered.connect(self.reference_file)

    def on_tree_view_clicked(self, index):
        if self.dir_model.isDir(index):
            path = self.dir_model.filePath(index)
            print(f"Selected directory: {path}")  # 调试
            if path == "":  # 处理“此电脑”等特殊路径
                path = str(Path.home())
            if Path(path).exists():
                self.file_model.setRootPath("")
                self.file_model.setRootPath(path)
                self.list_view.setRootIndex(self.file_model.index(path))
                print(f"List view root set to: {path}")
            else:
                print(f"Invalid path: {path}")
                QtWidgets.QMessageBox.warning(
                    self, "Warning", f"Directory does not exist: {path}"
                )
        else:
            print(f"Selected item is not a directory: {self.dir_model.filePath(index)}")

    def on_tree_view_selection_changed(self, selected, deselected):
        indexes = selected.indexes()
        if indexes:
            index = indexes[0]
            if self.dir_model.isDir(index):
                path = self.dir_model.filePath(index)
                print(f"Selection changed to directory: {path}")  # 调试
                if path == "":
                    path = str(Path.home())
                if Path(path).exists():
                    self.file_model.setRootPath("")
                    self.file_model.setRootPath(path)
                    self.list_view.setRootIndex(self.file_model.index(path))
                    print(f"List view root updated to: {path}")
                else:
                    print(f"Invalid path: {path}")
                    QtWidgets.QMessageBox.warning(
                        self, "Warning", f"Directory does not exist: {path}"
                    )

    def on_list_view_double_clicked(self, index):
        if not self.file_model.isDir(index):
            path = self.file_model.filePath(index)
            try:
                pm.openFile(path, force=True)
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Failed to open file: {str(e)}"
                )

    def on_refresh_btn_clicked(self):
        self.root_path = self.get_root_path() or pm.internalVar(userAppDir=True)
        print(f"Refresh root path: {self.root_path}")  # 调试
        self.dir_model.setRootPath(self.root_path)
        self.file_model.setRootPath(self.root_path)
        self.tree_view.setRootIndex(self.dir_model.index(self.root_path))
        self.list_view.setRootIndex(self.file_model.index(self.root_path))

    def on_go_up_btn_clicked(self):
        current_index = self.dir_model.index(self.dir_model.rootPath())
        parent_index = self.dir_model.parent(current_index)
        if parent_index.isValid():
            self.root_path = self.dir_model.filePath(parent_index)
            print(f"Go up to: {self.root_path}")  # 调试
            self.dir_model.setRootPath(self.root_path)
            self.file_model.setRootPath(self.root_path)
            self.tree_view.setRootIndex(parent_index)
            self.list_view.setRootIndex(self.file_model.index(self.root_path))
        else:
            QtWidgets.QMessageBox.warning(
                self, "Warning", "Already at the root directory!"
            )

    def show_context_menu(self, position):
        if self.list_view.geometry().contains(self.mapToGlobal(position)):
            selected_indexes = self.list_view.selectedIndexes()
            if selected_indexes:
                context_menu = QtWidgets.QMenu()
                context_menu.addActions(
                    [self.open_action, self.import_action, self.reference_action]
                )
                context_menu.exec_(self.mapToGlobal(position))

    def open_file(self):
        selected_indexes = self.list_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.file_model.filePath(file_index)
        try:
            pm.openFile(file_path, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to open file: {str(e)}"
            )

    def import_file(self):
        selected_indexes = self.list_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.file_model.filePath(file_index)
        file_name = re.sub(r"[^a-zA-Z0-9_]", "_", Path(file_path).stem)
        try:
            pm.importFile(file_path, namespace=file_name, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to import file: {str(e)}"
            )

    def reference_file(self):
        selected_indexes = self.list_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.file_model.filePath(file_index)
        file_name = re.sub(r"[^a-zA-Z0-9_]", "_", Path(file_path).stem)
        try:
            pm.createReference(file_path, namespace=file_name)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to reference file: {str(e)}"
            )

    def closeEvent(self, event):
        AssetsViewDialog._ui_instance = None
        super().closeEvent(event)

    @staticmethod
    def get_root_path() -> str:
        scene_path = pm.sceneName()
        print(f"Scene path: {scene_path}")  # 调试
        return str(Path(scene_path).parent) if scene_path else ""

    @staticmethod
    def get_maya_main_win():
        return pm.ui.Window("MayaWindow").asQtObject()

    @classmethod
    def show_ui(cls):
        if not cls._ui_instance:
            cls._ui_instance = cls()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


if __name__ == "__main__":
    AssetsViewDialog.show_ui()
