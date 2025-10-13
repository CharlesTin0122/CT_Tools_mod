import maya.api.OpenMaya as om
import math


def maya_useNewAPI():
    """Maya Python API 2.0 requirement"""
    pass


class MatrixConstraintNode(om.MPxNode):
    """A simplified matrix constraint node using only core attributes."""

    kNodeName = "matrixConstraint"
    kNodeId = om.MTypeId(0x87010)  # Unique ID for this node (change for production)

    # -----------------------------
    # Attributes
    # -----------------------------
    aDriverMatrix = None
    aDrivenParentInverseMatrix = None

    aOutputMatrix = None

    aTranslate = None
    aTranslateX = None
    aTranslateY = None
    aTranslateZ = None

    aRotate = None
    aRotateX = None
    aRotateY = None
    aRotateZ = None

    aScale = None
    aScaleX = None
    aScaleY = None
    aScaleZ = None

    aShear = None
    aShearX = None
    aShearY = None
    aShearZ = None

    # -----------------------------
    # Compute
    # -----------------------------
    def compute(self, plug, data_block):
        """Main compute function."""
        if plug not in (
            self.aOutputMatrix,
            self.aTranslate,
            self.aRotate,
            self.aScale,
            self.aShear,
        ):
            return

        # --- Get Inputs ---
        driver_matrix = data_block.inputValue(self.aDriverMatrix).asMatrix()
        parent_inverse = data_block.inputValue(
            self.aDrivenParentInverseMatrix
        ).asMatrix()

        # --- Compute Output ---
        result_matrix = driver_matrix * parent_inverse
        result_tfm = om.MTransformationMatrix(result_matrix)

        # --- Set outputMatrix ---
        out_matrix_handle = data_block.outputValue(self.aOutputMatrix)
        out_matrix_handle.setMMatrix(result_matrix)
        data_block.setClean(self.aOutputMatrix)

        # --- Decompose and output components ---
        translation = result_tfm.translation(om.MSpace.kWorld)
        euler_rot = result_tfm.rotation(asQuaternion=False)
        scale = result_tfm.scale(om.MSpace.kWorld)
        shear = result_tfm.shear(om.MSpace.kWorld)

        # Translate
        t_handle = data_block.outputValue(self.aTranslate)
        t_handle.set3Double(*translation)
        data_block.setClean(self.aTranslate)

        # Rotate (Euler)
        r_handle = data_block.outputValue(self.aRotate)
        r_handle.set3Double(euler_rot.x, euler_rot.y, euler_rot.z)
        data_block.setClean(self.aRotate)

        # Scale
        s_handle = data_block.outputValue(self.aScale)
        s_handle.set3Double(*scale)
        data_block.setClean(self.aScale)

        # Shear
        sh_handle = data_block.outputValue(self.aShear)
        sh_handle.set3Double(*shear)
        data_block.setClean(self.aShear)

    # -----------------------------
    # Initialization
    # -----------------------------
    @classmethod
    def initialize(cls):
        nAttr = om.MFnNumericAttribute()
        mAttr = om.MFnMatrixAttribute()
        uAttr = om.MFnUnitAttribute()

        # Input matrices
        cls.aDriverMatrix = mAttr.create(
            "driverMatrix", "drvMat", om.MFnMatrixAttribute.kDouble
        )
        mAttr.writable = True
        mAttr.readable = False
        cls.addAttribute(cls.aDriverMatrix)

        cls.aDrivenParentInverseMatrix = mAttr.create(
            "drivenParentInverseMatrix", "drvInvMat", om.MFnMatrixAttribute.kDouble
        )
        mAttr.writable = True
        mAttr.readable = False
        cls.addAttribute(cls.aDrivenParentInverseMatrix)

        # Output matrix
        cls.aOutputMatrix = mAttr.create(
            "outputMatrix", "outMat", om.MFnMatrixAttribute.kDouble
        )
        mAttr.writable = False
        mAttr.readable = True
        cls.addAttribute(cls.aOutputMatrix)

        # --- Output decomposed components ---
        # Translate
        cls.aTranslateX = nAttr.create("translateX", "tx", om.MFnNumericData.kDouble)
        cls.aTranslateY = nAttr.create("translateY", "ty", om.MFnNumericData.kDouble)
        cls.aTranslateZ = nAttr.create("translateZ", "tz", om.MFnNumericData.kDouble)
        cls.aTranslate = nAttr.create(
            "translate", "t", cls.aTranslateX, cls.aTranslateY, cls.aTranslateZ
        )
        nAttr.writable = False
        nAttr.readable = True
        cls.addAttribute(cls.aTranslate)

        # Rotate
        cls.aRotateX = uAttr.create("rotateX", "rx", om.MFnUnitAttribute.kAngle)
        cls.aRotateY = uAttr.create("rotateY", "ry", om.MFnUnitAttribute.kAngle)
        cls.aRotateZ = uAttr.create("rotateZ", "rz", om.MFnUnitAttribute.kAngle)
        cls.aRotate = nAttr.create(
            "rotate", "r", cls.aRotateX, cls.aRotateY, cls.aRotateZ
        )
        nAttr.writable = False
        nAttr.readable = True
        cls.addAttribute(cls.aRotate)

        # Scale
        cls.aScaleX = nAttr.create("scaleX", "sx", om.MFnNumericData.kDouble, 1.0)
        cls.aScaleY = nAttr.create("scaleY", "sy", om.MFnNumericData.kDouble, 1.0)
        cls.aScaleZ = nAttr.create("scaleZ", "sz", om.MFnNumericData.kDouble, 1.0)
        cls.aScale = nAttr.create("scale", "s", cls.aScaleX, cls.aScaleY, cls.aScaleZ)
        nAttr.writable = False
        nAttr.readable = True
        cls.addAttribute(cls.aScale)

        # Shear
        cls.aShearX = nAttr.create("shearX", "shx", om.MFnNumericData.kDouble, 0.0)
        cls.aShearY = nAttr.create("shearY", "shy", om.MFnNumericData.kDouble, 0.0)
        cls.aShearZ = nAttr.create("shearZ", "shz", om.MFnNumericData.kDouble, 0.0)
        cls.aShear = nAttr.create("shear", "sh", cls.aShearX, cls.aShearY, cls.aShearZ)
        nAttr.writable = False
        nAttr.readable = True
        cls.addAttribute(cls.aShear)

        # --- Attribute Affects ---
        for input_attr in (cls.aDriverMatrix, cls.aDrivenParentInverseMatrix):
            for output_attr in (
                cls.aOutputMatrix,
                cls.aTranslate,
                cls.aRotate,
                cls.aScale,
                cls.aShear,
            ):
                cls.attributeAffects(input_attr, output_attr)

    # -----------------------------
    # Node type definition
    # -----------------------------
    @classmethod
    def creator(cls):
        return MatrixConstraintNode()


# -----------------------------
# Plugin registration
# -----------------------------
def initializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin, "Charles Tian", "1.0.0")
    try:
        plugin_fn.registerNode(
            MatrixConstraintNode.kNodeName,
            MatrixConstraintNode.kNodeId,
            MatrixConstraintNode.creator,
            MatrixConstraintNode.initialize,
            om.MPxNode.kDependNode,
        )
    except Exception as e:
        om.MGlobal.displayError(f"Failed to register node: {e}")


def uninitializePlugin(plugin):
    plugin_fn = om.MFnPlugin(plugin)
    try:
        plugin_fn.deregisterNode(MatrixConstraintNode.kNodeId)
    except Exception as e:
        om.MGlobal.displayError(f"Failed to deregister node: {e}")
