# -*- encoding: utf-8 -*-
"""
@File    :   root_motion_tool_01.py
@Time    :   2025/05/27 18:01:03
@Author  :   Charles Tian
@Version :   1.1
@Contact :   tianchao0533@gmail.com
@Desc    :   A Maya tool for converting animations between in-place and root motion.
"""

import math
from functools import partial
import pymel.core as pc


class RootMotionToolsUI:
    def __init__(self):
        self.window_name = "RootMotionToolsWindow"
        self.window_title = "根动画工具 (Root Motion Tools) v1.1"

        # --- Instance Variables for Controllers and UI Elements ---
        self.root_ctrl_name: str = None
        self.pelvis_ctrl_name: str = None
        self.ik_ctrl_names_from_ui: list = []  # Store IK controller names from UI

        self.ctrl_loc_list: list = []  # CORRECTED: Was managed globally, now an instance variable

        # --- Instance Variables for Root Motion Attributes (to be set from UI) ---
        self.root_motion_tx: bool = True  # Default to True
        self.root_motion_ty: bool = True
        self.root_motion_tz: bool = True
        self.root_motion_rx: bool = False
        self.root_motion_ry: bool = True  # Typically Y-axis rotation is root motion
        self.root_motion_rz: bool = False

        if pc.window(self.window_name, exists=True):
            try:
                pc.deleteUI(self.window_name)
            except Exception as e:
                pc.warning(f"Could not delete existing UI window: {e}")

        self.window = pc.window(
            self.window_name, title=self.window_title, sizeable=True, menuBar=True
        )

        # --- Main Layout ---
        self.main_layout = pc.columnLayout(adj=True, rs=5, cal="center")

        # --- Root Controller ---
        pc.rowLayout(numberOfColumns=3, adjustableColumn=2)
        pc.text(label="根控制器 (Root): ")
        self.root_ctrl_field = pc.textField(
            tx="Root_CTRL", ann="根控制器名称 (例如: Root_CTRL)"
        )  # ADDED: Default example
        pc.button(
            label="<<",  # CORRECTED: Standard "get from selection" label
            w=30,
            h=20,
            command=partial(self.select_object_cmd, self.root_ctrl_field),
            ann="从场景选择中获取根控制器",
        )
        pc.setParent("..")

        # --- Pelvis Controller ---
        pc.rowLayout(numberOfColumns=3, adjustableColumn=2)
        pc.text(label="骨盆控制器 (Pelvis): ")
        self.pelvis_ctrl_field = pc.textField(
            tx="Pelvis_CTRL", ann="骨盆控制器名称 (例如: Pelvis_CTRL)"
        )  # ADDED: Default example
        pc.button(
            label="<<",
            w=30,
            h=20,
            command=partial(self.select_object_cmd, self.pelvis_ctrl_field),
            ann="从场景选择中获取骨盆控制器",
        )
        pc.setParent("..")

        # --- IK Controllers List ---
        pc.frameLayout(
            label="IK 控制器列表 (IK Controllers)",
            collapsable=True,
            cl=False,
            mw=5,
            mh=5,
        )
        pc.columnLayout(adj=True, rs=5)
        self.ik_ctrls_text_scroll_list = pc.textScrollList(
            allowMultiSelection=True, h=80
        )
        pc.rowLayout(numberOfColumns=3, adjustableColumn=1)
        pc.button(
            label="添加选中 (Add Selected)",
            command=partial(
                self.add_selected_to_scroll_list_cmd, self.ik_ctrls_text_scroll_list
            ),
            ann="添加选中的IK控制器到列表",
        )
        pc.button(
            label="移除选中 (Remove)",
            command=partial(
                self.remove_selected_from_scroll_list_cmd,
                self.ik_ctrls_text_scroll_list,
            ),
            ann="从列表中移除选中的IK控制器",
        )
        pc.button(
            label="清空 (Clear)",
            command=partial(self.clear_scroll_list_cmd, self.ik_ctrls_text_scroll_list),
            ann="清空IK控制器列表",
        )
        pc.setParent("..")  # End rowLayout
        pc.setParent("..")  # End columnLayout
        pc.setParent("..")  # End frameLayout

        # --- Root Motion Attributes ---
        pc.frameLayout(
            label="根动画属性 (Root Motion Attributes)",
            collapsable=True,
            cl=False,
            mw=5,
            mh=5,
        )
        pc.columnLayout(adj=True, rs=3)
        # CORRECTED: Storing checkbox groups and using labelArray3
        self.translate_cb_grp = pc.checkBoxGrp(
            numberOfCheckBoxes=3,
            label="平移 (Translate):",
            labelArray3=["X", "Y", "Z"],
            valueArray3=[
                self.root_motion_tx,
                self.root_motion_ty,
                self.root_motion_tz,
            ],  # ADDED: Initial values
        )
        self.rotate_cb_grp = pc.checkBoxGrp(
            numberOfCheckBoxes=3,
            label="旋转 (Rotate):",
            labelArray3=["X", "Y", "Z"],
            valueArray3=[
                self.root_motion_rx,
                self.root_motion_ry,
                self.root_motion_rz,
            ],  # ADDED: Initial values
        )
        pc.setParent("..")  # End columnLayout for checkboxes
        pc.setParent("..")  # End frameLayout for attributes

        # --- Action Buttons ---
        pc.separator(h=10, style="in")
        pc.rowLayout(
            numberOfColumns=2,
            adjustableColumn=1,
            columnAttach=[(1, "both", 5), (2, "both", 5)],
            cat=[(1, "both", 0), (2, "both", 0)],
        )
        pc.button(
            label="原地 -> 根动画 (In-place to Root Motion)",
            command=self.apply_inplace_to_root_motion_cmd,
            h=30,
            ann="将原地动画转换为根动画",
        )
        pc.button(
            label="根动画 -> 原地 (Root Motion to In-place)",
            command=self.apply_root_motion_to_inplace_cmd,
            h=30,
            ann="将根动画转换为原地动画",
        )
        pc.setParent("..")

        pc.separator(h=10, style="in")
        pc.text(
            label="作者: Charles Tian | tianchao0533@gmail.com",
            align="center",
            font="smallObliqueLabelFont",
        )

        pc.setParent("..")  # Back to main_layout

        self.window.show()

    def _get_selected_object_name(self):
        """Helper to get the first selected object's name."""
        selected_objects = pc.ls(selection=True, type="transform")
        if selected_objects:
            return selected_objects[0].name()
        return None

    def select_object_cmd(self, text_field, *args):
        """Selects an object and sets its name to the text field."""
        obj_name = self._get_selected_object_name()
        if obj_name:
            text_field.setText(obj_name)
        else:
            pc.warning("请先选择一个对象 (Please select an object first).")

    def add_selected_to_scroll_list_cmd(self, text_scroll_list_ui, *args):
        """Adds selected objects to the text scroll list."""
        selected_objects = pc.ls(selection=True, type="transform")
        if selected_objects:
            current_items = text_scroll_list_ui.getAllItems()
            for obj in selected_objects:
                if obj.name() not in current_items:  # Avoid duplicates
                    text_scroll_list_ui.append(obj.name())
        else:
            pc.warning(
                "请先选择一个或多个对象 (Please select one or more objects first)."
            )

    def remove_selected_from_scroll_list_cmd(self, text_scroll_list_ui, *args):
        """Removes selected items from the text scroll list."""
        selected_items = text_scroll_list_ui.getSelectItem()
        if selected_items:
            for item in selected_items:
                text_scroll_list_ui.removeItem(item)
        else:
            pc.warning(
                "请在列表中选择要移除的项 (Please select items in the list to remove)."
            )

    def clear_scroll_list_cmd(self, text_scroll_list_ui, *args):
        """Clears all items from the text scroll list."""
        text_scroll_list_ui.removeAll()

    def _update_root_motion_flags_from_ui(self):
        """Gets root motion attribute flags from checkboxes."""
        translate_values = pc.checkBoxGrp(
            self.translate_cb_grp, q=True, valueArray3=True
        )
        self.root_motion_tx = translate_values[0]
        self.root_motion_ty = translate_values[1]
        self.root_motion_tz = translate_values[2]

        rotate_values = pc.checkBoxGrp(self.rotate_cb_grp, q=True, valueArray3=True)
        self.root_motion_rx = rotate_values[0]
        self.root_motion_ry = rotate_values[1]
        self.root_motion_rz = rotate_values[2]

    def _validate_controller_inputs(self):
        """Validates that essential controller names are provided and exist."""
        self.root_ctrl_name = self.root_ctrl_field.getText()
        self.pelvis_ctrl_name = self.pelvis_ctrl_field.getText()
        self.ik_ctrl_names_from_ui = self.ik_ctrls_text_scroll_list.getAllItems() or []

        if not self.root_ctrl_name or not pc.objExists(self.root_ctrl_name):
            pc.error(
                f"根控制器 '{self.root_ctrl_name}' 不存在或未指定 (Root controller not found or specified)."
            )
            return False
        if not self.pelvis_ctrl_name or not pc.objExists(self.pelvis_ctrl_name):
            pc.error(
                f"骨盆控制器 '{self.pelvis_ctrl_name}' 不存在或未指定 (Pelvis controller not found or specified)."
            )
            return False

        for ik_ctrl_name in self.ik_ctrl_names_from_ui:
            if not pc.objExists(ik_ctrl_name):
                pc.error(
                    f"IK 控制器 '{ik_ctrl_name}' 不存在 (IK controller not found)."
                )
                return False
        return True

    def _get_animation_range(self, *object_names):
        """Determines animation range from given objects or playback range."""
        min_time = pc.playbackOptions(q=True, minTime=True)
        max_time = pc.playbackOptions(q=True, maxTime=True)

        all_keys = []
        for obj_name in object_names:
            if pc.objExists(obj_name):
                keys = pc.keyframe(obj_name, q=True, tc=True)
                if keys:
                    all_keys.extend(keys)

        if all_keys:
            firstFrame = math.floor(min(all_keys))
            lastFrame = math.ceil(max(all_keys))
            if (
                firstFrame == lastFrame
            ):  # Single keyframe, expand range slightly for baking
                lastFrame = firstFrame + 1
        else:
            pc.warning(
                "在指定的控制器上未找到动画关键帧。将使用当前播放范围。(No animation keyframes found on specified controllers. Using current playback range.)"
            )
            firstFrame = min_time
            lastFrame = max_time
            if firstFrame == lastFrame:  # If playback range is also single frame
                lastFrame = firstFrame + 1
        return firstFrame, lastFrame

    def get_unique_name(self, base_name):
        """Generates a unique name in the scene by appending a counter."""
        name = base_name
        counter = 1
        while pc.objExists(name):
            name = f"{base_name}_{counter}"
            counter += 1
        return name

    def pin_ctrl_anim(self, ctrl_pyobj_list=None):
        """
        Pins selected controllers in world space using locators.
        Stores created locators in self.ctrl_loc_list.
        """
        if ctrl_pyobj_list is None or not ctrl_pyobj_list:
            pc.warning(
                "没有控制器被指定用于Pin操作 (No controllers specified for pinning)."
            )
            return

        self.ctrl_loc_list = []  # CORRECTED: Initialize/clear instance variable
        ctrl_con_list = []

        firstFrame, lastFrame = self._get_animation_range(
            *[c.name() for c in ctrl_pyobj_list]
        )

        for ctrl in ctrl_pyobj_list:
            ctrl_loc_name = self.get_unique_name(f"{ctrl.name()}_pin_loc")
            ctrl_loc = pc.spaceLocator(name=ctrl_loc_name)
            self.ctrl_loc_list.append(ctrl_loc)
            # Match locator's initial transform to controller's initial transform
            pc.matchTransform(ctrl_loc, ctrl)
            ctrl_cons = pc.parentConstraint(
                ctrl, ctrl_loc, mo=False
            )  # Maintain offset False to transfer world space
            ctrl_con_list.append(ctrl_cons)

        if not self.ctrl_loc_list:
            pc.warning(
                "未能创建定位器用于Pin操作 (Failed to create locators for pinning)."
            )
            return

        pc.bakeResults(
            self.ctrl_loc_list,
            simulation=True,
            t=(firstFrame, lastFrame),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,  # ADDED: Good for preventing flips
        )
        if ctrl_con_list:
            pc.delete(ctrl_con_list)

        # Now constrain controllers to their respective locators
        for i, ctrl in enumerate(ctrl_pyobj_list):
            pc.parentConstraint(
                self.ctrl_loc_list[i], ctrl, mo=True
            )  # Maintain offset True

        print(f"控制器已Pin住: {[ctrl.name() for ctrl in ctrl_pyobj_list]}")

    def bake_pined_anim(self, ctrl_pyobj_list=None):
        """Bakes animation onto pinned controllers and cleans up locators."""
        if not ctrl_pyobj_list:
            pc.warning(
                "没有控制器被指定用于烘焙Pin住的动画 (No controllers specified for baking pinned animation)."
            )
            return

        firstFrame, lastFrame = self._get_animation_range(
            *[c.name() for c in ctrl_pyobj_list]
        )

        # Find constraints targetting the controllers and delete them before baking
        constraints_to_delete = []
        for ctrl in ctrl_pyobj_list:
            # Find parentConstraints targeting this controller
            # The locators are constraining these controllers.
            cons = pc.listConnections(ctrl, type="parentConstraint", d=True, s=False)
            if cons:
                constraints_to_delete.extend(cons)

        if constraints_to_delete:
            pc.delete(list(set(constraints_to_delete)))  # Delete unique constraints

        pc.bakeResults(
            ctrl_pyobj_list,
            simulation=True,
            t=(firstFrame, lastFrame),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
        )

        if self.ctrl_loc_list:
            pc.delete(self.ctrl_loc_list)
            self.ctrl_loc_list = []  # Clear the list

        print(f"Pin住的动画已烘焙到: {[ctrl.name() for ctrl in ctrl_pyobj_list]}")

    def apply_inplace_to_root_motion_cmd(self, *args):
        """Command for 'In-place to Root Motion' button."""
        if not self._validate_controller_inputs():
            return
        self._update_root_motion_flags_from_ui()

        root_ctrl = pc.PyNode(self.root_ctrl_name)
        pelvis_ctrl = pc.PyNode(self.pelvis_ctrl_name)
        ik_ctrls = [pc.PyNode(name) for name in self.ik_ctrl_names_from_ui]

        print("开始转换: 原地 -> 根动画 (Starting conversion: In-place to Root Motion)")
        self.inplace_to_root_motion_logic(root_ctrl, pelvis_ctrl, ik_ctrls)
        pc.success(
            "转换完成: 原地 -> 根动画 (Conversion complete: In-place to Root Motion)!"
        )

    def inplace_to_root_motion_logic(self, root_ctrl, pelvis_ctrl, ik_ctrls=None):
        """
        Converts in-place animation to root motion.
        Args:
            root_ctrl (PyNode): The root controller.
            pelvis_ctrl (PyNode): The pelvis controller.
            ik_ctrls (list[PyNode], optional): List of IK controllers.
        """
        ik_ctrls = ik_ctrls or []

        firstFrame, lastFrame = self._get_animation_range(
            root_ctrl.name(), pelvis_ctrl.name(), *[ik.name() for ik in ik_ctrls]
        )
        pc.currentTime(firstFrame)

        # --- Create Locators ---
        loc_root_anim = pc.spaceLocator(name=self.get_unique_name("loc_RootAnim"))
        loc_pelvis_anim = pc.spaceLocator(name=self.get_unique_name("loc_PelvisAnim"))

        # Store initial root transform in case we need to restore it or parts of it
        initial_root_world_matrix = root_ctrl.getMatrix(worldSpace=True)
        pc.xform(loc_root_anim, matrix=initial_root_world_matrix, worldSpace=True)

        # --- Pin IK and Pelvis controllers to maintain their world space animation ---
        # This uses self.ctrl_loc_list
        # The pelvis is the primary driver for the root's new motion.
        # IK controls are pinned to compensate for the new root motion.
        controls_to_pin = [pelvis_ctrl] + ik_ctrls
        self.pin_ctrl_anim(
            controls_to_pin
        )  # Creates self.ctrl_loc_list and constrains controls

        # --- Transfer Pelvis Animation to loc_RootAnim ---
        # 1. Match loc_PelvisAnim to Pelvis_CTRL and bake its world animation
        pc.matchTransform(loc_pelvis_anim, pelvis_ctrl)
        pelvis_to_loc_pelvis_constraint = pc.parentConstraint(
            pelvis_ctrl, loc_pelvis_anim, mo=False
        )
        pc.bakeResults(
            loc_pelvis_anim,
            simulation=True,
            t=(firstFrame, lastFrame),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
        )
        pc.delete(pelvis_to_loc_pelvis_constraint)

        # 2. loc_RootAnim should follow loc_PelvisAnim for selected attributes
        #    For attributes NOT selected, loc_RootAnim should remain static (like initial root_ctrl)
        #    or follow some other logic. Here, we'll make loc_RootAnim copy loc_PelvisAnim,
        #    then filter its curves.

        # Constrain loc_RootAnim to loc_PelvisAnim to transfer motion
        # The loc_RootAnim is currently at the root_ctrl's initial world position.
        # We want its translation and Y-rotation to come from the pelvis.
        # This constraint should be set up carefully.
        # We'll bake loc_pelvis_anim, then drive loc_root_anim from loc_pelvis_anim attributes directly.

        pc.currentTime(firstFrame)
        # Store initial values of loc_root_anim (which matches root_ctrl's initial pose)
        initial_loc_root_values = {
            "tx": loc_root_anim.tx.get(),
            "ty": loc_root_anim.ty.get(),
            "tz": loc_root_anim.tz.get(),
            "rx": loc_root_anim.rx.get(),
            "ry": loc_root_anim.ry.get(),
            "rz": loc_root_anim.rz.get(),
        }

        for frame in range(int(firstFrame), int(lastFrame) + 1):
            pc.currentTime(frame)

            # Get pelvis world transform at current frame
            pelvis_matrix = loc_pelvis_anim.getMatrix(
                worldSpace=True
            )  # loc_pelvis_anim has baked pelvis anim

            # Update loc_root_anim based on selected channels from pelvis
            # Translation
            if self.root_motion_tx:
                loc_root_anim.tx.set(pelvis_matrix.translate.x)
            else:
                loc_root_anim.tx.set(initial_loc_root_values["tx"])

            if self.root_motion_ty:
                loc_root_anim.ty.set(pelvis_matrix.translate.y)
            else:
                loc_root_anim.ty.set(initial_loc_root_values["ty"])

            if self.root_motion_tz:
                loc_root_anim.tz.set(pelvis_matrix.translate.z)
            else:
                loc_root_anim.tz.set(initial_loc_root_values["tz"])

            # Rotation (Euler) - more complex due to rotation order and potential gimbal lock.
            # Simpler: copy all, then filter curves if not needed.
            # For simplicity, let's assume Y rotation is primary for root motion.
            # Other rotations could be zeroed or kept from initial pose.
            pelvis_rotation = pc.xform(
                loc_pelvis_anim, q=True, rotation=True, worldSpace=True
            )

            if self.root_motion_rx:
                loc_root_anim.rx.set(pelvis_rotation[0])
            else:
                loc_root_anim.rx.set(initial_loc_root_values["rx"])

            if self.root_motion_ry:
                loc_root_anim.ry.set(pelvis_rotation[1])
            else:
                loc_root_anim.ry.set(initial_loc_root_values["ry"])

            if self.root_motion_rz:
                loc_root_anim.rz.set(pelvis_rotation[2])
            else:
                loc_root_anim.rz.set(initial_loc_root_values["rz"])

            pc.setKeyframe(loc_root_anim, attribute=["translate", "rotate"])

        pc.filterCurve(loc_root_anim.rotate)  # Euler filter

        # --- Apply loc_RootAnim's animation to the actual Root_CTRL ---
        root_constraint = pc.parentConstraint(
            loc_root_anim, root_ctrl, mo=False
        )  # root_ctrl now follows loc_RootAnim
        pc.bakeResults(
            root_ctrl,
            simulation=True,
            t=(firstFrame, lastFrame),
            sampleBy=1,
            disableImplicitControl=True,
            preserveOutsideKeys=True,
            minimizeRotation=True,
        )
        pc.delete(root_constraint)
        pc.filterCurve(root_ctrl.rotate)

        # --- Bake pinned animation (pelvis, IK) now that root_ctrl has its new motion ---
        # The list of controls to bake is [pelvis_ctrl] + ik_ctrls
        # self.ctrl_loc_list (locators for pinning) are still constraining them.
        self.bake_pined_anim(controls_to_pin)  # This also cleans up self.ctrl_loc_list

        # --- Cleanup ---
        pc.delete([loc_root_anim, loc_pelvis_anim])
        pc.select(cl=True)
        pc.select(root_ctrl)  # Select the modified root controller

    def apply_root_motion_to_inplace_cmd(self, *args):
        """Command for 'Root Motion to In-place' button."""
        if not self._validate_controller_inputs():
            return
        # No checkboxes needed for this direction typically, as root is usually zeroed out.

        root_ctrl = pc.PyNode(self.root_ctrl_name)
        pelvis_ctrl = pc.PyNode(self.pelvis_ctrl_name)
        ik_ctrls = [pc.PyNode(name) for name in self.ik_ctrl_names_from_ui]

        print("开始转换: 根动画 -> 原地 (Starting conversion: Root Motion to In-place)")
        self.root_motion_to_inplace_logic(root_ctrl, pelvis_ctrl, ik_ctrls)
        pc.success(
            "转换完成: 根动画 -> 原地 (Conversion complete: Root Motion to In-place)!"
        )

    def root_motion_to_inplace_logic(self, root_ctrl, pelvis_ctrl, ik_ctrls=None):
        """
        Converts root motion animation to in-place animation.
        Args:
            root_ctrl (PyNode): The root controller.
            pelvis_ctrl (PyNode): The pelvis controller.
            ik_ctrls (list[PyNode], optional): List of IK controllers.
        """
        ik_ctrls = ik_ctrls or []
        controls_to_process = [pelvis_ctrl] + ik_ctrls

        firstFrame, lastFrame = self._get_animation_range(
            root_ctrl.name(), *[c.name() for c in controls_to_process]
        )
        pc.currentTime(firstFrame)

        # 1. Pin pelvis and IK controllers to maintain their current world space animation
        #    while the root is being modified.
        self.pin_ctrl_anim(
            controls_to_process
        )  # Creates self.ctrl_loc_list and constrains controls

        # 2. Zero out the root_ctrl's animation (or set to its first frame pose if preferred)
        #    Get root's transform at the first frame. This will be the new static pose.
        initial_root_tx = pc.getAttr(f"{root_ctrl.name()}.tx", time=firstFrame)
        initial_root_ty = pc.getAttr(f"{root_ctrl.name()}.ty", time=firstFrame)
        initial_root_tz = pc.getAttr(f"{root_ctrl.name()}.tz", time=firstFrame)
        initial_root_rx = pc.getAttr(f"{root_ctrl.name()}.rx", time=firstFrame)
        initial_root_ry = pc.getAttr(f"{root_ctrl.name()}.ry", time=firstFrame)
        initial_root_rz = pc.getAttr(f"{root_ctrl.name()}.rz", time=firstFrame)

        attributes_to_reset = ["tx", "ty", "tz", "rx", "ry", "rz"]
        initial_values = [
            initial_root_tx,
            initial_root_ty,
            initial_root_tz,
            initial_root_rx,
            initial_root_ry,
            initial_root_rz,
        ]

        for i, attr_suffix in enumerate(attributes_to_reset):
            attr_node = root_ctrl.attr(attr_suffix)
            pc.cutKey(
                attr_node, time=(firstFrame, lastFrame), clear=True
            )  # Clear existing animation
            attr_node.set(initial_values[i])  # Set to first frame's value
            pc.setKeyframe(
                attr_node, time=(firstFrame, lastFrame)
            )  # Key this static value across the range

        pc.filterCurve(root_ctrl.rotate)  # Apply Euler filter if rotations were changed

        # 3. Bake the animation onto pelvis and IK controllers.
        #    Since they were pinned in world space (by self.pin_ctrl_anim),
        #    and the root_ctrl is now static, their animation will be baked
        #    relative to this new static root_ctrl, effectively making the overall character motion in-place.
        self.bake_pined_anim(
            controls_to_process
        )  # This also cleans up self.ctrl_loc_list

        pc.select(cl=True)
        pc.select(root_ctrl, pelvis_ctrl, ik_ctrls if ik_ctrls else None)
        print(
            f"根动画已转换为原地动画. 根控制器 '{root_ctrl.name()}' 已被设置为静态（基于其第一帧的姿态）。"
        )


# --- Function to launch the UI ---
def show_root_motion_tools_ui():
    """Creates and shows the RootMotionToolsUI instance."""
    # CORRECTED: Instantiate the class
    try:
        # Make it a singleton or ensure only one instance if preferred
        # For simplicity, just create a new one, previous __init__ handles deletion
        RootMotionToolsUI()
        print("根动画工具UI已启动 (Root Motion Tools UI launched).")
    except Exception as e:
        pc.error(f"启动根动画工具UI失败 (Failed to launch Root Motion Tools UI): {e}")


# --- If run directly, show the UI ---
if __name__ == "__main__":
    # This block allows the script to be run directly in Maya's script editor
    # or imported as a module.
    show_root_motion_tools_ui()
