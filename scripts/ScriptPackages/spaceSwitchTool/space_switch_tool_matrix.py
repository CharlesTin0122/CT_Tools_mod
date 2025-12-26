# -*- encoding: utf-8 -*-
"""
@File    :   space_switch_tool_matrix.py
@Time    :   2025/10/16 10:54:05
@Author  :   Charles Tian
@Version :   1.0
@Contact :   tianchao0533@gmail.com
@Desc    :   使用矩阵节点实现空间切换，性能更好，不能直接应用于骨骼，可能导致引擎内动画无效。
"""

import pymel.core as pm
import pymel.core.nodetypes as nt
import pymel.core.datatypes as dt


def addSpaceSwitching(
    target_node: nt.Transform,
    switch_attribute: str,
    driver_list: list[nt.Transform],
    enum_item_list=None,
) -> None:
    """为目标节点添加空间切换功能

    Args:
        target_node (nt.Transform): 要添加空间切换的目标节点
        switch_attributre (str): 要添加到目标节点的枚举属性名称，一般为"Follow"或"Space"
        driver_list (list[nt.Transform]): 驱动节点列表
        enum_item_list (list[str]):添加到目标节点的空间名称列表，与驱动节点列表一一对应
    """
    with pm.UndoChunk():
        if not enum_item_list:
            enum_item_list = [node.name() for node in driver_list]
        # 添加空间切换空间切换的枚举属性
        if not target_node.hasAttr(switch_attribute):
            target_node.addAttr(
                switch_attribute,
                attributeType="enum",
                enumName=":".join(enum_item_list),  # 枚举选项
                defaultValue=0,
                keyable=True,
            )
        # 为位移、旋转、缩放添加独立的权重开关
        if not target_node.hasAttr("UseTranslate"):
            target_node.addAttr(
                "UseTranslate",
                attributeType="float",
                minValue=0.0,
                maxValue=1.0,
                defaultValue=1,
                keyable=True,
            )
        if not target_node.hasAttr("UseRotate"):
            target_node.addAttr(
                "UseRotate",
                attributeType="float",
                minValue=0.0,
                maxValue=1.0,
                defaultValue=1,
                keyable=True,
            )
        if not target_node.hasAttr("UseScale"):
            target_node.addAttr(
                "UseScale",
                attributeType="float",
                minValue=0.0,
                maxValue=1.0,
                defaultValue=1,
                keyable=True,
            )
        # 创建定位器
        loc_list = []
        for driver in driver_list:
            driver_loc = pm.spaceLocator(name=f"{driver}_loc")
            pm.hide(driver_loc)
            pm.parent(driver_loc, driver)
            pm.matchTransform(
                driver_loc, target_node, position=True, rotation=True, scale=False
            )
            loc_list.append(driver_loc)
        # 创建混合矩阵节点
        blendMatrix_node = pm.createNode(
            "blendMatrix", name=f"{target_node}_blendMatrix"
        )
        # 获取目标对象静态父对象逆矩阵
        target_pim = target_node.parentInverseMatrix[0].get()
        # 遍历驱动对象列表
        for i, driver in enumerate(loc_list):
            # 驱动对象世界矩阵乘以目标对象静态父对象逆矩阵，矩阵和连接混合矩阵节点的目标矩阵
            multMatrix_node = pm.createNode("multMatrix", name=f"{driver}_multMatrix")
            driver.worldMatrix[0].connect(multMatrix_node.matrixIn[0])
            multMatrix_node.matrixIn[1].set(target_pim)
            multMatrix_node.matrixSum.connect(blendMatrix_node.target[i].targetMatrix)
            # 创建条件节点连接混合矩阵节点的混合权重
            condition_node = pm.createNode("condition", name=f"{driver}_condition")
            condition_node.operation.set(0)  # Equal
            target_node.attr(switch_attribute).connect(condition_node.firstTerm)
            condition_node.secondTerm.set(i)
            condition_node.colorIfTrue.set([1, 1, 1])
            condition_node.colorIfFalse.set([0, 0, 0])
            condition_node.outColorR.connect(blendMatrix_node.target[i].weight)
            # 连接useTranslateRotateScale
            target_node.UseTranslate.connect(blendMatrix_node.target[i].translateWeight)
            target_node.UseRotate.connect(blendMatrix_node.target[i].rotateWeight)
            target_node.UseScale.connect(blendMatrix_node.target[i].scaleWeight)
        # 混合矩阵节点连接目标节点偏移父矩阵
        blendMatrix_node.outputMatrix.connect(target_node.offsetParentMatrix)
        # 目标节点属性置零
        target_node.translate.set(dt.Vector())
        target_node.rotate.set(dt.Vector())
        if isinstance(target_node, nt.Joint):
            target_node.jointOrient.set(dt.Vector())


