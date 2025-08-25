# -*- encoding: utf-8 -*-

"""
@File    :   anim_curve_filter_logic.py
@Time    :   2025/08/25 17:49:07
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用

使用方法：
    1. 将此文件放入 Maya 脚本路径下，例如："\\Documents\\maya\\20xx\\scripts"
    2. 在 Maya 的脚本编辑器中执行以下 Python 代码:
       import anim_curve_filter_refactored
       anim_curve_filter_refactored.show_ui()
"""

import maya.cmds as cmds
from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma

oma.
class AnimCurveFilterLogic:
    """
    动画曲线过滤器核心逻辑类。
    所有功能均使用 Maya Python API 2.0 实现，以保证性能。
    """

    def __init__(self):
        # 缓存数据结构: { "animCurveNodeName": MFnAnimCurve, "keys": [(time, value), ...] }
        self.buffer_data = {}

    def get_selected_anim_curves(self):
        """
        获取当前在Graph Editor中选择的关键帧所在的动画曲线。
        返回一个字典，键为动画曲线节点名，值为 MFnAnimCurve 实例。
        """
        curves = {}
        selection = om.MGlobal.getActiveSelectionList()
        if selection.isEmpty():
            return curves
        sel_iter = om.MItSelectionList(selection, om.MFn.kAnimCurve)
        
        while not sel_iter.isDone():
            depend_node = sel_iter.getDependNode()
            if depend_node.apiType in [
                    om.MFn.kAnimCurveTimeToAngular,# 旋转
                    om.MFn.kAnimCurveTimeToDistance,# 位移
                    om.MFn.kAnimCurveTimeToTime,
                    om.MFn.kAnimCurveTimeToUnitless,# 旋转
                ]:
                anim_curve_fn = oma.MFnAnimCurve(depend_node)
                curves[anim_curve_fn.name()] = anim_curve_fn
        return curves

    def cache_current_curves(self):
        """
        在修改前，缓存所选动画曲线的所有关键帧数据。
        """
        self.buffer_data.clear()
        anim_curves = self.get_selected_anim_curves()
        for name, curve_fn in anim_curves.items():
            keys_data = []
            for i in range(curve_fn.numKeys):
                time = curve_fn.time(i)
                value = curve_fn.value(i)
                keys_data.append((time, value))
            self.buffer_data[name] = {"curve_fn": curve_fn, "keys": keys_data}
        print(f"已缓存 {len(self.buffer_data)} 条曲线数据。")

    def restore_cached_curves(self):
        """
        恢复缓存的动画曲线数据。
        """
        if not self.buffer_data:
            om.MGlobal.displayWarning("没有可恢复的缓存数据。")
            return

        cmds.undoInfo(openChunk=True)
        try:
            for name, data in self.buffer_data.items():
                curve_fn = data["curve_fn"]

                # 清除现有关键帧
                while curve_fn.numKeys > 0:
                    curve_fn.remove(0)

                # 重新插入缓存的关键帧
                for time, value in data["keys"]:
                    curve_fn.addKey(time, value)
        finally:
            cmds.undoInfo(closeChunk=True)

        om.MGlobal.displayInfo("曲线已从缓存中恢复。")

    def apply_butterworth_filter(self, scale_value):
        """
        应用Butterworth过滤器。
        原理：对每相邻的三帧，求其平均值，以此为轴心对中间帧进行缩放。
        """
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 3:
                continue

            original_values = [curve_fn.value(i) for i in range(num_keys)]

            for i in range(1, num_keys - 1):
                pre_value = original_values[i - 1]
                cur_value = original_values[i]
                nex_value = original_values[i + 1]

                average_value = (pre_value + cur_value + nex_value) / 3.0
                new_value = average_value + (cur_value - average_value) * scale_value
                curve_fn.setValue(i, new_value)
                # API暂无直接设置切线为auto的方法，通常在修改后Maya会自动调整
                # 如需强制重设，可后续调用cmds.keyTangent

    def apply_dampen_filter(self, scale_value):
        """
        应用Dampen过滤器。
        原理：将首尾两帧连线，找出曲线上每一帧投射到连线上的值，以此为轴心进行缩放。
        """
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 2:
                continue

            start_time = curve_fn.time(0)
            start_value = curve_fn.value(0)
            end_time = curve_fn.time(num_keys - 1)
            end_value = curve_fn.value(num_keys - 1)

            time_diff = end_time.value - start_time.value
            if abs(time_diff) < 1e-6:  # 避免除以零
                continue

            tangent = (end_value - start_value) / time_diff

            for i in range(1, num_keys - 1):
                current_time = curve_fn.time(i)
                current_value = curve_fn.value(i)

                pivot_value = start_value + tangent * (
                    current_time.value - start_time.value
                )
                new_value = pivot_value + (current_value - pivot_value) * scale_value
                curve_fn.setValue(i, new_value)

    def apply_smooth_filter(self, iterations):
        """
        应用Smooth过滤器。
        原理：对每相邻的三帧，求其平均值，直接赋给中间帧。可多次迭代。
        """
        for _ in range(iterations):
            for data in self.buffer_data.values():
                curve_fn = data["curve_fn"]
                num_keys = curve_fn.numKeys
                if num_keys < 3:
                    continue

                original_values = [curve_fn.value(i) for i in range(num_keys)]

                for i in range(1, num_keys - 1):
                    pre_value = original_values[i - 1]
                    cur_value = original_values[i]
                    nex_value = original_values[i + 1]
                    average_value = (pre_value + cur_value + nex_value) / 3.0
                    curve_fn.setValue(i, average_value)

    def apply_simplify_filter(self, tolerance_value):
        """
        应用Simplify过滤器。
        使用 MFnAnimCurve.simplify() API 调用。
        """
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            if curve_fn.numKeys > 2:
                time_tolerance = om.MTime(tolerance_value, om.MTime.uiUnit())
                value_tolerance = tolerance_value
                curve_fn.simplify(time_tolerance, value_tolerance)

    def apply_twinner_filter(self, scale_value):
        """
        应用Twinner过滤器。
        在当前时间点，根据前后帧的值按比例创建或修改关键帧。
        """
        current_time = oma.MAnimControl.currentTime()
        selection = om.MGlobal.getRichSelection()
        mfn_selection = oma.MSelectionList()

        # 查找所有动画层上的动画曲线
        anim_layers = cmds.ls(type="animLayer")
        for layer in anim_layers:
            plugs = cmds.animLayer(layer, query=True, attribute=True)
            if plugs:
                for plug_str in plugs:
                    try:
                        sel_list = om.MSelectionList()
                        sel_list.add(plug_str)
                        plug = sel_list.getPlug(0)

                        source = plug.source()
                        if not source.isNull:
                            source_node = source.node()
                            if source_node.hasFn(om.MFn.kAnimCurve):
                                curve_fn = oma.MFnAnimCurve(source_node)
                                self._tween_curve(curve_fn, current_time, scale_value)

                    except Exception as e:
                        # print(f"Could not process plug {plug_str}: {e}")
                        pass

    def _tween_curve(self, curve_fn, current_time, scale_value):
        """Twinner过滤器的辅助函数，处理单条曲线。"""

        # 查找前一个和后一个关键帧的索引
        pre_index = curve_fn.findClosest(current_time)
        if curve_fn.time(pre_index) > current_time and pre_index > 0:
            pre_index -= 1

        next_index = pre_index + 1

        if pre_index >= 0 and next_index < curve_fn.numKeys:
            pre_value = curve_fn.value(pre_index)
            next_value = curve_fn.value(next_index)

            if abs(next_value - pre_value) > 1e-6:
                # 算法：后值 - 前值 * 比例 + 前值
                new_value = (next_value - pre_value) * scale_value + pre_value

                # 检查当前时间是否已有关键帧，有则修改，无则添加
                found_exact = False
                for i in range(curve_fn.numKeys):
                    if curve_fn.time(i) == current_time:
                        curve_fn.setValue(i, new_value)
                        found_exact = True
                        break

                if not found_exact:
                    curve_fn.addKey(current_time, new_value)

    @staticmethod
    def remap(i_min, i_max, o_min, o_max, v):
        """
        将一个线性比例尺上的值重新映射到另一个线性比例尺上。
        """
        if i_max - i_min == 0:
            return o_min
        return o_min + (o_max - o_min) * ((v - i_min) / (i_max - i_min))


# --- 主程序入口 ---
if __name__ == "__main__":
    # 在Maya中，最好通过一个独立的函数来调用UI，以避免多重实例问题
    try:
        if ui_instance:
            ui_instance.close()
            ui_instance.deleteLater()
    except:
        pass

    show_ui()
