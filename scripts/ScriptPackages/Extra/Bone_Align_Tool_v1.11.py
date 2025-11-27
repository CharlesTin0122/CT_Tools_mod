import maya.cmds as cmds
import maya.api.OpenMaya as om
import numpy as np
import math

"""
世界思路：
矩阵乘法规则：
a.从左到右乘，从右向左结算；但maya的符号*规则强行从左到右结算
b.不满足乘法交换律
世界旋转（maya逻辑顺序左到右）=父级旋转（P）*关节方向矩阵（O）*旋转轴矩阵（A）*局部旋转矩阵（LR）
新世界旋转=世界旋转（W）世界坐标增量（AW）
W * AW=P * O * A * LR
LR（运算/写作则：从右向左）=A^{-1} * o^{-1} * P^{-1} *（W * AW）
需要求值：
1.旋转轴矩阵
2.关节方向矩阵
3.世界旋转
4.父级旋转
5.世界坐标增量
6.还原原长度

某旋转轴RotateAxis=(0，90，180)的计算结果为
若Rotate0rder=0,即xyz,则矩阵乘法顺序是从右向左zyx，总矩阵：x(0）<-* y(90）<-* z（180）单位矩阵=

[cos(180) -sin(180) 0]   [cos(90)   0  sin(90)]   [1        0        0 ]
[sin(180) cos(180)  0] x [0         1  0      ] x [0        1        0 ]
[0        0        1 ] x [-sin(90)  0  cos(90)]   [0        0        1 ]

对于世界旋转，某骨骼Rotate=(0, 0，120)，RotateAxis=(0，0，150)，JointOrient=(0，0，-90)的计算结果为：

[cos(180) -sin(180) 0 0]
[sin(180) cos(180)  0 0]
[0        0         1 0]
[0        0         0 1]


"""


def safeGetAttr(joint, attr, default=0.0):
    """安全获取属性值，若属性不存在则返回默认值"""
    if cmds.objExists(joint + "." + attr):
        return cmds.getAttr(joint + "." + attr)[0]
    return (default, default, default)


def getAxisROrder(joint):
    """获取关节的旋转顺序，0=xyz，1=yzx，2=zxy，3=xzy，4=yxz，5=zyx"""
    return cmds.getAttr(joint + ".rotateOrder")


def getAxisR(joint):
    """获取关节的旋转轴矩阵"""
    axisJoint = safeGetAttr(joint, "rotateAxis")
    axisEuler = om.MEulerRotation(
        math.radians(axisJoint[0]),
        math.radians(axisJoint[1]),
        math.radians(axisJoint[2]),
        0,
    )
    return axisEuler.asMatrix()


def getJOrientR(joint):
    """获取关节的关节方向矩阵"""
    orientJoint = safeGetAttr(joint, "jointOrient")
    orientEuler = om.MEulerRotation(
        math.radians(orientJoint[0]),
        math.radians(orientJoint[1]),
        math.radians(orientJoint[2]),
    )
    orientMatrix = orientEuler.asMatrix()
    return orientMatrix


def getWorldR(joint):
    """获取关节的世界旋转矩阵"""
    matrix = cmds.xform(joint, q=True, m=True, ws=True)
    return (
        om.MTransformationMatrix(om.MMatrix(matrix))
        .rotation(asQuaternion=True)
        .asMatrix()
    )


def getParentJoint(joint):
    """获取关节的父关节"""
    parents = cmds.listRelatives(joint, parent=True, fullPath=True)
    if not parents:
        cmds.warning(f"{joint} 没有父关节!")
        return (0, 0, 0)
    parentJoint = parents[0]
    if "twist" in parentJoint.lower():  # 不区分twist大小写
        grandparents = cmds.listRelatives(parentJoint, parent=True, fullPath=True)
        if grandparents:
            parentJoint = grandparents[0]
    return parentJoint


def getParentR(joint):
    """获取关节的父级旋转矩阵"""
    parents = cmds.listRelatives(joint, parent=True, fullPath=True)
    if not parents:
        return om.MMatrix()  # 单位矩阵
    return getWorldR(parents[0])


def getWorldPosition(joint, as_vector=True):
    """获取关节的世界位置"""
    pos = cmds.xform(joint, query=True, worldSpace=True, translation=True)
    if as_vector:
        return om.MVector(pos[0], pos[1], pos[2])
    return pos


