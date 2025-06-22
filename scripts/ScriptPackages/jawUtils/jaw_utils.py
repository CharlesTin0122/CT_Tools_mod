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
        "transform", name=f"{CENTER}_{JAW}_lipMinor_{GUIDE}_{GROUP}", parent=locs_grp
    )
    # create locators
    for part in [UPPER, LOWER]:
        # 创建上下嘴唇中间定位器
        part_mult = 1 if part == UPPER else -1
        mid_data = (0, part_mult, 0)
        mid_loc = pc.spaceLocator(name=f"{CENTER}_{JAW}_{part}_lip_{GUIDE}")
        pc.parent(mid_loc, lip_locs_grp)
        # 创建左右嘴唇定位器
        for side in [LEFT, RIGHT]:
            for x in range(number):
                # 计算位置
                multiplier = x + 1 if side == LEFT else -(x + 1)
                loc_data = (multiplier, part_mult, 0)  # (x,y,z) coordinates
                # 创建定位器，
                # {:02d} 是字符串格式化（str.format()）中的一种占位符
                # 表示将一个整数格式化为至少2位数字，如果不足两位，则在左侧填充0。
                # d：表示格式化的值是一个十进制整数（decimal）
                loc = pc.spaceLocator(
                    name=f"{side}_{JAW}_{part}_lip_{GUIDE}_{(x + 1):02d}"
                )
                pc.parent(loc, lip_locs_grp)
                pc.setAttr(f"{loc}.translate", *loc_data)  # 设置定位器位置
        # 设置中间定位器
        pc.setAttr(f"{mid_loc}.translate", *mid_data)
    # 创建嘴角定位器
    left_corner_loc = pc.spaceLocator(name=f"{LEFT}_{JAW}_corner_lip_{GUIDE}")
    right_corner_loc = pc.spaceLocator(name=f"{RIGHT}_{JAW}_corner_lip_{GUIDE}")

    pc.parent(left_corner_loc, lip_locs_grp)
    pc.parent(right_corner_loc, lip_locs_grp)

    pc.setAttr(f"{left_corner_loc}.translate", *(number + 1, 0, 0))  # 设置定位器位置
    pc.setAttr(
        f"{right_corner_loc}.translate", *(-(number + 1), 0, 0)
    )  # 设置定位器位置
    pc.select(clear=True)  # 清除选择

    # 创建下颌定位器
    jaw_base_gid_grp = pc.createNode(
        "transform", name=f"{CENTER}_{JAW}_base_{GUIDE}_{GROUP}", parent=jaw_guide_grp
    )
    jaw_gid = pc.spaceLocator(name=f"{CENTER}_{JAW}_{GUIDE}")
    jaw_inverse_gid = pc.spaceLocator(name=f"{CENTER}_{JAW}_inverse_{GUIDE}")
    # 设置下颌定位器位置
    pc.setAttr(f"{jaw_gid}.translate", *(0, -1, -number))
    pc.setAttr(f"{jaw_inverse_gid}.translate", *(0, 1, -number))
    # 父级定位器
    pc.parent(jaw_gid, jaw_base_gid_grp)
    pc.parent(jaw_inverse_gid, jaw_base_gid_grp)

    pc.select(clear=True)  # 清除选择


def lip_guides():
    grp = f"{CENTER}_{JAW}_lipMinor_{GUIDE}_{GROUP}"
    return [loc for loc in pc.listRelatives(grp, children=True) if pc.objExists(grp)]


def jaw_guides():
    grp = f"{CENTER}_{JAW}_base_{GUIDE}_{GROUP}"
    return [grp for grp in pc.listRelatives(grp, children=True) if pc.objExists(grp)]


