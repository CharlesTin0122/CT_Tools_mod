import pymel.core as pm


def zeroOut(node_name: str = ""):
    """
    为指定或选定的节点创建一个偏移组。

    Args:
        node_name (str, optional): 要处理的单个节点的名称。
                                   如果为空字符串，则处理当前选择的节点。
                                   默认为 ""。

    Returns:
        List[pm.nt.Transform]: 一个包含所有新创建的偏移组的 PyMEL 节点列表。
    """
    target_nodes = []
    # 如果没有提供节点名，则获取当前选择
    if not node_name:
        target_nodes = pm.ls(selection=True)
        if not target_nodes:
            pm.warning("No node name provided and nothing is selected.")
            return []
    else:
        # 如果提供了名称，确保它存在并将其放入列表中
        if pm.objExists(node_name):
            # 使用 pm.PyNode 将字符串转换为 PyMEL 对象
            target_nodes = [pm.PyNode(node_name)]
        else:
            pm.warning(f"Node '{node_name}' does not exist.")
            return []

    zero_groups = []

    # 遍历所有目标节点
    for node in target_nodes:
        # --- 1. 创建唯一的组名 ---
        # 获取节点短名称并首字母大写
        # e.g., "myJoint" -> "MyJoint"
        capitalized_name = node.name()

        # 构建基础名称
        base_name = f"{capitalized_name}_offset"
        name = base_name

        # 如果名称已存在，添加数字后缀以确保唯一性
        num = 1
        while pm.objExists(name):
            num += 1
            name = f"{capitalized_name}_offset_{num}"

        # --- 2. 创建并放置归零组 ---
        # 创建一个空组在世界中心
        grp = pm.group(empty=True, world=True, name=name)

        # 获取原节点的父节点
        parent = node.getParent()

        # 如果原节点有父节点，将新组移动到同一个父节点下
        if parent:
            pm.parent(grp, parent)

        dupe = pm.duplicate(node, renameChildren=True)[0]

        # b. 执行对齐 (调用 MEL 过程)
        #    ndsSnap(source, target)
        pm.matchTransform(dupe, grp)

        # c. 删除临时复制体
        pm.delete(dupe)

        # --- 4. 重新设置父子关系 ---
        # 将原始节点设置为新归零组的子节点
        pm.parent(node, grp)

        # 将新创建的组添加到返回列表中
        zero_groups.append(grp)

    # 重新选择最初的节点，保持用户体验一致
    pm.select(target_nodes, replace=True)

    # 返回所有创建的归-零组
    return zero_groups


if __name__ == "__main__":
    zeroOut()
