import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


def connect_twist_swing(
    driver=None,
    driven=None,
    twist: float = 0.0,
    swing: float = 0.0,
    twist_axis: str = "X",
):
    """
    将扭转和摆动驱动的矩阵连接到给定的对象。
    扭转和摆动值用于驱动四元数在源对象的局部矩阵和目标对象的局部矩阵之间进行插值。
    要将被驱动对象放到驱动对象同层级下
        Args:
            driver (nt.Transform): 用于插值的源对象.
            driven (nt.Transform): 用于插值的目标对象.
            twist (float): 扭转值 (0.0 to 1.0).
            swing (float): 摆动值 (0.0 to 1.0).
            twist_axis (str): 扭转轴向 (X, Y, or Z).
        Returns:
            None
    """
    # 获取对象
    if not driver or not driven:
        selection = pm.selected()
        if len(selection) < 2:
            pm.error("请选择至少两个对象：第一个是源对象，第二个是目标对象。")
        driver, driven = selection[0], selection[1]

    if not isinstance(driver, nt.Transform) or not isinstance(driven, nt.Transform):
        pm.error("驱动对象和目标对象必须是 Transform 类型")

    if isinstance(driven, nt.Joint):
        driven_is_joint = True

    with pm.UndoChunk():
        # 添加属性
        for attr in ["twist", "swing"]:
            if not driven.hasAttr(attr):
                driven.addAttr(
                    attr,
                    type=float,
                    minValue=0,
                    maxValue=1,
                    defaultValue=0,
                    keyable=True,
                )
        driven.twist.set(twist)
        driven.swing.set(swing)
        # 核心逻辑
        ## 计算源对象本地变化量矩阵
        ###计算源对象本地矩阵
        diver_local_matrix_node = pm.createNode(
            "multMatrix", name=f"{driver}_local_matrix"
        )
        driver.worldMatrix[0].connect(diver_local_matrix_node.matrixIn[0])
        driver.parentInverseMatrix[0].connect(diver_local_matrix_node.matrixIn[1])
        ### 计算本地逆矩阵
        driver_world_matrix = driver.worldMatrix[0].get()
        driver_parentInverseMatrix = driver.parentInverseMatrix[0].get()
        inverse_local_matrix = (
            driver_world_matrix * driver_parentInverseMatrix
        ).inverse()
        ### 对象动态本地矩阵 * 本地静态逆矩阵 = 变化量矩阵
        diver_local_matrix_node.matrixIn[2].set(inverse_local_matrix)

        ## 获取Twist四元数
        driver_quat_node = pm.createNode("decomposeMatrix", name=f"{driver}_quat")
        diver_local_matrix_node.matrixSum.connect(driver_quat_node.inputMatrix)
        driver_twist_node = pm.createNode("quatNormalize", name=f"{driver}_twist_quat")
        driver_quat_node.outputQuatW.connect(driver_twist_node.inputQuatW)
        driver_quat_node.attr(f"outputQuat{twist_axis}").connect(
            driver_twist_node.attr(f"inputQuat{twist_axis}")
        )
        ## 获取Swing四元数
        twist_invert_node = pm.createNode("quatInvert", name=f"{driver}_twist_invert")
        driver_twist_node.outputQuat.connect(twist_invert_node.inputQuat)
        driver_swing_node = pm.createNode("quatProd", name=f"{driver}_swing")
        twist_invert_node.outputQuat.connect(driver_swing_node.input1Quat)
        driver_quat_node.outputQuat.connect(driver_swing_node.input2Quat)
        ## 设置Twist和Swing的四元数插值
        twist_slerp_node = pm.createNode("quatSlerp", name=f"{driver}_twist_slerp")
        twist_slerp_node.input1QuatW.set(1)
        twist_slerp_node.inputT.set(twist)
        driven.twist.connect(twist_slerp_node.inputT)
        driver_twist_node.outputQuat.connect(twist_slerp_node.input2Quat)

        swing_slerp_node = pm.createNode("quatSlerp", name=f"{driver}_swing_slerp")
        swing_slerp_node.input1QuatW.set(1)
        swing_slerp_node.inputT.set(swing)
        driven.swing.connect(swing_slerp_node.inputT)
        driver_swing_node.outputQuat.connect(swing_slerp_node.input2Quat)

        slerp_quat_node = pm.createNode("quatProd", name=f"{driver}_slerp_quat")
        twist_slerp_node.outputQuat.connect(slerp_quat_node.input1Quat)
        swing_slerp_node.outputQuat.connect(slerp_quat_node.input2Quat)
        ## 计算目标对象偏移矩阵
        slerp_matrix_node = pm.createNode(
            "composeMatrix", name=f"{driver}_slerp_matrix"
        )
        slerp_matrix_node.useEulerRotation.set(0)
        slerp_quat_node.outputQuat.connect(slerp_matrix_node.inputQuat)

        driven_offset_matrix_node = pm.createNode(
            "multMatrix", name=f"{driven}_offset_matrix"
        )
        driven_worldMatrix = driven.worldMatrix[0].get()
        driven_parentInverseMatrix = driven.parentInverseMatrix[0].get()
        driven_local_matrix = driven_worldMatrix * driven_parentInverseMatrix

        slerp_matrix_node.outputMatrix.connect(driven_offset_matrix_node.matrixIn[0])
        driven_offset_matrix_node.matrixIn[1].set(driven_local_matrix)
        ## 直连属性
        final_rotation_node = pm.createNode(
            "decomposeMatrix", name=f"{driven}_final_rotation"
        )
        driven_offset_matrix_node.matrixSum.connect(final_rotation_node.inputMatrix)
        final_rotation_node.outputRotate.connect(driven.rotate)

        ## 连接父对象偏移矩阵
        # driven_offset_matrix_node.matrixSum.connect(driven.offsetParentMatrix)

        ## 目标对象是骨骼，则jointOrient置零
        if driven_is_joint:
            for attr in [f"jointOrient{axis}" for axis in "XYZ"]:
                is_locked = driven.attr(attr).isLocked()
                if is_locked:
                    driven.attr(attr).setLocked(False)
                driven.attr(attr).set(0)
                if is_locked:
                    driven.attr(attr).setLocked(True)