def create_hierachy():
    """Create the hierarchy for the jaw guides."""
    # 创建下颌组
    mian_grp = pc.createNode("transform", name=f"{CENTER}_{JAW}_rig_{GROUP}")
    lip_grp = pc.createNode(
        "transform", name=f"{CENTER}_{JAW}_lip_{GROUP}", parent=mian_grp
    )
    base_grp = pc.createNode(
        "transform", name=f"{CENTER}_{JAW}_base_{GROUP}", parent=mian_grp
    )
    # 创建嘴唇次级定位器组
    lip_minor_grp = pc.createNode(
        "transform",
        name=f"{CENTER}_{JAW}_lipMinor_{GROUP}",
        parent=lip_grp,
    )
    lip_broad_grp = pc.createNode(
        "transform",
        name=f"{CENTER}_{JAW}_lipBroad_{GROUP}",
        parent=lip_grp,
    )
    pc.select(clear=True)  # 清除选择


def add_offset(destination, suffix="offset"):
    """Add offset groups for the jaw guides."""
    # 创建偏移组
    offset_grp = pc.createNode("transform", name=f"{destination}_{suffix}")
    pc.matchTransform(offset_grp, destination, position=True, rotation=True)
    dst_parent = pc.listRelatives(destination, parent=True)
    if dst_parent:
        pc.parent(offset_grp, dst_parent[0])
    pc.parent(destination, offset_grp)  # 将目标组作为偏移组的子级
    return offset_grp


def create_minor_joints():
    """Create minor joints for the jaw guides."""
    minor_joints = list()
    for loc in lip_guides():
        # 获取定位器名称
        loc_name = pc.ls(loc, long=True)[0]
        # 创建关节
        joint = pc.joint(name=loc_name.replace(GUIDE, JOINT), radius=0.3)
        # 设置关节位置
        pc.matchTransform(joint, loc, position=True, rotation=True)
        # 父子关系
        pc.parent(joint, f"{CENTER}_{JAW}_lipMinor_{GROUP}")
        minor_joints.append(joint)
    return minor_joints


def create_broad_joints():
    """Create broad joints for the jaw guides."""
    upper_mid_joints = pc.joint(name=f"{CENTER}_{JAW}_broadUpper_{JOINT}", radius=0.5)
    pc.select(clear=True)
    lower_mid_joints = pc.joint(name=f"{CENTER}_{JAW}_broadLower_{JOINT}", radius=0.5)
    pc.select(clear=True)
    left_corner_joint = pc.joint(name=f"{LEFT}_{JAW}_broadCorner_{JOINT}", radius=0.5)
    pc.select(clear=True)
    right_corner_joint = pc.joint(name=f"{RIGHT}_{JAW}_broadCorner_{JOINT}", radius=0.5)
    pc.select(clear=True)
    # parent joints under broad group
    pc.parent(
        [upper_mid_joints, lower_mid_joints, left_corner_joint, right_corner_joint],
        f"{CENTER}_{JAW}_lipBroad_{GROUP}",
    )
    # 骨骼对位
    pc.matchTransform(upper_mid_joints, f"{CENTER}_{JAW}_upper_lip_{GUIDE}")
    pc.matchTransform(lower_mid_joints, f"{CENTER}_{JAW}_lower_lip_{GUIDE}")
    pc.matchTransform(left_corner_joint, f"{LEFT}_{JAW}_corner_lip_{GUIDE}")
    pc.matchTransform(right_corner_joint, f"{RIGHT}_{JAW}_corner_lip_{GUIDE}")
    pc.select(clear=True)  # 清除选择


def create_jaw_base_joint():
    """Create the base joint for the jaw."""
    jaw_base_joint = pc.joint(name=f"{CENTER}_{JAW}_{JOINT}", radius=1)
    jaw_inverse_joint = pc.joint(name=f"{CENTER}_{JAW}_inverse_{JOINT}", radius=1)
    # 设置关节位置
    pc.matchTransform(jaw_base_joint, f"{CENTER}_{JAW}_{GUIDE}")
    pc.matchTransform(jaw_inverse_joint, f"{CENTER}_{JAW}_inverse_{GUIDE}")
    # 父级关节
    pc.parent(jaw_base_joint, f"{CENTER}_{JAW}_base_{GROUP}")
    pc.parent(jaw_inverse_joint, f"{CENTER}_{JAW}_base_{GROUP}")
    pc.select(clear=True)  # 清除选择
    # add offset groups
    add_offset(jaw_base_joint, suffix="offset")
    add_offset(jaw_inverse_joint, suffix="offset")
    # 再次添加偏移组用于自动变换
    add_offset(jaw_base_joint, suffix="auto")
    add_offset(jaw_inverse_joint, suffix="auto")

    pc.select(clear=True)  # 清除选择


