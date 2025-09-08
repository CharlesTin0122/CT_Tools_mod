# -*- encoding: utf-8 -*-
"""
@File    :   file_explorer.py
@Time    :   2025/09/08 11:31:17
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

from pathlib import Path
from Qt import QtCore, QtWidgets, QtGui
import pymel.core as pm


class AssetsViewDialog(QtWidgets.QDialog):
    WINDOW_TITLE = "Assets Explorer"
    _ui_instance = None

    def __init__(self, parent=None):
        """构造函数"""
        if not parent:
            parent = AssetsViewDialog.get_maya_main_win()
        super().__init__(parent)

        self.setWindowTitle(AssetsViewDialog.WINDOW_TITLE)
        self.setMinimumSize(800, 500)
        # 默认根路径为：D:\Backup\Documents\maya
        self.root_path = pm.internalVar(userAppDir=True)
        # 构建界面
        self.create_actions()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

        # 设置上下文菜单,仅在tree_view中点右键才有效果
        self.tree_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)

    def create_actions(self):
        """构建右键菜单"""
        self.open_action = QtWidgets.QAction("Open", self)
        self.import_action = QtWidgets.QAction("Import", self)
        self.reference_action = QtWidgets.QAction("Reference", self)
        self.reveal_action = QtWidgets.QAction("Reveal", self)

    def create_widgets(self):
        """创建控件"""
        # 获取跟路径：当前场景所在的路径，
        self.root_path = AssetsViewDialog.get_root_path()
        # 如果获取失败（当前为空场景），则使用 userAppDir：Documents/maya/
        if not self.root_path:
            self.root_path = pm.internalVar(userAppDir=True)

        # 标签：显示当前路径
        self.path_label = QtWidgets.QLabel(self.root_path)
        self.path_label.setFixedHeight(30)
        self.path_label.setStyleSheet("font-size: 16px;")
        # 设置树视图模型，用于表示文件系统的层次结构（如目录和文件）
        self.model = QtWidgets.QFileSystemModel()  # 创建模型
        self.model.setRootPath(self.root_path)  # 设置模型根路径
        self.model.setNameFilters(["*.ma", "*.mb", "*.fbx"])  # 过滤
        # self.model.setNameFilterDisables(False)  # 隐藏过滤文件

        # 设置树视图控件
        self.tree_view = QtWidgets.QTreeView()  # 创建树视图控件
        self.tree_view.setModel(self.model)  # 设置模型
        self.tree_view.setRootIndex(self.model.index(self.root_path))  # 设置根索引
        # self.tree_view.hideColumn(1)  # 隐藏size列
        self.tree_view.setColumnWidth(0, 250)  # 设置name列宽度为250
        # 创建按钮
        self.refresh_btn = QtWidgets.QPushButton("Refresh")
        self.go_up_btn = QtWidgets.QPushButton("Go Up")

    def create_layout(self):
        """创建布局"""
        btn_layou = QtWidgets.QHBoxLayout()
        btn_layou.addWidget(self.refresh_btn)
        btn_layou.addWidget(self.go_up_btn)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.path_label)
        main_layout.addWidget(self.tree_view)
        main_layout.addLayout(btn_layou)

    def create_connections(self):
        """创建连接"""
        self.tree_view.doubleClicked.connect(self.on_double_clicked)  # 双击
        self.refresh_btn.clicked.connect(self.on_refresh_btn_clicked)  # 刷新
        self.go_up_btn.clicked.connect(self.on_go_up_btn_clicked)  # 向上
        self.open_action.triggered.connect(self.open_file)  # 打开
        self.import_action.triggered.connect(self.import_file)  # 导入
        self.reference_action.triggered.connect(self.reference_file)  # 参考
        self.reveal_action.triggered.connect(self.reveal_in_explorer)  # 转到

    def refresh_file_list(self, file_path):
        """刷新列表"""
        # 获取路径
        self.root_path = file_path
        if not self.root_path:
            self.root_path = pm.internalVar(userAppDir=True)
        # 根据路径获取索引
        current_index = self.model.index(self.root_path)
        # 设置根路径
        self.model.setRootPath(self.root_path)
        # 设置根索引
        self.tree_view.setRootIndex(current_index)
        # 设置路径标签
        self.path_label.setText(self.root_path)

    @QtCore.Slot()
    def show_context_menu(self, position):
        """右键菜单"""
        # 获取选中对象索引
        selected_indexes = self.tree_view.selectedIndexes()
        # 如果选中的对象索引存在且不为路径文件夹，显示右键菜单
        if selected_indexes and not self.model.isDir(selected_indexes[0]):
            context_menu = QtWidgets.QMenu()
            context_menu.addActions(
                [
                    self.open_action,
                    self.import_action,
                    self.reference_action,
                    self.reveal_action,
                ]
            )
            context_menu.exec_(self.tree_view.mapToGlobal(position))

    @QtCore.Slot()
    def on_double_clicked(self, index):
        """双击槽函数"""
        path = self.model.filePath(index)  # 获取双击的树视图对象路径
        # 如果对象是文件夹路径
        if self.model.isDir(index):
            self.refresh_file_list(path)
        # 如果对象是文件路径
        else:
            if pm.system.isModified():
                QtWidgets.QMessageBox.information(
                    self,
                    "unsave change",
                    text="Current scene has unsaved changes,please save first.",
                )
            else:
                try:
                    pm.openFile(path, force=True)
                except Exception as e:
                    print(e)

    @QtCore.Slot()
    def on_refresh_btn_clicked(self):
        """刷新按钮槽函数"""
        # 获取跟路径：当前场景所在的路径，
        current_path = AssetsViewDialog.get_root_path()
        self.refresh_file_list(current_path)

    @QtCore.Slot()
    def on_go_up_btn_clicked(self):
        """向上槽函数"""
        current_index = self.model.index(self.model.rootPath())
        parent_index = self.model.parent(current_index)
        if parent_index.isValid():
            parent_path = self.model.filePath(parent_index)
            self.refresh_file_list(parent_path)
        else:
            pm.warning("已在文件系统根目录，无法再向上！")

    @QtCore.Slot()
    def open_file(self):
        """打开文件槽函数"""
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
        """导入文件槽函数"""
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "Warning", "No file selected!")
            return
        file_index = selected_indexes[0]
        file_path = self.model.filePath(file_index)
        file_name = Path(file_path).stem  # 文件名称（移除后缀）
        try:
            pm.importFile(file_path, namespace=file_name, force=True)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to open file: {str(e)}"
            )

    @QtCore.Slot()
    def reference_file(self):
        """参考文件槽函数"""
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

    @QtCore.Slot()
    def reveal_in_explorer(self):
        """
        在系统的文件浏览器中定位并高亮显示所选的项目。
        """
        # 获取当前选中项的索引
        selected_indexes = self.tree_view.selectedIndexes()
        if not selected_indexes:
            QtWidgets.QMessageBox.warning(self, "警告", "没有选择任何文件或目录！")
            return

        # 获取选中项的【原始】文件路径
        original_path = self.model.filePath(selected_indexes[0])

        # 检查路径是否存在
        if not original_path:
            QtWidgets.QMessageBox.warning(
                self, "错误", f"路径不存在：\n{original_path}"
            )
            return

        # 到本地分隔符,避免 / 和 \ 混用问题
        native_path = QtCore.QDir.toNativeSeparators(original_path)
        # 使用 QProcess.startDetached 来执行命令
        QtCore.QProcess.startDetached("explorer", ["/select,", native_path])

    @staticmethod
    def get_root_path() -> str:
        """返回当前场景文件路径"""
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
