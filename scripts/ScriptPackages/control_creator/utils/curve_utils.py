import pymel.core as pc


def validate_nurbs_curve(curve_transform):
    """验证是否为有效 NURBS 曲线"""
    curve_shape = curve_transform.getShape()
    if not curve_shape or not isinstance(curve_shape, pc.nodetypes.NurbsCurve):
        pc.warning(f"{curve_transform.name()} 不是有效的 NURBS 曲线。")
        return None
    return curve_shape


def extract_curve_data(curve_shape):
    """提取曲线几何数据"""
    return {
        "cvs": [list(cv)[:3] for cv in curve_shape.getCVs(space="object")],
        "knots": list(curve_shape.getKnots()),
        "degree": curve_shape.degree(),
        "form": curve_shape.form().index,
    }


def extract_color_attributes(curve_shape):
    """提取曲线颜色属性"""
    return {
        "overrideEnabled": curve_shape.overrideEnabled.get(),
        "overrideRGBColors": curve_shape.overrideRGBColors.get(),
        "overrideColorRGB": list(curve_shape.overrideColorRGB.get()),
        "useOutlinerColor": curve_shape.useOutlinerColor.get(),
        "outlinerColor": list(curve_shape.outlinerColor.get()),
        "overrideColor": curve_shape.overrideColor.get(),
    }


def get_curve_info(curve_transform):
    """获取曲线信息"""
    curve_shape = validate_nurbs_curve(curve_transform)
    if not curve_shape:
        return None
    shape_name = curve_shape.name()
    curve_data = extract_curve_data(curve_shape)
    curve_data.update(extract_color_attributes(curve_shape))
    return {shape_name: curve_data}