def constraint_broad_joints():
    """Constraint the broad joints to the guides."""
    # 获取主关节
    jaw_joint = f"{CENTER}_{JAW}_{JOINT}"
    jaw_inverse_joint = f"{CENTER}_{JAW}_inverse_{JOINT}"

    broad_upper_joint = f"{CENTER}_{JAW}_broadUpper_{JOINT}"
    broad_lower_joint = f"{CENTER}_{JAW}_broadLower_{JOINT}"
    left_corner_joint = f"{LEFT}_{JAW}_broadCorner_{JOINT}"
    right_corner_joint = f"{RIGHT}_{JAW}_broadCorner_{JOINT}"

    # add offset groups to broad joints
    upper_offset = add_offset(broad_upper_joint)
    lower_offset = add_offset(broad_lower_joint)
    left_offset = add_offset(left_corner_joint)
    right_offset = add_offset(right_corner_joint)
    # create constraints
    pc.parentConstraint(jaw_joint, lower_offset, maintainOffset=True)
    pc.parentConstraint(jaw_inverse_joint, upper_offset, maintainOffset=True)
    pc.parentConstraint(upper_offset, lower_offset, left_offset, maintainOffset=True)
    pc.parentConstraint(upper_offset, lower_offset, right_offset, maintainOffset=True)

    pc.select(clear=True)  # 清除选择


def get_lip_parts():
    """获取骨骼的约束骨骼字典
    Returns:
        dict: 字典的键为骨骼名称，值为该骨骼被约束骨骼列表
    """

    upper_token = "jaw_upper"
    lower_token = "jaw_lower"
    corner_token = "jaw_corner"

    c_upper = f"{CENTER}_{JAW}_broadUpper_{JOINT}"
    c_lower = f"{CENTER}_{JAW}_broadLower_{JOINT}"
    l_corner = f"{LEFT}_{JAW}_broadCorner_{JOINT}"
    r_corner = f"{RIGHT}_{JAW}_broadCorner_{JOINT}"
    # 列出群组的所有子对象
    lip_joints = mc.listRelatives(
        f"{CENTER}_{JAW}_lip_{GROUP}", type="joint", allDescendents=True
    )
    # 创建数据结构
    look_up = {
        "c_upper": {},
        "c_lower": {},
        "l_upper": {},
        "l_lower": {},
        "r_upper": {},
        "r_lower": {},
        "l_corner": {},
        "r_corner": {},
    }
    # 遍历所有关节，分类存储,字典的键为骨骼名称，值为该骨骼被约束骨骼列表
    for joint in lip_joints:
        if joint.startswith("C") and upper_token in joint:
            look_up["c_upper"][joint] = [c_upper]
        if joint.startswith("C") and lower_token in joint:
            look_up["c_lower"][joint] = [c_lower]

        if joint.startswith("L") and upper_token in joint:
            look_up["l_upper"][joint] = [c_upper, l_corner]
        if joint.startswith("L") and lower_token in joint:
            look_up["l_lower"][joint] = [c_lower, l_corner]
        if joint.startswith("R") and upper_token in joint:
            look_up["r_upper"][joint] = [c_upper, r_corner]
        if joint.startswith("R") and lower_token in joint:
            look_up["r_lower"][joint] = [c_lower, r_corner]

        if joint.startswith("L") and corner_token in joint:
            look_up["l_corner"][joint] = [l_corner]
        if joint.startswith("R") and corner_token in joint:
            look_up["r_corner"][joint] = [r_corner]
    return look_up


