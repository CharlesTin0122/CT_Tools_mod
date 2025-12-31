import pymel.core as pm
import pymel.core.nodetypes as nt


def switch_skin_weights(jnt_a: nt.Joint, jnt_b: nt.Joint) -> None:
    """
    两个骨骼之间互换蒙皮权重
    Args:
            jnt: 移动权重的骨骼
            other_jnt: 被移动权重的骨骼

    Returns:None

    """
    pm.select(cl=True)  # 取消所有选择
    skin_clusters = pm.listConnections(jnt_a, type="skinCluster")  # 获取蒙皮节点
    # 列表去重
    skin_list = list(set(skin_clusters))
    for skin_cluster in skin_list:
        # 选择父骨骼蒙皮影响的点
        pm.skinCluster(skin_cluster, edit=True, selectInfluenceVerts=jnt_a)
        # 传递父骨骼的蒙皮权重到子骨骼
        pm.skinPercent(skin_cluster, transformMoveWeights=[jnt_a.name(), jnt_b.name()])


def remove_childJoint_Influence(mesh, rootJoint, parentJoint):
    """
    将面部子骨骼权重赋予面部根骨骼后，移除面部子骨骼权重

    Args:
        mesh (meshtransform): 要处理的模型
        rootJoint (joint): 要处理蒙皮骨骼链的根骨骼
        parentJoint (joint): 要处理蒙皮骨骼链的父骨骼

    Returns:
        list: 要处理蒙皮骨骼链
    """
    meshVtx = pm.ls("{}.vtx[*]".format(mesh), fl=True)  # 获取物体所有顶点
    skClu = pm.listHistory(mesh, type="skinCluster")[0]  # 获取SkinCluster
    # 锁定所有骨骼权重
    joints = pm.ls(rootJoint, dag=True, type="joint")
    for jnt in joints:
        pm.setAttr("{}.liw".format(jnt), 1)
    # 解锁所有面部骨骼权重
    faceJnt = pm.ls(parentJoint, dag=True, type="joint")
    for jnt in faceJnt:
        pm.setAttr("{}.liw".format(jnt), 0)
    # 物体所有顶点权重赋予面部根骨骼
    for vtx in meshVtx:
        pm.skinPercent(skClu, vtx, transformValue=(parentJoint, 1))
    # 移除面部子骨骼蒙皮
    for jnt in faceJnt[1:]:
        pm.skinCluster(skClu, e=1, removeInfluence=jnt)
    # 移除微小权重
    pm.skinPercent(skClu, mesh, pruneWeights=0.1)
    # 返回骨骼链
    return faceJnt
