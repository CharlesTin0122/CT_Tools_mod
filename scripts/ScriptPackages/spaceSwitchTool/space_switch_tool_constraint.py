import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


def addSpaceSwitching(
    target_node: nt.Transform,
    target_group: nt.Transform,
    switch_attributre: str,
    switch_constraint: str,
    driver_list: list[nt.Transform],
    enum_item_list=None,
) -> None:
    """为目标节点添加空间切换功能

    Args:
        target_node (nt.Transform): 要添加空间切换的目标节点
        target_group (nt.Transform): 要添加空间切换的目标节点的父级组
        switch_attributre (str): 要添加到目标节点的枚举属性名称，一般为"Follow"
        switch_constraint (str): 约束类型：parent，orient, point
        driver_list (list[nt.Transform]): 驱动节点列表
        enum_item_list (list[str]):要添加到目标节点的枚举项
    """
    if not enum_item_list:
        enum_item_list = [node.name() for node in driver_list]
    # 添加空间切换空间切换的枚举属性
    if not target_node.hasAttr(switch_attributre):
        target_node.addAttr(
            switch_attributre,
            attributeType="enum",
            enumName=":".join(enum_item_list),  # 枚举选项
            defaultValue=0,
            keyable=True,
        )
    # 创建定位器
    loc_list = []
    for node in driver_list:
        driver_loc = pm.spaceLocator(name=f"{node.name()}_loc")
        pm.hide(driver_loc)
        pm.parent(driver_loc, node)
        pm.matchTransform(driver_loc, target_node)
        loc_list.append(driver_loc)
    # 创建约束
    constraint_node = None
    if switch_constraint == "parent":
        constraint_node = pm.parentConstraint(
            loc_list, target_group, maintainOffset=True
        )
    elif switch_constraint == "orient":
        constraint_node = pm.orientConstraint(
            loc_list, target_group, maintainOffset=True
        )
    elif switch_constraint == "point":
        constraint_node = pm.pointConstraint(
            loc_list, target_group, maintainOffset=True
        )
    # 检查约束是否成功创建
    if not constraint_node:
        pm.warning(f"无效的约束类型: '{switch_constraint}'。空间切换设置失败。")
        return
    # 直接获取权重属性列表，而不是手动拼接字符串
    weight_alias_list = constraint_node.getWeightAliasList()
    # 连接节点
    for i, node in enumerate(driver_list):
        condition_node = pm.createNode(
            "condition", name=f"{enum_item_list[i]}_condition"
        )
        condition_node.operation.set(0)  # Equal
        condition_node.secondTerm.set(i)
        condition_node.colorIfTrueR.set(1)
        condition_node.colorIfFalseR.set(0)

        target_node.attr(switch_attributre).connect(condition_node.firstTerm)
        condition_node.outColorR.connect(weight_alias_list[i])


def seamless_space_switch(
    target_node: nt.Transform,
    target_group: nt.Transform,
    switch_attribute: str,
    new_space_index: int,
) -> None:
    """
    执行无缝的空间切换，确保目标节点在切换时世界空间位置不变。

    Args:
        target_node (nt.Transform): 带有空间切换属性的控制器。
        switch_attribute (str): 控制空间切换的枚举属性的名称 (例如 "Follow")。
        new_space_index (int): 要切换到的新空间的索引值 (枚举的整数值)。
    """
    # 为前一帧设置关键帧
    current_frame = pm.currentTime()
    pre_frame = current_frame - 1
    pm.setKeyframe(target_node.attr(switch_attribute), time=pre_frame)

    # 在切换前，记录下控制器当前的世界矩阵
    original_world_matrix = target_node.getMatrix(worldSpace=True)

    # 执行切换：设置枚举属性为新的值,这会导致 target_group 发生跳变
    try:
        target_node.attr(switch_attribute).set(new_space_index)
    except Exception as e:
        pm.warning(f"无法设置属性 '{switch_attribute}' 为 {new_space_index}。错误: {e}")
        return

    # 计算补偿矩阵
    ## 获取 target_group 在新位置下的世界矩阵及其逆矩阵
    new_parent_world_matrix = target_group.getMatrix(worldSpace=True)
    new_parent_world_inverse_matrix = new_parent_world_matrix.inverse()

    # 计算出控制器新的本地矩阵,新本地矩阵 = 旧世界矩阵 * 新父级逆世界矩阵
    new_local_matrix = original_world_matrix * new_parent_world_inverse_matrix

    # 应用新的本地变换到控制器上,使用TransformationMatrix来方便地提取平移和旋转值
    xform_matrix = dt.TransformationMatrix(new_local_matrix)
    translation = xform_matrix.getTranslation("world")
    # getRotation() 返回弧度(radians)，需要转换为角度(degrees)
    rotation = xform_matrix.getRotation()
    rotation_in_degrees = [dt.degrees(angle) for angle in rotation]
    # 设置位移和旋转
    target_node.translate.set(translation)
    target_node.rotate.set(rotation_in_degrees)

    # 在当前帧K上关键帧
    pm.setKeyframe(target_node, attribute=["translate", "rotate"])
    pm.setKeyframe(target_node.attr(switch_attribute))

    print(f"空间已切换到索引 {new_space_index}，并已自动K帧。")
