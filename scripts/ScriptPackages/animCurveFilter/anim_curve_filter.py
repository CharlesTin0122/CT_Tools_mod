# -*- coding: utf-8 -*-
"""
@FileName      : anim_curve_filter.py
@DateTime      : 2023/07/27 17:01:26
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2023.3
@PythonVersion : python 3.9.7

灵感来源：
    动画曲线编辑辅助工具 - JAY JMS的文章 - 知乎
    https://zhuanlan.zhihu.com/p/35690523
    帖子中提供的脚本为加密文件，无法看到源代码，并且不支持Python3，在maya2022+版本无法使用，顾根据其解释的算法重新编写。

使用方法：
    0.该脚本用 python 3.9.7，Pymel 库编写，请确保maya已安装Pymel库。
    1.将此文件放入maya环境变量下路径中，一般为"\\Documents\\maya\\20xx\\scripts"
    2.在maya中执行 curve_filter = AnimCurveFilter();curve_filter.create_ui()
"""

from functools import partial
import pymel.core as pm


class AnimCurveFilter:
    """定义动画曲线过滤器类"""

    def __init__(self):
        """构造方法"""
        self.filter_radioCol = None
        self.value_slider = None
        self.default_value = 0
        self.keyframe_data = {}

    def create_ui(self):
        """创建UI"""
        try:
            pm.deleteUI("FilterCurve")
        except Exception as exc:
            print(exc)

        main_window = pm.window("FilterCurve", title="Curve filter")
        pm.columnLayout()
        # 创建radioButton选择器
        self.filter_radioCol = pm.radioCollection()
        rb_grp1 = pm.radioButtonGrp(
            numberOfRadioButtons=3,
            label="filters: ",
            labelArray3=["butterworth", "Dampen", "Smooth"],
            changeCommand1=partial(self.switch_filter, 0),
            changeCommand2=partial(self.switch_filter, 1),
            changeCommand3=partial(self.switch_filter, 2),
            select=0,
        )
        pm.radioButtonGrp(
            numberOfRadioButtons=2,
            shareCollection=rb_grp1,
            label="",
            labelArray2=["simplify", "Twinner"],
            changeCommand1=partial(self.switch_filter, 3),
            changeCommand2=partial(self.switch_filter, 4),
        )
        # 创建浮点滑条按钮组件
        self.value_slider = pm.floatSliderButtonGrp(
            label="Value: ",
            field=True,
            dragCommand=self.butterworth_filter,
            changeCommand=self.reset_slider,
            buttonLabel="reverse",
            buttonCommand=self.anim_curve_reverse,
            minValue=0.0,
            maxValue=100.0,
            fieldMinValue=0.0,
            fieldMaxValue=100.0,
            value=0.0,
        )
        pm.text(
            label="Butterworth:    在最大限度保持曲线细节的情况下, 对曲线进行一些光滑.",
            align="center",
        )
        pm.text(
            label="Dampen:    在保持曲线连续性的情况下, 对曲线上选择的点增加或减少曲线的振幅.",
            align="center",
        )
        pm.text(
            label="Smooth:    忽略最大限度的保持曲线细节, 对曲线进行大幅度的光滑. 需谨慎使用.",
            align="center",
        )
        pm.text(label="simplify:    对动画曲线进行简化，减少关键帧.", align="center")
        pm.text(
            label="Twinner:    根据前后帧的值按照比例插值添加中间帧。", align="center"
        )

        pm.showWindow(main_window)

    def switch_filter(self, filter_type: int, *args):
        """
        切换过滤器函数，根据过滤器类型切换过滤器

        Args:
            filter_type (int): 过滤器类型
        """
        filter_settings = {
            0: (0, self.butterworth_filter, 0.0, 100.0, 0.0),
            1: (50, self.dampon_filter, 0.0, 100.0, 50.0),
            2: (0, self.smooth_filter, 1, 5, 1),
            3: (0, self.simplify_filter, 0.0, 100.0, 0.0),
            4: (50.0, self.twinner_filter, 0.0, 100.0, 50.0),
        }

        if filter_type in filter_settings:
            self.default_value, drag_cmd, min_val, max_val, default_val = (
                filter_settings[filter_type]
            )
            pm.floatSliderButtonGrp(
                self.value_slider,
                edit=True,
                dragCommand=drag_cmd,
                changeCommand=self.reset_slider,
                buttonCommand=self.anim_curve_reverse,
                minValue=min_val,
                maxValue=max_val,
                fieldMinValue=min_val,
                fieldMaxValue=max_val,
                value=default_val,
            )

    @staticmethod
    def get_keyframe_data(*args):
        """获取所选对象的关键帧数据。
        根据所选的对象列出他们的关键帧属性名称。关键帧时间点。关键帧数值。

        Returns:
            attr_list (list): 关键帧属性名称列表。
            time_value_list (list): 关键帧时间点的列表。
            key_value_list (list): 关键帧数值的列表。
        """
        key_value_list = []
        time_value_list = []
        attr_list = []

        sel_obj_list = pm.selected()
        if sel_obj_list:
            for obj in sel_obj_list:
                attrs = pm.listAnimatable(obj)
                attr_list.extend(attrs)
                for attr in attrs:
                    key_value = pm.keyframe(
                        attr,
                        sl=True,
                        query=True,
                        valueChange=True,
                        absolute=True,
                    )
                    key_value_list.append(key_value)

                    time_value = pm.keyframe(
                        attr, sl=True, query=True, timeChange=True, absolute=True
                    )
                    time_value_list.append(time_value)

        return attr_list, time_value_list, key_value_list

    def butterworth_filter(self, *args):
        """给给定的关键帧动画应用Butterworth过滤器。"""
        filter_value = pm.floatSliderButtonGrp(self.value_slider, q=True, v=True)
        scale_value = self.remap(0.0, 100.0, 1.0, -2.0, filter_value)
        pm.bufferCurve(animation="keys", overwrite=False)

        attr_list, time_value_list, key_value_list = self.get_keyframe_data()

        for i, attr in enumerate(attr_list):
            time_value = time_value_list[i]
            key_value = key_value_list[i]

            if len(key_value) >= 3:
                for j in range(1, len(key_value) - 1):
                    pre_value = key_value[j - 1]
                    cur_value = key_value[j]
                    nex_value = key_value[j + 1]
                    average_value = (pre_value + cur_value + nex_value) / 3
                    pm.scaleKey(
                        attr,
                        time=(time_value[j], time_value[j]),
                        valuePivot=average_value,
                        valueScale=scale_value,
                    )
                    pm.keyTangent(itt="auto", ott="auto")

    def dampon_filter(self, *args):
        """给给定的关键帧动画应用dampon过滤器"""
        filter_value = pm.floatSliderButtonGrp(self.value_slider, q=True, v=True)
        scale_value = self.remap(0.0, 100.0, 0.5, 1.5, filter_value)
        pm.bufferCurve(animation="keys", overwrite=False)

        attr_list, time_value_list, key_value_list = self.get_keyframe_data()

        for i, attr in enumerate(attr_list):
            time_value = time_value_list[i]
            key_value = key_value_list[i]

            if len(key_value) >= 2 and len(time_value) >= 2:
                tangent = (key_value[-1] - key_value[0]) / abs(
                    time_value[-1] - time_value[0]
                )
                for j in range(1, len(time_value) - 1):
                    scale_pivot = (
                        tangent * (time_value[j] - time_value[0]) + key_value[0]
                    )
                    pm.scaleKey(
                        attr,
                        time=(time_value[j], time_value[j]),
                        valuePivot=scale_pivot,
                        valueScale=scale_value,
                    )

    def smooth_filter(self, *args):
        """给给定的关键帧动画应用smooth过滤器"""
        filter_value = pm.floatSliderButtonGrp(self.value_slider, q=True, v=True)
        pm.bufferCurve(animation="keys", overwrite=False)

        attr_list, time_value_list, key_value_list = self.get_keyframe_data()

        for i, attr in enumerate(attr_list):
            time_value = time_value_list[i]
            key_value = key_value_list[i]
            if len(key_value) >= 3:
                for j in range(1, len(key_value) - 1):
                    pre_value = key_value[j - 1]
                    cur_value = key_value[j]
                    nex_value = key_value[j + 1]

                    average_value = (pre_value + cur_value + nex_value) / 3

                    pm.keyframe(
                        attr,
                        time=(time_value[j], time_value[j]),
                        valueChange=average_value,
                    )
        try:
            for i in range(filter_value):
                self.smooth_filter()
        except TypeError:
            pass

    def simplify_filter(self, *args):
        """对给定的关键帧动画应用simplify过滤器"""
        filter_value = pm.floatSliderButtonGrp(self.value_slider, q=True, v=True)
        scale_value = self.remap(0.0, 100.0, 0.0, 3.0, filter_value)

        pm.bufferCurve(animation="keys", overwrite=False)

        attr_list, time_value_list, _ = self.get_keyframe_data()

        for i, attr in enumerate(attr_list):
            time_value = time_value_list[i]
            if len(time_value) > 0:
                pm.simplify(
                    attr,
                    time=(time_value[0], time_value[-1]),
                    timeTolerance=scale_value,
                    floatTolerance=scale_value,
                    valueTolerance=scale_value,
                )
                pm.selectKey(
                    attr,
                    replace=True,
                    time=(time_value[0], time_value[-1]),
                )

    def twinner_filter(self, *args):
        """和Twinning machine工具类似"""
        filter_value = pm.floatSliderButtonGrp(self.value_slider, q=True, v=True)
        scale_value = self.remap(0.0, 100.0, 0, 1.0, filter_value)

        current_time = pm.currentTime(query=True)
        attr_list, time_value_list, key_value_list = self.get_keyframe_data()

        for attr in attr_list:
            current_value = pm.keyframe(attr, time=current_time, query=True, eval=True)
            if current_value:
                pre_time = pm.findKeyframe(attr, time=current_time, which="previous")
                pre_value = pm.keyframe(attr, time=pre_time, query=True, eval=True)
                next_time = pm.findKeyframe(attr, time=current_time, which="next")
                next_value = pm.keyframe(attr, time=next_time, query=True, eval=True)
                if pre_value and next_value:
                    if not pm.keyframe(attr, time=current_time, query=True):
                        pm.setKeyframe(attr, time=current_time)
                    if next_value[0] != pre_value[0]:
                        current_key_value = (
                            scale_value * (next_value[0] - pre_value[0]) + pre_value[0]
                        )
                        pm.keyframe(
                            attr, time=current_time, valueChange=current_key_value
                        )

    @staticmethod
    def anim_curve_reverse(*args):
        """将动画曲线返回修改前的状态"""
        try:
            pm.bufferCurve(animation="keys", swap=True)
            pm.bufferCurve(animation="keys", overwrite=True)
        except Exception as exc:
            print(exc)

    def reset_slider(self, *args):
        """重设浮点滑条"""
        try:
            pm.floatSliderButtonGrp(
                self.value_slider, edit=True, value=self.default_value
            )
        except Exception as exc:
            print(exc)

    @staticmethod
    def remap(i_min, i_max, o_min, o_max, v):
        """将一个线性比例尺上的值重新映射到另一个线性比例尺上"""
        return (1 - (v - i_min) / (i_max - i_min)) * o_min + (v - i_min) / (
            i_max - i_min
        ) * o_max


if __name__ == "__main__":
    curve_filter = AnimCurveFilter()
    curve_filter.create_ui()
