import pymel.core as pc
from PySide2 import QtWidgets, QtGui


class ColorManager:
    """管理控制器颜色，包括索引和 RGB 模式"""

    def __init__(self, default_index=17):
        self.default_color_index = default_index
        self.current_rgb_color = pc.colorIndex(default_index, q=True)
        self.use_index_mode = True

    def pick_color(self, swatch):
        """打开颜色编辑器并更新颜色"""
        # 获取控件的背景颜色
        initial_color = swatch.palette().color(QtGui.QPalette.Background).getRgbF()[:3]
        pc.colorEditor(rgb=initial_color)
        if not pc.colorEditor(query=True, result=True):
            pc.displayInfo("颜色选择已取消。")
            return False
        rgb_color = pc.colorEditor(query=True, rgb=True)
        self.current_rgb_color = rgb_color
        if self.use_index_mode:
            self.default_color_index = self._find_closest_index(rgb_color)
            swatch.setStyleSheet(
                f"background-color: rgb({self.current_rgb_color[0] * 255}, {self.current_rgb_color[1] * 255}, {self.current_rgb_color[2] * 255});"
            )
            pc.displayInfo(f"选择了索引颜色: {self.default_color_index}")
        else:
            swatch.setStyleSheet(
                f"background-color: rgb({rgb_color[0] * 255}, {rgb_color[1] * 255}, {rgb_color[2] * 255});"
            )
            pc.displayInfo(f"选择了RGB颜色: {rgb_color}")
        return True

    def _find_closest_index(self, rgb_color):
        """找到最接近的 Maya 索引颜色"""
        min_dist = float("inf")
        closest_index = 0
        for i in range(32):
            index_rgb = pc.colorIndex(i, q=True)
            dist = sum([(rgb_color[j] - index_rgb[j]) ** 2 for j in range(3)])
            if dist < min_dist:
                min_dist = dist
                closest_index = i
        return closest_index

    def toggle_mode(self, use_index):
        """切换颜色模式（索引或 RGB）"""
        self.use_index_mode = use_index
        pc.displayInfo(f"颜色模式: {'索引' if use_index else 'RGB'}")

    def apply_color_to_curve(
        self, curve_shape, curve_data, new_color_index=None, new_rgb_color=None
    ):
        """应用颜色到曲线形状"""
        if new_color_index is not None:
            curve_shape.overrideEnabled.set(True)
            curve_shape.overrideRGBColors.set(False)
            curve_shape.overrideColor.set(new_color_index)
        elif new_rgb_color is not None:
            curve_shape.overrideEnabled.set(True)
            curve_shape.overrideRGBColors.set(True)
            curve_shape.overrideColorRGB.set(new_rgb_color)
        elif curve_data.get("overrideEnabled"):
            curve_shape.overrideEnabled.set(curve_data["overrideEnabled"])
            curve_shape.overrideRGBColors.set(curve_data["overrideRGBColors"])
            if curve_data["overrideRGBColors"]:
                curve_shape.overrideColorRGB.set(curve_data["overrideColorRGB"])
            elif "overrideColor" in curve_data:
                curve_shape.overrideColor.set(curve_data["overrideColor"])
