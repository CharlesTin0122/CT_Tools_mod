# -*- coding: utf-8 -*-
'''
@FileName      : pose_tools.py
@DateTime      : 2023/10/25 17:57:12
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7
@Description   :
'''
import pymel.core as pm


class PoseToolsUI:
    def __init__(self):
        self.attr = []
        self.attrVal = []
        self.data = {}
        self.template = pm.uiTemplate('cpTemplate', force=True)
        self.template.define(pm.button, width=200, height=30, align='right')
        self.template.define(pm.frameLayout, borderVisible=True, labelVisible=False)
        self.createUI()

    def createUI(self):
        try:
            pm.deleteUI('cpWindow')
        except Exception as e:
            print(e)

        with pm.window('cpWindow', menuBarVisible=True, title='CopyNPastPose') as win:
            with self.template:
                with pm.columnLayout(rowSpacing=5, adj=1):
                    with pm.frameLayout():
                        with pm.columnLayout(adj=1):
                            pm.button(label='Copy Pose', c=self.copyPose)
                            pm.button(label='Paste Pose', c=self.pastePose)
                            pm.button(label='Paste Mirror Pose', c=self.pasteMirPose)
                            pm.button(label="Mirror Animation", c=self.mirror_anim)
        pm.showWindow(win)

    def copyPose(self, *args):
        sel_obj = pm.selected()  # 获取选中的对象列表
        attr_list = [obj.listAnimatable() for obj in sel_obj]  # 获取每个对象的属性列表
        # 遍历属性列表中的每个属性
        for attrs in attr_list:
            for attr in attrs:
                sttr_str = str(attr)
                self.attr.append(sttr_str)

        self.attrVal = [pm.getAttr(s) for s in self.attr]

        zip_list = zip(self.attr, self.attrVal)
        self.data = dict(zip_list)

    def pastePose(self, *args):
        for key, value in self.data.items():
            pm.setAttr(key, value)

    def pasteMirPose(self, *args):
        mir_list = []
        for a in self.attr:
            if '_L' in a:
                mir = a.replace('_L', '_R')
            elif '_R' in a:
                mir = a.replace('_R', '_L')
            else:
                mir = a
            mir_list.append(mir)

        mir_zip_list = zip(mir_list, self.attrVal)
        mir_data = dict(mir_zip_list)

        for key, value in mir_data.items():
            if ('leg' in key and 'ik' in key) and ('translateX' in key or 'rotateY' in key or 'rotateZ' in key):
                pm.setAttr(key, value * -1)
            elif ('_C' in key) and ('translateX' in key or 'rotateY' in key or 'rotateZ' in key):
                pm.setAttr(key, value * -1)
            else:
                pm.setAttr(key, value)

    def mirror_anim(self, *args):
        first_frame = pm.env.getMinTime()
        last_frame = pm.env.getMaxTime()
        for frame in range(int(first_frame), int(last_frame)+1):
            pm.currentTime(frame)
            self.copyPose()
            self.pasteMirPose()


# Create an instance of the CopyNPastePoseUI class to run the script
ui = PoseToolsUI()
