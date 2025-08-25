FILTER_MODES = {
    "Butterworth": {
        "tip": "在最大限度保持曲线细节的情况下, 对曲线进行一些光滑。",
        "slider_range": (0, 100),
        "default_value": 0,
        "SingleStep": 1,
        "PageStep": 10,
        "remap_range": (
            1.0,
            -2.0,
        ),  # remap (input_min, input_max, output_min, output_max)
    },
    "Dampen": {
        "tip": "在保持曲线连续性的情况下, 增加或减少曲线的振幅。",
        "slider_range": (0, 100),
        "default_value": 50,
        "SingleStep": 1,
        "PageStep": 10,
        "remap_range": (0.5, 1.5),
    },
    "Smooth": {
        "tip": "对曲线进行大幅度的光滑处理, 会过滤掉很多动画细节。",
        "slider_range": (1, 5),
        "default_value": 1,
        "SingleStep": 1,
        "PageStep": 1,
        "remap_range": None,
    },
    "Simplify": {
        "tip": "对动画曲线进行简化，减少关键帧。",
        "slider_range": (0, 100),
        "default_value": 0,
        "SingleStep": 1,
        "PageStep": 10,
        "remap_range": (0.0, 3.0),
    },
    "Twinner": {
        "tip": "根据前后帧的值按照比例插值添加中间帧。",
        "slider_range": (0, 100),
        "default_value": 50,
        "SingleStep": 1,
        "PageStep": 10,
        "remap_range": (0.0, 1.0),
    },
}