# Result: {'c_lower': {'C_jaw_lower_lip_jnt': ['C_jaw_broadLower_jnt']},
#  'c_upper': {'C_jaw_upper_lip_jnt': ['C_jaw_broadUpper_jnt']},
#  'l_corner': {'L_jaw_corner_lip_jnt': ['L_jaw_broadCorner_jnt']},
#  'l_lower': {'L_jaw_lower_lip_jnt_01': ['C_jaw_broadLower_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_lower_lip_jnt_02': ['C_jaw_broadLower_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_lower_lip_jnt_03': ['C_jaw_broadLower_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_lower_lip_jnt_04': ['C_jaw_broadLower_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_lower_lip_jnt_05': ['C_jaw_broadLower_jnt',
#                                         'L_jaw_broadCorner_jnt']},
#  'l_upper': {'L_jaw_upper_lip_jnt_01': ['C_jaw_broadUpper_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_upper_lip_jnt_02': ['C_jaw_broadUpper_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_upper_lip_jnt_03': ['C_jaw_broadUpper_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_upper_lip_jnt_04': ['C_jaw_broadUpper_jnt',
#                                         'L_jaw_broadCorner_jnt'],
#              'L_jaw_upper_lip_jnt_05': ['C_jaw_broadUpper_jnt',
#                                         'L_jaw_broadCorner_jnt']},
#  'r_corner': {'R_jaw_corner_lip_jnt': ['R_jaw_broadCorner_jnt']},
#  'r_lower': {'R_jaw_lower_lip_jnt_01': ['C_jaw_broadLower_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_lower_lip_jnt_02': ['C_jaw_broadLower_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_lower_lip_jnt_03': ['C_jaw_broadLower_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_lower_lip_jnt_04': ['C_jaw_broadLower_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_lower_lip_jnt_05': ['C_jaw_broadLower_jnt',
#                                         'R_jaw_broadCorner_jnt']},
#  'r_upper': {'R_jaw_upper_lip_jnt_01': ['C_jaw_broadUpper_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_upper_lip_jnt_02': ['C_jaw_broadUpper_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_upper_lip_jnt_03': ['C_jaw_broadUpper_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_upper_lip_jnt_04': ['C_jaw_broadUpper_jnt',
#                                         'R_jaw_broadCorner_jnt'],
#              'R_jaw_upper_lip_jnt_05': ['C_jaw_broadUpper_jnt',
#                                         'R_jaw_broadCorner_jnt']}}


def lip_part(part):
    """得到嘴唇骨骼从左向右的骨骼顺序
    Args:
        part (str): 关键字，upper 或 lower
    Returns:
        list: 左向右的骨骼顺序列表
    """
    lip_parts = [
        # 正向排序并反转得到逆序
        reversed(sorted(get_lip_parts()[f"l_{part}"].keys())),
        get_lip_parts()[f"c_{part}"].keys(),
        # 正向排序
        sorted(get_lip_parts()[f"r_{part}"].keys()),
    ]
    return [joint for joint in lip_parts for joint in joint]


