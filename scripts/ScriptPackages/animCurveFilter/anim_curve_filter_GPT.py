from functools import partial
import pymel.core as pm


class AnimCurveFilter:
    FILTER_TYPES = {
        "butterworth": {
            "default_value": 0,
            "func": "butterworth_filter",
            "args": {
                "minValue": 0.0,
                "maxValue": 100.0,
                "description": "在最大限度保持曲线细节的情况下, 对曲线进行一些光滑.",
            },
        },
        "dampon": {
            "default_value": 50,
            "func": "dampon_filter",
            "args": {
                "minValue": 0.0,
                "maxValue": 100.0,
                "description": "在保持曲线连续性的情况下, 对曲线上选择的点增加或减少曲线的振幅.",
            },
        },
        "smooth": {
            "default_value": 0,
            "func": "smooth_filter",
            "args": {
                "minValue": 1,
                "maxValue": 5,
                "precision": 0,
                "step": 1.0,
                "fieldStep": 1.0,
                "sliderStep": 1.0,
                "description": "忽略最大限度的保持曲线细节, 对曲线进行大幅度的光滑. 需谨慎使用.",
            },
        },
        "simplify": {
            "default_value": 0,
            "func": "simplify_filter",
            "args": {
                "minValue": 0.0,
                "maxValue": 100.0,
                "description": "对动画曲线进行简化，减少关键帧.",
            },
        },
        "twinner": {
            "default_value": 50.0,
            "func": "twinner_filter",
            "args": {
                "minValue": 0.0,
                "maxValue": 100.0,
                "description": "根据前后帧的值按照比例插值添加中间帧。",
            },
        },
    }

    def __init__(self):
        self.filter_radioCol = None
        self.value_slider = None
        self.default_value = 0
        self.keyframe_data = {}

    def create_ui(self, *args):
        try:
            pm.deleteUI("FilterCurve")
        except Exception as exc:
            print(exc)

        main_window = pm.window("FilterCurve", title="Curve filter")
        pm.columnLayout()

        self.filter_radioCol = pm.radioCollection()

        for filter_name, filter_info in self.FILTER_TYPES.items():
            pm.radioButtonGrp(
                numberOfRadioButtons=3 if filter_name != "smooth" else 1,
                shareCollection=self.filter_radioCol,
                label="filters: ",
                labelArray3=(
                    ["butterworth", "Dampen", "Smooth"]
                    if filter_name != "smooth"
                    else ["Smooth"]
                ),
                select=1 if filter_name == "butterworth" else 0,
                changeCommand=partial(self.switch_filter, filter_name),
                **filter_info["args"],
            )

        self.value_slider = pm.floatSliderButtonGrp(
            label="Value: ",
            field=True,
            dragCommand=self.filter_drag_command,
            changeCommand=self.reset_slider,
            buttonLabel="reverse",
            buttonCommand=self.anim_curve_reverse,
            **self.FILTER_TYPES["butterworth"]["args"],
        )

        for filter_name, filter_info in self.FILTER_TYPES.items():
            pm.text(
                label=f"{filter_name.capitalize()}: {filter_info['description']}",
                align="center",
            )

        pm.showWindow(main_window)

    def switch_filter(self, filter_type, *args):
        """
        Switches the filter based on the given filter type.

        Parameters:
            filter_type (str): The type of filter to switch to.
            *args: Additional arguments to pass to the filter function.

        Returns:
            None
        """
        self.default_value = self.FILTER_TYPES[filter_type]["default_value"]
        self.update_slider_args(self.FILTER_TYPES[filter_type]["args"])

    def update_slider_args(self, args):
        """
        Updates the arguments of the float slider button group with the given dictionary of key-value pairs.

        Parameters:
            args (dict): A dictionary containing the key-value pairs to update the slider button group.

        Returns:
            None
        """
        for key, value in args.items():
            pm.floatSliderButtonGrp(self.value_slider, edit=True, **{key: value})

    def filter_drag_command(self, *args):
        """
        Executes the filter function based on the selected filter type.

        Parameters:
            *args: Additional arguments to be passed to the filter function.

        Returns:
            None
        """
        filter_type = pm.radioCollection(self.filter_radioCol, query=True, select=True)
        if filter_type:
            filter_func = getattr(self, self.FILTER_TYPES[filter_type]["func"])
            filter_func()

    def get_keyframe_data(self, *args):
        """
        Retrieves keyframe data for selected objects.
        
        Parameters:
            *args: Additional arguments (not used in the current implementation).
        
        Returns:
            Tuple containing lists of attribute names, time values, and key values.
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
                        attr, sl=True, query=True, valueChange=True, absolute=True
                    )
                    key_value_list.append(key_value)

                    time_value = pm.keyframe(
                        attr, sl=True, query=True, timeChange=True, absolute=True
                    )
                    time_value_list.append(time_value)

        return attr_list, time_value_list, key_value_list

    def butterworth_filter(self, *args):
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
            attr_list,
            replace=True,
            time=(time_value_list[0][0], time_value_list[0][-1]),
        )

    def twinner_filter(self, *args):
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
        try:
            pm.bufferCurve(animation="keys", swap=True)
            pm.bufferCurve(animation="keys", overwrite=True)
        except Exception as exc:
            print(exc)

    def reset_slider(self, *args):
        try:
            pm.floatSliderButtonGrp(
                self.value_slider, edit=True, value=self.default_value
            )
        except Exception as exc:
            print(exc)

    @staticmethod
    def remap(i_min, i_max, o_min, o_max, v):
        return (1 - (v - i_min) / (i_max - i_min)) * o_min + (v - i_min) / (
            i_max - i_min
        ) * o_max


if __name__ == "__mian__":
    acf = AnimCurveFilter()
    acf.create_ui()
