import pymel.core as pc


def rename_obj(name="tail{3}Grp"):
    name = name.replace("{", "{i:0>")
    objList = pc.selected()
    for i, obj in enumerate(objList):
        pc.rename(obj, name.format(i=i + 1))


rename_obj(name="tail{2}jnt")


def creatFKCtrl():
    obj_list = pc.selected()
    prefix = "FK"
    ctrl = pc.group(n="{}Grp".format(prefix), em=True)

    for i, jnt in enumerate(obj_list):
        print(i, jnt)
        grpName = pc.createNode(
            "transform", n="{}{i:0>2}Grp".format(prefix, i=i + 1), p=jnt
        )
        pc.parent(grpName, ctrl)
        ctrl = pc.circle(
            ch=False, nr=[1, 0, 0], n="{}{i:0>2}ctrl".format(prefix, i=i + 1), r=30
        )[0]
        pc.parent(ctrl, grpName)
        pc.setAttr(ctrl + ".t", 0, 0, 0)
        pc.setAttr(ctrl + ".r", 0, 0, 0)
        pc.createNode("joint", p=ctrl, n="{}{i:0>2}Jnt".format(prefix, i=i + 1))


creatFKCtrl()


def getSkinJoint():
    for mesh in pc.ls(ni=1, v=1, type="mesh"):
        for skin in mesh.listHistory(type="skinCluster"):
            jnt = skin.listHistory(type="joint")