def create_seal(part):
    """
    为每个minor骨骼创建密封变换，该变换用于将张开的嘴插值到封闭状态.
    密封变换受到左右嘴角的父子约束，约束权重为线性插值，
    靠近l_corner的minor骨骼，受到l_corner的约束权重更大，
    靠近r_corner的minor骨骼，受到r_corner的约束权重更大.
    Args:
        part (str): 关键字，upper 或 lower
    """
    # 创建密封组
    seal_name = f"{CENTER}_seal_{GROUP}"
    seal_parent = (
        seal_name
        if pc.objExists(seal_name)
        else pc.createNode(
            "transform", name=seal_name, parent=f"{CENTER}_{JAW}_rig_{GROUP}"
        )
    )
    part_group = pc.createNode(
        "transform", name=seal_name.replace("seal", f"seal_{part}"), parent=seal_parent
    )
    # 获取左右嘴角骨骼
    l_corner = f"{LEFT}_{JAW}_broadCorner_{JOINT}"
    r_corner = f"{RIGHT}_{JAW}_broadCorner_{JOINT}"
    # 获取嘴唇骨骼
    lip_part_count = len(lip_part(part))
    # 创建密封关节
    for index, joint in enumerate(lip_part(part)):
        # 创建关节
        node = pc.createNode(
            "transform", name=joint.replace(JOINT, f"{part}_seal"), parent=part_group
        )
        # 设置关节位置
        pc.matchTransform(node, joint, position=True, rotation=True)
        # 设置关节的约束
        constraint = pc.parentConstraint(l_corner, r_corner, node, maintainOffset=True)
        # interpType 是父子约束的一个属性，这个属性决定了如何混合计算这些目标的旋转值
        # 0:NoFlip, 1:Average, 2:Shortest, 3:Longest, 4:Cache
        constraint.interpType.set(2)
        # 设置约束权重,如果有5个骨骼，那么第5个骨骼的权重就是：4/(5-1)=1.0，因为lip_part_count比index多1
        # l_corner对minor骨骼的约束权重是从左向右1.0到0.0递减，
        # r_corner对minor骨骼的约束权重是从右向左1.0到0.0递减
        r_corner_weight = float(index) / float(lip_part_count - 1)
        l_corner_weight = 1.0 - r_corner_weight
        # 设置约束权重
        constraint.getWeightAliasList()[0].set(l_corner_weight)
        constraint.getWeightAliasList()[1].set(r_corner_weight)
        pc.select(clear=True)  # 清除选择


def create_jaw_attrs():
    # 创建一个变换承载属性
    node = pc.createNode(
        "transform", name="jaw_attributes", parent=f"{CENTER}_{JAW}_rig_{GROUP}"
    )
    # 添加C_jaw_upper_lip_jnt属性并锁定为0
    pc.addAttr(
        node,
        longName=sorted(get_lip_parts()["c_upper"].keys())[0],
        attributeType="double",
        min=0,
        max=1,
        defaultValue=0,
    )
    pc.setAttr(f"{node}.{sorted(get_lip_parts()['c_upper'].keys())[0]}", lock=True)
    # 添加L_jaw_upper_lip_jnt_01：05属性
    for joint in sorted(get_lip_parts()["l_upper"].keys()):
        pc.addAttr(
            node,
            longName=joint,
            attributeType="double",
            min=0,
            max=1,
            defaultValue=0,
        )
    # 添加L_jaw_corner_lip_jnt属性,并锁定
    pc.addAttr(
        node,
        longName=sorted(get_lip_parts()["l_corner"].keys())[0],
        attributeType="double",
        min=0,
        max=1,
        defaultValue=0,
    )
    pc.setAttr(f"{node}.{sorted(get_lip_parts()['l_corner'].keys())[0]}", lock=True)
    # 添加L_jaw_lower_lip_jnt_01：05属性,并反向排序：list[start=None : stop=None : step=-1]
    for joint in sorted(get_lip_parts()["l_lower"].keys())[::-1]:
        pc.addAttr(
            node,
            longName=joint,
            attributeType="double",
            min=0,
            max=1,
            defaultValue=0,
        )
    # 添加C_jaw_lower_lip_jnt属性并锁定为0
    pc.addAttr(
        node,
        longName=sorted(get_lip_parts()["c_lower"].keys())[0],
        attributeType="double",
        min=0,
        max=1,
        defaultValue=0,
    )
    pc.setAttr(f"{node}.{sorted(get_lip_parts()['c_lower'].keys())[0]}", lock=True)


