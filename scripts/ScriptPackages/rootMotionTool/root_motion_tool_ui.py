# -*- encoding: utf-8 -*-
"""
@File    :   root_motion_tool_01.py
@Time    :   2025/04/27 18:01:03
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用
"""

import math
from Qt import QtCore, QtWidgets
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import pymel.core as pc


class RootMotionTool(QtWidgets.QDialog):
    _ui_instance = None
    WINDOW_TITLE = "RootMotionTool"

    def __init__(self, parent=None):
        if parent is None:
            parent = self.get_maya_main_window()
        super().__init__(parent)

        self.root_name = None
        self.pelvis_name = None

        self.ctrl_loc_list = []

        self.root_motion_tx = False
        self.root_motion_ty = True
        self.root_motion_tz = False

        self.root_motion_rx = False
        self.root_motion_ry = False
        self.root_motion_rz = False

        self.setWindowTitle(RootMotionTool.WINDOW_TITLE)
        self.setMinimumSize(300, 120)
        # 窗口在关闭时自动彻底销毁对象
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.root_obj_label = QtWidgets.QLabel("Root Obj: ")
        self.root_obj_line = QtWidgets.QLineEdit()
        self.root_obj_btn = QtWidgets.QPushButton("<<")

        self.pelvis_obj_label = QtWidgets.QLabel("Pelvis Obj: ")
        self.pelvis_obj_line = QtWidgets.QLineEdit()
        self.pelvis_obj_btn = QtWidgets.QPushButton("<<")

        self.ik_ctrls_label = QtWidgets.QLabel("Ik Ctrls: ")
        self.ik_ctrls_btn = QtWidgets.QPushButton("Load Ik Ctrls")
        self.ik_ctrls_list = QtWidgets.QListWidget()

        self.tx_label = QtWidgets.QLabel("Translate X: ")
        self.tx_checkBox = QtWidgets.QCheckBox()
        self.ty_label = QtWidgets.QLabel("Translate Y: ")
        self.ty_checkBox = QtWidgets.QCheckBox()
        self.tz_label = QtWidgets.QLabel("Translate Z: ")
        self.tz_checkBox = QtWidgets.QCheckBox()
        self.rx_label = QtWidgets.QLabel("Rotate X: ")
        self.rx_checkBox = QtWidgets.QCheckBox()
        self.ry_label = QtWidgets.QLabel("Rotate Y: ")
        self.ry_checkBox = QtWidgets.QCheckBox()
        self.rz_label = QtWidgets.QLabel("Rotate Z: ")
        self.rz_checkBox = QtWidgets.QCheckBox()

        self.inplace_to_rootmotion_btn = QtWidgets.QPushButton("Inplace To Rootmotion")
        self.rootmotion_to_inplace_btn = QtWidgets.QPushButton("Rootmotion To Inplace")

    def create_layout(self):
        root_obj_layout = QtWidgets.QHBoxLayout()
        root_obj_layout.addWidget(self.root_obj_label)
        root_obj_layout.addWidget(self.root_obj_line)
        root_obj_layout.addWidget(self.root_obj_btn)

        pelvis_obj_layout = QtWidgets.QHBoxLayout()
        pelvis_obj_layout.addWidget(self.pelvis_obj_label)
        pelvis_obj_layout.addWidget(self.pelvis_obj_line)
        pelvis_obj_layout.addWidget(self.pelvis_obj_btn)

        ik_ctrls_layout = QtWidgets.QVBoxLayout()
        ik_ctrls_layout.addWidget(self.ik_ctrls_label)
        ik_ctrls_layout.addWidget(self.ik_ctrls_list)
        ik_ctrls_layout.addWidget(self.ik_ctrls_btn)

        translate_layout = QtWidgets.QHBoxLayout()
        translate_layout.addWidget(self.tx_label)
        translate_layout.addWidget(self.tx_checkBox)
        translate_layout.addWidget(self.ty_label)
        translate_layout.addWidget(self.ty_checkBox)
        translate_layout.addWidget(self.tz_label)
        translate_layout.addWidget(self.tz_checkBox)

        rotate_layout = QtWidgets.QHBoxLayout()
        rotate_layout.addWidget(self.rx_label)
        rotate_layout.addWidget(self.rx_checkBox)
        rotate_layout.addWidget(self.ry_label)
        rotate_layout.addWidget(self.ry_checkBox)
        rotate_layout.addWidget(self.rz_label)
        rotate_layout.addWidget(self.rz_checkBox)

        axis_layout = QtWidgets.QVBoxLayout()
        axis_layout.addLayout(translate_layout)
        axis_layout.addLayout(rotate_layout)

        axis_grp = QtWidgets.QGroupBox("Root Motion Axis")
        axis_grp.setLayout(axis_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(root_obj_layout)
        main_layout.addLayout(pelvis_obj_layout)
        main_layout.addLayout(ik_ctrls_layout)
        main_layout.addWidget(axis_grp)
        main_layout.addWidget(self.inplace_to_rootmotion_btn)
        main_layout.addWidget(self.rootmotion_to_inplace_btn)

    def create_connections(self):
        pass

    @QtCore.Slot()
    def template_slot(self):
        pass

    # def pin_ctrl_anim(self, ctrl_list=None):
    #     """为选定的控制器生成pin控制动画
    #     原理：
    #     1. 为每个控制器创建一个空间定位器.
    #     2. 控制器约束定位器，并烘焙定位器动画，便将控制器的动画传递到定位器上.
    #     3. 删除约束节点.
    #     4. 反过来,定位器约束控制器,控制器便被Pin住了.
    #     5. 这样便可以在不破坏身体动画的前提下修改main和root控制器,一般用来处理根骨骼动画
    #     """
    #     global ctrl_loc_list
    #     if ctrl_list is None:
    #         ctrl_list = pc.selected()
    #     sel_list = ctrl_list
    #     ctrl_loc_list = []
    #     ctrl_con_list = []
    #     for ctrl in sel_list:
    #         ctrl_loc = pc.spaceLocator(n=f"{ctrl}_loc")
    #         ctrl_loc_list.append(ctrl_loc)
    #         ctrl_cons = pc.parentConstraint(ctrl, ctrl_loc, mo=False)
    #         ctrl_con_list.append(ctrl_cons)
    #     pc.bakeResults(
    #         ctrl_loc_list,
    #         simulation=True,
    #         t=(pc.env.getMinTime(), pc.env.getMaxTime()),
    #         sampleBy=1,
    #     )
    #     pc.delete(ctrl_con_list)
    #     for i, ctrl in enumerate(sel_list):
    #         pc.parentConstraint(ctrl_loc_list[i], ctrl, mo=True)

    # def bake_pined_anim(self,ctrl_list=None):
    #     """烘焙控制器动画，并删除空间定位器"""
    #     pc.bakeResults(
    #         ctrl_list,
    #         simulation=True,
    #         t=(pc.env.getMinTime(), pc.env.getMaxTime()),
    #         sampleBy=1,
    #     )
    #     pc.delete(ctrl_loc_list)

    # def Inplace_to_RootMotion(self,root_ctrl, pelvis_ctrl, ik_ctrl_list=None):
    #     """
    #     在maya中转换原地动画为根动画.

    #     Args:
    #                     root_name (str): 根骨骼名称.
    #                     pelvis_name (str): 胯骨骼名称

    #     Raises:
    #                     ValueError: 如果对象不存在.
    #     """
    #     # 验证输入参数
    #     if not pc.objExists(root_ctrl):
    #         raise ValueError(f"Root bone '{root_ctrl}' does not exist in the scene.")
    #     if not pc.objExists(pelvis_ctrl):
    #         raise ValueError(f"Pelvis bone '{pelvis_ctrl}' does not exist in the scene.")

    #     # 获取动画时间范围
    #     firstFrame = math.floor(pc.findKeyframe(pelvis_ctrl, which="first"))
    #     lastFrame = math.ceil(pc.findKeyframe(pelvis_ctrl, which="last"))
    #     pc.currentTime(firstFrame)
    #     # 用唯一的名称创建定位器
    #     loc_root = pc.spaceLocator(name="loc_root")
    #     loc_pelvis = pc.spaceLocator(name="loc_pelvis")

    #     try:
    #         # 控制器约束定位器
    #         loc_root_constr = pc.parentConstraint(root_ctrl, loc_root)
    #         loc_pelvis_constr = pc.parentConstraint(pelvis_ctrl, loc_pelvis)

    #         # 烘焙定位器动画
    #         pc.bakeResults(
    #             loc_root, loc_pelvis, time=(firstFrame, lastFrame), sparseAnimCurveBake=True
    #         )

    #         # 删除约束节点
    #         pc.delete(loc_root_constr, loc_pelvis_constr)
    #         # 钉住pelvis控制器和IK控制器
    #         pin_ctrl_anim([pelvis_ctrl] + (ik_ctrl_list or []))

    #         # 胯定位器分别用点约束和方向约束约束根定位器
    #         loc_point_contr = pc.pointConstraint(loc_pelvis, loc_root, maintainOffset=True)
    #         loc_orient_contr = pc.orientConstraint(
    #             loc_pelvis, loc_root, maintainOffset=True
    #         )

    #         # 烘焙动画
    #         pc.bakeResults(
    #             loc_root,
    #             time=(firstFrame, lastFrame),
    #             sparseAnimCurveBake=True,
    #             minimizeRotation=True,
    #         )
    #         # 删除约束节点
    #         pc.delete(loc_point_contr, loc_orient_contr)

    #         # 执行欧拉过滤器防止跳变
    #         pc.filterCurve(loc_root, filter="euler")
    #         # 根据根动画所需属性修改跟定位器动画
    #         if not root_motion_tx:
    #             loc_root.translateX.disconnect()
    #             pc.setKeyframe(loc_root.translateX)
    #         if not root_motion_ty:
    #             loc_root.translateY.disconnect()
    #             pc.setKeyframe(loc_root.translateY)
    #         if not root_motion_tz:
    #             loc_root.translateZ.disconnect()
    #             pc.setKeyframe(loc_root.translateZ)
    #         if not root_motion_rx:
    #             loc_root.rotateX.disconnect()
    #             pc.setKeyframe(loc_root.rotateX)
    #         if not root_motion_ry:
    #             loc_root.rotateY.disconnect()
    #             pc.setKeyframe(loc_root.rotateY)
    #         if not root_motion_rz:
    #             loc_root.rotateZ.disconnect()
    #             pc.setKeyframe(loc_root.rotateZ)

    #         # 定位器约束骨骼
    #         jnt_root_constr = pc.parentConstraint(loc_root, root_ctrl)

    #         # 烘焙最终动画到骨骼
    #         pc.bakeResults(
    #             root_ctrl,
    #             time=(firstFrame, lastFrame),
    #             sparseAnimCurveBake=True,
    #         )
    #         # 删除约束节点
    #         pc.delete(jnt_root_constr)
    #         bake_pined_anim([pelvis_ctrl] + (ik_ctrl_list or []))
    #         # 执行欧拉过滤器
    #         pc.filterCurve(root_ctrl, filter="euler")
    #     finally:
    #         # 清理定位器
    #         pc.delete([obj for obj in [loc_root, loc_pelvis] if pc.objExists(obj)])

    # def RootMotion_to_Inplace(self,root_name, pelvis_name, ik_ctrl_list=None):
    #     # 验证输入参数
    #     if not pc.objExists(root_name):
    #         raise ValueError(f"Root bone '{root_name}' does not exist in the scene.")
    #     if not pc.objExists(pelvis_name):
    #         raise ValueError(f"Pelvis bone '{pelvis_name}' does not exist in the scene.")
    #     # 获取动画时间范围
    #     firstFrame = math.floor(pc.findKeyframe(pelvis_name, which="first"))
    #     lastFrame = math.ceil(pc.findKeyframe(pelvis_name, which="last"))
    #     pc.currentTime(firstFrame)
    #     # 用唯一的名称创建定位器
    #     locPelvis = pc.spaceLocator(name="locPelvis")
    #     locLFoot = pc.spaceLocator(name="locLFoot")
    #     locRFoot = pc.spaceLocator(name=g"locRFoot")
    #     # 控制器约束定位器
    #     pelvis_constr = pc.parentConstraint(pelvis_name, locPelvis)
    #     foot_l_constr = pc.parentConstraint(foot_l_name, locLFoot)
    #     foot_r_constr = pc.parentConstraint(foot_r_name, locRFoot)
    #     # 烘焙定位器动画
    #     pc.bakeResults(locPelvis, locLFoot, locRFoot, time=(firstFrame, lastFrame))
    #     pc.delete(pelvis_constr, foot_l_constr, foot_r_constr)
    #     # 定位器约束控制器
    #     pelvis_constr = pc.parentConstraint(locPelvis, root_name)
    #     foot_l_constr = pc.parentConstraint(locLFoot, foot_l_name)
    #     foot_r_constr = pc.parentConstraint(locRFoot, foot_r_name)
    #     # 列出需要断开连接的根骨骼属性
    #     Attrs = [
    #         f"{root_name}.tx",
    #         f"{root_name}.ty",
    #         f"{root_name}.tz",
    #         f"{root_name}.rx",
    #         f"{root_name}.ry",
    #         f"{root_name}.rz",
    #     ]
    #     # 断开连接并设置为0
    #     for attr in Attrs:
    #         attr.disconnect()
    #         attr.set(0)
    #         pc.setKeyframe(attr)
    #     # 烘焙动画到控制器
    #     pc.bakeResults(pelvis_name, foot_l_name, foot_r_name, time=(firstFrame, lastFrame))
    #     # 清理场景
    #     pc.delete(
    #         pelvis_constr, foot_l_constr, foot_r_constr, locPelvis, locLFoot, locRFoot
    #     )

    def closeEvent(self, event):
        """关闭窗口时清空实例"""
        RootMotionTool._ui_instance = None
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
            cls._ui_instance = RootMotionTool()
            cls._ui_instance.show()
        # 其他情况实例抬起并激活
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()


# 执行代码
def run():
    RootMotionTool.show_ui()
