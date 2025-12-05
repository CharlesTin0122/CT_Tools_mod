import pymel.core as pm
import pymel.core.nodetypes as nt


DIRPATH = r"H:\MetaHuman\blendshape_transfer\blendshapetransferfiles"


def find_blendshape_info(source_mesh: nt.Transform | nt.Mesh) -> list:
    """用于返回给出模型的混合变形信息，包含名称和属性

    Args:
        source_mesh (pc.nodetypes.Transform): 给出的源模型

    Returns:
        list: 混合变形信息列表
    """

    blendshapes = pm.listHistory(source_mesh, type="blendShape")

    # 通过blendshape.listAliases()，获取混合变形信息。
    bs_info_list = []
    for blendshape in blendshapes:
        # [('Breathe', Attribute('blendShape1.weight[0]')),...]
        bs_infos = blendshape.listAliases()
        bs_info_list.extend(bs_infos)

    return bs_info_list


def transfer_blendshape_targets(mesh_a, mesh_b):
    pass


def transfer_blendshape_targets_sameTopo(
    source_mesh: nt.Transform, target_mesh: nt.Transform
):
    # 模型A的变形目标组
    target_grp_name = "grp_trgt"
    # 创建组用于接收输出的变形目标
    grp_output = pm.createNode("transform", name=f"grp_{target_mesh}")
    # 模型A变形目标列表
    target_list = [
        target for target in pm.listRelatives(target_grp_name, children=True)
    ]
    # 模型A 变形目标列表添加 模型B
    target_list.append(target_mesh)
    # 创建混合变形，并设置全中初始值，最后一个 target（mesh_b） 设置权重为 1，其他都是 0
    blendShape_source_mesh = pm.blendShape(
        target_list,
        source_mesh,
        name=f"blendshape_{source_mesh}",
        # 只给最后一个 target 设置权重为 1，其他都是 0
        weight=(len(target_list) - 1, 1),
        frontOfChain=True,  # 否把 blendShape 节点放在变形链的最前面（在 skinCluster 之前）
        topologyCheck=False,  # 关闭拓扑检查
    )

    # 获取源模型混合变形信息
    bs_info_list = find_blendshape_info(source_mesh)
    # 通过推导式生成字典，形式为{变形名称：变形属性,...}
    bs_info_dict = {bs_info[0]: bs_info[1] for bs_info in bs_info_list}
    output_targets = []
    for bs_name, bs_attr in bs_info_dict.items():
        if bs_name == target_mesh.name():
            continue
        bs_attr.set(1)  # 将该混合变形属性设置为1
        # 通过在变形状态下复制模型的方法，生成混合变形所需的目标模型，并将其添加到bs_group中
        bs_mesh = pm.duplicate(source_mesh)[0]
        pm.parent(bs_mesh, grp_output)
        pm.select(clear=True)  # 清除选择
        bs_mesh.rename(bs_name)
        # 将该混合变形属性设置为0，返回未变形状态。
        output_targets.append(bs_mesh)
        bs_info_dict[bs_name].set(0)
    # 清理场景
    pm.delete(blendShape_source_mesh)
    pm.delete(source_mesh, constructionHistory=True)  # 删除历史
    grp_target_new = pm.group(
        pm.listRelatives(grp_output, children=True, path=True),
        n=f"grp_target_{target_mesh}",
    )  # 创建新组，因为有重名文件所以要 path=True
    pm.hide(grp_target_new)
    new_mesh = pm.duplicate(target_mesh, name=f"{source_mesh}__OUTPUT")[0]
    pm.parent(new_mesh, grp_output)
    pm.rename(new_mesh, target_mesh.name())
    print(
        f"SUCCESS: Transfered The Following BlendShape Target {source_mesh} -> {target_mesh}"
    )

    # 创建新的混合变形
    final_blendshape = pm.blendShape(
        output_targets,
        new_mesh,
        frontOfChain=True,
        topologyCheck=False,
    )
    return final_blendshape