def create_minor_constraints():
    """
    minor骨骼的约束关系：
    C_jaw_upper_lip_jnt，上唇中间骨骼受C_jaw_broadUpper_jnt骨骼和C_jaw_upper_lip_upper_seal的约束
    L_jaw_corner_lip_jnt，左嘴角骨骼受L_jaw_broadCorner_jnt骨骼的约束
    C_jaw_upper_lip_jnt到L_jaw_corner_lip_jnt中间骨骼受C_jaw_broadUpper_jnt、L_jaw_broadCorner_jnt和对应seal的约束
    """
    for value in get_lip_parts().values():
        for lip_jnt, broad_jnt in value.items():
            # 获取嘴唇密封组名称
            seal_token = "upper_seal" if "upper" in lip_jnt else "lower_seal"
            lip_seal = lip_jnt.replace(JOINT, seal_token)

            # 设置约束，如果存在对应的lip_seal，使用broad_jnt, lip_seal约束lip_jnt
            if pc.objExists(lip_seal):
                constr = pc.parentConstraint(
                    broad_jnt, lip_seal, lip_jnt, maintainOffset=True
                )
                constr.interpType.set(2)
                # 设置约束权重
                # 如果只存在一个broad_jnt说明是嘴唇中间骨骼，使broad和seal权重0：1相反
                if len(broad_jnt) == 1:
                    seal_attr = f"{lip_jnt}_parentConstraint1.{lip_seal}W1"
                    rev_node = pc.createNode(
                        "reverse", name=lip_jnt.replace(JOINT, "rev")
                    )
                    pc.connectAttr(seal_attr, f"{rev_node}.inputX")
                    pc.connectAttr(
                        f"{rev_node}.outputX",
                        f"{lip_jnt}_parentConstraint1.{broad_jnt[0]}W0",
                    )
                    pc.setAttr(seal_attr, 0)  # 设置seal的权重为0
                """
                如果存在两个broad_jnt，说明是嘴唇两侧骨骼
                我们要让两个broad骨骼的约束权重0:1互斥，然后seal的约束权重跟两个broad骨骼的约束权重再次0:1互斥
                seal的约束权重为0的时候，两个broad_jnt的约束权重为0:1互斥，
                seal的约束权重为1的时候，两个broad_jnt的约束权重均为0
                实现：
                1.使用reverse节点使两个broad_jnt的约束权重为0:1互斥
                2.使用reverse节点和一个乘法节点使seal的约束权重与两个broad_jnt0:1互斥（乘以0，乘以1）
                """
                if len(broad_jnt) == 2:
                    seal_attr = f"{lip_jnt}_parentConstraint1.{lip_seal}W2"
                    pc.setAttr(seal_attr, 0)  # 设置seal的权重为0
                    seal_rev_node = pc.createNode(
                        "reverse", name=lip_jnt.replace(JOINT, "seal_rev")
                    )
                    broad_rev_node = pc.createNode(
                        "reverse", name=lip_jnt.replace(JOINT, "broad_rev")
                    )
                    seal_mult_node = pc.createNode(
                        "multiplyDivide", name=lip_jnt.replace(JOINT, "seal_mult")
                    )

                    pc.connectAttr(seal_attr, f"{seal_rev_node}.inputX")
                    pc.connectAttr(
                        f"{seal_rev_node}.outputX", f"{seal_mult_node}.input2X"
                    )
                    pc.connectAttr(
                        f"{seal_rev_node}.outputX",
                        f"{seal_mult_node}.input2Y",
                    )

                    pc.connectAttr(
                        f"jaw_attributes.{lip_jnt.replace(lip_jnt[0], 'L')}",
                        f"{seal_mult_node}.input1Y",
                    )
                    pc.connectAttr(
                        f"jaw_attributes.{lip_jnt.replace(lip_jnt[0], 'L')}",
                        f"{broad_rev_node}.inputX",
                    )
                    pc.connectAttr(
                        f"{broad_rev_node}.outputX",
                        f"{seal_mult_node}.input1X",
                    )

                    pc.connectAttr(
                        f"{seal_mult_node}.outputX",
                        f"{lip_jnt}_parentConstraint1.{broad_jnt[0]}W0",
                    )
                    pc.connectAttr(
                        f"{seal_mult_node}.outputY",
                        f"{lip_jnt}_parentConstraint1.{broad_jnt[1]}W1",
                    )

            else:  # 如果不存在对应的lip_seal，只使用broad_jnt约束lip_jnt
                constr = pc.parentConstraint(broad_jnt, lip_jnt, maintainOffset=True)
                constr.interpType.set(2)