def seamless_space_switch(
    target_node: nt.Transform,
    switch_attribute: str,
    new_space_index: int,
) -> None:
    """
    执行无缝的空间切换，确保目标节点在切换时世界空间位置不变。

    Args:
        target_node (nt.Transform): 带有空间切换属性的控制器。
        switch_attribute (str): 控制空间切换的枚举属性的名称 (例如 "Follow")。
        new_space_index (int): 要切换到的新空间的索引值 (枚举的整数值)。
    """
    with pm.UndoChunk():
        # 在切换前，记录下控制器当前的世界矩阵
        original_world_matrix = target_node.getMatrix(worldSpace=True)
        pre_frame = pm.currentTime() - 1
        pm.setKeyframe(target_node, time=pre_frame, attribute="translate")
        pm.setKeyframe(target_node, time=pre_frame, attribute="rotate")
        pm.setKeyframe(target_node, time=pre_frame, attribute="scale")
        pm.setKeyframe(target_node, time=pre_frame, attribute=switch_attribute)
        # 执行切换：设置枚举属性为新的值,这会导致目标对象发生跳变
        try:
            target_node.attr(switch_attribute).set(new_space_index)
            # 设置世界矩阵
            target_node.setMatrix(original_world_matrix, worldSpace=True)
            # 精确地为变换和切换属性设置关键帧
            pm.setKeyframe(target_node, attribute="translate")
            pm.setKeyframe(target_node, attribute="rotate")
            pm.setKeyframe(target_node, attribute="scale")
            pm.setKeyframe(target_node, attribute=switch_attribute)
        except Exception as e:
            pm.warning(
                f"无法设置属性 '{switch_attribute}' 为 {new_space_index}。错误: {e}"
            )
            return


def bake_space(
    target_node: nt.Transform,
    switch_attribute: str,
    new_space_index: int,
    start_frame: int,
    end_frame: int,
):
    """在指定帧范围内烘焙空间切换，保持对象世界空间位置不变。
    Args:
        target_node (nt.Transform): 目标对象
        switch_attribute (str): 空间切换属性
        new_space_index (int): 新的空间属性索引
        start_frame (int): 开始帧
        end_frame (int): 结束帧
    """
    # 采集每一帧的世界矩阵
    world_matrix_list: list[dt.Matrix] = []
    for frame in range(start_frame, end_frame + 1):
        pm.currentTime(frame)
        world_matrix = target_node.getMatrix(worldSpace=True)
        world_matrix_list.append(world_matrix)
    # 切换空间并应用采集到的矩阵
    with pm.UndoChunk():
        for i in range(start_frame, end_frame + 1):
            pm.currentTime(i)
            try:
                # 切换空间
                target_node.attr(switch_attribute).set(new_space_index)
                # 获取矩阵列表索引
                matrix_index = i - start_frame
                # 设置世界矩阵
                target_node.setMatrix(world_matrix_list[matrix_index], worldSpace=True)
                # 为变换和切换属性设置关键帧
                pm.setKeyframe(target_node, attribute="translate")
                pm.setKeyframe(target_node, attribute="rotate")
                pm.setKeyframe(target_node, attribute="scale")
                pm.setKeyframe(target_node, attribute=switch_attribute)
            except Exception as e:
                pm.warning(
                    f"无法设置属性 '{switch_attribute}' 为 {new_space_index}。错误: {e}"
                )
