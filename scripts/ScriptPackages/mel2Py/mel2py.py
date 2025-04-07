# -*- coding: utf-8 -*-
"""
@FileName    :   mel2py.py
@DateTime    :   2023/04/13 10:57:57
@Author  :   Tian Chao
@Contact :   tianchao0533@163.com
"""

import pymel.core as pc
import pymel.tools.mel2py as mel2py


class Mel2Pymel:
    def __init__(self):
        self.mel_cmd = None
        self.py_cmd = None
        self.mel_feild = None
        self.py_feild = None
        self.win = None
        self.mel2py_ui()

    def mel2py_ui(self):
        """UI界面编写"""
        try:
            pc.deleteUI("melpy")
        except Exception as e:
            print(e)

        with pc.window("melpy", title="mel2py") as self.win:
            with pc.columnLayout(adj=1):
                with pc.frameLayout(label="mel"):
                    self.mel_feild = pc.cmdScrollFieldExecuter(
                        "melcode",
                        h=150,
                        w=450,
                        showTabsAndSpaces=True,
                        showLineNumbers=True,
                        showTooltipHelp=True,
                    )
                with pc.frameLayout(label="pymel"):
                    self.py_feild = pc.cmdScrollFieldExecuter(
                        "pymelcode",
                        h=150,
                        w=450,
                        sourceType="python",
                        showTabsAndSpaces=True,
                        showLineNumbers=True,
                        showTooltipHelp=True,
                    )
            with pc.rowLayout(
                numberOfColumns=3,
                columnWidth3=(55, 140, 5),
                adjustableColumn=2,
                columnAlign=(1, "right"),
                columnAttach=[(1, "both", 0), (2, "both", 0), (3, "both", 0)],
            ):
                pc.button(label="Clear All", h=30, w=100, c=self.clear_feild_py)
                pc.button(label="Tanslate To Pymel !!!", h=30, w=200, c=self.mel2pymel)
                pc.button(label="Copy Pymel", h=30, w=100, c=self.copy_code_py)
        pc.window(self.win, e=True, h=350, w=500)
        pc.showWindow(self.win)

    def mel2pymel(self, *args):
        """
        该函数用于调用mel2py工具将mel字符串转换为pymel字符串
        """
        self.mel_cmd = pc.cmdScrollFieldExecuter(
            self.mel_feild, q=1, t=1
        )  # 读取输入的mel语言字符串
        self.py_cmd = mel2py.mel2pyStr(
            self.mel_cmd, pymelNamespace="pc"
        )  # 将mel字符串转换为pymel字符串
        pc.cmdScrollFieldExecuter(
            self.py_feild, e=1, t=self.py_cmd
        )  # 将修正后的字符串写入UI

    def clear_feild_py(self, *args):
        pc.cmdScrollFieldExecuter(self.py_feild, clear=True, e=True)
        pc.cmdScrollFieldExecuter(self.mel_feild, clear=True, e=True)

    def copy_code_py(self, *args):
        pc.cmdScrollFieldExecuter(self.py_feild, selectAll=True, e=True)
        pc.cmdScrollFieldExecuter(self.py_feild, copySelection=True, e=True)


if __name__ == "__main__":
    ct = Mel2Pymel()
