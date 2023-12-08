# -*- coding: utf-8 -*-
"""
@FileName      : pose_tools.py
@DateTime      : 2023/10/25 17:57:12
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
@Description   :
"""
import json
import os
import pymel.core as pm


class PoseToolsUI:
    def __init__(self):
        self.sel_list = []
        self.attr = []
        self.attrVal = []
        self.data = {}

        self.world_matrix_list = []

        self.ctrl_loc_list = []
        self.ctrl_con_list = []

        self.template = pm.uiTemplate("cpTemplate", force=True)
        self.template.define(pm.button, width=200, height=30, align="right")
        self.template.define(pm.frameLayout, borderVisible=True, labelVisible=False)
        self.createUI()

    def createUI(self):
        try:
            pm.deleteUI("cpWindow")
        except Exception as e:
            print(e)

        with pm.window("cpWindow", menuBarVisible=True, title="CopyNPastPose"):
            with self.template:
                with pm.columnLayout(rowSpacing=5, adj=1):
                    with pm.frameLayout():
                        with pm.columnLayout(adj=1):
                            pm.button(label="Copy Pose", c=self.copyPose)
                            pm.button(label="Paste Pose", c=self.pastePose)
                            pm.button(label="Paste Mirror Pose", c=self.pasteMirPose)
                            pm.separator(height=10)
                            pm.button(label="Mirror Animation", c=self.mirror_anim)
                            pm.separator(height=10)
                            pm.button(label="Get World Matrix", c=self.get_world_matrix)
                            pm.button(
                                label="Set World Matrix Range",
                                c=self.set_world_matrix_range,
                            )
                            pm.separator(height=10)
                            pm.button(label="Pin Ctrl Anim", c=self.pin_ctrl_anim)
                            pm.button(label="Bake Pined Anim", c=self.bake_pined_anim)

    # TODO :引入Jason文件
    def write_json(self):
        """将导出信息写入json文件"""
        self.anim_data = {
            "sel_list": self.sel_list,
            "anim_data": self.data,
            "world_matrix_list": self.world_matrix_list,
        }
        current_path = rf"{os.path.dirname(__file__)}"
        json_file = os.path.join(current_path, "anim_data.json")
        with open(json_file, "w") as d:
            json.dump(self.anim_data, d, indent=4)

    def copyPose(self):
        """复制选定对象的动画属性"""
        sel_list = pm.selected()  # 获取选中的对象列表
        attr_list = [obj.listAnimatable() for obj in sel_list]  # 获取每个对象的属性列表
        # 遍历属性列表中的每个属性
        self.attr = []
        for attrs in attr_list:
            for attr in attrs:
                sttr_str = str(attr)
                self.attr.append(sttr_str)

        self.attrVal = [pm.getAttr(s) for s in self.attr]

        zip_list = zip(self.attr, self.attrVal)
        self.data = dict(zip_list)

    def pastePose(self):
        """粘贴选定对象的动画属性"""
        for key, value in self.data.items():
            pm.setAttr(key, value)

    def pasteMirPose(self):
        """镜像粘贴选定对象的动画属性"""
        mir_list = []
        for a in self.attr:
            if "_L" in a:
                mir = a.replace("_L", "_R")
            elif "_R" in a:
                mir = a.replace("_R", "_L")
            else:
                mir = a
            mir_list.append(mir)

        mir_zip_list = zip(mir_list, self.attrVal)
        mir_data = dict(mir_zip_list)

        for key, value in mir_data.items():
            if ("leg" in key and "ik" in key) and (
                "translateX" in key or "rotateY" in key or "rotateZ" in key
            ):
                pm.setAttr(key, value * -1)
            elif ("_C" in key) and (
                "translateX" in key or "rotateY" in key or "rotateZ" in key
            ):
                pm.setAttr(key, value * -1)
            else:
                pm.setAttr(key, value)

    def mirror_anim(self):
        """镜像整段动画"""
        first_frame = pm.env.getMinTime()
        last_frame = pm.env.getMaxTime()
        for frame in range(int(first_frame), int(last_frame) + 1):
            pm.currentTime(frame)
            self.copyPose()
            self.pasteMirPose()

    def get_world_matrix(self):
        """获取选定对象的世界矩阵"""
        self.sel_list = pm.selected()
        self.world_matrix_list = [
            obj.getMatrix(worldSpace=True) for obj in self.sel_list
        ]

    def set_world_matrix_range(self):
        """在选定帧范围内设置对象的世界矩阵，主要用来定脚"""
        aTimeSlider = pm.mel.eval("$tmpVar=$gPlayBackSlider")  # 获取时间栏组件
        timeRange = pm.timeControl(aTimeSlider, q=True, rangeArray=True)  # 获取选定时间范围
        # 遍历所有帧并设置获取的世界矩阵
        for frame in range(int(timeRange[0]), int(timeRange[1])):
            pm.currentTime(frame)
            for i, obj in enumerate(self.sel_list):
                obj.setMatrix(self.world_matrix_list[i], worldSpace=True)
                pm.setKeyframe(obj)

    def pin_ctrl_anim(self):
        """为选定的控制器生成pin控制动画
        原理：
        1. 为每个控制器创建一个空间定位器.
        2. 控制器约束定位器，并烘焙定位器动画，便将控制器的动画传递到定位器上.
        3. 删除约束节点.
        4. 反过来,定位器约束控制器,控制器便被Pin住了.
        5. 这样便可以在不破坏身体动画的前提下修改main和root控制器,一般用来处理根骨骼动画
        """
        self.sel_list = pm.selected()
        self.ctrl_loc_list = []
        self.ctrl_con_list = []
        for ctrl in self.sel_list:
            ctrl_loc = pm.spaceLocator(n=f"{ctrl}_loc")
            self.ctrl_loc_list.append(ctrl_loc)
            ctrl_cons = pm.parentConstraint(ctrl, ctrl_loc, mo=False)
            self.ctrl_con_list.append(ctrl_cons)
        pm.bakeResults(
            self.ctrl_loc_list,
            simulation=True,
            t=(pm.env.getMinTime(), pm.env.getMaxTime()),
            sampleBy=1,
        )
        pm.delete(self.ctrl_con_list)
        for i, ctrl in enumerate(self.sel_list):
            pm.parentConstraint(self.ctrl_loc_list[i], ctrl, mo=True)

    def bake_pined_anim(self):
        """烘焙控制器动画，并删除空间定位器"""
        pm.bakeResults(
            self.sel_list,
            simulation=True,
            t=(pm.env.getMinTime(), pm.env.getMaxTime()),
            sampleBy=1,
        )
        pm.delete(self.ctrl_loc_list)


# Create an instance of the CopyNPastePoseUI class to run the script
ui = PoseToolsUI()
