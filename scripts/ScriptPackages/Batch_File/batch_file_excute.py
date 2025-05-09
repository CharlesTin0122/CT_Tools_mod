# -*- coding: utf-8 -*-
# @FileName :  batch_mayafile_execute.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/6/1 14:58
# @Software : PyCharm
# Description:
import os
import pymel.core as pc


class BatchMayaFile:
    def __init__(self):
        self.radioCol = None
        self.file_list = []
        self.savePath = None
        self.file_field = None
        self.py_field = None
        self.path_field = None

    def create_ui(self):
        try:
            pc.deleteUI("Batch Tool")
        except Exception as e:
            print(e)

        with pc.window("Batch Tool", title="Maya Batch Tool") as win:
            with pc.columnLayout(rowSpacing=5, adj=True):
                with pc.frameLayout(label="Load Maya File"):
                    with pc.columnLayout(adj=1):
                        pc.button(label="Load ALL Maya File", c=self.load)
                    with pc.scrollLayout(
                        w=200, h=150, bgc=(0.5, 0.5, 0.5)
                    ) as self.file_field:
                        pc.text("File Name:")
                    with pc.frameLayout(label="pymel"):
                        self.py_field = pc.cmdScrollFieldExecuter(
                            "pymelcode",
                            h=150,
                            w=200,
                            sourceType="python",
                            showTabsAndSpaces=True,
                            showLineNumbers=True,
                            showTooltipHelp=True,
                        )
                    with pc.rowLayout(
                        numberOfColumns=2, columnWidth2=(150, 125), adjustableColumn=2
                    ):
                        self.radioCol = pc.radioCollection()
                        pc.radioButton(
                            "rb_save", label="Save File", align="left", select=True
                        )
                        pc.radioButton("rb_export", label="Export File", align="right")
                    with pc.rowLayout(
                        numberOfColumns=3,
                        columnWidth3=(55, 140, 5),
                        adjustableColumn=2,
                        columnAlign=(1, "right"),
                        columnAttach=[(1, "both", 0), (2, "both", 0), (3, "both", 0)],
                    ):
                        pc.text(label="Save Path:")
                        self.path_field = pc.textField("ImporterTextField")
                        pc.button(label="...", w=30, h=20, c=self.select_path)
                    with pc.columnLayout(adj=1):
                        pc.button(label="Batch !!!", c=self.doit)

        pc.window(win, e=True, w=250, h=300)
        pc.showWindow(win)

    def load(self, *args):
        self.file_list = pc.fileDialog2(fileFilter="All Files (*.*)", fileMode=4)

        if not self.file_list:
            pc.PopupError("Nothing Selected")
            self.file_list = []
            return

        for file_path in self.file_list:
            file_name = os.path.basename(file_path)
            with self.file_field:
                pc.text(label=file_name)

    def select_path(self, *args):
        save_path = pc.fileDialog2(fileFilter="*folder", fileMode=2)
        if save_path:
            self.savePath = save_path[0]
            pc.textField(self.path_field, e=True, text=self.savePath)

    def doit(self, *args):
        if not self.file_list:
            pc.PopupError("Nothing To Batch")
            return

        modify_code = pc.cmdScrollFieldExecuter(self.py_field, q=True, text=True)
        radio_btn = pc.radioCollection(self.radioCol, q=True, select=True)
        for file in self.file_list:
            pc.openFile(file, force=True)  # 分别打开每个文件
            exec(modify_code)  # 以字符串的形式执行代码
            # 如果为'Export File选项且存在导出路径，则执行导出命令
            if (radio_btn == "rb_export") and self.savePath:
                short_name = os.path.splitext(os.path.basename(file))[0]
                file_path = os.path.join(self.savePath, short_name + ".fbx")
                print(file_path)
                pc.exportAll(file_path, force=True)
            # 如果为'Save File选项且存在保存路径，则执行保存命令
            elif (radio_btn == "rb_save") and self.savePath:
                short_name = os.path.splitext(os.path.basename(file))[0]
                file_path = os.path.join(self.savePath, short_name + ".mb")
                print(file_path)
                pc.saveAs(file_path, force=True)
            else:
                pc.PopupError("Please Input SavePath!")

        confirm = pc.confirmDialog(
            title="Finish", message="Done!", button=["OK", "Open Folder"]
        )
        if confirm == "Open Folder" and self.savePath:
            os.startfile(self.savePath)


if __name__ == "__main__":
    batch_tool = BatchMayaFile()
    batch_tool.create_ui()
