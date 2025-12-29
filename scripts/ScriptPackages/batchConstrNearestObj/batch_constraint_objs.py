from Qt import QtCore, QtWidgets
import pymel.core as pm
from RigUtils.rig_utils import matrix_constraint


class BatchConstrNearestObjs(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "Constraint Nearest Tool"
    OBJECT_NAME = "BatchConstrNearestWin"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setObjectName(self.OBJECT_NAME)
        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(400, 500)  # 调大默认尺寸
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # 初始化数据变量
        self.driver_list = []
        self.driven_list = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.load_driver_objs_btn = QtWidgets.QPushButton(
            "1. Load Driver Objects (Parents)"
        )
        self.driver_objs_list_wdg = QtWidgets.QListWidget()

        self.load_driven_objs_btn = QtWidgets.QPushButton(
            "2. Load Driven Objects (Children)"
        )
        self.driven_objs_list_wdg = QtWidgets.QListWidget()

        # 约束类型
        self.type_grp_box = QtWidgets.QGroupBox("Constraint Types")
        self.matrix_rb = QtWidgets.QRadioButton("Matrix")
        self.matrix_rb.setChecked(True)
        self.parent_rb = QtWidgets.QRadioButton("Parent")
        self.point_rb = QtWidgets.QRadioButton("Point")
        self.orient_rb = QtWidgets.QRadioButton("Orient")
        self.scale_rb = QtWidgets.QRadioButton("Scale")

        self.btn_grp = QtWidgets.QButtonGroup(self)
        for i, rb in enumerate(
            [
                self.matrix_rb,
                self.parent_rb,
                self.point_rb,
                self.orient_rb,
                self.scale_rb,
            ],
            1,
        ):
            self.btn_grp.addButton(rb, i)

        self.constraint_btn = QtWidgets.QPushButton("Batch Constraint Nearest")
        self.constraint_btn.setFixedHeight(60)
        self.constraint_btn.setStyleSheet("background-color: #444; font-weight: bold;")

    def create_layout(self):
        h_layout = QtWidgets.QHBoxLayout(self.type_grp_box)
        h_layout.addWidget(self.matrix_rb)
        h_layout.addWidget(self.parent_rb)
        h_layout.addWidget(self.point_rb)
        h_layout.addWidget(self.orient_rb)
        h_layout.addWidget(self.scale_rb)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.load_driver_objs_btn)
        main_layout.addWidget(self.driver_objs_list_wdg)
        main_layout.addWidget(self.load_driven_objs_btn)
        main_layout.addWidget(self.driven_objs_list_wdg)
        main_layout.addWidget(self.type_grp_box)
        main_layout.addWidget(self.constraint_btn)

    def create_connections(self):
        self.load_driver_objs_btn.clicked.connect(lambda: self.on_load_objs("driver"))
        self.load_driven_objs_btn.clicked.connect(lambda: self.on_load_objs("driven"))
        self.constraint_btn.clicked.connect(self.on_constraint_btn_clicked)

    def on_load_objs(self, mode):
        """统一处理加载逻辑"""
        sel = pm.selected()
        if not sel:
            pm.warning("Nothing selected!")
            return

        if mode == "driver":
            self.driver_list = sel
            self.driver_objs_list_wdg.clear()
            self.driver_objs_list_wdg.addItems([obj.name() for obj in sel])
        else:
            self.driven_list = sel
            self.driven_objs_list_wdg.clear()
            self.driven_objs_list_wdg.addItems([obj.name() for obj in sel])

    @QtCore.Slot()
    def on_constraint_btn_clicked(self):
        if not self.driver_list or not self.driven_list:
            pm.warning("Missing driver or driven objects!")
            return

        constraint_type = self.btn_grp.checkedId()
        self.batch_constraint_nearest_objs(
            self.driver_list, self.driven_list, constraint_type
        )
        pm.displayInfo("Batch constraint finished!")

    def batch_constraint_nearest_objs(self, driver_list, diven_list, constraint_type):
        """核心逻辑改进：添加 UndoChunk 和更安全的坐标获取"""

        with pm.UndoChunk():
            for obj in driver_list:
                closest_obj = None
                closest_distance = float("inf")
                pos1 = obj.getTranslation(space="world")

                for other_obj in diven_list:
                    if other_obj == obj:
                        continue

                    pos2 = other_obj.getTranslation(space="world")
                    distance = (pos1 - pos2).length()

                    if distance < closest_distance:
                        closest_obj = other_obj
                        closest_distance = distance

                if closest_obj:
                    if constraint_type == 1:
                        matrix_constraint(obj, closest_obj, maintainOffset=True)
                    elif constraint_type == 2:
                        pm.parentConstraint(obj, closest_obj, mo=True)
                    elif constraint_type == 3:
                        pm.pointConstraint(obj, closest_obj, mo=True)
                    elif constraint_type == 4:
                        pm.orientConstraint(obj, closest_obj, mo=True)
                    elif constraint_type == 5:
                        pm.scaleConstraint(obj, closest_obj, mo=True)

    def closeEvent(self, event):
        BatchConstrNearestObjs._ui_instance = None
        super().closeEvent(event)

    @staticmethod
    def get_maya_main_window():
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == "MayaWindow":
                return widget
        return None

    @classmethod
    def show_ui(cls):
        if cls._ui_instance and cls._ui_instance.isVisible():
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()
            return cls._ui_instance

        if cls._ui_instance:
            cls._ui_instance.close()
            cls._ui_instance.deleteLater()

        cls._ui_instance = BatchConstrNearestObjs()
        cls._ui_instance.show()
        return cls._ui_instance


def run():
    BatchConstrNearestObjs.show_ui()
