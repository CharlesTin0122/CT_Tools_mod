# coding: utf-8
# @Time    : 2023/4/3 13:32
# @Author  : TianChao
# @File    : test001.py
# @Email: tianchao0533@gamil.com
# @Software: PyCharm

import pymel.core as pc


class BatchConstrNearestObj(object):
    def __init__(self):
        self.window = None
        self.list1_ui = None
        self.list2_ui = None
        self.list1 = []
        self.list2 = []
        self.constrain_list = []

    def create_ui(self):
        try:
            pc.deleteUI("MyWin")
        except Exception as exc:
            print(exc)

        self.window = pc.window("MyWin", title="Batch Constrain Tool")
        with pc.columnLayout(rowSpacing=5, adj=True):
            with pc.frameLayout(label="BatchConstrNearestObj"):
                with pc.columnLayout(adj=1):
                    pc.button(
                        label="Load Constrain Obj", w=150, h=30, c=self.load_list1_click
                    )
                with pc.scrollLayout(
                    w=200, h=150, bgc=(0.5, 0.5, 0.5)
                ) as self.list1_ui:
                    pc.text("Obj List A:")
                with pc.columnLayout(adj=1):
                    pc.button(
                        label="Load be Constrained Obj",
                        w=150,
                        h=30,
                        c=self.load_list2_click,
                    )
                with pc.scrollLayout(
                    w=200, h=150, bgc=(0.5, 0.5, 0.5)
                ) as self.list2_ui:
                    pc.text("Obj List B:")
                with pc.columnLayout(adj=1):
                    pc.button(
                        label="Batch Constrain !!!", w=150, h=50, c=self.batch_constrain
                    )
        self.window.show()

    def load_list_click(self, list_ui, list_attr):
        selected_list = pc.selected()
        if not selected_list:
            pc.warning("No selected obj !!!")
            return
        setattr(self, list_attr, selected_list)
        with list_ui:
            for obj in selected_list:
                pc.text(label=f"{obj}")
        return selected_list

    def load_list1_click(self, *args):
        return self.load_list_click(self.list1_ui, "list1")

    def load_list2_click(self, *args):
        return self.load_list_click(self.list2_ui, "list2")

    def batch_constrain(self, *args):
        """用于在另一个对象列表中找到另一个对象列表中距离最近的对象并创建父子约束。
        Returns:None
        """
        # 遍历选定的所有对象
        for obj in self.list1:
            closest_obj = None  # 创建最近骨骼变量
            closest_distance = float("inf")  # 创建最近距离变量为正无穷
            pos1 = obj.getTranslation(space="world")  # 获取骨骼位置坐标

            # 遍历场景查找最近的骨骼
            for other_obj in self.list2:
                if other_obj == obj:  # 如果该骨骼已存在所选择骨骼
                    continue  # 则跳过
                pos2 = other_obj.getTranslation(space="world")  # 获取其他骨骼位置
                distance = (
                    pos1 - pos2
                ).length()  # 获取选择骨骼和其他骨骼之间的距离,注意.length求两点之间的距离
                """通过遍历所有其他骨骼和选择骨骼之间的距离，得到离选择骨骼最近的其他骨骼的距离"""
                if distance < closest_distance:  # 如果该距离小于最近骨骼距离即正无穷
                    closest_obj = other_obj  # 那么最近骨骼就是该骨骼
                    closest_distance = distance  # 最近距离就是该距离

            # 如果最近骨骼存在,同时骨骼没有被约束,父子约束到最近的骨骼
            if closest_obj:
                pc.parentConstraint(obj, closest_obj, maintainOffset=True)  # 执行约束
                constrain_list = f"{obj}->{closest_obj}"
                self.constrain_list.append(constrain_list)
        print(self.constrain_list)
        return self.constrain_list


if __name__ == "__main__":
    ui = BatchConstrNearestObj()
    ui.create_ui()
