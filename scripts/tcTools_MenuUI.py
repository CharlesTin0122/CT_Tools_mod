# -*- coding: utf-8 -*-
# @FileName :  fbx_exporter.py
# @Author   : TianChao
# @Email    : tianchao0533@gamil.com
# @Time     :  2023/5/19 9:38
# @Software : PyCharm
# Description:

import os
import sys
import pymel.core as pc

# 确定菜单分类
menuList = ["Modeling", "Rigging", "Animation", "TD"]
# 获取当前脚本所在路径
currentFilePath = r"{}".format(os.path.dirname(__file__))
# 获取脚本包所在路径
ScriptPackagesPath = r"{}\ScriptPackages".format(currentFilePath)
# 添加子菜单文件夹所在路径进入命令路径
commPath = [r"{}\{}".format(currentFilePath, folder) for folder in menuList]
# 添加脚本包所在路径进入命令路径
commPath.append(ScriptPackagesPath)
print(commPath, ScriptPackagesPath)

# 添加菜单文件夹路径到Python路径
for path in commPath:
    if path in sys.path:
        print("Already In Evn Path!")
    else:
        sys.path.append(path)
# 添加菜单文件夹路径到Mel路径
for path in commPath:
    if path in os.environ["MAYA_SCRIPT_PATH"]:
        print("Already In Evn Path!")
    else:
        os.environ["MAYA_SCRIPT_PATH"] = "{};{}".format(
            path, os.getenv("MAYA_SCRIPT_PATH")
        )

# 获取菜单和子菜单目录
menuItemDict = {}  # 创建字典以接受菜单和子菜单数据
# 遍历菜单路径找到路径下的模块文件
for item in menuList:
    itemlist = []
    item_path = os.path.join(currentFilePath, item)
    # 遍历路径找到所有文件
    for root_file, dirnames, filenames in os.walk(item_path):
        if filenames:
            for f in filenames:
                # 如果模块文件名以py结尾并且不在itemlist中
                if (f.split(".")[-1] == "py") and (f.split(".")[0] not in itemlist):
                    # 将模块名添加进itemlist列表
                    itemlist.append(f.split(".")[0])
    # 将item和itemlist添加到字典中
    menuItemDict[item] = itemlist
print(menuItemDict)


# 创建菜单函数
def createMenu(*args):
    # 尝试删除菜单，防止重复创建
    try:
        pc.deleteUI("myMenu")
    except Exception as exc:
        print(exc)
    # 获取maya主窗口变量
    gMainWindow = pc.mel.eval("$tmpVar=$gMainWindow")
    print(gMainWindow)
    # 在主窗口菜单栏创建菜单
    myMenu = pc.menu("myMenu", label="tcTools", p=gMainWindow, tearOff=True)

    for item, itemlist in menuItemDict.items():
        # 创建子菜单
        pc.menuItem(
            "{}_mItem".format(item), label=item, subMenu=True, p=myMenu, tearOff=True
        )
        # 创建子菜单的菜单项
        for comm in itemlist:
            pc.menuItem(
                "{}_mItem".format(comm),
                label=comm,
                p="{}_mItem".format(item),
                c="import {0};from importlib import reload;reload({0})".format(comm),
            )


# 删除菜单函数
def deleteMenu(*args):
    if pc.menu("myMenu", ex=True):
        pc.deleteUI("myMenu")
