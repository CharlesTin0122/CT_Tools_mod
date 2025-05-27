import pymel.core as pm

def build_joint_hierarchy():
    """
    构建一个字典，表示场景中所有关节的层级关系。
    字典的键是关节名称，值是其直接子关节名称的列表。
    """
    joints = pm.ls(type='joint')
    hierarchy = {}
    for joint in joints:
        children = [child for child in joint.getChildren() if isinstance(child, pm.nodetypes.Joint)]
        child_names = [child.name() for child in children]
        hierarchy[joint.name()] = child_names
    return hierarchy
"""
{
    'Root': ['Child1', 'Child2'],
    'Child1': ['Grandchild1'],
    'Child2': [],
    'Grandchild1': []
}
"""
# 使用示例
hierarchy = build_joint_hierarchy()
print(hierarchy)