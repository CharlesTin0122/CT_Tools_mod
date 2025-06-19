import pymel.core as pc
import maya.cmds as mc


def split_animation(start_frame, end_frame, init_pose_frame, Judgment_jnt):
    """根据骨骼的初始Pose，分割动画

    Args:
        start_frame (int): 动画开始帧数
        end_frame (int): 动画结束帧数
        init_pose_frame (int): 动画初始姿态帧数
        Judgment_jnt (str): 判断所使用的骨骼
    """
    # 获取判定骨骼的属性值列表
    Judgment_joint = pc.PyNode(Judgment_jnt)
    mc.currentTime(init_pose_frame)
    attrs = pc.listAnimatable(Judgment_joint)
    attr_val_list1 = []
    for attr in attrs:
        attr_val = round(attr.get(), 6)
        attr_val_list1.append(attr_val)
    print(attr_val_list1)
    # 用于储存属性相同的帧数
    anim_clip_frame = []
    # 遍历时间栏，对比属性
    for i in range(start_frame, end_frame + 1):
        mc.currentTime(i)
        attr_val_list2 = []
        for attr in attrs:
            attr_val = round(attr.get(), 6)
            attr_val_list2.append(attr_val)
        if attr_val_list2 == attr_val_list1:
            anim_clip_frame.append(i)
    print(anim_clip_frame)


if __name__ == "__main__":
    split_animation(0, 2870, 0, "Bip01FBXASC045Neck")

a = [
    0,
    60,
    61,
    95,
    121,
    122,
    212,
    213,
    264,
    303,
    304,
    466,
    508,
    509,
    599,
    600,
    765,
    766,
    826,
    827,
    928,
    929,
    1049,
    1132,
    1202,
    1215,
    1241,
    1292,
    1463,
    1615,
    1795,
    1856,
    1918,
    1979,
    2039,
    2040,
    2160,
    2161,
    2281,
    2282,
    2327,
    2328,
    2373,
    2399,
    2459,
    2699,
    2761,
    2821,
]
