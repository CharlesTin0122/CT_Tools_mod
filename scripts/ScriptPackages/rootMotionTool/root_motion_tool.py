# coding=utf-8

import pymel.core as pc


def mainUI():
    try:
        pc.deleteUI("motionTool")
    except Exception as e:
        print(e)

    temlate = pc.uiTemplate("ctTemplate", force=True)
    temlate.define(pc.button, w=200, h=50)
    temlate.define(pc.frameLayout, borderVisible=True, cll=True, cl=False)

    with pc.window("motionTool", title="Motion Tool") as win:
        with temlate:
            with pc.columnLayout(rowSpacing=5, adj=True):
                with pc.frameLayout(label="Motion Switch"):
                    with pc.columnLayout(
                        adj=1, columnAttach=("both", 5), rowSpacing=10
                    ):
                        pc.button(label="Local Motion", c=rootToLocal)
                        pc.button(label="Root Motion", c=localToRoot)
    pc.window(win, e=True, w=250, h=100)
    pc.showWindow(win)


def rootToLocal(*args):
    firstFrame = pc.findKeyframe("RootX_M", which="first")
    lastFrame = pc.findKeyframe("RootX_M", which="last")

    pc.spaceLocator(name="locPelvis")
    pc.spaceLocator(name="locLFoot")
    pc.spaceLocator(name="locRFoot")

    pc.parentConstraint("RootX_M", "locPelvis")
    pc.parentConstraint("IKLeg_L", "locLFoot")
    pc.parentConstraint("IKLeg_R", "locRFoot")

    pc.bakeResults("locPelvis", "locLFoot", "locRFoot", time=(firstFrame, lastFrame))

    pc.parentConstraint("locPelvis", "RootX_M")
    pc.parentConstraint("locLFoot", "IKLeg_L")
    pc.parentConstraint("locRFoot", "IKLeg_R")

    disAttr = [
        "Main.tx",
        "Main.ty",
        "Main.tz",
        "Main.rx",
        "Main.ry",
        "Main.rz",
        "root_ctrl.tx",
        "root_ctrl.ty",
        "root_ctrl.tz",
        "root_ctrl.rx",
        "root_ctrl.ry",
        "root_ctrl.rz",
    ]

    for _ in disAttr:
        pc.disconnectAttr(disAttr)

    pc.xform("Main", translation=(0, 0, 0), rotation=(0, 0, 0))
    pc.xform("root_ctrl", translation=(0, 0, 0), rotation=(0, 0, 0))

    pc.bakeResults("RootX_M", "IKLeg_L", "IKLeg_R", time=(firstFrame, lastFrame))

    pc.delete("locPelvis", "locLFoot", "locRFoot")


def localToRoot(*args):
    firstFrame = pc.findKeyframe("RootX_M", which="first")
    lastFrame = pc.findKeyframe("RootX_M", which="last")

    pc.spaceLocator(name="locPelvis")
    pc.spaceLocator(name="locLFoot")
    pc.spaceLocator(name="locRFoot")

    pc.parentConstraint("RootX_M", "locPelvis")
    pc.parentConstraint("IKLeg_L", "locLFoot")
    pc.parentConstraint("IKLeg_R", "locRFoot")

    pc.bakeResults("locPelvis", "locLFoot", "locRFoot", time=(firstFrame, lastFrame))

    pc.parentConstraint("locPelvis", "RootX_M")
    pc.parentConstraint("locLFoot", "IKLeg_L")
    pc.parentConstraint("locRFoot", "IKLeg_R")

    pelvisTX = pc.getAttr("RootX_M.translateX")
    # pelvisTY = pc.getAttr('RootX_M.translateY')
    pelvisTZ = pc.getAttr("RootX_M.translateZ")
    # pelvisRX = pc.getAttr('RootX_M.rotateX')
    pelvisRY = pc.getAttr("RootX_M.rotateY")
    # pelvisRZ = pc.getAttr('RootX_M.rotateZ')

    pc.setAttr("root_ctrl.translateX", pelvisTX)
    pc.setAttr("root_ctrl.translateY", pelvisTZ * -1)
    pc.setAttr("root_ctrl.translateZ", 0)
    pc.setAttr("root_ctrl.rotateX", 0)
    pc.setAttr("root_ctrl.rotateY", 0)
    pc.setAttr("root_ctrl.rotateZ", pelvisRY)

    pc.parentConstraint(
        "locPelvis", "root_ctrl", mo=True, skipTranslate=["z"], skipRotate=["x", "y"]
    )

    pc.bakeResults(
        "RootX_M",
        "IKLeg_L",
        "IKLeg_R",
        "root_ctrl",
        "Main",
        time=(firstFrame, lastFrame),
    )

    pc.delete("locPelvis", "locLFoot", "locRFoot")


if __name__ == "__main__":
    mainUI()
