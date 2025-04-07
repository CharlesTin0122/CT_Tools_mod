import pymel.core as pc
import pymel.core.nodetypes as nt


def find_blendshape_info(source_mesh: nt.Transform) -> list:
    """用于返回给出模型的混合变形信息，包含名称和属性

    Args:
        source_mesh (pc.nodetypes.Transform): 给出的源模型

    Returns:
        list: 混合变形信息列表
    """

    blendshapes = pc.listHistory(source_mesh, type="blendShape")

    # 通过blendshape.listAliases()，获取混合变形信息。
    bs_info_list = []
    for blendshape in blendshapes:
        # [('Breathe', Attribute('blendShape1.weight[0]')),...]
        bs_infos = blendshape.listAliases()
        bs_info_list.extend(bs_infos)

    return bs_info_list


def copy_bs_mesh(source_mesh: nt.Transform, trans_bs_name: str):
    """
    该函数用于将角色A的面部混合变形传递到角色B(角色AB相同拓扑)
    将角色B作为目标模型, 添加到A的混合变形中, 然后将角色A中的角色B名称的的混合变形权重设置为1。
    以此将角色A的其他混合变形叠加到角色B后复制A模型得到相对于B的混合变形模型目标模型

    Args:
        source_mesh: 源模型A
        trans_bs_name: 目标模型B
    Returns:
        None
    """
    # 获取源模型混合变形信息
    bs_info_list = find_blendshape_info(source_mesh)
    # 通过推导式生成字典，形式为{变形名称：变形属性,...}
    bs_info_dict = {bs_info[0]: bs_info[1] for bs_info in bs_info_list}

    for bs_name, bs_attr in bs_info_dict.items():
        if bs_name == trans_bs_name:
            continue
        bs_attr.set(1)  # 将该混合变形属性设置为1
        # 通过在变形状态下复制模型的方法，生成混合变形所需的目标模型，并将其添加到bs_group中
        bs_mesh = pc.duplicate(source_mesh)[0]
        pc.select(clear=True)  # 清除选择
        bs_mesh.rename(bs_name)
        # 将该混合变形属性设置为0，返回未变形状态。
        bs_info_dict[bs_name].set(0)


if __name__ == "__main__":
    # 选择源模型
    source_mesh = pc.ls(selection=True)[0]
    trans_bs_name = "SK_Human_Male_001"
    copy_bs_mesh(source_mesh, trans_bs_name)
