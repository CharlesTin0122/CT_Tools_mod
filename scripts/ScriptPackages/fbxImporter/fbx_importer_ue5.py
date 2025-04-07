# -*- coding: utf-8 -*-
"""
@FileName      : fbx_importer_mgear.py
@DateTime      : 2023/09/18 17:22:33
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
"""

import logging
import os

import pymel.core as pc
from fbxImporter.config import FKIK_ATTRS, SKELETON_TO_CONTROLLER_MAP
from mgear.core import anim_utils

# 配置日志
logging.basicConfig(level=logging.INFO)


class AdvAnimToolsUI:
    """项目用mGear绑定批量传递fbx动画到绑定控制器"""

    def __init__(self):
        self.fbxList = []
        self.savePath = None
        self.fbx_list_display = None
        self.fbx_field = None
        self.path_field = None
        self.PFS_field = None
        self.all_ctrls = []
        self.arm_rbgrp = None
        self.leg_rbgrp = None
        self.first_frame = None
        self.last_frame = None

    def create_ui(self) -> None:
        """创建用户界面，用于批量导入 FBX 文件"""
        try:
            pc.deleteUI("FBXImporter")
        except Exception:
            pass
        with pc.window("FBXImporter", title="FBX Importer") as win:
            with pc.columnLayout(rowSpacing=5, adj=True):
                with pc.frameLayout(label="Import Multiple FBX Files"):
                    # 加载 FBX 文件按钮
                    with pc.columnLayout(adj=1):
                        pc.button(label="Load FBX Files", c=self.load)
                    # 显示已加载的 FBX 文件列表
                    self.fbx_list_display = pc.textScrollList(
                        w=200, h=150, bgc=(0.5, 0.5, 0.5)
                    )
                    # 保存文件选项
                    with pc.rowLayout(
                        numberOfColumns=5, columnWidth5=(50, 100, 50, 30, 30)
                    ):
                        pc.text(label="Save Path:")
                        self.path_field = pc.textField()
                        pc.button(label="...", w=30, h=20, c=self.select_path)
                        pc.text(label="FPS:")
                        self.PFS_field = pc.textField(text="30")
                        # FKIK切换按钮
                    with pc.columnLayout(adj=1):
                        self.arm_rbgrp = pc.radioButtonGrp(
                            numberOfRadioButtons=2,
                            label="Arm: ",
                            labelArray2=["FK", "IK"],
                            select=1,
                            columnAlign=(1, "left"),
                        )
                        self.leg_rbgrp = pc.radioButtonGrp(
                            numberOfRadioButtons=2,
                            label="Leg: ",
                            labelArray2=["FK", "IK"],
                            select=2,
                            columnAlign=(1, "left"),
                        )
                    pc.button(label="Import and Save", c=self.import_and_save)

        pc.window(win, e=True, w=250, h=300)
        pc.showWindow(win)

    def load(self, *args):
        """载入导入fbx文件路径"""
        self.fbxList = pc.fileDialog2(fileFilter="FBX Files (*.fbx)", fileMode=4) or []
        if not self.fbxList:
            pc.warning("Nothing Selected")
            return

        for fbxPath in self.fbxList:
            fbx_name = os.path.basename(fbxPath)
            self.fbx_list_display.append(fbx_name)

    def select_path(self, *args):
        """选择保存路径"""
        # # fileMode=3 表示选择文件夹
        save_path = pc.fileDialog2(dialogStyle=2, fileMode=3)
        if save_path:
            self.savePath = save_path[0]
            pc.textField(self.path_field, e=True, text=self.savePath)

    def delete_connection(self, plug):
        """移除给出属性接口的链接（删除动画）"""
        if pc.connectionInfo(plug, isDestination=True):
            plug = pc.connectionInfo(plug, getExactDestination=True)
            readOnly = pc.ls(plug, readOnly=True)
            if readOnly:
                source = pc.connectionInfo(plug, sourceFromDestination=True)
                pc.disconnectAttr(source, plug)
            else:
                pc.delete(plug, inputConnectionsAndNodes=True)

    def reset_controllers(self):
        """删除动画并重置控制器位置"""
        self.all_ctrls = pc.PyNode("rig_controllers_grp").members()
        for ctrl in self.all_ctrls:
            keyable_attrs = pc.listAttr(ctrl, keyable=True)
            animatable_attrs = pc.listAnimatable(ctrl)
            for attr in animatable_attrs:
                self.delete_connection(f"{attr}")
            anim_utils.reset_selected_channels_value([ctrl], keyable_attrs)

    def setup_constraints(self):
        """创建传递动画骨骼并约束控制器"""
        pc.duplicate("skin:root")
        root_jnt = pc.PyNode("root")
        constraints = pc.ls(root_jnt, dag=True, type="constraint")
        pc.delete(constraints)
        # 约束控制器

        for joint, ctrl in SKELETON_TO_CONTROLLER_MAP.items():
            try:
                if pc.objExists(joint) and pc.objExists(ctrl):
                    pc.parentConstraint(joint, ctrl, mo=True)
                    logging.info(f"为骨骼 '{joint}' 和控制器 '{ctrl}' 创建约束。")
                else:
                    logging.warning(f"骨骼 '{joint}' 或控制器 '{ctrl}' 不存在。")
            except Exception as e:
                logging.error(f"Failed to constrain '{joint}' to '{ctrl}': {e}")
                pc.warning(f"约束失败: {joint} -> {ctrl}")

    def reset_rig(self) -> None:
        """将手臂和腿设置为 FK 模式"""
        for attr in FKIK_ATTRS:
            pc.setAttr(attr, 0)
        fps_val = pc.textField(self.PFS_field, q=True, text=True)
        pc.currentUnit(time=f"{fps_val}fps")  # 设置帧率为60fps
        # 设置时间滑块范围并在第0帧设置关键帧
        pc.env.setMinTime(0)
        pc.env.setMaxTime(1)
        pc.currentTime(0)
        pc.setKeyframe(self.all_ctrls)

    def confirm_dialog(self):
        confirm = pc.confirmDialog(
            title="Finish", message="Done!", button=["OK", "Open Folder"]
        )
        if confirm == "Open Folder" and self.savePath:
            os.startfile(self.savePath)

    def save_file(self, fbxPath):
        short_name = os.path.splitext(os.path.basename(fbxPath))[0]
        file_path = os.path.join(self.savePath, short_name + ".mb")
        logging.info(file_path)
        pc.saveAs(file_path, force=True)

    def _bake_fk_ik(self, first_frame, last_frame, arm=False, leg=False):
        for frame in range(first_frame, last_frame + 1):
            pc.currentTime(frame)
            for attr in FKIK_ATTRS:
                pc.setAttr(attr, 0)
            if arm:
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
            if leg:
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

    def match_ik(self):
        arm_select = self.arm_rbgrp.getSelect()
        leg_select = self.leg_rbgrp.getSelect()

        if arm_select == 2 and leg_select == 1:
            self._bake_fk_ik(self.first_frame, self.last_frame, arm=True, leg=False)
        elif leg_select == 2 and arm_select == 1:
            self._bake_fk_ik(self.first_frame, self.last_frame, arm=False, leg=True)
        elif arm_select == 2 and leg_select == 2:
            self._bake_fk_ik(self.first_frame, self.last_frame, arm=True, leg=True)
        else:
            logging.info("No valid FK/IK switch selected.")
            # 欧拉过滤器
        pc.filterCurve(self.all_ctrls, filter="euler")

    def bake_anim(self):
        time_value = pc.keyframe(
            "pelvis.rotateX", query=True, timeChange=True, absolute=True
        )
        # 设置当前动画时间范围
        self.first_frame = int(time_value[0])
        self.last_frame = int(time_value[-1])
        pc.env.setMinTime(self.first_frame)
        pc.env.setMaxTime(self.last_frame)
        # 烘焙动画
        bake_ctrls = list(SKELETON_TO_CONTROLLER_MAP.values())
        pc.select(bake_ctrls)
        pc.bakeResults(
            bake_ctrls,
            simulation=True,
            time=(self.first_frame, self.last_frame),
            shape=True,
        )
        pc.select(clear=True)
        # 删除传递骨骼
        pc.delete("root")

    def import_and_save(self, *args):
        """执行批量导入"""
        if not self.fbxList:
            logging.warning("Nothing To Import")
            return

        try:
            pc.progressWindow("progress_window", endProgress=True)
        except Exception as e:
            logging.warning(e)  # 如果没有窗口，则忽略错误
        # 创建可中断进度窗口
        pc.progressWindow(
            "progress_window",
            title="Importing Animatrion",
            isInterruptable=True,
            maxValue=len(self.fbxList),
            status="Starting...",
        )
        # 遍历所有选择的FBX文件
        for i, fbxPath in enumerate(self.fbxList):
            # 检查用户是否按下 Esc 键取消任务
            if pc.progressWindow("progress_window", query=True, isCancelled=True):
                logging.warning("任务已被用户取消")
                break
            pc.progressWindow(
                "progress_window",
                e=True,
                progress=i,
                status=f"Processing: {os.path.basename(fbxPath)}",
            )
            # 重置控制器位置
            self.reset_controllers()
            # 设置手臂和腿为FK
            self.reset_rig()
            # 设置约束
            self.setup_constraints()
            # 导入文件
            pc.importFile(fbxPath, defaultNamespace=True)
            # 通过"pelvis.rotateX"属性获取当前动画时间范围
            self.bake_anim()
            # 设置FKIK匹配
            self.match_ik()

            if self.savePath:
                self.save_file(fbxPath)
        try:
            pc.progressWindow("progress_window", endProgress=True)
        except Exception as e:
            logging.warning(e)  # 如果没有窗口，则忽略错误
        if self.savePath:
            self.confirm_dialog()


if __name__ == "__main__":
    advAnimToolsUI = AdvAnimToolsUI()
    advAnimToolsUI.create_ui()