def getBoneVec(joint):
    """获取关节的骨骼向量（归一化）"""
    parentJoint = getParentJoint(joint)
    boneVec = getWorldPosition(joint) - getWorldPosition(parentJoint)
    return (
        boneVec.normal() if boneVec.length() > 1e-6 else om.MVector(1, 0, 0)
    )  # 归一化向量


def getDeltaWorldR(v1, v2):
    """获取从向量v1旋转到向量v2的旋转矩阵"""
    if v1.length() < 1e-6 or v2.length() < 1e-6:
        return om.MMatrix()
    return v1.rotateTo(v2).asMatrix()


def getBoneVecOriLength(joint):
    """获取关节的原始骨骼长度"""
    parentJoint = getParentJoint(joint)
    boneVec = getWorldPosition(joint) - getWorldPosition(parentJoint)
    return boneVec.length()


def alignVec(joint, targetVec, restoreLength=True):
    """对齐关节骨骼向量到目标向量方向"""
    parentJoint = getParentJoint(joint)
    targetRotateEuler = (
        om.MTransformationMatrix(
            getAxisR(parentJoint).inverse()
            * getJOrientR(parentJoint).inverse()
            * getParentR(parentJoint).inverse()
            * getWorldR(parentJoint)
            * getDeltaWorldR(getBoneVec(joint), targetVec)
        )
        .rotation(asQuaternion=True)
        .asEulerRotation()
        .reorderIt(getAxisROrder(parentJoint))
    )
    print(f"1:{getAxisR(parentJoint).inverse()}")
    print(f"2:{getWorldR(parentJoint)}")
    print(f"3:{getDeltaWorldR(getBoneVec(joint), targetVec)}")
    print(f"4:{getJOrientR(parentJoint)}")
    print(f"5:{getParentR(parentJoint)}")
    print(f"目标局部旋转欧拉角: {targetRotateEuler}")

    oriLength = getBoneVecOriLength(joint)
    print(f"原始骨骼长度: {oriLength}")

    oriChildJPos = getWorldPosition(joint)

    cmds.setAttr(parentJoint + ".rotateX", math.degrees(targetRotateEuler[0]))
    cmds.setAttr(parentJoint + ".rotateY", math.degrees(targetRotateEuler[1]))
    cmds.setAttr(parentJoint + ".rotateZ", math.degrees(targetRotateEuler[2]))

    if restoreLength:
        newBoneVec = getBoneVec(joint)
        if newBoneVec.length() > 1e-6:
            scaleFactor = oriLength / newBoneVec.length()
            correctedChildPos = getWorldPosition(parentJoint) + newBoneVec * scaleFactor
            cmds.xform(
                joint,
                t=(correctedChildPos.x, correctedChildPos.y, correctedChildPos.z),
                ws=True,
            )
        else:
            cmds.xform(joint, t=oriChildJPos, ws=True)


if __name__ == "__main__":
    selectedJoints = cmds.ls(selection=True, type="joint")
    if not selectedJoints:
        cmds.warning("至少选择一个JOINT!")
    # 单关节模式：使用预设目标向量
    elif len(selectedJoints) == 1:
        targetVec = np.array([0, -1, 0])
        targetVecNor = om.MVector(targetVec).normal()
        print("=" * 70)
        print(f"使用数组 '{targetVecNor}' 作为目标方向")
        alignVec(selectedJoints[0], targetVecNor)
    # 多关节模式：使用最后一个关节的方向作为目标向量
    elif len(selectedJoints) >= 2:
        targetJoint = selectedJoints[-1]
        targetVec = getBoneVec(targetJoint)
        print("=" * 70)
        print(f"使用关节 '{targetJoint}' 的方向作为目标向量:")
        print(f"目标向量: ({targetVec.x:.4f}, {targetVec.y:.4f}, {targetVec.z:.4f})")
        print(f"将对齐 {len(selectedJoints) - 1} 个骨骼到该方向")
        for childJoint in selectedJoints[:-1]:
            print("-" * 70)
            print(f"已对齐关节: {childJoint} -> 目标方向: {targetVec}")
            alignVec(childJoint, targetVec)
        print("=" * 70)
