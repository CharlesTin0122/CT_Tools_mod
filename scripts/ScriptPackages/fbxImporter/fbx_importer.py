# -*- coding: utf-8 -*-
'''
@FileName      : fbx_importer_mgear.py
@DateTime      : 2023/09/18 17:22:33
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
'''
import os
import pymel.core as pm
from mgear.core import pyFBX
from mgear.core import anim_utils


class AdvAnimToolsUI:
    """项目用mGear绑定批量传递fbx动画到绑定控制器
    """
    def __init__(self):
        self.fbxList = []
        self.savePath = None
        self.fbx_field = None
        self.path_field = None
        self.all_ctrls = []

    def create_ui(self):
        """构建UI
        """
        try:
            pm.deleteUI('advTool')
        except Exception as e:
            print(e)

        with pm.window('advTool', title='advAnimtools') as win:
            with pm.columnLayout(rowSpacing=5, adj=True):
                with pm.frameLayout(label='Import multiple FBX'):
                    with pm.columnLayout(adj=1):
                        pm.button(label="Load All fbx", c=self.load)
                    with pm.scrollLayout(w=200, h=150, bgc=(0.5, 0.5, 0.5)) as self.fbx_field:
                        pm.text('fbx Name:')
                    with pm.rowLayout(numberOfColumns=3,
                                      columnWidth3=(55, 140, 5),
                                      adjustableColumn=2,
                                      columnAlign=(1, 'right'),
                                      columnAttach=[(1, 'both', 0), (2, 'both', 0), (3, 'both', 0)]
                                      ):
                        pm.text(label='Save Path:')
                        self.path_field = pm.textField("ImporterTextField")
                        pm.button(label='...', w=30, h=20, c=self.select_path)
                    with pm.columnLayout(adj=1):
                        pm.button(label="Import fbx And Save File !!!", c=self.import_and_save)

        pm.window(win, e=True, w=250, h=300)
        pm.showWindow(win)

    def load(self, *args):
        """载入导入fbx文件路径
        """
        self.fbxList = pm.fileDialog2(fileFilter="*fbx", fileMode=4)

        if not self.fbxList:
            pm.PopupError('Nothing Selected')
            self.fbxList = []
            return

        for fbxPath in self.fbxList:
            fbx_name = os.path.basename(fbxPath)
            with self.fbx_field:
                pm.text(label=fbx_name)

    def select_path(self, *args):
        """选择保存路径
        """
        save_path = pm.fileDialog2(fileFilter='*folder', fileMode=2)
        if save_path:
            self.savePath = save_path[0]
            pm.textField(self.path_field, e=True, text=self.savePath)

    def deleteConnection(self, plug):
        """
            移除给出属性接口的链接（删除动画）
            Parameters:
                plug (str): The plug to delete the connection for.
            Returns:
                None
        """
        # 如果接口是连接的目标，则返回 true，否则返回 false。参数isDestination：是连接目标
        if pm.connectionInfo(plug, isDestination=True):
            # 获取确切目标接口，如果没有这样的连接，则返回None。
            plug = pm.connectionInfo(plug, getExactDestination=True)
            readOnly = pm.ls(plug, readOnly=True)
            # 如果该属性为只读
            if readOnly:
                # 获取连接的源接口
                source = pm.connectionInfo(plug, sourceFromDestination=True)
                # 断开源接口和目标接口
                pm.disconnectAttr(source, plug)
            else:
                # 如果不为只读，则删除目标接口
                # inputConnectionsAndNodes: 如果目标接口为只读，则不会删除
                pm.delete(plug, inputConnectionsAndNodes=True)

    def import_and_save(self, *args):
        """执行批量导入
        """
        # 判断是否有导入文件
        if not self.fbxList:
            pm.PopupError('Nothing To Import')
            return

        all_ctrl_sets = pm.PyNode('rig_controllers_grp')
        self.all_ctrls = all_ctrl_sets.members()
        # 遍历导入文件
        for fbxPath in self.fbxList:
            # 删除动画并重置控制器位置
            for ctrl in self.all_ctrls:
                keyable_attrs = pm.listAttr(ctrl, keyable=True)
                animatable_attrs = pm.listAnimatable(ctrl)
                for attr in animatable_attrs:
                    self.deleteConnection(f"{attr}")
                anim_utils.reset_selected_channels_value([ctrl], keyable_attrs)

            # 设定帧率
            pm.currentUnit(time='ntsc')  # 30 fps
            pm.env.setMinTime(0)
            pm.env.setMaxTime(1)
            pm.currentTime(0)
            # 全部控制器尅帧
            pm.setKeyframe(self.all_ctrls)
            # 设置绑定手脚为FK模式
            fkik_attr = [
                "armUI_L0_ctl.arm_blend",
                "armUI_R0_ctl.arm_blend",
                "legUI_L0_ctl.leg_blend",
                "legUI_R0_ctl.leg_blend"
            ]
            for a in fkik_attr:
                pm.setAttr(a, 0)

            # 创建传递动画骨骼并约束控制器
            pm.duplicate("skin:root")
            root_jnt = pm.PyNode("root")
            constarins = pm.ls(root_jnt, dag=True, type="constraint")  # 列出骨骼链的所有约束节点，注意参数dag
            pm.delete(constarins)

            pm.parentConstraint("root", "root_main_C0_ctl", mo=True)
            pm.parentConstraint("pelvis", "body_C0_ctl", mo=True)
            pm.parentConstraint("Weapon_L", "Weapon_L_L0_ctl", mo=True)
            pm.parentConstraint("Weapon_R", "Weapon_R_R0_ctl", mo=True)

            joint_sl = [
                "spine_01", "spine_02", "spine_03", "neck_01", "head",
                "clavicle_l", "upperarm_l", "lowerarm_l", "hand_l",
                "thumb_01_l", "thumb_02_l", "thumb_03_l",
                "index_01_l", "index_02_l", "index_03_l",
                "middle_01_l", "middle_02_l", "middle_03_l",
                "ring_01_l", "ring_02_l", "ring_03_l",
                "pinky_01_l", "pinky_02_l", "pinky_03_l",
                "clavicle_r", "upperarm_r", "lowerarm_r", "hand_r",
                "thumb_01_r", "thumb_02_r", "thumb_03_r",
                "index_01_r", "index_02_r", "index_03_r",
                "middle_01_r", "middle_02_r", "middle_03_r",
                "ring_01_r", "ring_02_r", "ring_03_r",
                "pinky_01_r", "pinky_02_r", "pinky_03_r",
                "thigh_l", "calf_l", "foot_l", "ball_l",
                "thigh_r", "calf_r", "foot_r", "ball_r"
            ]

            ctrl_sl = [
                "spine_C0_fk0_ctl", "spine_C0_fk1_ctl", "spine_C0_fk2_ctl", "neck_C0_fk0_ctl", "neck_C0_head_ctl",
                "clavicle_L0_ctl", "arm_L0_fk0_ctl", "arm_L0_fk1_ctl", "arm_L0_fk2_ctl",
                "thumb_L0_fk0_ctl", "thumb_L0_fk1_ctl", "thumb_L0_fk2_ctl",
                "index_L0_fk0_ctl", "index_L0_fk1_ctl", "index_L0_fk2_ctl",
                "middle_L0_fk0_ctl", "middle_L0_fk1_ctl", "middle_L0_fk2_ctl",
                "ring_L0_fk0_ctl", "ring_L0_fk1_ctl", "ring_L0_fk2_ctl",
                "pinky_L0_fk0_ctl", "pinky_L0_fk1_ctl", "pinky_L0_fk2_ctl",
                "clavicle_R0_ctl", "arm_R0_fk0_ctl", "arm_R0_fk1_ctl", "arm_R0_fk2_ctl",
                "thumb_R0_fk0_ctl", "thumb_R0_fk1_ctl", "thumb_R0_fk2_ctl",
                "index_R0_fk0_ctl", "index_R0_fk1_ctl", "index_R0_fk2_ctl",
                "middle_R0_fk0_ctl", "middle_R0_fk1_ctl", "middle_R0_fk2_ctl",
                "ring_R0_fk0_ctl", "ring_R0_fk1_ctl", "ring_R0_fk2_ctl",
                "pinky_R0_fk0_ctl", "pinky_R0_fk1_ctl", "pinky_R0_fk2_ctl",
                "leg_L0_fk0_ctl", "leg_L0_fk1_ctl", "leg_L0_fk2_ctl", "foot_L0_fk0_ctl",
                "leg_R0_fk0_ctl", "leg_R0_fk1_ctl", "leg_R0_fk2_ctl", "foot_R0_fk0_ctl"
            ]

            for i in range(len(joint_sl)):
                pm.parentConstraint(joint_sl[i], ctrl_sl[i], mo=True, skipTranslate=["x", "y", "z"])
            # 通过使用fbxSDK移除fbx文件中的namespace
            fbx_file = pyFBX.FBX_Class(fbxPath)
            try:
                fbx_file.remove_namespace()
                fbx_file.save()
            except Exception as e:
                print(e)
            # 执行导入文件
            pm.importFile(fbxPath)
            # 确定时间范围
            time_value = pm.keyframe("pelvis.rotateX", query=True, timeChange=True, absolute=True)
            first_frame = int(time_value[0])
            last_frame = int(time_value[-1])
            pm.env.setMinTime(first_frame)
            pm.env.setMaxTime(last_frame)
            # 烘焙动画
            ctrl_bk = [
                "root_main_C0_ctl", "root_C0_ctl", "body_C0_ctl",
                "spine_C0_fk0_ctl", "spine_C0_fk1_ctl", "spine_C0_fk2_ctl", "neck_C0_fk0_ctl", "neck_C0_head_ctl",
                "clavicle_L0_ctl", "arm_L0_fk0_ctl", "arm_L0_fk1_ctl", "arm_L0_fk2_ctl", "Weapon_L_L0_ctl",
                "thumb_L0_fk0_ctl", "thumb_L0_fk1_ctl", "thumb_L0_fk2_ctl",
                "index_L0_fk0_ctl", "index_L0_fk1_ctl", "index_L0_fk2_ctl",
                "middle_L0_fk0_ctl", "middle_L0_fk1_ctl", "middle_L0_fk2_ctl",
                "ring_L0_fk0_ctl", "ring_L0_fk1_ctl", "ring_L0_fk2_ctl",
                "pinky_L0_fk0_ctl", "pinky_L0_fk1_ctl", "pinky_L0_fk2_ctl",
                "clavicle_R0_ctl", "arm_R0_fk0_ctl", "arm_R0_fk1_ctl", "arm_R0_fk2_ctl", "Weapon_R_R0_ctl",
                "thumb_R0_fk0_ctl", "thumb_R0_fk1_ctl", "thumb_R0_fk2_ctl",
                "index_R0_fk0_ctl", "index_R0_fk1_ctl", "index_R0_fk2_ctl",
                "middle_R0_fk0_ctl", "middle_R0_fk1_ctl", "middle_R0_fk2_ctl",
                "ring_R0_fk0_ctl", "ring_R0_fk1_ctl", "ring_R0_fk2_ctl",
                "pinky_R0_fk0_ctl", "pinky_R0_fk1_ctl", "pinky_R0_fk2_ctl",
                "leg_L0_fk0_ctl", "leg_L0_fk1_ctl", "leg_L0_fk2_ctl", "foot_L0_fk0_ctl",
                "leg_R0_fk0_ctl", "leg_R0_fk1_ctl", "leg_R0_fk2_ctl", "foot_R0_fk0_ctl"
            ]
            pm.bakeResults(ctrl_bk, simulation=True, time=(first_frame, last_frame), sampleBy=1, oversamplingRate=1,
                           disableImplicitControl=True, preserveOutsideKeys=True, sparseAnimCurveBake=False,
                           removeBakedAttributeFromLayer=False, removeBakedAnimFromLayer=False,
                           bakeOnOverrideLayer=False, minimizeRotation=True, controlPoints=False, shape=True)
            # 删除传递动画骨骼
            pm.delete('root')
            # 烘焙手脚为动画为IK（以修正手肘膝盖旋转错误）
            for frame in range(int(first_frame), int(last_frame) + 1):
                # 设置当前帧设置为FK
                pm.currentTime(frame)
                for a in fkik_attr:
                    pm.setAttr(a, 0)
                # 将FK匹配到IK
                anim_utils.ikFkMatch(
                    "rig",
                    "arm_blend",
                    "armUI_R0_ctl",
                    ["arm_R0_fk0_ctl", "arm_R0_fk1_ctl", "arm_R0_fk2_ctl"],
                    "arm_R0_ik_ctl",
                    "arm_R0_upv_ctl"
                )
                anim_utils.ikFkMatch(
                    "rig",
                    "arm_blend",
                    "armUI_L0_ctl",
                    ["arm_L0_fk0_ctl", "arm_L0_fk1_ctl", "arm_L0_fk2_ctl"],
                    "arm_L0_ik_ctl",
                    "arm_L0_upv_ctl"
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
            # 欧拉过滤
            ctrl_grp = pm.PyNode("rig_controllers_grp")
            all_ctrls = ctrl_grp.members()
            pm.filterCurve(all_ctrls)
            # 保存文件
            if self.savePath:
                short_name = os.path.splitext(os.path.basename(fbxPath))[0]
                file_path = os.path.join(self.savePath, short_name + ".mb")
                print(file_path)
                pm.saveAs(file_path, force=True)

        if self.savePath:
            confirm = pm.confirmDialog(title='Finish', message="Done!", button=['OK', 'Open Folder'])
            if confirm == 'Open Folder' and self.savePath:
                os.startfile(self.savePath)


if __name__ == '__main__':
    advAnimToolsUI = AdvAnimToolsUI()
    advAnimToolsUI.create_ui()
