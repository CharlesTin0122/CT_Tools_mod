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
from functools import partial
import pymel.core as pc


class RootMotionToolsUI:
    def __init__(self):
        self.window_name = "RootMotionToolsWindow"
        self.window_title = "根动画工具 (Root Motion Tools)"

        self.root_ctrl_name: str = None
        self.pelvis_ctrl_name: str = None

        self.ik_ctrls_list: list = []
        self.ctrl_loc_list: list = []

        self.root_motion_tx: bool = None
        self.root_motion_ty: bool = None
        self.root_motion_tz: bool = None

        self.root_motion_rx: bool = None
        self.root_motion_ry: bool = None
        self.root_motion_rz: bool = None

        if pc.window(self.window_name, exists=True):
            try:
                pc.deleteUI(self.window_name)
            except Exception as e:
                print(e)

        self.window = pc.window(
            self.window_name, title=self.window_title, sizeable=True, menuBar=True
        )

        # --- 主布局 ---
        self.main_layout = pc.columnLayout(adj=True, rs=5, cal="center")
        # 根控制器名称
        pc.rowLayout(numberOfColumns=3)
        pc.text(label="根控制器名称: ")
        self.root_ctrl_field = pc.textField()
        pc.button(
            label="...",
            w=30,
            h=20,
            command=partial(self.select_object_cmd, self.root_ctrl_field),
            ann="选择根控制器",
        )
        # 返回上级控件
        pc.setParent("..")
        # 骨盆控制器名称
        pc.rowLayout(numberOfColumns=3)
        pc.text(label="骨盆控制器名称: ")
        self.pelvis_ctrl_field = pc.textField()
        pc.button(
            label="...",
            w=30,
            h=20,
            command=partial(self.select_object_cmd, self.pelvis_ctrl_field),
            ann="选择骨盆控制器",
        )
        pc.setParent("..")
        # IK控制器列表
        pc.columnLayout(adj=True, rs=5, cal="center")
        pc.text(label="IK控制器列表:")
        self.ik_ctrls_list = pc.textScrollList(allowMultiSelection=True)
        pc.button(
            label="选择IK控制器",
            command=partial(self.select_objects_cmd, self.ik_ctrls_list),
            ann="选择IK控制器",
        )
        pc.setParent("..")
        # 根动画属性
        pc.columnLayout(adj=True, rs=5, cal="center")
        pc.text(label="根动画属性:")
        pc.checkBoxGrp(
            numberOfCheckBoxes=3,
            label="根动画平移属性",
            labelArray6=["X", "Y", "Z"],
        )
        pc.checkBoxGrp(
            numberOfCheckBoxes=3,
            label="根动画旋转属性",
            labelArray6=["X", "Y", "Z"],
        )
        # 按钮布局
        pc.rowLayout(numberOfColumns=2, adjustableColumn=1)
        pc.button(label="应用根动画", command=self.apply_root_motion)

        self.window.show()

    def select_object_cmd(self, text_field):
        """选择对象并将其名称设置到文本字段中."""
        selected_objects = pc.ls(selection=True)
        if selected_objects:
            text_field.setText(selected_objects[0])
        else:
            pc.warning("请先选择一个对象。")

    def select_objects_cmd(self, text_scroll_list):
        """选择多个对象并将其名称添加到文本滚动列表中."""
        selected_objects = pc.ls(selection=True)
        if selected_objects:
            for obj in selected_objects:
                text_scroll_list.append(obj)
        else:
            pc.warning("请先选择一个或多个对象。")

    def get_unique_name(self, base_name):
        """在场景中生成一个唯一的名称."""
        name = base_name
        counter = 1
        while pc.objExists(name):
            name = f"{base_name}_{counter}"
            counter += 1
        return name

    def pin_ctrl_anim(self, ctrl_list=None):
        """为选定的控制器生成pin控制动画
        原理：
        1. 为每个控制器创建一个空间定位器.
        2. 控制器约束定位器，并烘焙定位器动画，便将控制器的动画传递到定位器上.
        3. 删除约束节点.
        4. 反过来,定位器约束控制器,控制器便被Pin住了.
        5. 这样便可以在不破坏身体动画的前提下修改main和root控制器,一般用来处理根骨骼动画
        """
        global ctrl_loc_list
        if ctrl_list is None:
            ctrl_list = pc.selected()
        sel_list = ctrl_list
        ctrl_loc_list = []
        ctrl_con_list = []
        for ctrl in sel_list:
            ctrl_loc = pc.spaceLocator(n=f"{ctrl}_loc")
            ctrl_loc_list.append(ctrl_loc)
            ctrl_cons = pc.parentConstraint(ctrl, ctrl_loc, mo=False)
            ctrl_con_list.append(ctrl_cons)
        pc.bakeResults(
            ctrl_loc_list,
            simulation=True,
            t=(pc.env.getMinTime(), pc.env.getMaxTime()),
            sampleBy=1,
        )
        pc.delete(ctrl_con_list)
        for i, ctrl in enumerate(sel_list):
            pc.parentConstraint(ctrl_loc_list[i], ctrl, mo=True)

    def bake_pined_anim(self, ctrl_list=None):
        """烘焙控制器动画，并删除空间定位器"""
        pc.bakeResults(
            ctrl_list,
            simulation=True,
            t=(pc.env.getMinTime(), pc.env.getMaxTime()),
            sampleBy=1,
        )
        pc.delete(ctrl_loc_list)

    def Inplace_to_RootMotion(self, root_ctrl, pelvis_ctrl, ik_ctrls=None):
        """
        在maya中转换原地动画为根动画.

        Args:
                        root_name (str): 根骨骼名称.
                        pelvis_name (str): 胯骨骼名称

        Raises:
                        ValueError: 如果对象不存在.
        """
        # 验证输入参数
        if not pc.objExists(root_ctrl):
            raise ValueError(f"Root bone '{root_ctrl}' does not exist in the scene.")
        if not pc.objExists(pelvis_ctrl):
            raise ValueError(
                f"Pelvis bone '{pelvis_ctrl}' does not exist in the scene."
            )

        # 获取动画时间范围
        firstFrame = math.floor(pc.findKeyframe(pelvis_ctrl, which="first"))
        lastFrame = math.ceil(pc.findKeyframe(pelvis_ctrl, which="last"))
        pc.currentTime(firstFrame)
        # 用唯一的名称创建定位器
        loc_root = pc.spaceLocator(name=self.get_unique_name("loc_root"))
        loc_pelvis = pc.spaceLocator(name=self.get_unique_name("loc_pelvis"))

        try:
            # 控制器约束定位器
            loc_root_constr = pc.parentConstraint(root_ctrl, loc_root)
            loc_pelvis_constr = pc.parentConstraint(pelvis_ctrl, loc_pelvis)

            # 烘焙定位器动画
            pc.bakeResults(
                loc_root,
                loc_pelvis,
                time=(firstFrame, lastFrame),
                sparseAnimCurveBake=True,
            )

            # 删除约束节点
            pc.delete(loc_root_constr, loc_pelvis_constr)
            # 钉住pelvis控制器和IK控制器
            self.pin_ctrl_anim([pelvis_ctrl] + (ik_ctrls or []))

            # 胯定位器分别用点约束和方向约束约束根定位器
            loc_point_contr = pc.pointConstraint(
                loc_pelvis, loc_root, maintainOffset=True
            )
            loc_orient_contr = pc.orientConstraint(
                loc_pelvis, loc_root, maintainOffset=True
            )

            # 烘焙动画
            pc.bakeResults(
                loc_root,
                time=(firstFrame, lastFrame),
                sparseAnimCurveBake=True,
                minimizeRotation=True,
            )
            # 删除约束节点
            pc.delete(loc_point_contr, loc_orient_contr)

            # 执行欧拉过滤器防止跳变
            pc.filterCurve(loc_root, filter="euler")
            # 根据根动画所需属性修改跟定位器动画
            if not self.root_motion_tx:
                loc_root.translateX.disconnect()
                pc.setKeyframe(loc_root.translateX)
            if not self.root_motion_ty:
                loc_root.translateY.disconnect()
                pc.setKeyframe(loc_root.translateY)
            if not self.root_motion_tz:
                loc_root.translateZ.disconnect()
                pc.setKeyframe(loc_root.translateZ)
            if not self.root_motion_rx:
                loc_root.rotateX.disconnect()
                pc.setKeyframe(loc_root.rotateX)
            if not self.root_motion_ry:
                loc_root.rotateY.disconnect()
                pc.setKeyframe(loc_root.rotateY)
            if not self.root_motion_rz:
                loc_root.rotateZ.disconnect()
                pc.setKeyframe(loc_root.rotateZ)

            # 定位器约束骨骼
            jnt_root_constr = pc.parentConstraint(loc_root, root_ctrl)

            # 烘焙最终动画到骨骼
            pc.bakeResults(
                root_ctrl,
                time=(firstFrame, lastFrame),
                sparseAnimCurveBake=True,
            )
            # 删除约束节点
            pc.delete(jnt_root_constr)
            self.bake_pined_anim([pelvis_ctrl] + (ik_ctrls or []))
            # 执行欧拉过滤器
            pc.filterCurve(root_ctrl, filter="euler")
        finally:
            # 清理定位器
            pc.delete([obj for obj in [loc_root, loc_pelvis] if pc.objExists(obj)])

    # TODO : 根动画转换为原地动画
    def RootMotion_to_Inplace(self, root_ctrl, pelvis_ctrl, ik_ctrls=None):
        # 验证输入参数
        if not pc.objExists(root_ctrl):
            raise ValueError(f"Root bone '{root_ctrl}' does not exist in the scene.")
        if not pc.objExists(pelvis_ctrl):
            raise ValueError(
                f"Pelvis bone '{pelvis_ctrl}' does not exist in the scene."
            )
        # 获取动画时间范围
        firstFrame = math.floor(pc.findKeyframe(pelvis_ctrl, which="first"))
        lastFrame = math.ceil(pc.findKeyframe(pelvis_ctrl, which="last"))
        pc.currentTime(firstFrame)
        # 用唯一的名称创建定位器
        locPelvis = pc.spaceLocator(name=self.get_unique_name("locPelvis"))
        loc_list = []
        for ctrl in ik_ctrls or []:
            locFoot = pc.spaceLocator(name=self.get_unique_name(f"loc{ctrl}_Foot"))
            loc_list.append(locFoot)

        # 控制器约束定位器
        pelvis_constr = pc.parentConstraint(pelvis_ctrl, locPelvis)
        ik_ctrl_constrs = []
        for ctrl in ik_ctrls or []:
            ik_ctrl_constr = pc.parentConstraint(ctrl, loc_list)
            ik_ctrl_constrs.append(ik_ctrl_constr)

        # 烘焙定位器动画
        pc.bakeResults((locPelvis + loc_list), time=(firstFrame, lastFrame))
        pc.delete(pelvis_constr, ik_ctrl_constrs)
        # 定位器约束控制器
        pelvis_constr = pc.parentConstraint(locPelvis, root_ctrl)
        loc_ctrl_constr_list = []
        for ctrl in ik_ctrls or []:
            ik_ctrl_constr = pc.parentConstraint(loc_list, ctrl)
            loc_ctrl_constr_list.append(ik_ctrl_constr)

        # 列出需要断开连接的根骨骼属性
        Attrs = [
            f"{root_ctrl}.tx",
            f"{root_ctrl}.ty",
            f"{root_ctrl}.tz",
            f"{root_ctrl}.rx",
            f"{root_ctrl}.ry",
            f"{root_ctrl}.rz",
        ]
        # 断开连接并设置为0
        for attr in Attrs:
            attr.disconnect()
            attr.set(0)
            pc.setKeyframe(attr)
        # 烘焙动画到控制器
        pc.bakeResults(pelvis_ctrl + loc_ctrl_constr_list, time=(firstFrame, lastFrame))
        # 清理场景
        pc.delete(pelvis_constr, loc_ctrl_constr_list, locPelvis, loc_list)


# --- 用于启动UI的函数 ---
def show_root_motion_tools_ui():
    RootMotionToolsUI


# --- 如果直接运行此脚本，显示UI ---
if __name__ == "__main__":
    show_root_motion_tools_ui()