def create_initial_values(part, degree=1.3):
    # 获取左侧minor骨骼
    jaw_attr = [
        jnt
        for jnt in lip_part(part)
        if not jnt.startswith("C") and not jnt.startswith("R")
    ]
    count = len(jaw_attr)
    # 遍历骨骼计算初始值
    for index, attr_name in enumerate(jaw_attr[::-1]):
        attr = f"jaw_attributes.{attr_name}"
        # 计算线性值，从0到1的递增值
        linear_value = float(index) / float(count - 1)
        # 线性值除以 degree (1.3)。这会稍微减小这个值
        div_value = linear_value / degree
        # 将上一步的结果与 linear_value 再次相乘。这实际上是在进行一个 平方 操作
        # 会产生一个 非线性的、加速的曲线。
        # 当 linear_value 接近 0 时，mult_value 会更小；当 linear_value 接近 1 时，mult_value 会急剧增长并接近 1/degree 的值。
        mult_value = div_value * linear_value
        pc.setAttr(attr, mult_value)


def create_offset_follow():
    jaw_attr = "jaw_attributes"
    jaw_joint = f"{CENTER}_{JAW}_{JOINT}"
    jaw_auto_grp = f"{CENTER}_{JAW}_{JOINT}_auto"

    pc.addAttr(
        jaw_attr,
        longName="follow_ty",
        attributeType="double",
        min=-10,
        max=10,
        defaultValue=0,
    )
    pc.addAttr(
        jaw_attr,
        longName="follow_tz",
        attributeType="double",
        min=-10,
        max=10,
        defaultValue=0,
    )

    unit_node = pc.createNode("unitConversion", name=f"{CENTER}_{JAW}_follow_unit")

    remap_y_node = pc.createNode("remapValue", name=f"{CENTER}_{JAW}_follow_y_remap")
    pc.setAttr(f"{remap_y_node}.inputmax", 1)

    remap_z_node = pc.createNode("remapValue", name=f"{CENTER}_{JAW}_follow_z_remap")
    pc.setAttr(f"{remap_z_node}.inputmax", 1)

    mult_y_node = pc.createNode(
        "multDoubleLinear", name=f"{CENTER}_{JAW}_follow_y_mult"
    )
    pc.setAttr(f"{mult_y_node}.input2", -1)

    pc.connectAttr(f"{jaw_joint}_rx", f"{unit_node}.input")
    pc.connectAttr(f"{unit_node}_output", f"{remap_y_node}.inputValue")
    pc.connectAttr(f"{unit_node}_output", f"{remap_z_node}.inputValue")

    pc.connectAttr(f"{jaw_attr}.follow_ty", f"{mult_y_node}.input1")
    pc.connectAttr(f"{jaw_attr}.follow_tz", f"{remap_z_node}.outputMax")
    pc.connectAttr(f"{remap_y_node}.output", f"{jaw_auto_grp}.ty")


def build():
    """Build the jaw guides and joints."""
    create_hierachy()  # 创建分组层级
    create_minor_joints()  # 创建次级关节
    create_broad_joints()  # 创建主关节
    create_jaw_base_joint()  # 创建下颌关节
    constraint_broad_joints()  # 下颌关节约束主关节
    create_seal("upper")  # 创建上唇密封关节
    create_seal("lower")  # 创建下唇密封关节
    create_jaw_attrs()  # 创建下颌属性承载节点
    create_minor_constraints()  # 创建次级关节约束关系
    create_initial_values("upper")  # 创建上唇初始值
    create_initial_values("lower")  # 创建下唇初始值:
