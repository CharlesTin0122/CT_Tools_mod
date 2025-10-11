# -*- coding: utf-8 -*-
import math
import maya.api.OpenMaya as om


def maya_useNewAPI():
    pass


class QuatDecomposeNode(om.MPxNode):
    """四元数分解节点：输入一个旋转四元数和轴方向，输出Swing和Twist四元数"""

    kNodeName = "quatDecompose"
    kNodeId = om.MTypeId(0x87001)  # 请在项目中换成自己的唯一ID

    # 属性对象
    inputQuat = None
    twistAxis = None
    twistQuat = None
    swingQuat = None

    @staticmethod
    def creator():
        return QuatDecomposeNode()

    @staticmethod
    def initialize():
        nAttr = om.MFnNumericAttribute()
        eAttr = om.MFnEnumAttribute()
        cAttr = om.MFnCompoundAttribute()

        # 输入四元数（x, y, z, w）
        quatX = nAttr.create("quatX", "qx", om.MFnNumericData.kDouble, 0.0)
        quatY = nAttr.create("quatY", "qy", om.MFnNumericData.kDouble, 0.0)
        quatZ = nAttr.create("quatZ", "qz", om.MFnNumericData.kDouble, 0.0)
        quatW = nAttr.create("quatW", "qw", om.MFnNumericData.kDouble, 1.0)
        QuatDecomposeNode.inputQuat = cAttr.create("inputQuat", "inQuat")
        cAttr.addChild(quatX)
        cAttr.addChild(quatY)
        cAttr.addChild(quatZ)
        cAttr.addChild(quatW)
        cAttr.keyable = True
        cAttr.storable = True
        cAttr.readable = True
        cAttr.writable = True

        # Twist轴选择
        QuatDecomposeNode.twistAxis = eAttr.create("twistAxis", "axis", 1)
        eAttr.addField("X", 0)
        eAttr.addField("Y", 1)
        eAttr.addField("Z", 2)
        eAttr.keyable = True
        eAttr.storable = True

        # 输出：Twist四元数
        twistX = nAttr.create("twistX", "tx", om.MFnNumericData.kDouble, 0.0)
        twistY = nAttr.create("twistY", "ty", om.MFnNumericData.kDouble, 0.0)
        twistZ = nAttr.create("twistZ", "tz", om.MFnNumericData.kDouble, 0.0)
        twistW = nAttr.create("twistW", "tw", om.MFnNumericData.kDouble, 1.0)
        QuatDecomposeNode.twistQuat = cAttr.create("twistQuat", "tQuat")
        cAttr.addChild(twistX)
        cAttr.addChild(twistY)
        cAttr.addChild(twistZ)
        cAttr.addChild(twistW)
        cAttr.readable = True
        cAttr.writable = False

        # 输出：Swing四元数
        swingX = nAttr.create("swingX", "sx", om.MFnNumericData.kDouble, 0.0)
        swingY = nAttr.create("swingY", "sy", om.MFnNumericData.kDouble, 0.0)
        swingZ = nAttr.create("swingZ", "sz", om.MFnNumericData.kDouble, 0.0)
        swingW = nAttr.create("swingW", "sw", om.MFnNumericData.kDouble, 1.0)
        QuatDecomposeNode.swingQuat = cAttr.create("swingQuat", "sQuat")
        cAttr.addChild(swingX)
        cAttr.addChild(swingY)
        cAttr.addChild(swingZ)
        cAttr.addChild(swingW)
        cAttr.readable = True
        cAttr.writable = False

        # 添加属性
        QuatDecomposeNode.addAttribute(QuatDecomposeNode.inputQuat)
        QuatDecomposeNode.addAttribute(QuatDecomposeNode.twistAxis)
        QuatDecomposeNode.addAttribute(QuatDecomposeNode.twistQuat)
        QuatDecomposeNode.addAttribute(QuatDecomposeNode.swingQuat)

        # 设置依赖关系
        QuatDecomposeNode.attributeAffects(
            QuatDecomposeNode.inputQuat, QuatDecomposeNode.twistQuat
        )
        QuatDecomposeNode.attributeAffects(
            QuatDecomposeNode.inputQuat, QuatDecomposeNode.swingQuat
        )
        QuatDecomposeNode.attributeAffects(
            QuatDecomposeNode.twistAxis, QuatDecomposeNode.twistQuat
        )
        QuatDecomposeNode.attributeAffects(
            QuatDecomposeNode.twistAxis, QuatDecomposeNode.swingQuat
        )

    def compute(self, plug, dataBlock):
        if plug not in (QuatDecomposeNode.twistQuat, QuatDecomposeNode.swingQuat):
            return

        # 输入四元数
        quatHandle = dataBlock.inputValue(self.inputQuat)
        qx = quatHandle.child(0).asDouble()
        qy = quatHandle.child(1).asDouble()
        qz = quatHandle.child(2).asDouble()
        qw = quatHandle.child(3).asDouble()

        q = om.MQuaternion(qx, qy, qz, qw)
        q.normalizeIt()

        # Twist 轴
        axis_value = dataBlock.inputValue(self.twistAxis).asShort()
        twist_axis = [om.MVector(1, 0, 0), om.MVector(0, 1, 0), om.MVector(0, 0, 1)][
            axis_value
        ]

        # 计算 Swing / Twist
        rotated_axis = q * twist_axis
        dot_val = max(-1.0, min(1.0, rotated_axis * twist_axis))

        if abs(dot_val - 1.0) < 1e-8:
            swing = om.MQuaternion()
        else:
            swing_axis = (rotated_axis ^ twist_axis).normalize()
            swing_angle = math.acos(dot_val)
            swing = om.MQuaternion(swing_axis, swing_angle)

        twist = q * swing.inverse()

        # 输出 Twist
        twistHandle = dataBlock.outputValue(self.twistQuat)
        twistHandle.child(0).setDouble(twist.x)
        twistHandle.child(1).setDouble(twist.y)
        twistHandle.child(2).setDouble(twist.z)
        twistHandle.child(3).setDouble(twist.w)

        # 输出 Swing
        swingHandle = dataBlock.outputValue(self.swingQuat)
        swingHandle.child(0).setDouble(swing.x)
        swingHandle.child(1).setDouble(swing.y)
        swingHandle.child(2).setDouble(swing.z)
        swingHandle.child(3).setDouble(swing.w)

        # 标记干净
        dataBlock.setClean(plug)


# 注册与反注册函数
def initializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    pluginFn.registerNode(
        QuatDecomposeNode.kNodeName,
        QuatDecomposeNode.kNodeId,
        QuatDecomposeNode.creator,
        QuatDecomposeNode.initialize,
    )


def uninitializePlugin(plugin):
    pluginFn = om.MFnPlugin(plugin)
    pluginFn.deregisterNode(QuatDecomposeNode.kNodeId)
