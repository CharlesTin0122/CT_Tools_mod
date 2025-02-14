# -*- coding: utf-8 -*-
"""
@FileName      : fbx_importer_mgear.py
@DateTime      : 2023/09/18 17:22:33
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
"""

import os
import pymel.core as pm
from mgear.core import anim_utils

# 常量定义
FKIK_ATTRS = [
    "armUI_L0_ctl.arm_blend",
    "armUI_R0_ctl.arm_blend",
    "legUI_L0_ctl.leg_blend",
    "legUI_R0_ctl.leg_blend",
]

JOINT_SL = [
    "spine_01",
    "spine_02",
    "spine_03",
    "neck_01",
    "head",
    "clavicle_l",
    "upperarm_l",
    "lowerarm_l",
    "hand_l",
    "thumb_01_l",
    "thumb_02_l",
    "thumb_03_l",
    "index_01_l",
    "index_02_l",
    "index_03_l",
    "middle_01_l",
    "middle_02_l",
    "middle_03_l",
    "ring_01_l",
    "ring_02_l",
    "ring_03_l",
    "pinky_01_l",
    "pinky_02_l",
    "pinky_03_l",
    "clavicle_r",
    "upperarm_r",
    "lowerarm_r",
    "hand_r",
    "thumb_01_r",
    "thumb_02_r",
    "thumb_03_r",
    "index_01_r",
    "index_02_r",
    "index_03_r",
    "middle_01_r",
    "middle_02_r",
    "middle_03_r",
    "ring_01_r",
    "ring_02_r",
    "ring_03_r",
    "pinky_01_r",
    "pinky_02_r",
    "pinky_03_r",
    "thigh_l",
    "calf_l",
    "foot_l",
    "ball_l",
    "thigh_r",
    "calf_r",
    "foot_r",
    "ball_r",
]

CTRL_SL = [
    "spine_C0_fk0_ctl",
    "spine_C0_fk1_ctl",
    "spine_C0_fk2_ctl",
    "neck_C0_fk0_ctl",
    "neck_C0_head_ctl",
    "clavicle_L0_ctl",
    "arm_L0_fk0_ctl",
    "arm_L0_fk1_ctl",
    "arm_L0_fk2_ctl",
    "thumb_L0_fk0_ctl",
    "thumb_L0_fk1_ctl",
    "thumb_L0_fk2_ctl",
    "index_L0_fk0_ctl",
    "index_L0_fk1_ctl",
    "index_L0_fk2_ctl",
    "middle_L0_fk0_ctl",
    "middle_L0_fk1_ctl",
    "middle_L0_fk2_ctl",
    "ring_L0_fk0_ctl",
    "ring_L0_fk1_ctl",
    "ring_L0_fk2_ctl",
    "pinky_L0_fk0_ctl",
    "pinky_L0_fk1_ctl",
    "pinky_L0_fk2_ctl",
    "clavicle_R0_ctl",
    "arm_R0_fk0_ctl",
    "arm_R0_fk1_ctl",
    "arm_R0_fk2_ctl",
    "thumb_R0_fk0_ctl",
    "thumb_R0_fk1_ctl",
    "thumb_R0_fk2_ctl",
    "index_R0_fk0_ctl",
    "index_R0_fk1_ctl",
    "index_R0_fk2_ctl",
    "middle_R0_fk0_ctl",
    "middle_R0_fk1_ctl",
    "middle_R0_fk2_ctl",
    "ring_R0_fk0_ctl",
    "ring_R0_fk1_ctl",
    "ring_R0_fk2_ctl",
    "pinky_R0_fk0_ctl",
    "pinky_R0_fk1_ctl",
    "pinky_R0_fk2_ctl",
    "leg_L0_fk0_ctl",
    "leg_L0_fk1_ctl",
    "leg_L0_fk2_ctl",
    "foot_L0_fk0_ctl",
    "leg_R0_fk0_ctl",
    "leg_R0_fk1_ctl",
    "leg_R0_fk2_ctl",
    "foot_R0_fk0_ctl",
]


