# -*- coding: utf-8 -*-
# @FileName :  fbx_exporter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/19 9:38
# @Software : PyCharm
# Description:
import os
import json
import pymel.core as pm


class FbxExporterUI:
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

    def show(self):
        try:
            pm.deleteUI("fbxExport")
        except Exception as exc:
            print(exc)

        self.window = pm.window("fbxExport", title="FBX Exporter")
        with pm.columnLayout(rowSpacing=5, adj=True):
            with pm.frameLayout(label="Export multiple files"):
                with pm.columnLayout(adj=1):
                    pm.button(label="Load All Export Files", c=self.load_files)
                with pm.scrollLayout(w=200, h=150, bgc=(0.5, 0.5, 0.5)) as self.slyFile:
                    pm.text("File Name:")
                with pm.columnLayout(adj=1):
                    pm.button(label="Load Objects To Export", c=self.load_objects)
                with pm.scrollLayout(w=200, h=150, bgc=(0.5, 0.5, 0.5)) as self.slyOBJ:
                    pm.text("OBJ Name:")
                with pm.rowLayout(
                    numberOfColumns=3,
                    columnWidth3=(55, 140, 5),
                    adjustableColumn=2,
                    columnAlign=(1, "right"),
                    columnAttach=[(1, "both", 0), (2, "both", 0), (3, "both", 0)],
                ):
                    pm.text(label="Export Path:", w=65)
                    self.export_path_field = pm.textField("ExporterTextField")
                    pm.button(label="...", w=30, h=20, c=self.select_export_path)
                with pm.columnLayout(adj=1):
                    pm.button(label="Export All !!!", c=self.export_all)
        self.window.show()

    def load_files(self, *args):
        self.fileList = pm.fileDialog2(fileFilter="Maya Files (*.ma *.mb)", fileMode=4)
        if not self.fileList:
            pm.warning("No files selected for export.")
            return
        with self.slyFile:
            for file in self.fileList:
                pm.text(label=os.path.basename(file))

    def load_objects(self, *args):
        self.objList = [str(x) for x in pm.selected()]
        if not self.objList:
            pm.warning("No objects selected for export.")
            return
        with self.slyOBJ:
            for obj in self.objList:
                pm.text(label=obj)

        # 设定需要烘焙的动画属性。分别为位移，旋转，缩放
        attrsToBake = ["tx", "ty", "tz", "rx", "ry", "rz", "sx", "sy", "sz"]
        # 要需要烘焙的每根骨骼的每个属性放入everyBakeAttr变量
        for eachJoint in self.objList:
            for eachAttr in attrsToBake:
                self.everyBakeAttr.append(f"{eachJoint}.{eachAttr}")

    def select_export_path(self, *args):
        export_path = pm.fileDialog2(fileFilter="*folder", fileMode=2)
        if export_path:
            self.exportPath = export_path[0]
            pm.textField(self.export_path_field, e=True, text=self.exportPath)

    def write_json(self, *args):
        self.exp_data = {
            "file_list": self.fileList,
            "jnt_list": self.objList,
            "everyBakeAttr": self.everyBakeAttr,
            "export_path": self.exportPath,
        }
        current_path = rf'{os.path.dirname(__file__)}'
        json_file = os.path.join(current_path, "exp_data.json")
        with open(json_file, "w") as d:
            json.dump(self.exp_data, d, indent=4)

    def export_all(self, *args):
        if not self.fileList:
            pm.warning("No files selected for export.")
            return
        if not self.objList:
            pm.warning("No objects selected for export.")
            return
        if not self.exportPath:
            pm.warning("No export path selected.")
            return

        self.write_json()
        current_path = rf'{os.path.dirname(__file__)}'
        json_file = os.path.join(current_path, "exp_data.json")
        with open(json_file, "r") as r:
            exp_data = json.load(r)

        for f in exp_data["file_list"]:
            file_name = os.path.basename(f)
            bace_name = os.path.splitext(file_name)
            exp_name = str(bace_name[0]) + ".fbx"
            pm.openFile(f, force=True)
            # 烘焙关键帧
            try:
                pm.bakeResults(
                    exp_data["everyBakeAttr"],
                    simulation=True,
                    shape=False,
                    sampleBy=1,
                    sparseAnimCurveBake=False,
                    bakeOnOverrideLayer=False,
                    removeBakedAnimFromLayer=True,
                    # resolveWithoutLayer=cmds.ls(type='animLayer'),
                    time=(pm.env.getMinTime(), pm.env.getMaxTime()),
                )
                # 执行欧拉过滤器以防止动画曲线翻转
                everyRotation = [jnt.r for jnt in exp_data["jnt_list"]]
                pm.filterCurve(everyRotation, filter="euler")
            except Exception as exc:
                print(exc)

            pm.select(exp_data["jnt_list"])
            pm.exportSelected(
                os.path.join(exp_data["export_path"], exp_name),
                force=True,
                type="FBX export",
                constraints=False,
                expressions=False,
                constructionHistory=False
            )
        confirm = pm.confirmDialog(title='Finish', message="Done!", button=['OK', 'Open Folder'])
        if confirm == 'Open Folder':
            os.startfile(exp_data["export_path"])


if __name__ == "__main__":
    ui = FbxExporterUI()
    ui.show()