def transfer_blendshape_targets_diffTopo(
    source_mesh: nt.Transform,
    source_mesh_openMouth_target: nt.Transform,
    target_mesh: nt.Transform,
    target_mesh_openMouth_target: nt.Transform,
):
    # 变量名
    grp_target = "grp_trgt"
    # 创建输出组
    output_target_grp = pm.createNode("transform", n=f"grp_{target_mesh}")
    # 获取变形目标
    target_list = [target for target in pm.listRelatives(grp_target, children=True)]
    # 创建混合变形
    bs_source_mesh = pm.blendShape(
        target_list,
        source_mesh,
        name=f"bs_{source_mesh}",
        frontOfChain=True,
        topologyCheck=False,
    )
    # 复制源模型张嘴混合目标，因为该模型要作为源模型的变形目标，不能再被包裹变形
    source_mesh_trans = pm.duplicate(
        source_mesh_openMouth_target, name=f"{source_mesh.name()}_trans"
    )
    pm.parent(source_mesh_trans, world=True)
    # 执行包裹变形
    pm.select(target_mesh_openMouth_target, source_mesh_trans, replace=True)
    pm.mel.performCreateWrap(False)  # 不弹出窗口
    wrap_node = pm.listHistory(target_mesh_openMouth_target, type="wrap")
    # 创建原模型和source_mesh_trans的混合变形,并将权重设为1，获得中性的pose（不张嘴）
    bs_source_trans = pm.blendShape(
        source_mesh,
        source_mesh_trans,
        name="bs_source_trans",
        weight=(0, 1),
        frontOfChain=True,
        topologyCheck=False,
    )
    # 复制该模型作为中间模型，该模型有目标模型的拓扑和原模型的形状
    mesh_between = pm.duplicate(target_mesh_openMouth_target, name="mesh_between")[0]
    # 创建混合变形来传递变形
    pm.blendShape(
        [target_mesh_openMouth_target, target_mesh],
        mesh_between,
        name="bs_between",
        weight=[(0, 1), (1, 1)],
        frontOfChain=True,
        topologyCheck=False,
    )

    # 获取源模型混合变形信息
    bs_info_list = find_blendshape_info(source_mesh)
    # 通过推导式生成字典，形式为{变形名称：变形属性,...}
    bs_info_dict = {bs_info[0]: bs_info[1] for bs_info in bs_info_list}
    output_targets = []
    for bs_name, bs_attr in bs_info_dict.items():
        bs_attr.set(1)  # 将该混合变形属性设置为1
        # 通过在变形状态下复制模型的方法，生成混合变形所需的目标模型，并将其添加到bs_group中
        bs_mesh = pm.duplicate(mesh_between)[0]
        pm.parent(bs_mesh, output_target_grp)
        pm.select(clear=True)  # 清除选择
        bs_mesh.rename(bs_name)
        # 将该混合变形属性设置为0，返回未变形状态。
        output_targets.append(bs_mesh)
        bs_info_dict[bs_name].set(0)
    # 清理场景
    pm.delete(source_mesh, constructionHistory=True)
    pm.delete(wrap_node)
    pm.delete(source_mesh_trans)
    pm.delete(mesh_between)
    # 目标对象重新打组
    grp_target_new = pm.group(
        pm.listRelatives(output_target_grp, children=True, path=True),
        n=f"grp_target_{target_mesh}",
    )
    grp_target_new.visibility.set(0)
    # 复制目标模型
    new_mesh = pm.duplicate(target_mesh, name=f"{source_mesh}__OUTPUT")[0]
    pm.parent(new_mesh, output_target_grp)
    pm.rename(new_mesh, target_mesh.name())
    # 打印信息
    print(
        f"SUCCESS: Transfered The Following BlendShape Target {source_mesh} -> {target_mesh}"
    )

    # 创建新的混合变形
    final_blendshape = pm.blendShape(
        output_targets,
        new_mesh,
        frontOfChain=True,
        topologyCheck=False,
    )
    return final_blendshape


def run_dev():
    filepath = rf"{DIRPATH}\00_example.mb"
    pm.openFile(filepath, force=True)
    pm.renameFile("untitled")

    mesh_a = nt.Transform("mesh_head")
    mesh_a_trans = nt.Transform("trgt_head_xfer")
    mesh_b = nt.Transform("mesh_arnie")
    mesh_b_trans = nt.Transform("trgt_arnie_xfer")

    transfer_blendshape_targets_diffTopo(mesh_a, mesh_a_trans, mesh_b, mesh_b_trans)

    return True


if __name__ == "__main__":
    run_dev()
