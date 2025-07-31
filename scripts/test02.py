import maya.OpenMaya as om

# 创建并添加选择列表
selection_list = om.MSelectionList()
selection_list.add("pPlane1")

# 创建MObject和DagPath
m_obj = om.MObject()
dag_path = om.MDagPath()


# 获取选择列表获取MObject和dagpath
selection_list.getDependNode(0, m_obj)
selection_list.getDagPath(0, dag_path)

# 使用MFn函数集,MFnMesh接收DagPath和MObject，而MFnDepend只接受MObject
mFnMesh = om.MFnMesh(dag_path)  # mFnMesh获取的是shape节点：|pPlane1|pPlaneShape1
print(mFnMesh.fullPathName())
mFnDependNode = om.MFnDependencyNode(m_obj)  # 获取的是transform节点：pPlane1
print(mFnDependNode.name())

# 获取shape节点的所有连接
mPlugArray = om.MPlugArray()
mFnMesh.getConnections(mPlugArray)
mPlugArray.length()  # 连接的plug数量2
print(mPlugArray[0].name())  # pPlaneShape1.instObjGroups[0]-材质连接
print(mPlugArray[1].name())  # pPlaneShape1.inMesh - Mesh连接

mPlugArray2 = om.MPlugArray()
# connectedTo函数获取连接，shape节点作为目标，获取源节点的所有连接（只有一个）
# 参数：array:MPlugArray, asDst:bool, asSrc:bool, ReturnStatus:MStatus = Null
mPlugArray[1].connectedTo(mPlugArray2, True, False)
print(mPlugArray2[0].name())  # polyPlane1.output

# 通过plug获取node
m_obj2 = mPlugArray2[0].node()
mFnDependNode2 = om.MFnDependencyNode(m_obj2)
print(mFnDependNode2.name())  # polyPlane1

# 获取属性
mPlug_width = mFnDependNode2.findPlug("width")
mPlug_height = mFnDependNode2.findPlug("height")
mPlug_subWidth = mFnDependNode2.findPlug("subdivisionsWidth")
mPlug_subHeight = mFnDependNode2.findPlug("subdivisionsHeight")

print(mPlug_width.asInt())  # 10
print(mPlug_height.asInt())  # 15
print(mPlug_subWidth.asInt())  # 20
print(mPlug_subHeight.asInt())  # 25

# 设置属性
mPlug_subWidth.setInt(10)
mPlug_subHeight.setInt(10)
