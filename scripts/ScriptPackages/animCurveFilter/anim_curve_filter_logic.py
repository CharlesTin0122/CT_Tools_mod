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

from maya.api import OpenMaya as om
from maya.api import OpenMayaAnim as oma
import pymel.core as pm


class AnimCurveFilterLogic:
    """
    动画曲线过滤器核心逻辑类。
    所有功能均使用 Maya Python API 2.0 实现，以保证性能。
    """

    def __init__(self):
        # 缓存数据结构: { "animCurveNodeName": MFnAnimCurve, "keys": [(time, value), ...] }
        self.buffer_data = {}

    @staticmethod
    def get_selected_anim_curves() -> dict:
        """获取当前在Graph Editor中选择的关键帧所在的动画曲线。
        Returns:
            dict: {curve_name : MFnAnimCurve, ...}
        """

        # 用于选择的储存动画曲线数据
        curves: dict = {}
        # 获取当前选择列表
        selection = om.MGlobal.getActiveSelectionList()

        # 检查选择列表是否为空
        if selection.isEmpty():
            print("No objects selected in Graph Editor.")
            return curves
        # 选择列表迭代器
        sel_iter = om.MItSelectionList(selection)
        # 遍历选择列表
        while not sel_iter.isDone():
            try:
                # 获取MObject
                depend_node = sel_iter.getDependNode()
                # 确保节点是有效的 MObject
                if not depend_node.isNull() and depend_node.hasFn(om.MFn.kAnimCurve):
                    # 检查是否是支持的动画曲线类型
                    if depend_node.apiType() in [
                        om.MFn.kAnimCurveTimeToAngular,  # 旋转
                        om.MFn.kAnimCurveTimeToDistance,  # 位移
                        om.MFn.kAnimCurveTimeToTime,  # 时间扭曲
                        om.MFn.kAnimCurveTimeToUnitless,  # 旋转
                    ]:
                        # 获取动画曲线函数集
                        anim_curve_fn = oma.MFnAnimCurve(depend_node)
                        # 获取动画曲线名称
                        curve_name = anim_curve_fn.name()
                        # 填充数据
                        curves[curve_name] = anim_curve_fn
                        print(f"Found animation curve: {curve_name}")
                else:
                    print(
                        f"Skipping invalid or unsupported node: {depend_node.apiTypeStr()}"
                    )
            except Exception as e:
                print(f"Error processing node: {e}")
            sel_iter.next()  # 推进迭代器，防止无限循环

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
                time = curve_fn.input(i)
                value = curve_fn.value(i)
                keys_data.append((time, value))
            self.buffer_data[name] = {"curve_fn": curve_fn, "keys": keys_data}
        print(f"已缓存 {len(self.buffer_data)} 条曲线数据。")

    def restore_cached_curves(self):
        """将动画曲线返回修改前的状态
        原理：利用maya曲线编辑器的缓存曲线（bufferCurve）
        """
        try:
            # 返回修改前缓存曲线的状态
            pm.bufferCurve(animation="keysOrObjects", swap=True)
            # TODO: 待验证，覆盖缓存曲线为当前曲线
            pm.bufferCurve(animation="keysOrObjects", overwrite=True)
        except Exception as exc:
            print(exc)

    def apply_butterworth_filter(self, scale_value):
        """
        应用Butterworth过滤器。
        原理：对每相邻的三帧，求其平均值，以此为轴心对中间帧进行缩放。
        """
        # 关闭缓存曲线更新，以便后面返回原始曲线数据。
        pm.bufferCurve(animation="keysOrObjects", overwrite=False)

        # 遍历数据
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 3:
                continue
            # 获取帧的值列表
            original_values = [curve_fn.value(i) for i in range(num_keys)]
            # 从第二帧开始遍历
            for i in range(1, num_keys - 1):
                pre_value = original_values[i - 1]  # 前一帧的值
                cur_value = original_values[i]  # 当前帧的值
                nex_value = original_values[i + 1]  # 后一帧的做
                # 三帧的平均值
                average_value = (pre_value + cur_value + nex_value) / 3.0
                # 当前帧的值与平均值进行插值计算
                new_value = cur_value + (average_value - cur_value) * scale_value
                # 设置关键帧的值
                curve_fn.setValue(i, new_value)

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
        anim_layers = pm.ls(type="animLayer")
        for layer in anim_layers:
            plugs = pm.animLayer(layer, query=True, attribute=True)
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