class AdvAnimToolsUI:
    """项目用mGear绑定批量传递fbx动画到绑定控制器"""

    def __init__(self):
        self.fbxList = []
        self.savePath = None
        self.fbx_field = None
        self.path_field = None
        self.all_ctrls = []

    def create_ui(self):
        """构建UI"""
        try:
            pm.deleteUI("advTool")
        except Exception as e:
            print(e)

        with pm.window("advTool", title="advAnimtools") as win:
            with pm.columnLayout(rowSpacing=5, adj=True):
                with pm.frameLayout(label="Import multiple FBX"):
                    with pm.columnLayout(adj=1):
                        pm.button(label="Load All fbx", c=self.load)
                    with pm.scrollLayout(
                        w=200, h=150, bgc=(0.5, 0.5, 0.5)
                    ) as self.fbx_field:
                        pm.text("fbx Name:")
                    with pm.rowLayout(
                        numberOfColumns=3,
                        columnWidth3=(55, 140, 5),
                        adjustableColumn=2,
                        columnAlign=(1, "right"),
                        columnAttach=[(1, "both", 0), (2, "both", 0), (3, "both", 0)],
                    ):
                        pm.text(label="Save Path:")
                        self.path_field = pm.textField("ImporterTextField")
                        pm.button(label="...", w=30, h=20, c=self.select_path)
                    with pm.columnLayout(adj=1):
                        pm.button(
                            label="Import fbx And Save File !!!", c=self.import_and_save
                        )

        pm.window(win, e=True, w=250, h=300)
        pm.showWindow(win)

    def load(self, *args):
        """载入导入fbx文件路径"""
        self.fbxList = pm.fileDialog2(fileFilter="*fbx", fileMode=4)

        if not self.fbxList:
            pm.PopupError("Nothing Selected")
            self.fbxList = []
            return

        for fbxPath in self.fbxList:
            fbx_name = os.path.basename(fbxPath)
            with self.fbx_field:
                pm.text(label=fbx_name)

    def select_path(self, *args):
        """选择保存路径"""
        save_path = pm.fileDialog2(fileFilter="*folder", fileMode=2)
        if save_path:
            self.savePath = save_path[0]
            pm.textField(self.path_field, e=True, text=self.savePath)

    def delete_connection(self, plug):
        """移除给出属性接口的链接（删除动画）"""
        if pm.connectionInfo(plug, isDestination=True):
            plug = pm.connectionInfo(plug, getExactDestination=True)
            readOnly = pm.ls(plug, readOnly=True)
            if readOnly:
                source = pm.connectionInfo(plug, sourceFromDestination=True)
                pm.disconnectAttr(source, plug)
            else:
                pm.delete(plug, inputConnectionsAndNodes=True)

    def reset_controllers(self):
        """删除动画并重置控制器位置"""
        for ctrl in self.all_ctrls:
            keyable_attrs = pm.listAttr(ctrl, keyable=True)
            animatable_attrs = pm.listAnimatable(ctrl)
            for attr in animatable_attrs:
                self.delete_connection(f"{attr}")
            anim_utils.reset_selected_channels_value([ctrl], keyable_attrs)

    def setup_constraints(self):
        """创建传递动画骨骼并约束控制器"""
        pm.duplicate("skin:root")
        root_jnt = pm.PyNode("root")
        constraints = pm.ls(root_jnt, dag=True, type="constraint")
        pm.delete(constraints)

        pm.parentConstraint("root", "root_main_C0_ctl", mo=True)
        pm.parentConstraint("pelvis", "body_C0_ctl", mo=True)
        try:
            pm.parentConstraint("Weapon_L", "Weapon_L_L0_ctl", mo=True)
            pm.parentConstraint("Weapon_R", "Weapon_R_R0_ctl", mo=True)
        except Exception as e:
            print(e)

        for joint, ctrl in zip(JOINT_SL, CTRL_SL):
            pm.parentConstraint(joint, ctrl, mo=True, skipTranslate=["x", "y", "z"])

    def import_and_save(self, *args):
        """执行批量导入"""
        if not self.fbxList:
            pm.PopupError("Nothing To Import")
            return

        all_ctrl_sets = pm.PyNode("rig_controllers_grp")
        self.all_ctrls = all_ctrl_sets.members()

        for fbxPath in self.fbxList:
            self.reset_controllers()
            pm.currentUnit(time="ntsc")
            pm.env.setMinTime(0)
            pm.env.setMaxTime(1)
            pm.currentTime(0)
            pm.setKeyframe(self.all_ctrls)

            for attr in FKIK_ATTRS:
                pm.setAttr(attr, 0)

            self.setup_constraints()
            pm.importFile(fbxPath, defaultNamespace=True)

            time_value = pm.keyframe(
                "pelvis.rotateX", query=True, timeChange=True, absolute=True
            )
            first_frame = int(time_value[0])
            last_frame = int(time_value[-1])
            pm.env.setMinTime(first_frame)
            pm.env.setMaxTime(last_frame)

            pm.bakeResults(
                self.all_ctrls,
                simulation=True,
                time=(first_frame, last_frame),
                sampleBy=1,
                oversamplingRate=1,
                disableImplicitControl=True,
                preserveOutsideKeys=True,
                sparseAnimCurveBake=False,
                removeBakedAttributeFromLayer=False,
                removeBakedAnimFromLayer=False,
                bakeOnOverrideLayer=False,
                minimizeRotation=True,
                controlPoints=False,
                shape=True,
            )
            pm.delete("root")

            for frame in range(int(first_frame), int(last_frame) + 1):
                pm.currentTime(frame)
                for attr in FKIK_ATTRS:
                    pm.setAttr(attr, 0)
                anim_utils.ikFkMatch(
                    "rig",
                    "arm_blend",
                    "armUI_R0_ctl",
                    ["arm_R0_fk0_ctl", "arm_R0_fk1_ctl", "arm_R0_fk2_ctl"],
                    "arm_R0_ik_ctl",
                    "arm_R0_upv_ctl",
                )
                anim_utils.ikFkMatch(
                    "rig",
                    "arm_blend",
                    "armUI_L0_ctl",
                    ["arm_L0_fk0_ctl", "arm_L0_fk1_ctl", "arm_L0_fk2_ctl"],
                    "arm_L0_ik_ctl",
                    "arm_L0_upv_ctl",
                )
                anim_utils.ikFkMatch(
                    "rig",
                    "leg_blend",
                    "legUI_R0_ctl",
                    ["leg_R0_fk0_ctl", "leg_R0_fk1_ctl", "leg_R0_fk2_ctl"],
                    "leg_R0_ik_ctl",
                    "leg_R0_upv_ctl",
                )
                anim_utils.ikFkMatch(
                    "rig",
                    "leg_blend",
                    "legUI_L0_ctl",
                    ["leg_L0_fk0_ctl", "leg_L0_fk1_ctl", "leg_L0_fk2_ctl"],
                    "leg_L0_ik_ctl",
                    "leg_L0_upv_ctl",
                )

            pm.filterCurve(self.all_ctrls, filter="euler")

            if self.savePath:
                short_name = os.path.splitext(os.path.basename(fbxPath))[0]
                file_path = os.path.join(self.savePath, short_name + ".mb")
                print(file_path)
                pm.saveAs(file_path, force=True)

        if self.savePath:
            confirm = pm.confirmDialog(
                title="Finish", message="Done!", button=["OK", "Open Folder"]
            )
            if confirm == "Open Folder" and self.savePath:
                os.startfile(self.savePath)


if __name__ == "__main__":
    advAnimToolsUI = AdvAnimToolsUI()
    advAnimToolsUI.create_ui()
