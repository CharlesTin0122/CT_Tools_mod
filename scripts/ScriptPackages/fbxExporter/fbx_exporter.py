# -*- coding: utf-8 -*-
# @FileName :  fbx_exporter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/19 9:38
# @Software : PyCharm
# Description:
import os
import json
import pymel.core as pc


class FbxExporterUI:
    """骨骼动画批量导出
    因为使用mGear绑定框架,绑定的骨骼通道被矩阵约束链接，而不是约束节点约束，所以一般的烘焙动画功能无法使用。
    所以使用了枚举属性烘焙的方法，将动画烘焙到骨骼属性通道。然后再导出骨骼动画。
    """

    def __init__(self):
        self.export_path_field = None
        self.fileList = []
        self.objList = []
        self.everyBakeAttr = []
        self.exportPath = None
        self.exp_data = {}
        self.window = None
        self.slyFile = None
        self.slyOBJ = None
        self.json_file = None

    def show(self):
        """创建UI"""
        try:
            pc.deleteUI("fbxExport")
        except Exception as exc:
            print(exc)

        self.window = pc.window("fbxExport", title="FBX Exporter")
        with pc.columnLayout(rowSpacing=5, adj=True):
            with pc.frameLayout(label="Export multiple files"):
                with pc.columnLayout(adj=1):
                    pc.button(label="Load All Export Files", c=self.load_files)
                with pc.scrollLayout(w=200, h=150, bgc=(0.5, 0.5, 0.5)) as self.slyFile:
                    pc.text("File Name:")
                with pc.columnLayout(adj=1):
                    pc.button(label="Load Objects To Export", c=self.load_objects)
                with pc.scrollLayout(w=200, h=150, bgc=(0.5, 0.5, 0.5)) as self.slyOBJ:
                    pc.text("OBJ Name:")
                with pc.rowLayout(
                    numberOfColumns=3,
                    columnWidth3=(55, 140, 5),
                    adjustableColumn=2,
                    columnAlign=(1, "right"),
                    columnAttach=[(1, "both", 0), (2, "both", 0), (3, "both", 0)],
                ):
                    pc.text(label="Export Path:", w=65)
                    self.export_path_field = pc.textField("ExporterTextField")
                    pc.button(label="...", w=30, h=20, c=self.select_export_path)
                with pc.columnLayout(adj=1):
                    pc.button(label="Export All !!!", c=self.export_all)
        self.window.show()

    def load_files(self, *args):
        """载入要导出的maya文件(*.ma *.mb)"""
        self.fileList = pc.fileDialog2(fileFilter="Maya Files (*.ma *.mb)", fileMode=4)
        if not self.fileList:
            pc.warning("No files selected for export.")
            return
        with self.slyFile:
            for file in self.fileList:
                pc.text(label=os.path.basename(file))

    def load_objects(self, *args):
        """载入文件中要导出的对象，一般为所有骨骼链"""
        self.objList = [str(x) for x in pc.selected()]
        if not self.objList:
            pc.warning("No objects selected for export.")
            return
        with self.slyOBJ:
            for obj in self.objList:
                pc.text(label=obj)

        # 设定需要烘焙的动画属性。分别为位移，旋转，缩放
        attrsToBake = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        # 要需要烘焙的每根骨骼的每个属性放入everyBakeAttr变量
        self.everyBakeAttr = [
            f"{joint}.{attr}" for joint in self.objList for attr in attrsToBake
        ]

    def select_export_path(self, *args):
        """选择导出路径"""
        export_path = pc.fileDialog2(fileFilter="*folder", fileMode=2)
        if export_path:
            self.exportPath = export_path[0]
            pc.textField(self.export_path_field, e=True, text=self.exportPath)

    def write_json(self, *args):
        """将导出信息写入json文件"""
        self.exp_data = {
            "file_list": self.fileList,
            "jnt_list": self.objList,
            "everyBakeAttr": self.everyBakeAttr,
            "export_path": self.exportPath,
        }
        script_path = pc.internalVar(userScriptDir=True)
        self.json_file = os.path.join(script_path, "exp_data.json")
        with open(self.json_file, "w") as d:
            json.dump(self.exp_data, d, indent=4)

    def export_all(self, *args):
        """执行批量导出"""
        if not all([self.fileList, self.objList, self.exportPath]):
            pc.warning("Please select files, objects, and export path.")
            return

        self.write_json()
        exp_data = self.exp_data
        # 'H:/Project_PJX/Animation/Unarmed/Locomotion/Anim_Male_Unarmed_Stand_Jump_Fall_Loop.0001.mb'
        for f in exp_data["file_list"]:
            # Anim_Male_Unarmed_Stand_Jump_Fall_Loop.0001.mb
            file_name = os.path.basename(f)
            # 'Anim_Male_Unarmed_Stand_Jump_Fall_Loop', '0001', 'mb'
            base_name = file_name.split(".")[0]
            # 'Anim_Male_Unarmed_Stand_Jump_Fall_Loop.fbx'
            exp_name = str(base_name) + ".fbx"

            pc.openFile(f, force=True)
            # 烘焙关键帧
            try:
                pc.bakeResults(
                    exp_data["everyBakeAttr"],
                    simulation=True,
                    shape=False,
                    sampleBy=1,
                    sparseAnimCurveBake=False,
                    bakeOnOverrideLayer=False,
                    removeBakedAnimFromLayer=True,
                    # resolveWithoutLayer=cmds.ls(type='animLayer'),
                    time=(pc.env.getMinTime(), pc.env.getMaxTime()),
                )
                # 执行欧拉过滤器以防止动画曲线翻转
                everyRotation = [f"{jnt}.r" for jnt in exp_data["jnt_list"]]
                pc.filterCurve(everyRotation, filter="euler")
            except Exception as exc:
                print(exc)

            pc.select(exp_data["jnt_list"])
            pc.exportSelected(
                os.path.join(exp_data["export_path"], exp_name),
                force=True,
                type="FBX export",
                constraints=False,
                expressions=False,
                constructionHistory=False,
            )
        # 关闭当前文件，防止烘焙文件被误保存
        pc.newFile(f=True)
        # 弹出对话框
        confirm = pc.confirmDialog(
            title="Finish", message="Done!", button=["OK", "Open Folder"]
        )
        if confirm == "Open Folder":
            os.startfile(exp_data["export_path"])


if __name__ == "__main__":
    ui = FbxExporterUI()
    ui.show()
