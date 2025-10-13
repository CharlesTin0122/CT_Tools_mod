from Qt import QtCore, QtWidgets
import pymel.core as pm
import pymel.core.nodetypes as nt
from RigUtils.rig_utils import addOffsetGroups


class ReverseFootTool(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "ReverseFootTool"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.setWindowTitle(ReverseFootTool.WINDOW_TITLE)
        self.setMinimumSize(300, 120)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.suffix_label = QtWidgets.QLabel("Locator Suffix: ")
        self.suffix_line = QtWidgets.QLineEdit()
        # self.suffix_line.setFixedWidth(120)
        self.create_locator_btn = QtWidgets.QPushButton("Create Locators")
        # self.creat_locator_btn.setMaximumWidth(360)

        self.foot_ik_ctrl_label = QtWidgets.QLabel("foot_ik_ctrl: ")
        self.foot_ik_ctrl_line = QtWidgets.QLineEdit()
        self.foot_ik_ctrl_btn = QtWidgets.QPushButton("<<")

        self.toe_ik_ctrl_label = QtWidgets.QLabel("toe_ik_ctrl: ")
        self.toe_ik_ctrl_line = QtWidgets.QLineEdit()
        self.toe_ik_ctrl_btn = QtWidgets.QPushButton("<<")

        self.foot_ik_handle_label = QtWidgets.QLabel("foot_ik_handle: ")
        self.foot_ik_handle_line = QtWidgets.QLineEdit()
        self.foot_ik_handle_btn = QtWidgets.QPushButton("<<")

        self.ball_ik_handle_label = QtWidgets.QLabel("ball_ik_handle: ")
        self.ball_ik_handle_line = QtWidgets.QLineEdit()
        self.ball_ik_handle_btn = QtWidgets.QPushButton("<<")

        self.tip_ik_handle_label = QtWidgets.QLabel("tip_ik_handle: ")
        self.tip_ik_handle_line = QtWidgets.QLineEdit()
        self.tip_ik_handle_btn = QtWidgets.QPushButton("<<")

        self.create_reverse_foot_btn = QtWidgets.QPushButton("Create Reverse Foot")
        # self.create_reverse_foot_btn.setMaximumWidth(360)

    def create_layout(self):
        suffix_layout = QtWidgets.QHBoxLayout()
        suffix_layout.setSpacing(5)
        suffix_layout.addWidget(self.suffix_label)
        suffix_layout.addWidget(self.suffix_line)
        create_locator_layout = QtWidgets.QVBoxLayout()

        create_locator_layout.addLayout(suffix_layout)
        create_locator_layout.addWidget(self.create_locator_btn)
        create_locator_grp = QtWidgets.QGroupBox("Creat Locators")
        create_locator_grp.setLayout(create_locator_layout)

        ctrl_layout = QtWidgets.QHBoxLayout()
        ctrl_layout.setSpacing(5)
        ctrl_layout.addWidget(self.foot_ik_ctrl_label)
        ctrl_layout.addWidget(self.foot_ik_ctrl_line)
        ctrl_layout.addWidget(self.foot_ik_ctrl_btn)

        ctrl_layout.addWidget(self.toe_ik_ctrl_label)
        ctrl_layout.addWidget(self.toe_ik_ctrl_line)
        ctrl_layout.addWidget(self.toe_ik_ctrl_btn)

        foot_ik_handle_layout = QtWidgets.QHBoxLayout()
        foot_ik_handle_layout.addWidget(self.foot_ik_handle_line)
        foot_ik_handle_layout.addWidget(self.foot_ik_handle_btn)

        ball_ik_handle_layout = QtWidgets.QHBoxLayout()
        ball_ik_handle_layout.addWidget(self.ball_ik_handle_line)
        ball_ik_handle_layout.addWidget(self.ball_ik_handle_btn)

        tip_ik_handle_layout = QtWidgets.QHBoxLayout()
        tip_ik_handle_layout.addWidget(self.tip_ik_handle_line)
        tip_ik_handle_layout.addWidget(self.tip_ik_handle_btn)

        handle_layout = QtWidgets.QVBoxLayout()
        handle_layout.setSpacing(5)

        handle_layout.addWidget(self.foot_ik_handle_label)
        handle_layout.addLayout(foot_ik_handle_layout)

        handle_layout.addWidget(self.ball_ik_handle_label)
        handle_layout.addLayout(ball_ik_handle_layout)

        handle_layout.addWidget(self.tip_ik_handle_label)
        handle_layout.addLayout(tip_ik_handle_layout)

        create_reverse_foot_layout = QtWidgets.QVBoxLayout()

        create_reverse_foot_layout.addLayout(ctrl_layout)
        create_reverse_foot_layout.addLayout(handle_layout)
        create_reverse_foot_layout.addWidget(self.create_reverse_foot_btn)

        create_reverse_foot_grp = QtWidgets.QGroupBox("Creat Reverse Foot")
        create_reverse_foot_grp.setLayout(create_reverse_foot_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(create_locator_grp)
        main_layout.addWidget(create_reverse_foot_grp)

    def create_connections(self):
        self.create_locator_btn.clicked.connect(self.on_creat_locator)
        self.create_reverse_foot_btn.clicked.connect(self.on_create_reverse_foot)
        self.foot_ik_ctrl_btn.clicked.connect(self.on_load_obj_btn_clicked)
        self.toe_ik_ctrl_btn.clicked.connect(self.on_load_obj_btn_clicked)
        self.foot_ik_handle_btn.clicked.connect(self.on_load_obj_btn_clicked)
        self.ball_ik_handle_btn.clicked.connect(self.on_load_obj_btn_clicked)
        self.tip_ik_handle_btn.clicked.connect(self.on_load_obj_btn_clicked)

    @QtCore.Slot()
    def on_load_obj_btn_clicked(self):
        line_edit = None
        sender = self.sender()
        if sender == self.foot_ik_ctrl_btn:
            line_edit = self.foot_ik_ctrl_line
        elif sender == self.toe_ik_ctrl_btn:
            line_edit = self.toe_ik_ctrl_line
        elif sender == self.foot_ik_handle_btn:
            line_edit = self.foot_ik_handle_line
        elif sender == self.ball_ik_handle_btn:
            line_edit = self.ball_ik_handle_line
        elif sender == self.tip_ik_handle_btn:
            line_edit = self.tip_ik_handle_line
        else:
            pm.warning("Unknown button clicked")

        select_obj = pm.selected()
        if not select_obj:
            pm.warning("Please select objects")
        line_edit.setText(select_obj[0].name())

    @QtCore.Slot()
    def on_creat_locator(self):
        suffix = self.suffix_line.text()
        self.locator_list = self.create_locators(suffix)

    @QtCore.Slot()
    def on_create_reverse_foot(self):
        # 获取参数
        foot_ik_ctrl = nt.Transform(self.foot_ik_ctrl_line.text())
        toe_ik_ctrl = nt.Transform(self.toe_ik_ctrl_line.text())
        foot_ik_handle = nt.IkHandle(self.foot_ik_handle_line.text())
        ball_ik_handle = nt.IkHandle(self.ball_ik_handle_line.text())
        tip_ik_handle = nt.IkHandle(self.tip_ik_handle_line.text())
        # 验证参数
        if not all(
            [foot_ik_ctrl, toe_ik_ctrl, foot_ik_handle, ball_ik_handle, tip_ik_handle]
        ):
            pm.warning("Please make sure all controls and handles are assigned.")
            return
        if not self.locator_list or len(self.locator_list) < 6:
            pm.warning("Please create locators first.")
            return
        # 获取locator
        (
            heel_rev_ctrl,
            tip_rev_ctrl,
            out_rev_ctrl,
            in_rev_ctrl,
            pivot_rev_ctrl,
            ball_rev_ctrl,
        ) = self.locator_list
        # 执行创建
        self.reverse_foot(
            foot_ik_ctrl,
            toe_ik_ctrl,
            foot_ik_handle,
            ball_ik_handle,
            tip_ik_handle,
            heel_rev_ctrl,
            tip_rev_ctrl,
            out_rev_ctrl,
            in_rev_ctrl,
            pivot_rev_ctrl,
            ball_rev_ctrl,
        )

    def create_locators(self, suffix=None) -> list[nt.Transform]:
        """
        创建定位器用于定位反转脚控制器位置，其中：
            heel：脚后跟
            tip：脚尖
            out：脚掌外侧
            in:脚掌内侧
            pivot和ball：脚趾根部
        """
        loc_list = []
        heel_rev_loc = pm.spaceLocator(name=f"heel_rev_loc{suffix}")
        tip_rev_loc = pm.spaceLocator(name=f"tip_rev_loc{suffix}")
        out_rev_loc = pm.spaceLocator(name=f"out_rev_loc{suffix}")
        in_rev_loc = pm.spaceLocator(name=f"in_rev_loc{suffix}")
        pivot_rev_loc = pm.spaceLocator(name=f"pivot_rev_loc{suffix}")
        ball_rev_loc = pm.spaceLocator(name=f"ball_rev_loc{suffix}")
        pm.parent(ball_rev_loc, pivot_rev_loc)
        loc_list = [
            heel_rev_loc,
            tip_rev_loc,
            out_rev_loc,
            in_rev_loc,
            pivot_rev_loc,
            ball_rev_loc,
        ]
        return loc_list

    def reverse_foot(
        self,
        foot_ik_ctrl: nt.Transform,
        toe_ik_ctrl: nt.Transform,
        foot_ik_handle: nt.IkHandle,
        ball_ik_handle: nt.IkHandle,
        tip_ik_handle: nt.IkHandle,
        heel_rev_ctrl: nt.Transform,
        tip_rev_ctrl: nt.Transform,
        out_rev_ctrl: nt.Transform,
        in_rev_ctrl: nt.Transform,
        pivot_rev_ctrl: nt.Transform,
        ball_rev_ctrl: nt.Transform,
    ):
        """设置反转脚
        Args:
            foot_ik_ctrl (nt.Transform): 脚部IK控制器,控制脚部变换
            toe_ik_ctrl (nt.Transform): 脚趾IK控制器,控制脚趾的旋转
            foot_ik_handle (nt.IkHandle): 脚部IK句柄
            ball_ik_handle (nt.IkHandle): 脚趾根IK句柄
            tip_ik_handle (nt.IkHandle): 脚尖IK句柄
            heel_rev_ctrl (nt.Transform): 脚跟反转控制器
            tip_rev_ctrl (nt.Transform): 脚尖反转控制器
            out_rev_ctrl (nt.Transform): 脚外侧反转控制器
            in_rev_ctrl (nt.Transform): 脚内侧反转控制器
            ball_rev_ctrl (nt.Transform): 脚趾根反转控制器
        """
        # 创建控制器列表
        foot_ctrls = [
            toe_ik_ctrl,
            heel_rev_ctrl,
            tip_rev_ctrl,
            out_rev_ctrl,
            in_rev_ctrl,
            pivot_rev_ctrl,
            ball_rev_ctrl,
        ]
        # 为控制器创建偏移组
        (
            toe_ik_ctrl_osg,
            heel_ctrl_osg,
            tip_ctrl_osg,
            out_ctrl_osg,
            in_ctrl_osg,
            pivot_ctrl_osg,
            ball_ctrl_osg,
        ) = addOffsetGroups(foot_ctrls)
        # 创建反转脚
        pm.parent(heel_ctrl_osg, foot_ik_ctrl)
        pm.parent(tip_ctrl_osg, heel_rev_ctrl)
        pm.parent(out_ctrl_osg, tip_rev_ctrl)
        pm.parent(in_ctrl_osg, out_rev_ctrl)
        pm.parent(pivot_ctrl_osg, in_rev_ctrl)
        pm.parent(toe_ik_ctrl_osg, pivot_rev_ctrl)

        pm.parent(tip_ik_handle, toe_ik_ctrl)
        pm.parent(foot_ik_handle, ball_ik_handle, ball_rev_ctrl)
        pm.select(clear=True)

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
            cls._ui_instance = ReverseFootTool()
        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()

    def closeEvent(self, event):
        ReverseFootTool._ui_instance = None
        super().closeEvent(event)


if __name__ == "__main__":
    ReverseFootTool.show_ui()
