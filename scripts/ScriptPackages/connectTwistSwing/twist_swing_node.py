import maya.api.OpenMaya as om


def maya_useNewAPI():
    """告诉 Maya 使用 API 2.0"""
    pass


class TwistSwingNode(om.MPxNode):
    # 插件 ID (开发测试可用 0x80000 左右的值)
    TYPE_ID = om.MTypeId(0x00123456)
    TYPE_NAME = "twistSwingNode"

    # 属性对象
    aInMatrix = om.MObject()
    aRestMatrix = om.MObject()
    aTwistAxis = om.MObject()
    aTwistWeight = om.MObject()
    aSwingWeight = om.MObject()

    aOutRotate = om.MObject()

    def __init__(self):
        super(TwistSwingNode, self).__init__()

    @staticmethod
    def creator():
        return TwistSwingNode()

    @staticmethod
    def initialize():
        nAttr = om.MAttributeSpec()  # 占位
        mAttr = om.MMatrixAttribute()
        nAttr = om.MNumericAttribute()
        uAttr = om.MUnitAttribute()
        eAttr = om.MEnumAttribute()

        # 输入矩阵
        TwistSwingNode.aInMatrix = mAttr.create("inputMatrix", "inMat")

        # 静止状态矩阵 (用于计算相对旋转)
        TwistSwingNode.aRestMatrix = mAttr.create("restMatrix", "restMat")

        # 扭转轴
        TwistSwingNode.aTwistAxis = eAttr.create("twistAxis", "axis", 0)
        eAttr.addField("X", 0)
        eAttr.addField("Y", 1)
        eAttr.addField("Z", 2)

        # 权重系数
        TwistSwingNode.aTwistWeight = nAttr.create(
            "twistWeight", "tw", om.MFnNumericData.kFloat, 0.0
        )
        nAttr.keyable = True
        nAttr.setMin(-1.0)
        nAttr.setMax(1.0)

        TwistSwingNode.aSwingWeight = nAttr.create(
            "swingWeight", "sw", om.MFnNumericData.kFloat, 0.0
        )
        nAttr.keyable = True
        nAttr.setMin(-1.0)
        nAttr.setMax(1.0)

        # 输出旋转
        TwistSwingNode.aOutRotate = uAttr.create(
            "outputRotate", "outRot", om.MFnUnitAttribute.kAngle, 0.0
        )
        uAttr.writable = False
        # 实际输出通常是 3D 旋转，这里简化为复合属性
        uAttrX = uAttr.create(
            "outputRotateX", "outRotX", om.MFnUnitAttribute.kAngle, 0.0
        )
        uAttrY = uAttr.create(
            "outputRotateY", "outRotY", om.MFnUnitAttribute.kAngle, 0.0
        )
        uAttrZ = uAttr.create(
            "outputRotateZ", "outRotZ", om.MFnUnitAttribute.kAngle, 0.0
        )
        nAttrComp = om.MFnNumericAttribute()
        TwistSwingNode.aOutRotate = nAttrComp.create(
            "outputRotate", "outRot", uAttrX, uAttrY, uAttrZ
        )

        # 添加属性
        TwistSwingNode.addAttribute(TwistSwingNode.aInMatrix)
        TwistSwingNode.addAttribute(TwistSwingNode.aRestMatrix)
        TwistSwingNode.addAttribute(TwistSwingNode.aTwistAxis)
        TwistSwingNode.addAttribute(TwistSwingNode.aTwistWeight)
        TwistSwingNode.addAttribute(TwistSwingNode.aSwingWeight)
        TwistSwingNode.addAttribute(TwistSwingNode.aOutRotate)

        # 设置依赖关系
        TwistSwingNode.attributeAffects(
            TwistSwingNode.aInMatrix, TwistSwingNode.aOutRotate
        )
        TwistSwingNode.attributeAffects(
            TwistSwingNode.aTwistWeight, TwistSwingNode.aOutRotate
        )
        TwistSwingNode.attributeAffects(
            TwistSwingNode.aSwingWeight, TwistSwingNode.aOutRotate
        )

    def compute(self, plug, data):
        if (
            plug != TwistSwingNode.aOutRotate
            and plug.parent() != TwistSwingNode.aOutRotate
        ):
            return om.kUnknownParameter

        # 获取输入值
        in_mat = data.inputValue(TwistSwingNode.aInMatrix).asMatrix()
        rest_mat = data.inputValue(TwistSwingNode.aRestMatrix).asMatrix()
        twist_wt = data.inputValue(TwistSwingNode.aTwistWeight).asFloat()
        swing_wt = data.inputValue(TwistSwingNode.aSwingWeight).asFloat()
        axis_idx = data.inputValue(TwistSwingNode.aTwistAxis).asShort()

        # 1. 计算相对矩阵量
        local_mat = in_mat * rest_mat.inverse()
        m_transform = om.MTransformationMatrix(local_mat)
        full_quat = m_transform.rotation(asQuaternion=True)

        # 2. Swing-Twist 分解
        # 四元数 q = [w, x, y, z]
        twist_quat = om.MQuaternion()
        if axis_idx == 0:  # X 轴
            twist_quat.set(full_quat.x, 0, 0, full_quat.w).normalizeIt()
        elif axis_idx == 1:  # Y 轴
            twist_quat.set(0, full_quat.y, 0, full_quat.w).normalizeIt()
        else:  # Z 轴
            twist_quat.set(0, 0, full_quat.z, full_quat.w).normalizeIt()

        swing_quat = full_quat * twist_quat.invert()

        # 3. 插值 (Slerp)
        id_quat = om.MQuaternion()  # 恒等四元数 (无旋转)

        final_twist = om.MQuaternion.slerp(id_quat, twist_quat, twist_wt)
        final_swing = om.MQuaternion.slerp(id_quat, swing_quat, swing_wt)

        # 4. 合成并输出
        final_quat = final_twist * final_swing
        out_rot = final_quat.asEulerRotation()

        out_handle = data.outputValue(TwistSwingNode.aOutRotate)
        out_handle.setMVector(om.MVector(out_rot.x, out_rot.y, out_rot.z))
        data.setClean(plug)


# 注册插件
def initializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject, "YourName", "1.0", "Any")
    mplugin.registerNode(
        TwistSwingNode.TYPE_NAME,
        TwistSwingNode.TYPE_ID,
        TwistSwingNode.creator,
        TwistSwingNode.initialize,
    )


def uninitializePlugin(mobject):
    mplugin = om.MFnPlugin(mobject)
    mplugin.deregisterNode(TwistSwingNode.TYPE_ID)
