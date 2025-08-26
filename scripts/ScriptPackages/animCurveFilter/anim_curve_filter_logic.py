# -*- encoding: utf-8 -*-

"""
@File    :   anim_curve_filter_logic.py
@Time    :   2025/08/25 17:49:07
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   当前文件作用

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
                print(f"Skipping invalid or unsupported node: {depend_node.apiTypeStr}")
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
        原理：对每相邻的三帧，求其平均值，以此为轴心对中间帧进行值缩放。
        Args:
            scale_value (float): 缩放值,0:1
        """
        # 关闭缓存曲线更新，以便后面返回原始曲线数据。
        pm.bufferCurve(animation="keysOrObjects", overwrite=False)

        # 遍历数据
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 3:
                print((f"Skipping curve {curve_fn.name()} with fewer than 3 keys."))
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
        # 关闭缓存曲线更新，以便后面返回原始曲线数据。
        pm.bufferCurve(animation="keysOrObjects", overwrite=False)
        # 遍历数据
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 2:
                continue
            # 计算动画曲线的整体斜率（第一个关键帧到最后一个关键帧的平均变化率）：
            # 曲线首末帧的 值差/时间差
            start_time = curve_fn.input(0).asUnits(om.MTime.uiUnit())
            start_value = curve_fn.value(0)
            end_time = curve_fn.input(num_keys - 1).asUnits(om.MTime.uiUnit())
            end_value = curve_fn.value(num_keys - 1)

            time_diff = end_time - start_time
            value_diff = end_value - start_value
            # 避免除以零,1e-6 = 1 * 10 ^{-6} = 0.000001
            if abs(time_diff) < 1e-6:
                continue

            tangent = value_diff / time_diff
            # 遍历所有关键帧进行插值
            for i in range(1, num_keys - 1):
                current_time = curve_fn.input(i).asUnits(om.MTime.uiUnit())
                current_value = curve_fn.value(i)
                # 计算缩放的枢轴点：当前时间到第一帧时间的斜率插值
                pivot_value = start_value + tangent * (current_time - start_time)
                # 计算新值：当前值到枢轴值的缩放插值
                new_value = current_value + (pivot_value - current_value) * scale_value
                # 设置曲线值
                curve_fn.setValue(i, new_value)

    def apply_smooth_filter(self, iterations):
        """
        应用Smooth过滤器。
        原理：对每相邻的三帧，求其平均值，直接赋给中间帧。可多次迭代。
        """
        # 关闭缓存曲线更新，以便后面返回原始曲线数据。
        pm.bufferCurve(animation="keysOrObjects", overwrite=False)
        # 遍历迭代次数
        for _ in range(iterations):
            for data in self.buffer_data.values():
                curve_fn = data["curve_fn"]
                num_keys = curve_fn.numKeys
                if num_keys < 3:
                    continue
                # 获取帧数据
                original_values = [curve_fn.value(i) for i in range(num_keys)]
                # 计算临近三帧的平均值直接赋值给中间帧
                for i in range(1, num_keys - 1):
                    pre_value = original_values[i - 1]
                    cur_value = original_values[i]
                    nex_value = original_values[i + 1]
                    average_value = (pre_value + cur_value + nex_value) / 3.0
                    curve_fn.setValue(i, average_value)

    def apply_twinner_filter(self, scale_value):
        """
        应用Twinner过滤器。
        在当前时间点，根据前后帧的值按比例创建或修改关键帧。
        """
        # 关闭缓存曲线更新，以便后面返回原始曲线数据。
        pm.bufferCurve(animation="keysOrObjects", overwrite=False)
        # 获取当前时间栏时间
        current_time = oma.MAnimControl.currentTime()
        # 遍历数据
        for data in self.buffer_data.values():
            curve_fn = data["curve_fn"]
            num_keys = curve_fn.numKeys
            if num_keys < 2:
                continue

            # 查找当前时间前一个和后一个关键帧的索引
            pre_index = curve_fn.findClosest(current_time)
            if curve_fn.input(pre_index) > current_time and pre_index > 0:
                pre_index -= 1

            next_index = pre_index + 1
            # 获取前后关键帧的值
            if pre_index >= 0 and next_index < curve_fn.numKeys:
                pre_value = curve_fn.value(pre_index)
                next_value = curve_fn.value(next_index)
                # 如果前后帧的值不想等
                if abs(next_value - pre_value) > 1e-6:
                    # 算法：前值 + 后值 - 前值 * 比例
                    new_value = pre_value + (next_value - pre_value) * scale_value

                    # 检查当前时间是否已有关键帧，有则修改，无则添加
                    found_exact = False
                    for i in range(curve_fn.numKeys):
                        if curve_fn.input(i) == current_time:
                            curve_fn.setValue(i, new_value)
                            found_exact = True
                            break

                    if not found_exact:
                        key_index = curve_fn.insertKey(current_time)
                        curve_fn.setValue(key_index, new_value)

    @staticmethod
    def remap_value(in_min, in_max, out_min, out_max, v) -> float:
        """
        将一个线性比例尺上的值重新映射到另一个线性比例尺上，结合了线性插值和反线性插值。
        Args:
            i_min (float): 输入比例尺的最小值。
            i_max (float): 输入比例尺的最大值。
            o_min (float): 输出比例尺的最小值。
            o_max (float): 输出比例尺的最大值。
            v (float): 需要重新映射的值。
        Returns:
            float: 重新映射后的值。
        Examples:
            45 == remap(0, 100, 40, 50, 50)
            6.2 == remap(1, 5, 3, 7, 4.2)
        """
        # 排除除零错误
        if in_max - in_min == 0:
            return out_min
        # 获得 v 在 in_min, in_max 之间的比例，0：1
        t = (v - in_min) / (in_max - in_min)
        # 获取out_min, out_max 对于 t 的插值
        val = out_min + (out_max - out_min) * t
        # 返回结果
        return val
