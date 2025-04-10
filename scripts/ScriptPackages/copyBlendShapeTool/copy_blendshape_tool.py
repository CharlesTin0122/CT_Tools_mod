# -*- coding: utf-8 -*-
"""
@FileName      : copy_blendshape_tool.py
@DateTime      : 2024/03/14 10:03:48
@Author        : Tian Chao
@Contact       : tianchao0533@163.com
@Software      : Maya 2024.2
@PythonVersion : python 3.10.8
@librarys      : pymel 1.4.0
@Description   :copy blendshape from source to target
"""

import pymel.core as pc
import pymel.core.nodetypes as nt


class CopyBlendShapeTool:
    """copy blendshapes from source mesh to target meshes.
    Typically used to copy blendshapes from a body mesh to a clothing mesh.
    """

    def __init__(self):
        """构建函数"""
        self.source_mesh_field = None
        self.blendshape_field = None
        self.target_meshes_field = None

        self.source_mesh = None
        self.target_meshes = []
        self.select_blendshapes = []

    def create_ui(self):
        """创建UI"""
        try:
            pc.deleteUI("win_CopyBSTool")
        except Exception as exc:
            print(exc)

        win = pc.window(
            "win_CopyBSTool", title="Copy BlendShape Tool", widthHeight=(300, 500)
        )

        with pc.columnLayout(adj=True):
            pc.text(
                label="Copy BlendShapes",
                align="center",
                font="boldLabelFont",
                height=30,
            )
            with pc.rowLayout(numberOfColumns=2, columnWidth2=(100, 200), ad2=1):
                self.source_mesh_field = pc.textField(width=190)
                pc.button(
                    label="Add Source Mesh",
                    width=100,
                    height=30,
                    command=self.slot_add_source_mesh,
                )
            pc.text(label="BlendShapes:", height=20)
            self.blendshape_field = pc.textScrollList(
                allowMultiSelection=True, height=100
            )

            pc.separator(height=10)

            pc.text(label="Target Meshes:", height=20)
            pc.button(
                label="Add Target Meshes",
                width=50,
                height=30,
                command=self.slot_add_target_meshes,
            )
            self.target_meshes_field = pc.textScrollList(height=100)

            pc.separator(height=10)

            pc.button(
                label="Copy BlendShapes",
                width=30,
                height=60,
                command=self.slot_copy_blendshapes,
            )
        win.show()

    def find_blendshape_info(self, source_mesh: nt.Transform) -> list:
        """用于返回给出模型的混合变形信息，包含名称和属性

        Args:
            source_mesh (pc.nodetypes.Transform): 给出的源模型

        Returns:
            list: 混合变形信息列表
        """
        if not isinstance(source_mesh, nt.Transform):
            pc.inViewMessage(
                amg="Input object is not a valid source mesh...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
        blendshapes = pc.listHistory(source_mesh, type="blendShape")
        if not blendshapes:
            pc.inViewMessage(
                amg="No blendshapes found in the source mesh...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
        # 通过blendshape.listAliases()，获取混合变形信息。
        bs_info_list = []
        for blendshape in blendshapes:
            # [('Breathe', Attribute('blendShape1.weight[0]')),...]
            bs_infos = blendshape.listAliases()
            bs_info_list.extend(bs_infos)

        return bs_info_list

    def copy_blendshapes(
        self,
        source_mesh: nt.Transform,
        target_meshes: list[nt.Transform],
        select_blendshapes: list[str],
    ):
        """
        将指定的混合变形从源模型复制到多个目标模型。

        Args:
            source_mesh: 源模型
            target_meshes: 目标模型
            select_blendshapes: 指定的混合变形
        Returns:
            None
        """
        if not source_mesh:
            pc.inViewMessage(
                amg="Please input source mesh...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        # 选中模型并创建包裹变形器
        if not target_meshes:
            pc.inViewMessage(
                amg="Please input target meshes...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        if not select_blendshapes:
            pc.inViewMessage(
                amg="Please select blendshapes to copy from...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        pc.select(target_meshes, replace=1)
        pc.select(source_mesh, toggle=1)
        wrap_node = pc.mel.performCreateWrap(False)
        # wrap_node = pc.cmds.CreateWrap()
        # 获取源模型混合变形信息
        bs_info_list = self.find_blendshape_info(source_mesh)
        # 通过推导式生成字典，形式为{变形名称：变形属性,...}
        bs_info_dict = {bs_info[0]: bs_info[1] for bs_info in bs_info_list}
        # 遍历目标模型生成混合变形所需的目标模型，并进行混合变形
        for target_mesh in target_meshes:  # 遍历目标模型
            bs_group = []
            for bs_name in select_blendshapes:  # 遍历指定的混合变形
                bs_info_dict[bs_name].set(1)  # 将该混合变形属性设置为1
                # 通过在变形状态下复制模型的方法，生成混合变形所需的目标模型，并将其添加到bs_group中
                bs_mesh = pc.duplicate(target_mesh)[0]
                bs_mesh.rename(bs_name)
                bs_group.append(bs_mesh)
                # 将该混合变形属性设置为0，返回未变形状态。
                bs_info_dict[bs_name].set(0)
            pc.blendShape(bs_group, target_mesh)  # 创建混合变形
            # 重命名生成的混合变形所需的目标模型,并将其打组隐藏
            for mesh in bs_group:
                pc.rename(mesh, newname=f"{target_mesh}_{mesh}")
            target_grp = pc.group(bs_group, name=f"{target_mesh}_target")
            pc.hide(target_grp)
        # 删除包裹变形器
        for mesh in target_meshes:
            wrap_node = pc.listHistory(mesh, type="wrap")
            pc.delete(wrap_node)

    def slot_add_source_mesh(self, *args):
        """按钮点击槽函数:
        将选中的模型作为源模型添加到UI当中,并将该模型的混合变形名称添加到UI当中
        """
        # 将选中的模型作为源模型添加到UI当中
        source_mesh = pc.selected()[0]
        if not source_mesh:
            pc.inViewMessage(
                amg="Please select source mesh to input...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
        pc.textField(self.source_mesh_field, e=True, text=source_mesh)
        # 将该模型的混合变形名称添加到UI当中
        bs_info_list = self.find_blendshape_info(
            source_mesh
        )  # 获取该模型的混合变形信息
        # 通过混合变形信息，获取混合变形名称·
        bs_name_list = []
        for bs_info in bs_info_list:
            bs_name = bs_info[0]
            bs_name_list.append(bs_name)
        # 添加至UI之前先清空UI当中的内容
        pc.textScrollList(self.blendshape_field, e=True, removeAll=True)
        # 遍历混合变形名称并添加至UI当中
        for bs_name in bs_name_list:
            pc.textScrollList(self.blendshape_field, e=True, append=bs_name)

    def slot_add_target_meshes(self, *args):
        """按钮点击槽函数:
        将选中的模型作为目标模型添加到UI当中
        """
        # 添加至UI之前先清空UI当中的内容
        pc.textScrollList(self.target_meshes_field, e=True, removeAll=True)
        # 遍历目标名称并添加至UI当中
        target_meshes = pc.selected()
        if not target_meshes:
            pc.inViewMessage(
                amg="Please select target mesh to input...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
        for target_mesh in target_meshes:
            pc.textScrollList(self.target_meshes_field, e=True, append=target_mesh)

    def slot_copy_blendshapes(self, *args):
        """按钮点击槽函数：
        将选中的源模型混合变形复制到目标模型。
        """
        self.source_mesh = pc.textField(self.source_mesh_field, q=True, text=True)
        if not self.source_mesh:
            pc.inViewMessage(
                amg="Please input source mesh...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        self.target_meshes = pc.textScrollList(
            self.target_meshes_field, q=True, allItems=True
        )
        if not self.target_meshes:
            pc.inViewMessage(
                amg="Please input target meshes...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        self.select_blendshapes = pc.textScrollList(
            self.blendshape_field, q=True, selectItem=True
        )
        if not self.select_blendshapes:
            pc.inViewMessage(
                amg="Please select blendshapes...",
                alpha=0.5,
                dragKill=True,
                pos="midCenterTop",
                fade=True,
            )
            return
        self.copy_blendshapes(
            self.source_mesh, self.target_meshes, self.select_blendshapes
        )


if __name__ == "__main__":
    cbt = CopyBlendShapeTool()
    cbt.create_ui()
