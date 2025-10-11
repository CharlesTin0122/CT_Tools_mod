# -*- coding: utf-8 -*-
import maya.api.OpenMaya as om
import math


def maya_useNewAPI():
    pass


class MatrixConstraintNode(om.MPxNode):
    """矩阵约束节点：支持Quaternion旋转混合，避免旋转污染缩放。"""

    kNodeName = "matrixConstraint"
    kNodeId = om.MTypeId(0x0012CDEA)  # 随便选个未使用的ID（避免冲突可自行修改）

    # --- 属性声明 ---
    inputMatrix = None
    inputWeight = None
    offsetMatrix = None
    maintainOffset = None
    normalizeWeight = None

    outputMatrix = None
    outputTranslate = None
    outputRotate = None
    outputScale = None

    @staticmethod
    def creator():
        return MatrixConstraintNode()

    @staticmethod
    def initialize():
        mAttr = om.MFnMatrixAttribute()
        nAttr = om.MFnNumericAttribute()

        # 多个输入矩阵
        MatrixConstraintNode.inputMatrix = mAttr.create(
            "inputMatrix", "inMat", om.MFnMatrixAttribute.kDouble
        )
        mAttr.array = True
        mAttr.usesArrayDataBuilder = True
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.inputMatrix)

        # 权重
        MatrixConstraintNode.inputWeight = nAttr.create(
            "inputWeight", "inW", om.MFnNumericData.kFloat, 1.0
        )
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.inputWeight)

        # 偏移矩阵
        MatrixConstraintNode.offsetMatrix = mAttr.create(
            "offsetMatrix", "offMat", om.MFnMatrixAttribute.kDouble
        )
        mAttr.array = True
        mAttr.usesArrayDataBuilder = True
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.offsetMatrix)

        # 保持偏移
        MatrixConstraintNode.maintainOffset = nAttr.create(
            "maintainOffset", "moff", om.MFnNumericData.kBoolean, True
        )
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.maintainOffset)

        # 权重归一化
        MatrixConstraintNode.normalizeWeight = nAttr.create(
            "normalizeWeight", "norm", om.MFnNumericData.kBoolean, True
        )
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.normalizeWeight)

        # 输出
        MatrixConstraintNode.outputMatrix = mAttr.create(
            "outputMatrix", "outMat", om.MFnMatrixAttribute.kDouble
        )
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.outputMatrix)

        MatrixConstraintNode.outputTranslate = nAttr.createPoint(
            "outputTranslate", "outT"
        )
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.outputTranslate)

        MatrixConstraintNode.outputRotate = nAttr.createPoint(
            "outputRotate", "outR"
        )  # 欧拉角 XYZ
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.outputRotate)

        MatrixConstraintNode.outputScale = nAttr.createPoint("outputScale", "outS")
        MatrixConstraintNode.addAttribute(MatrixConstraintNode.outputScale)

        # 属性影响关系
        for src in [
            MatrixConstraintNode.inputMatrix,
            MatrixConstraintNode.inputWeight,
            MatrixConstraintNode.offsetMatrix,
            MatrixConstraintNode.maintainOffset,
            MatrixConstraintNode.normalizeWeight,
        ]:
            MatrixConstraintNode.attributeAffects(
                src, MatrixConstraintNode.outputMatrix
            )
            MatrixConstraintNode.attributeAffects(
                src, MatrixConstraintNode.outputTranslate
            )
            MatrixConstraintNode.attributeAffects(
                src, MatrixConstraintNode.outputRotate
            )
            MatrixConstraintNode.attributeAffects(src, MatrixConstraintNode.outputScale)

    def compute(self, plug, dataBlock):
        if plug not in (
            MatrixConstraintNode.outputMatrix,
            MatrixConstraintNode.outputTranslate,
            MatrixConstraintNode.outputRotate,
            MatrixConstraintNode.outputScale,
        ):
            return

        in_mats = om.MArrayDataHandle(
            dataBlock.inputArrayValue(MatrixConstraintNode.inputMatrix)
        )
        in_weights = om.MArrayDataHandle(
            dataBlock.inputArrayValue(MatrixConstraintNode.inputWeight)
        )
        in_offsets = om.MArrayDataHandle(
            dataBlock.inputArrayValue(MatrixConstraintNode.offsetMatrix)
        )

        normalize = dataBlock.inputValue(MatrixConstraintNode.normalizeWeight).asBool()

        matrices = []
        weights = []
        offsets = []

        # 收集输入数据
        while not in_mats.isDone():
            mat = om.MMatrix(in_mats.inputValue().asMatrix())
            matrices.append(mat)
            in_mats.next()

        while not in_weights.isDone():
            weights.append(in_weights.inputValue().asFloat())
            in_weights.next()

        while not in_offsets.isDone():
            offsets.append(om.MMatrix(in_offsets.inputValue().asMatrix()))
            in_offsets.next()

        count = len(matrices)
        if count == 0:
            return

        if normalize:
            w_sum = sum(weights) or 1.0
            weights = [w / w_sum for w in weights]

        # --- 平移、旋转、缩放分量 ---
        total_trans = om.MVector()
        total_scale = om.MVector()
        total_quat = om.MQuaternion(0, 0, 0, 0)

        for i, mat in enumerate(matrices):
            w = weights[i] if i < len(weights) else 1.0
            offset = offsets[i] if i < len(offsets) else om.MMatrix.kIdentity

            final_mat = mat * offset

            m_trans = om.MTransformationMatrix(final_mat)
            t = m_trans.translation(om.MSpace.kWorld)
            s = m_trans.scale(om.MSpace.kWorld)
            q = m_trans.rotation(asQuaternion=True)

            total_trans += t * w
            total_scale += om.MVector(s[0] * w, s[1] * w, s[2] * w)

            # 四元数累加（加权平均）
            if total_quat.isEquivalent(om.MQuaternion(0, 0, 0, 0)):
                total_quat = q * w
            else:
                total_quat = om.MQuaternion.slerp(total_quat, q, w)

        # --- 组合输出矩阵 ---
        out_trans = total_trans
        out_scale = (total_scale.x, total_scale.y, total_scale.z)
        out_rot_euler = total_quat.asEulerRotation()

        out_mtx = om.MTransformationMatrix()
        out_mtx.setTranslation(out_trans, om.MSpace.kWorld)
        out_mtx.setRotation(out_rot_euler)
        out_mtx.setScale(out_scale, om.MSpace.kWorld)

        # 输出设置
        dataBlock.outputValue(MatrixConstraintNode.outputMatrix).setMMatrix(
            out_mtx.asMatrix()
        )
        dataBlock.outputValue(MatrixConstraintNode.outputTranslate).set3Float(
            out_trans.x, out_trans.y, out_trans.z
        )
        dataBlock.outputValue(MatrixConstraintNode.outputRotate).set3Float(
            math.degrees(out_rot_euler.x),
            math.degrees(out_rot_euler.y),
            math.degrees(out_rot_euler.z),
        )
        dataBlock.outputValue(MatrixConstraintNode.outputScale).set3Float(
            out_scale[0], out_scale[1], out_scale[2]
        )
        dataBlock.setClean(plug)


# --- 注册与卸载 ---
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin, "Charles Tian", "1.0", "Any")
    try:
        pluginFn.registerNode(
            MatrixConstraintNode.kNodeName,
            MatrixConstraintNode.kNodeId,
            MatrixConstraintNode.creator,
            MatrixConstraintNode.initialize,
        )
    except Exception as e:
        om.MGlobal.displayError("Failed to register node: " + str(e))


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    try:
        pluginFn.deregisterNode(MatrixConstraintNode.kNodeId)
    except Exception as e:
        om.MGlobal.displayError("Failed to deregister node: " + str(e))
