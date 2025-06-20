import pymel.core as pc
import maya.cmds as mc

GROUP = "grp"
JOINT = "jnt"
GUIDE = "gid"
JAW = "jaw"

LEFT = "L"
RIGHT = "R"
CENTER = "C"
UPPER = "upper"
LOWER = "lower"


def create_guides(number: int = 5):
    """Create guide curves in the scene.

    Args:
        number (int, optional): The number of guide locators to create. Defaults to 5.
    """
    jaw_guide_grp = pc.createNode("transform", name=f"{CENTER}_{JAW}_{GUIDE}_{GROUP}")
    locs_grp = pc.createNode(
        "transform", name=f"{CENTER}_{JAW}_lip_{GUIDE}_{GROUP}", parent=jaw_guide_grp
    )
    lip_locs_grp = pc.createNode(
        "transform", name=f"{CENTER}_lipMinor_{GUIDE}_{GROUP}", parent=locs_grp
    )
    # create locators
    for part in [UPPER, LOWER]:
        # 创建上下嘴唇中间定位器
        mid_loc = pc.spaceLocator(name=f"{CENTER}_{JAW}_{part}_lip_{GUIDE}")[0]
        pc.parent(mid_loc, lip_locs_grp)
        # 创建左右嘴唇定位器
        for side in [LEFT, RIGHT]:
            for x in range(number):
                # 计算位置
                multiplier = x + 1 if side == LEFT else -(x + 1)
                loc_data = (multiplier, part, 0)  # (x,y,z) coordinates
                # 创建定位器，
                # {:02d} 是字符串格式化（str.format()）中的一种占位符
                # 表示将一个整数格式化为至少2位数字，如果不足两位，则在左侧填充0。
                # d：表示格式化的值是一个十进制整数（decimal）
                loc = pc.spaceLocator(name=f"{side}_{JAW}_{part}_lip_{(x + 1):02d}")[0]
                pc.parent(loc, lip_locs_grp)
                pc.setAttr(f"{loc}.translate", *loc_data)  # 设置定位器位置
