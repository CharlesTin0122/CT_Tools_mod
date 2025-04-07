# coding:UTF-8
# ***********************************************//
#                                               //
#               RePARENT PRO 1.5.1              //
#      copyright Dmitrii Kolpakov 2020          //
#                                               //
# ***********************************************//

import pymel.core as pc

pc.progressWindow(endProgress=1)
pc.optionVar(intValue=("animBlendingOpt", 1))
if pc.window("ReParentPanel", ex=1):
    pc.deleteUI("ReParentPanel")

window = str(
    pc.window(
        "ReParentPanel",
        s=0,
        toolbox=1,
        menuBar=1,
        t="ReParent v1.5.1 Pro",
        wh=(142, 159),
    )
)
pc.menu("aboutMenu", to=0, l="Advanced")
pc.menuItem(
    "onLayerMode",
    cb=0,
    ann="Each new overlapping animation will be baked on new animation layer",
    l="Bake on anim layer",
)
pc.menuItem(
    "DelRed",
    cb=1,
    ann="Delete all redundant keys on rePaent locators",
    l="Delete redundant",
)
pc.menuItem(
    c=lambda *args: pc.mel.BakeAndDelete_reParent(),
    ann="Bake All animation and delete rePaent locators",
    l="BAKE AND DELETE",
)
pc.menu("helpcenu", to=0, l="Help")
pc.menuItem(c=lambda *args: pc.mel.reParentIntro(), l="Intro")
pc.menuItem(c=lambda *args: pc.mel.reParentTutorial(), l="Tutorial")
pc.rowColumnLayout()
pc.rowLayout(nc=2, cw=(30, 30))
pc.rowColumnLayout(nc=1)
pc.checkBox(
    "PinCheckBox",
    h=18,
    ann="Pin selected controls (delete all animation and constrain to locator)",
    v=0,
    label=" Pin ",
)
pc.rowColumnLayout(columnWidth=[(1, 70), (2, 50)], nc=2)
pc.checkBox(
    "IKCheckBox",
    h=18,
    ann="rePArent three FK controls to IK mode",
    v=0,
    label=" IK mode ",
)
pc.checkBox(
    "IKCheckLocalBox",
    h=18,
    ann="rePArent three FK controls to IK mode with parent to the first control",
    v=0,
    label=" Local ",
)
pc.setParent("..")
pc.rowLayout(nc=1, cw=(30, 30))
pc.rowColumnLayout(columnWidth=(1, 130), nc=1)
pc.checkBox(
    "ManualCheckBox",
    h=18,
    ann="Move reParent locator to set required pivot and press Go",
    v=0,
    label=" Manual pivot ",
)
pc.checkBox(
    "FreezeCheckBox",
    h=18,
    ann="Freeze all contols regarding the first selected control",
    v=0,
    label=" Freeze main ",
)
pc.checkBox(
    "RelativeCheckBox",
    h=18,
    ann="Select controls for reParent then last control for relative",
    v=0,
    label=" All to the last ",
)
pc.button(
    "reParentButton",
    h=40,
    c=lambda *args: pc.mel.reParentStarter(),
    bgc=(0.8, 0.8, 0.8),
    l="reParent",
    w=120,
)
pc.rowColumnLayout(columnWidth=[(1, 70), (2, 50)], nc=2, rs=(1, 100))
pc.button(
    h=40, c=lambda *args: pc.mel.manualModeGo(), bgc=(0.8, 0.8, 0.8), l="Go", w=40
)
pc.button(
    h=40,
    c=lambda *args: pc.mel.manualModeCancel(),
    bgc=(0.22, 0.22, 0.22),
    l="Cancel",
    w=60,
)
pc.setParent("..")
pc.window("ReParentPanel", edit=1, widthHeight=(142, 159))
pc.showWindow("ReParentPanel")


def _reParentIntro():
    pc.launch(web="https://www.youtube.com/watch?v=7jqzIceFKbo")


def _BakeAndDelete_reParent():
    currentR = int(pc.playbackOptions(q=1, min=1))
    currentL = int(pc.playbackOptions(q=1, max=1))
    pc.select("All_Sessions_reParentControls_set", r=1)
    pc.bakeResults(
        sparseAnimCurveBake=0,
        minimizeRotation=1,
        removeBakedAttributeFromLayer=0,
        removeBakedAnimFromLayer=0,
        bakeOnOverrideLayer=0,
        preserveOutsideKeys=1,
        simulation=1,
        sampleBy=1,
        shape=0,
        t=(str(currentL) + ":" + str(currentR)),
        at=["tx", "ty", "tz", "rx", "ry", "rz"],
        disableImplicitControl=1,
        controlPoints=0,
    )
    if pc.objExists("All_Session_reParentLocator_set"):
        pc.select("All_Session_reParentLocator_set", r=1)
        pc.delete()

    if pc.objExists("reParent_sets"):
        pc.delete("reParent_sets")

    if pc.objExists("All_Sessions_reParentControls_set"):
        pc.delete("All_Sessions_reParentControls_set")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")

    if pc.objExists("*_reParentIK_grp"):
        pc.delete("*_reParentIK_grp")

    if pc.objExists("*:*_reParentIK_grp"):
        pc.delete("*:*_reParentIK_grp")

    if pc.objExists("*_ReParent_grp"):
        pc.delete("*_ReParent_grp")

    if pc.objExists("*:*_ReParent_grp"):
        pc.delete("*:*_ReParent_grp")


def _reParentTutorial():
    pc.launch(web="https://www.youtube.com/watch?v=7jqzIceFKbo")


def reParentStarter():
    FreezeButton = int(pc.checkBox("FreezeCheckBox", q=1, v=1))
    RelativeButton = int(pc.checkBox("RelativeCheckBox", q=1, v=1))
    IKButton = int(pc.checkBox("IKCheckBox", q=1, v=1))
    PinButton = int(pc.checkBox("PinCheckBox", q=1, v=1))
    ManualButton = int(pc.checkBox("ManualCheckBox", q=1, v=1))
    SelectedControls = pc.ls(sl=1)
    if not len(SelectedControls):
        pc.confirmDialog(b="Ok", m="SELECT ANY CONTROL", t="Oooops..")

    elif FreezeButton + RelativeButton + IKButton + PinButton + ManualButton > 1:
        pc.confirmDialog(b="Ok", m="Select one of mode", t="Oooops..")

    elif IKButton == 1:
        SelectedControls = pc.ls(sl=1)
        if len(SelectedControls) != 3:
            pc.confirmDialog(
                b="Ok", m="IK mode works only for three controls", t="Oooops.."
            )

        else:
            pc.mel.IKmode()

    if FreezeButton == 1:
        pc.mel.reParentStayHere()

    if (
        FreezeButton == 0
        and RelativeButton == 0
        and IKButton == 0
        and ManualButton == 0
    ):
        pc.mel.reParent()

    if (
        FreezeButton == 0
        and RelativeButton == 1
        and IKButton == 0
        and ManualButton == 0
    ):
        pc.mel.reParentRelativeStart()

    if (
        FreezeButton == 0
        and RelativeButton == 0
        and IKButton == 0
        and ManualButton == 1
    ):
        pc.mel.reParentManualStarter()


def reParent():
    """/////////////////////////////////////
                  reParent             //
    /////////////////////////////////////"""

    PinButton = int(pc.checkBox("PinCheckBox", q=1, v=1))
    DelRedMode = int(pc.menuItem("DelRed", query=1, cb=1))
    SelCtrl = ""
    SelectedControls = pc.ls(sl=1)
    currentR = int(pc.playbackOptions(q=1, min=1))
    currentL = int(pc.playbackOptions(q=1, max=1))
    if pc.objExists("TempLocator"):
        pc.delete("TempLocator")

    if not pc.objExists("reParent_sets"):
        pc.sets(em=1, name="reParent_sets")
        # Create Sets

    if pc.objExists("All_Sessions_reParentControls_set"):
        pc.sets(
            SelectedControls, edit=1, forceElement="All_Sessions_reParentControls_set"
        )
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="All_Sessions_reParentControls_set")
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets(
            SelectedControls, edit=1, forceElement="Last_Session_reParentControls_set"
        )
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    pc.select(cl=1)
    if pc.objExists("Last_Session_reParentLocator_set"):
        pc.delete("Last_Session_reParentLocator_set")
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    if not pc.objExists("All_Session_reParentLocator_set"):
        pc.sets(em=1, name="All_Session_reParentLocator_set")
        pc.sets("All_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    for SelCtrl in SelectedControls:
        pc.select(SelCtrl, r=1)
        SelectedControls = pc.ls(sl=1)
        pc.spaceLocator(n="TempLocator")
        pc.setAttr("TempLocator.rotateOrder", 2)
        pc.matchTransform("TempLocator", SelectedControls[0], rot=1, pos=1)
        pc.select(SelCtrl, r=1)
        pc.mel.reParentLocatorSize()
        # create Last_Session_reParentLocator_set
        pc.sets("TempLocator", edit=1, forceElement="Last_Session_reParentLocator_set")
        pc.sets("TempLocator", edit=1, forceElement="All_Session_reParentLocator_set")
        pc.select(SelCtrl, "TempLocator", r=1)
        print(PinButton)
        if PinButton == 0:
            pc.select(SelCtrl, "TempLocator", r=1)
            pc.orientConstraint(mo=1, weight=1, n="TempOrientConst")
            pc.pointConstraint(mo=1, weight=1, n="TempPointConst")

        pc.select("TempLocator")
        pc.rename("TempLocator", (str(SelCtrl) + "_ReParent_Locator"))
        pc.select(cl=1)

    pc.select("Last_Session_reParentLocator_set", r=1)
    if PinButton == 0:
        pc.bakeResults(
            sparseAnimCurveBake=0,
            minimizeRotation=1,
            removeBakedAttributeFromLayer=0,
            removeBakedAnimFromLayer=0,
            bakeOnOverrideLayer=0,
            preserveOutsideKeys=1,
            simulation=1,
            sampleBy=1,
            shape=0,
            t=(str(currentL) + ":" + str(currentR)),
            at=["tx", "ty", "tz", "rx", "ry", "rz"],
            disableImplicitControl=1,
            controlPoints=0,
        )

    pc.delete("TempOrientConst*", "TempPointConst*")
    if pc.objExists("TempLocator"):
        pc.delete("TempOrientConst*", "TempPointConst*")

    for SelCtrl in SelectedControls:
        if (
            pc.getAttr((str(SelCtrl) + ".tx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".tx"), lock=1) == 0
        ):
            pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
            pc.pointConstraint(weight=1, n=(str(SelCtrl) + "ReParent"))

        if (
            pc.getAttr((str(SelCtrl) + ".rx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".rx"), lock=1) == 0
        ):
            pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
            pc.orientConstraint(weight=1, n=(str(SelCtrl) + "ReParent"))

        pc.cutKey(SelCtrl, at=["tx", "ty", "tz", "rx", "ry", "rz"], f=":", t=":", cl=1)

    if DelRedMode == 1:
        pc.select("Last_Session_reParentLocator_set", r=1)
        # simplifier///
        SelectedControls = pc.ls(sl=1)
        pc.selectKey(k=1, r=1)
        selectedCurves = pc.keyframe(q=1, selected=1, name=1)
        # delete redundant
        for currentAnimCurve in selectedCurves:
            allKeys = pc.keyframe(currentAnimCurve, q=1, timeChange=1)
            valArray = pc.keyframe(currentAnimCurve, q=1, valueChange=1)
            keysSize = len(allKeys)
            for s in range(1, keysSize - 1):
                if valArray[s] == valArray[s - 1] and valArray[s] == valArray[s + 1]:
                    pc.cutKey(currentAnimCurve, clear=1, time=allKeys[s])

    ClearElemwnts = 0
    # euler all anim curves
    pc.melGlobals.initVar("string[]", "eulerFilterCurves")
    ClearElemwnts = len(pc.melGlobals["eulerFilterCurves"])
    for s in range(0, ClearElemwnts):
        pc.melGlobals["eulerFilterCurves"].pop(0)

    pc.select("Last_Session_reParentLocator_set", r=1)
    EulerArrays = pc.ls(sl=1)
    for obj in EulerArrays:
        listAnimAttrs = pc.listAttr(obj, k=1)
        for attr in listAnimAttrs:
            animCurve = pc.listConnections(
                (str(obj) + "." + str(attr)), type="animCurve"
            )
            ClearElemwnts = len(animCurve)
            pc.melGlobals["eulerFilterCurves"] += animCurve[:ClearElemwnts]

    pc.filterCurve(pc.melGlobals["eulerFilterCurves"])
    pc.select(SelectedControls, r=1)


def reParentManualStarter():
    """/////////////////////////////////////
                Manual MODE            //
    /////////////////////////////////////"""

    pc.window("ReParentPanel", edit=1, widthHeight=(142, 203))
    pc.button("reParentButton", edit=1, en=0)
    int(pc.checkBox("PinCheckBox", q=1, v=1))
    SelCtrl = ""
    SelectedControls = pc.ls(sl=1)
    if pc.objExists("TempLocator"):
        pc.delete("TempLocator")

    if not pc.objExists("reParent_sets"):
        pc.sets(em=1, name="reParent_sets")
        # Create Sets

    if pc.objExists("All_Sessions_reParentControls_set"):
        pc.sets(
            SelectedControls, edit=1, forceElement="All_Sessions_reParentControls_set"
        )
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="All_Sessions_reParentControls_set")
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets(
            SelectedControls, edit=1, forceElement="Last_Session_reParentControls_set"
        )
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    pc.select(cl=1)
    if pc.objExists("Last_Session_reParentLocator_set"):
        pc.delete("Last_Session_reParentLocator_set")
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    if not pc.objExists("All_Session_reParentLocator_set"):
        pc.sets(em=1, name="All_Session_reParentLocator_set")
        pc.sets("All_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    for SelCtrl in SelectedControls:
        pc.select(SelCtrl, r=1)
        SelectedControls = pc.ls(sl=1)
        pc.spaceLocator(n="TempLocator")
        pc.setAttr("TempLocator.rotateOrder", 2)
        pc.matchTransform("TempLocator", SelectedControls[0])
        pc.select(SelCtrl, r=1)
        pc.mel.reParentLocatorSize()
        pc.sets("TempLocator", edit=1, forceElement="Last_Session_reParentLocator_set")
        pc.sets("TempLocator", edit=1, forceElement="All_Session_reParentLocator_set")
        pc.select(SelCtrl, "TempLocator", r=1)
        temps = pc.pointConstraint(weight=1, offset=(0, 0, 0))
        pc.delete(temps)
        temps = pc.orientConstraint(weight=1, offset=(0, 0, 0))
        pc.delete(temps)
        pc.select("TempLocator")
        pc.rename("TempLocator", (str(SelCtrl) + "_ReParent_Locator"))


def manualModeCancel():
    if pc.window("ManualWindow", ex=1):
        pc.deleteUI("ManualWindow")

    pc.window("ReParentPanel", edit=1, widthHeight=(142, 159))
    pc.button("reParentButton", edit=1, en=1)
    pc.select("Last_Session_reParentLocator_set", r=1)
    pc.delete()


def manualModeGo():
    if pc.window("ManualWindow", ex=1):
        pc.deleteUI("ManualWindow")

    PinButton = int(pc.checkBox("PinCheckBox", q=1, v=1))
    DelRedMode = int(pc.menuItem("DelRed", query=1, cb=1))
    pc.select("Last_Session_reParentControls_set", r=1)
    SelectedControls = pc.ls(sl=1)
    currentR = int(pc.playbackOptions(q=1, min=1))
    currentL = int(pc.playbackOptions(q=1, max=1))
    for SelCtrl in SelectedControls:
        if PinButton == 0:
            pc.select(SelCtrl, (str(SelCtrl) + "_ReParent_Locator"), r=1)
            pc.parentConstraint(mo=1, weight=1, n="TempParentConst")

    pc.select("Last_Session_reParentLocator_set", r=1)
    if PinButton == 0:
        pc.bakeResults(
            sparseAnimCurveBake=0,
            minimizeRotation=1,
            removeBakedAttributeFromLayer=0,
            removeBakedAnimFromLayer=0,
            bakeOnOverrideLayer=0,
            preserveOutsideKeys=1,
            simulation=1,
            sampleBy=1,
            shape=0,
            t=(str(currentL) + ":" + str(currentR)),
            at=["tx", "ty", "tz", "rx", "ry", "rz"],
            disableImplicitControl=1,
            controlPoints=0,
        )

    pc.delete("TempParentConst*")
    if pc.objExists("TempLocator"):
        pc.delete("TempOrientConst*", "TempPointConst*")

    for SelCtrl in SelectedControls:
        if (
            pc.getAttr((str(SelCtrl) + ".tx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".tx"), lock=1) == 0
            and pc.getAttr((str(SelCtrl) + ".rx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".rx"), lock=1) == 0
        ):
            pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
            pc.parentConstraint(mo=1, weight=1, n=(str(SelCtrl) + "ReParent"))

        else:
            if (
                pc.getAttr((str(SelCtrl) + ".tx"), keyable=1) == 1
                and pc.getAttr((str(SelCtrl) + ".tx"), lock=1) == 0
            ):
                pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
                pc.pointConstraint(mo=1, weight=1, n=(str(SelCtrl) + "ReParent"))

            if (
                pc.getAttr((str(SelCtrl) + ".rx"), keyable=1) == 1
                and pc.getAttr((str(SelCtrl) + ".rx"), lock=1) == 0
            ):
                pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
                pc.orientConstraint(mo=1, weight=1, n=(str(SelCtrl) + "ReParent"))

        pc.cutKey(SelCtrl, at=["tx", "ty", "tz", "rx", "ry", "rz"], f=":", t=":", cl=1)

    if DelRedMode == 1:
        pc.select("Last_Session_reParentLocator_set", r=1)
        # simplifier///
        SelectedControls = pc.ls(sl=1)
        pc.selectKey(k=1, r=1)
        selectedCurves = pc.keyframe(q=1, selected=1, name=1)
        # delete redundant
        for currentAnimCurve in selectedCurves:
            allKeys = pc.keyframe(currentAnimCurve, q=1, timeChange=1)
            valArray = pc.keyframe(currentAnimCurve, q=1, valueChange=1)
            keysSize = len(allKeys)
            for s in range(1, keysSize - 1):
                if valArray[s] == valArray[s - 1] and valArray[s] == valArray[s + 1]:
                    pc.cutKey(currentAnimCurve, clear=1, time=allKeys[s])

    ClearElemwnts = 0
    # euler all anim curves
    pc.melGlobals.initVar("string[]", "pc.melGlobals['eulerFilterCurves'")
    ClearElemwnts = len(pc.melGlobals["eulerFilterCurves"])
    for s in range(0, ClearElemwnts):
        pc.melGlobals["eulerFilterCurves"].pop(0)

    pc.select("Last_Session_reParentLocator_set", r=1)
    EulerArrays = pc.ls(sl=1)
    for obj in EulerArrays:
        listAnimAttrs = pc.listAttr(obj, k=1)
        for attr in listAnimAttrs:
            animCurve = pc.listConnections(
                (str(obj) + "." + str(attr)), type="animCurve"
            )
            ClearElemwnts = len(animCurve)
            pc.melGlobals["eulerFilterCurves"] += animCurve[:ClearElemwnts]

    pc.filterCurve(pc.melGlobals["eulerFilterCurves"])
    pc.select(SelectedControls, r=1)
    pc.window("ReParentPanel", edit=1, widthHeight=(142, 159))
    pc.button("reParentButton", edit=1, en=1)


def reParentRelativeStart():
    """/////////////////////////////////////
             reParentRelative          //
    /////////////////////////////////////"""

    SelectedControls = pc.ls(sl=1)
    amountCheck = len(SelectedControls)
    if amountCheck > 1:
        pc.mel.reParentRelative()

    else:
        pc.confirmDialog(
            b="Ok",
            m=" FOR RELATIVE MODE YOU NEED TO SELECT 2 AND MORE CONTROLS \n First for reparent and second relative",
            t="Oooops..",
        )


def reParentRelative():
    int(pc.checkBox("PinCheckBox", q=1, v=1))
    DelRedMode = int(pc.menuItem("DelRed", query=1, cb=1))
    SelectedControls = pc.ls(sl=1)
    len(SelectedControls)
    currentR = int(pc.playbackOptions(q=1, min=1))
    currentL = int(pc.playbackOptions(q=1, max=1))
    if pc.objExists("TempLocator"):
        pc.delete("TempLocator")

    if not pc.objExists("reParent_sets"):
        pc.sets(em=1, name="reParent_sets")
        # Create Sets

    if pc.objExists("All_Sessions_reParentControls_set"):
        pc.sets(
            SelectedControls, edit=1, forceElement="All_Sessions_reParentControls_set"
        )
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="All_Sessions_reParentControls_set")
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets(
            SelectedControls, edit=1, forceElement="Last_Session_reParentControls_set"
        )
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    pc.select(cl=1)
    if pc.objExists("Last_Session_reParentLocator_set"):
        pc.delete("Last_Session_reParentLocator_set")
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    if not pc.objExists("All_Session_reParentLocator_set"):
        pc.sets(em=1, name="All_Session_reParentLocator_set")
        pc.sets("All_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    amountOfAllCtrls = len(SelectedControls)
    for r in range(0, amountOfAllCtrls - 1):
        pc.select(SelectedControls[r], r=1)
        pc.spaceLocator(n="TempLocator")
        pc.setAttr("TempLocator.rotateOrder", 2)
        pc.matchTransform("TempLocator", SelectedControls[r])
        pc.select(SelectedControls[r], r=1)
        pc.mel.reParentLocatorSize()
        pc.sets("TempLocator", edit=1, forceElement="Last_Session_reParentLocator_set")
        pc.sets("TempLocator", edit=1, forceElement="All_Session_reParentLocator_set")
        pc.group("TempLocator", name=(SelectedControls[r] + "_ReParent_grp"))
        pc.parentConstraint(
            SelectedControls[amountOfAllCtrls - 1],
            (SelectedControls[r] + "_ReParent_grp"),
            mo=1,
            w=1,
            n=(SelectedControls[r] + "_ReParent_Const"),
        )
        pc.select(SelectedControls[r], "TempLocator", r=1)
        pc.orientConstraint(mo=1, weight=1, n=(SelectedControls[r] + "TempOrientConst"))
        pc.pointConstraint(mo=1, weight=1, n=(SelectedControls[r] + "TempPointConst"))
        pc.rename("TempLocator", (SelectedControls[r] + "_ReParent_Locator"))

    pc.select("Last_Session_reParentLocator_set", r=1)
    pc.bakeResults(
        sparseAnimCurveBake=0,
        minimizeRotation=1,
        removeBakedAttributeFromLayer=0,
        removeBakedAnimFromLayer=0,
        bakeOnOverrideLayer=0,
        preserveOutsideKeys=1,
        simulation=1,
        sampleBy=1,
        shape=0,
        t=(str(currentL) + ":" + str(currentR)),
        at=["tx", "ty", "tz", "rx", "ry", "rz"],
        disableImplicitControl=1,
        controlPoints=0,
    )
    for r in range(0, amountOfAllCtrls - 1):
        if (
            pc.getAttr((SelectedControls[r] + ".tx"), keyable=1) == 1
            and pc.getAttr((SelectedControls[r] + ".tx"), lock=1) == 0
        ):
            pc.select((SelectedControls[r] + "_ReParent_Locator"), SelectedControls[r])
            pc.pointConstraint(weight=1, n=(SelectedControls[r] + "ReParent"))

        if (
            pc.getAttr((SelectedControls[r] + ".rx"), keyable=1) == 1
            and pc.getAttr((SelectedControls[r] + ".rx"), lock=1) == 0
        ):
            pc.select((SelectedControls[r] + "_ReParent_Locator"), SelectedControls[r])
            pc.orientConstraint(weight=1, n=(SelectedControls[r] + "ReParent"))

        pc.cutKey(
            SelectedControls[r],
            at=["tx", "ty", "tz", "rx", "ry", "rz"],
            f=":",
            t=":",
            cl=1,
        )
        pc.delete(
            (SelectedControls[r] + "TempOrientConst"),
            (SelectedControls[r] + "TempPointConst"),
        )

    if DelRedMode == 1:
        pc.select("Last_Session_reParentLocator_set", r=1)
        # simplifier///
        SelectedControls = pc.ls(sl=1)
        pc.selectKey(k=1, r=1)
        selectedCurves = pc.keyframe(q=1, selected=1, name=1)
        # delete redundant
        for currentAnimCurve in selectedCurves:
            allKeys = pc.keyframe(currentAnimCurve, q=1, timeChange=1)
            valArray = pc.keyframe(currentAnimCurve, q=1, valueChange=1)
            keysSize = len(allKeys)
            for s in range(1, keysSize - 1):
                if valArray[s] == valArray[s - 1] and valArray[s] == valArray[s + 1]:
                    pc.cutKey(currentAnimCurve, clear=1, time=allKeys[s])

    ClearElemwnts = 0
    # euler all anim curves
    pc.melGlobals.initVar("string[]", "pc.melGlobals['eulerFilterCurves'")
    ClearElemwnts = len(pc.melGlobals["eulerFilterCurves"])
    for s in range(0, ClearElemwnts):
        pc.melGlobals["eulerFilterCurves"].pop(0)

    pc.select("Last_Session_reParentLocator_set", r=1)
    EulerArrays = pc.ls(sl=1)
    for obj in EulerArrays:
        listAnimAttrs = pc.listAttr(obj, k=1)
        for attr in listAnimAttrs:
            animCurve = pc.listConnections(
                (str(obj) + "." + str(attr)), type="animCurve"
            )
            ClearElemwnts = len(animCurve)
            pc.melGlobals["eulerFilterCurves"] += animCurve[:ClearElemwnts]

    pc.filterCurve(pc.melGlobals["eulerFilterCurves"])
    pc.select(SelectedControls, r=1)


def reParentStayHere():
    """/////////////////////////////////////
                 freezeMain            //
    /////////////////////////////////////"""

    amount = 0
    # progressBar
    pc.progressWindow(
        status="Progress: 0%",
        progress=amount,
        isInterruptable=True,
        title="progress...",
    )
    SelCtrl = ""
    SelectedControls = pc.ls(sl=1)
    currentR = int(pc.playbackOptions(q=1, min=1))
    currentL = int(pc.playbackOptions(q=1, max=1))
    # Create Sets
    if not pc.objExists("reParent_sets"):
        pc.sets(em=1, name="reParent_sets")

    if pc.objExists("TempLocator"):
        pc.delete("TempLocator")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets(
            SelectedControls, edit=1, forceElement="Last_Session_reParentControls_set"
        )
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    pc.select(cl=1)
    if pc.objExists("Last_Session_reParentLocator_set"):
        pc.delete("Last_Session_reParentLocator_set")
        pc.sets(name="Last_Session_reParentLocator_set")

    else:
        pc.sets(name="Last_Session_reParentLocator_set")

    amount += 20
    # progressBar
    pc.progressWindow(
        edit=1, progress=amount, status=("Progress: " + str(amount) + "%")
    )
    for SelCtrl in SelectedControls:
        pc.select(SelCtrl, r=1)
        SelectedControls = pc.ls(sl=1)
        pc.spaceLocator(n="TempLocator")
        pc.setAttr("TempLocator.rotateOrder", 2)
        pc.matchTransform("TempLocator", SelectedControls[0], rot=1, pos=1)
        pc.select(SelCtrl, r=1)
        pc.mel.reParentLocatorSize()
        pc.sets("TempLocator", edit=1, forceElement="Last_Session_reParentLocator_set")
        pc.select(SelCtrl, "TempLocator", r=1)
        pc.select(SelCtrl, "TempLocator", r=1)
        pc.orientConstraint(mo=1, weight=1, n="TempOrientConst")
        pc.pointConstraint(mo=1, weight=1, n="TempPointConst")
        pc.select("TempLocator")
        pc.rename("TempLocator", (str(SelCtrl) + "_ReParent_Locator"))
        pc.select(cl=1)

    amount += 20
    # progressBar
    pc.progressWindow(
        edit=1, progress=amount, status=("Progress: " + str(amount) + "%")
    )
    pc.select("Last_Session_reParentLocator_set", r=1)
    pc.bakeResults(
        sparseAnimCurveBake=0,
        minimizeRotation=1,
        removeBakedAttributeFromLayer=0,
        removeBakedAnimFromLayer=0,
        bakeOnOverrideLayer=0,
        preserveOutsideKeys=1,
        simulation=1,
        sampleBy=1,
        shape=0,
        t=(str(currentL) + ":" + str(currentR)),
        at=["tx", "ty", "tz", "rx", "ry", "rz"],
        disableImplicitControl=1,
        controlPoints=0,
    )
    # progressBar
    amount += 20
    pc.progressWindow(
        edit=1, progress=amount, status=("Progress: " + str(amount) + "%")
    )
    pc.delete((SelectedControls[0]), constraints=1)
    for SelCtrl in SelectedControls:
        if (
            pc.getAttr((str(SelCtrl) + ".tx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".tx"), lock=1) == 0
        ):
            pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
            pc.pointConstraint(weight=1, n=(str(SelCtrl) + "ReParent"))

        if (
            pc.getAttr((str(SelCtrl) + ".rx"), keyable=1) == 1
            and pc.getAttr((str(SelCtrl) + ".rx"), lock=1) == 0
        ):
            pc.select((str(SelCtrl) + "_ReParent_Locator"), SelCtrl)
            pc.orientConstraint(weight=1, n=(str(SelCtrl) + "ReParent"))

    pc.select(SelectedControls[0], r=1)
    pc.cutKey(
        (SelectedControls[0]),
        at=["tx", "ty", "tz", "rx", "ry", "rz"],
        f=":",
        t=":",
        cl=1,
    )
    pc.delete((SelectedControls[0]), constraints=1)
    # progressBar
    amount += 20
    pc.progressWindow(
        edit=1, progress=amount, status=("Progress: " + str(amount) + "%")
    )
    pc.select("Last_Session_reParentControls_set", r=1)
    pc.select(SelectedControls[0], d=1)
    pc.bakeResults(
        sparseAnimCurveBake=0,
        minimizeRotation=1,
        removeBakedAttributeFromLayer=0,
        removeBakedAnimFromLayer=0,
        bakeOnOverrideLayer=0,
        preserveOutsideKeys=1,
        simulation=0,
        sampleBy=1,
        shape=0,
        t=(str(currentL) + ":" + str(currentR)),
        at=["tx", "ty", "tz", "rx", "ry", "rz"],
        disableImplicitControl=1,
        controlPoints=0,
    )
    # progressBar
    amount += 20
    pc.progressWindow(
        edit=1, progress=amount, status=("Progress: " + str(amount) + "%")
    )
    pc.select("Last_Session_reParentLocator_set", r=1)
    pc.delete()
    pc.select(SelectedControls, r=1)
    pc.progressWindow(endProgress=1)


def IKmode():
    """/////////////////////////////////////
                  IK mode              //
    /////////////////////////////////////"""

    SelectedControls = pc.ls(sl=1)
    pc.melGlobals.initVar("string[]", "UpHierarchyObject")
    # Create Sets
    if not pc.objExists("reParent_sets"):
        pc.sets(em=1, name="reParent_sets")

    if pc.objExists("All_Sessions_reParentControls_set"):
        pc.sets(
            SelectedControls, edit=1, forceElement="All_Sessions_reParentControls_set"
        )
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="All_Sessions_reParentControls_set")
        pc.sets("All_Sessions_reParentControls_set", edit=1, fe="reParent_sets")

    if pc.objExists("Last_Session_reParentControls_set"):
        pc.delete("Last_Session_reParentControls_set")
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets(
            SelectedControls, edit=1, forceElement="Last_Session_reParentControls_set"
        )
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentControls_set")
        pc.sets("Last_Session_reParentControls_set", edit=1, fe="reParent_sets")

    pc.select(cl=1)
    if pc.objExists("Last_Session_reParentLocator_set"):
        pc.delete("Last_Session_reParentLocator_set")
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    else:
        pc.sets(name="Last_Session_reParentLocator_set")
        pc.sets("Last_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    if not pc.objExists("All_Session_reParentLocator_set"):
        pc.sets(em=1, name="All_Session_reParentLocator_set")
        pc.sets("All_Session_reParentLocator_set", edit=1, fe="reParent_sets")

    # create locators for Joints
    for i in range(0, 3):
        pc.spaceLocator(n=(SelectedControls[i] + "_reParentIKlocator"))
        pc.parentConstraint(
            SelectedControls[i], (SelectedControls[i] + "_reParentIKlocator"), weight=1
        )

    pc.select(cl=1)
    # create Joints
    for i in range(0, 3):
        WorldTr = pc.xform((SelectedControls[i] + "_reParentIKlocator"), q=1, ws=1, t=1)
        pc.joint(
            p=(WorldTr[0], WorldTr[1], WorldTr[2]),
            rad=1,
            n=(SelectedControls[i] + "_reParentIKJoint"),
        )
        if i > 0:
            pc.joint(
                (SelectedControls[i - 1] + "_reParentIKJoint"),
                zso=1,
                e=1,
                oj="yxz",
                secondaryAxisOrient="zup",
            )

    pc.spaceLocator(n=(SelectedControls[1] + "_reParentIKPole"))
    PoleVectorLengths = float(
        (pc.getAttr(SelectedControls[1] + "_reParentIKJoint.translateY"))
        + (pc.getAttr(SelectedControls[2] + "_reParentIKJoint.translateY"))
    )
    PoleVectorMult = float(
        (pc.getAttr(SelectedControls[2] + "_reParentIKJoint.translateY"))
        / (pc.getAttr(SelectedControls[1] + "_reParentIKJoint.translateY"))
    )
    firstRePArentIK_locator_vector = pc.xform(
        (SelectedControls[0] + "_reParentIKlocator"), q=1, ws=1, t=1
    )
    secondRePArentIK_locator_vector = pc.xform(
        (SelectedControls[1] + "_reParentIKlocator"), q=1, ws=1, t=1
    )
    thindRePArentIK_locator_vector = pc.xform(
        (SelectedControls[2] + "_reParentIKlocator"), q=1, ws=1, t=1
    )
    mainVector = (
        (thindRePArentIK_locator_vector - firstRePArentIK_locator_vector)
        / (1 + PoleVectorMult)
    ) + firstRePArentIK_locator_vector
    poleVector = secondRePArentIK_locator_vector - mainVector
    poleVectorLen = float(
        pc.mel.sqrt(
            pow((poleVector.x), 2) + pow((poleVector.y), 2) + pow((poleVector.z), 2)
        )
    )
    poleNorm = [
        ((poleVector.x) / poleVectorLen),
        ((poleVector.y) / poleVectorLen),
        ((poleVector.z) / poleVectorLen),
    ]
    FinalPoleVector = poleNorm * (PoleVectorLengths) + mainVector
    pc.xform(
        (SelectedControls[1] + "_reParentIKPole"),
        ws=1,
        t=((FinalPoleVector.x), (FinalPoleVector.y), (FinalPoleVector.z)),
    )
    pc.parent(
        (SelectedControls[1] + "_reParentIKPole"),
        (SelectedControls[1] + "_reParentIKlocator"),
    )
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.translateX"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.translateY"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.translateZ"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.rotateX"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.rotateY"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKPole.rotateZ"), 0)
    pc.duplicate(
        (SelectedControls[1] + "_reParentIKPole"),
        n=(SelectedControls[1] + "_reParentIKoffset"),
    )
    pc.xform(
        (SelectedControls[1] + "_reParentIKPole"),
        ws=1,
        t=((FinalPoleVector.x), (FinalPoleVector.y), (FinalPoleVector.z)),
    )
    pc.parent(
        (SelectedControls[1] + "_reParentIKoffset"),
        (SelectedControls[1] + "_reParentIKJoint"),
    )
    pc.parentConstraint(
        (SelectedControls[1] + "_reParentIKlocator"),
        (SelectedControls[1] + "_reParentIKoffset"),
        mo=1,
        weight=1,
    )
    pc.spaceLocator(n=(SelectedControls[0] + "_reParentIKoffset"))
    pc.parent(
        (SelectedControls[0] + "_reParentIKoffset"),
        (SelectedControls[0] + "_reParentIKlocator"),
    )
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.translateX"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.translateY"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.translateZ"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.rotateX"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.rotateY"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.rotateZ"), 0)
    pc.parent(
        (SelectedControls[0] + "_reParentIKoffset"),
        (SelectedControls[0] + "_reParentIKJoint"),
    )
    pc.parentConstraint(
        (SelectedControls[0] + "_reParentIKlocator"),
        (SelectedControls[0] + "_reParentIKoffset"),
        mo=1,
        weight=1,
    )
    pc.parent((SelectedControls[1] + "_reParentIKPole"), w=1)
    pc.parentConstraint(
        (SelectedControls[1] + "_reParentIKlocator"),
        (SelectedControls[1] + "_reParentIKPole"),
        mo=1,
        weight=1,
    )
    pc.ikHandle(
        ee=(SelectedControls[2] + "_reParentIKJoint"),
        sj=(SelectedControls[0] + "_reParentIKJoint"),
        w=1,
        p=1,
        n=(SelectedControls[1] + "_ikHandle"),
    )
    pc.poleVectorConstraint(
        (SelectedControls[1] + "_reParentIKPole"),
        (SelectedControls[1] + "_ikHandle"),
        n=(SelectedControls[1] + "poleVectorConstraint"),
    )
    pc.parentConstraint(
        (SelectedControls[0] + "_reParentIKlocator"),
        (SelectedControls[0] + "_reParentIKJoint"),
        mo=1,
        weight=1,
    )
    pc.parentConstraint(
        (SelectedControls[2] + "_reParentIKlocator"),
        (SelectedControls[1] + "_ikHandle"),
        mo=1,
        weight=1,
    )
    # Locked attrs
    if (
        pc.getAttr((SelectedControls[1] + ".rotateX"), l=1) == 1
        or pc.getAttr((SelectedControls[1] + ".rotateY"), l=1) == 1
        or pc.getAttr((SelectedControls[1] + ".rotateZ"), l=1) == 1
    ):
        if pc.objExists(SelectedControls[1] + "tempLockedCtrl"):
            pc.delete(SelectedControls[1] + "tempLockedCtrl")

        pc.duplicate(
            SelectedControls[1], po=1, n=(SelectedControls[1] + "tempLockedCtrl")
        )
        pc.melGlobals.initVar("string", "LockedAttr1")
        pc.melGlobals.initVar("string", "LockedAttr2")
        if pc.getAttr((SelectedControls[1] + ".rotateX"), l=1) == 0:
            pc.melGlobals["LockedAttr1"] = "y"
            pc.melGlobals["LockedAttr2"] = "z"

        if pc.getAttr((SelectedControls[1] + ".rotateY"), l=1) == 0:
            pc.melGlobals["LockedAttr1"] = "x"
            pc.melGlobals["LockedAttr2"] = "z"

        if pc.getAttr((SelectedControls[1] + ".rotateZ"), l=1) == 0:
            pc.melGlobals["LockedAttr1"] = "y"
            pc.melGlobals["LockedAttr2"] = "x"

        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateX"), k=1)
        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateY"), k=1)
        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateZ"), k=1)
        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateX"), lock=0)
        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateY"), lock=0)
        pc.setAttr((SelectedControls[1] + "tempLockedCtrl.rotateZ"), lock=0)
        # parent to First Control
        pc.select(SelectedControls[0], r=1)
        pc.pickWalk(d="up")
        pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
        if SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]:
            pc.group(
                (SelectedControls[0] + "_reParentIKlocator"),
                n=(SelectedControls[0] + "_reParentIK_offset_grp"),
            )
            pc.parentConstraint(
                pc.melGlobals["UpHierarchyObject"][0],
                (SelectedControls[0] + "_reParentIK_offset_grp"),
                mo=1,
                weight=1,
            )

        pc.group(
            (SelectedControls[1] + "_reParentIKlocator"),
            (SelectedControls[2] + "_reParentIKlocator"),
            (SelectedControls[0] + "_reParentIKJoint"),
            (SelectedControls[1] + "_ikHandle"),
            (SelectedControls[1] + "_reParentIKPole"),
            (SelectedControls[0] + "_reParentIK_offset_grp"),
            n=(SelectedControls[0] + "_reParentIK_grp"),
        )
        # group
        # Local mode
        LocalPinButton = int(pc.checkBox("IKCheckLocalBox", q=1, v=1))
        pc.select(SelectedControls[0], r=1)
        pc.pickWalk(d="up")
        pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
        if (
            LocalPinButton == 1
            and SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]
        ):
            pc.delete((SelectedControls[0] + "_reParentIK_offset_grp"), constraints=1)
            pc.parentConstraint(
                pc.melGlobals["UpHierarchyObject"][0],
                (SelectedControls[0] + "_reParentIK_grp"),
                mo=1,
                weight=1,
            )

        currentR = int(pc.playbackOptions(q=1, min=1))
        currentL = int(pc.playbackOptions(q=1, max=1))
        pc.bakeResults(
            (SelectedControls[2] + "_reParentIKlocator"),
            (SelectedControls[0] + "_reParentIKlocator"),
            (SelectedControls[1] + "_reParentIKlocator"),
            (SelectedControls[1] + "_reParentIKPole"),
            (SelectedControls[0] + "_reParentIKoffset"),
            (SelectedControls[1] + "_reParentIKoffset"),
            sparseAnimCurveBake=0,
            minimizeRotation=1,
            removeBakedAttributeFromLayer=0,
            removeBakedAnimFromLayer=0,
            bakeOnOverrideLayer=0,
            preserveOutsideKeys=1,
            simulation=0,
            sampleBy=1,
            shape=0,
            t=(str(currentL) + ":" + str(currentR)),
            at=["tx", "ty", "tz", "rx", "ry", "rz"],
            disableImplicitControl=1,
            controlPoints=0,
        )
        pc.transformLimits((SelectedControls[1] + "tempLockedCtrl"), erx=(0, 0))
        pc.transformLimits((SelectedControls[1] + "tempLockedCtrl"), ery=(0, 0))
        pc.transformLimits((SelectedControls[1] + "tempLockedCtrl"), erz=(0, 0))
        pc.transformLimits(SelectedControls[1], erx=(0, 0))
        pc.transformLimits(SelectedControls[1], ery=(0, 0))
        pc.transformLimits(SelectedControls[1], erz=(0, 0))
        pc.orientConstraint(
            (SelectedControls[1] + "_reParentIKoffset"),
            (SelectedControls[1] + "tempLockedCtrl"),
            mo=1,
            weight=1,
        )
        pc.orientConstraint(
            (SelectedControls[0] + "_reParentIKoffset"),
            SelectedControls[0],
            mo=1,
            weight=1,
        )
        pc.orientConstraint(
            (SelectedControls[1] + "tempLockedCtrl"),
            SelectedControls[1],
            skip=[pc.melGlobals["LockedAttr1"], pc.melGlobals["LockedAttr2"]],
            mo=1,
            weight=1,
        )
        pc.orientConstraint(
            (SelectedControls[2] + "_reParentIKlocator"),
            SelectedControls[2],
            mo=1,
            weight=1,
        )

    else:
        pc.select(SelectedControls[0], r=1)
        # parent to First Control
        pc.pickWalk(d="up")
        pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
        if SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]:
            pc.group(
                (SelectedControls[0] + "_reParentIKlocator"),
                n=(SelectedControls[0] + "_reParentIK_offset_grp"),
            )
            pc.parentConstraint(
                pc.melGlobals["UpHierarchyObject"][0],
                (SelectedControls[0] + "_reParentIK_offset_grp"),
                mo=1,
                weight=1,
            )

        currentR = int(pc.playbackOptions(q=1, min=1))
        currentL = int(pc.playbackOptions(q=1, max=1))
        # group
        pc.group(
            (SelectedControls[1] + "_reParentIKlocator"),
            (SelectedControls[2] + "_reParentIKlocator"),
            (SelectedControls[0] + "_reParentIKJoint"),
            (SelectedControls[1] + "_ikHandle"),
            (SelectedControls[1] + "_reParentIKPole"),
            (SelectedControls[0] + "_reParentIK_offset_grp"),
            n=(SelectedControls[0] + "_reParentIK_grp"),
        )
        # Local mode
        LocalPinButton = int(pc.checkBox("IKCheckLocalBox", q=1, v=1))
        pc.select(SelectedControls[0], r=1)
        pc.pickWalk(d="up")
        pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
        if (
            LocalPinButton == 1
            and SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]
        ):
            pc.delete((SelectedControls[0] + "_reParentIK_offset_grp"), constraints=1)
            pc.parentConstraint(
                pc.melGlobals["UpHierarchyObject"][0],
                (SelectedControls[0] + "_reParentIK_grp"),
                mo=1,
                weight=1,
            )

        pc.bakeResults(
            (SelectedControls[2] + "_reParentIKlocator"),
            (SelectedControls[0] + "_reParentIKlocator"),
            (SelectedControls[1] + "_reParentIKPole"),
            (SelectedControls[0] + "_reParentIKoffset"),
            (SelectedControls[1] + "_reParentIKoffset"),
            sparseAnimCurveBake=0,
            minimizeRotation=1,
            removeBakedAttributeFromLayer=0,
            removeBakedAnimFromLayer=0,
            bakeOnOverrideLayer=0,
            preserveOutsideKeys=1,
            simulation=0,
            sampleBy=1,
            shape=0,
            t=(str(currentL) + ":" + str(currentR)),
            at=["tx", "ty", "tz", "rx", "ry", "rz"],
            disableImplicitControl=1,
            controlPoints=0,
        )
        pc.orientConstraint(
            (SelectedControls[0] + "_reParentIKoffset"),
            SelectedControls[0],
            mo=1,
            weight=1,
        )
        pc.orientConstraint(
            (SelectedControls[1] + "_reParentIKoffset"),
            SelectedControls[1],
            mo=1,
            weight=1,
        )
        pc.orientConstraint(
            (SelectedControls[2] + "_reParentIKlocator"),
            SelectedControls[2],
            mo=1,
            weight=1,
        )

    pc.setAttr((SelectedControls[0] + "_reParentIKJoint.drawStyle"), 2)
    # visibility
    pc.setAttr((SelectedControls[1] + "_reParentIKJoint.drawStyle"), 2)
    pc.setAttr((SelectedControls[2] + "_reParentIKJoint.drawStyle"), 2)
    pc.setAttr((SelectedControls[0] + "_reParentIKlocator.visibility"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKlocator.visibility"), 0)
    pc.setAttr((SelectedControls[0] + "_reParentIKoffset.visibility"), 0)
    pc.setAttr((SelectedControls[1] + "_reParentIKoffset.visibility"), 0)
    pc.setAttr((SelectedControls[1] + "_ikHandle.visibility"), 0)
    # size
    JointLentgts = float(
        pc.getAttr(SelectedControls[1] + "_reParentIKJoint.translateY")
    )
    pc.setAttr(
        (SelectedControls[2] + "_reParentIKlocator.localScaleX"), (JointLentgts / 2)
    )
    pc.setAttr(
        (SelectedControls[2] + "_reParentIKlocator.localScaleY"), (JointLentgts / 2)
    )
    pc.setAttr(
        (SelectedControls[2] + "_reParentIKlocator.localScaleZ"), (JointLentgts / 2)
    )
    pc.setAttr(
        (SelectedControls[1] + "_reParentIKPole.localScaleX"), (JointLentgts / 4)
    )
    pc.setAttr(
        (SelectedControls[1] + "_reParentIKPole.localScaleY"), (JointLentgts / 4)
    )
    pc.setAttr(
        (SelectedControls[1] + "_reParentIKPole.localScaleZ"), (JointLentgts / 4)
    )
    # color
    pc.setAttr((SelectedControls[2] + "_reParentIKlocatorShape.overrideEnabled"), 1)
    pc.setAttr((SelectedControls[2] + "_reParentIKlocatorShape.overrideColor"), 17)
    pc.setAttr((SelectedControls[1] + "_reParentIKPoleShape.overrideEnabled"), 1)
    pc.setAttr((SelectedControls[1] + "_reParentIKPoleShape.overrideColor"), 13)
    pc.sets(
        (SelectedControls[2] + "_reParentIKlocator"),
        edit=1,
        forceElement="Last_Session_reParentLocator_set",
    )
    pc.sets(
        (SelectedControls[2] + "_reParentIKlocator"),
        edit=1,
        forceElement="All_Session_reParentLocator_set",
    )
    pc.sets(
        (SelectedControls[1] + "_reParentIKPole"),
        edit=1,
        forceElement="Last_Session_reParentLocator_set",
    )
    pc.sets(
        (SelectedControls[1] + "_reParentIKPole"),
        edit=1,
        forceElement="All_Session_reParentLocator_set",
    )
    pc.select((SelectedControls[2] + "_reParentIKlocator"), r=1)


def reParentLocatorSize():
    """Locator Size"""

    SelectedControls = pc.ls(sl=1)
    # Clean Joints
    if (
        pc.objectType(SelectedControls[0]) == "joint"
        and not pc.objExists(SelectedControls[0] + "Shape")
        and not pc.objExists(SelectedControls[0] + "Shape1")
    ):
        firstPos = []
        secondPos = []
        firstVect = []
        firstLen = 0.0
        pc.melGlobals["UpHierarchyObject"] = []
        pc.select(SelectedControls[0], r=1)
        pc.pickWalk(d="down")
        pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
        if SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]:
            firstPos = pc.xform(SelectedControls[0], q=1, ws=1, t=1)
            secondPos = pc.xform(pc.melGlobals["UpHierarchyObject"][0], q=1, ws=1, t=1)
            firstVect = secondPos - firstPos
            firstLen = float(
                pc.mel.sqrt(
                    pow((firstVect.x), 2)
                    + pow((firstVect.y), 2)
                    + pow((firstVect.z), 2)
                )
            )
            pc.setAttr("TempLocatorShape.localScaleX", (firstLen * 2))
            pc.setAttr("TempLocatorShape.localScaleY", (firstLen * 2))
            pc.setAttr("TempLocatorShape.localScaleZ", (firstLen * 2))

        else:
            pc.select(SelectedControls[0], r=1)
            pc.pickWalk(d="up")
            pc.melGlobals["UpHierarchyObject"] = pc.ls(sl=1)
            if SelectedControls[0] != pc.melGlobals["UpHierarchyObject"][0]:
                firstPos = pc.xform(SelectedControls[0], q=1, ws=1, t=1)
                secondPos = pc.xform(
                    pc.melGlobals["UpHierarchyObject"][0], q=1, ws=1, t=1
                )
                firstVect = secondPos - firstPos
                firstLen = float(
                    pc.mel.sqrt(
                        pow((firstVect.x), 2)
                        + pow((firstVect.y), 2)
                        + pow((firstVect.z), 2)
                    )
                )
                pc.setAttr("TempLocatorShape.localScaleX", (firstLen * 2))
                pc.setAttr("TempLocatorShape.localScaleY", (firstLen * 2))
                pc.setAttr("TempLocatorShape.localScaleZ", (firstLen * 2))

    if pc.objectType(SelectedControls[0]) == "joint" and pc.objExists(
        SelectedControls[0] + "Shape"
    ):
        SelectedControls[0] = SelectedControls[0] + "Shape"
        # Joint with Shapes
        bbox = pc.exactWorldBoundingBox(SelectedControls[0])
        locatorSizeX = bbox[3] - bbox[0]
        locatorSizeY = bbox[4] - bbox[1]
        locatorSizeZ = bbox[5] - bbox[2]
        locatorSize = (locatorSizeX + locatorSizeY + locatorSizeZ) / 3
        pc.setAttr("TempLocatorShape.localScaleX", (locatorSize / 1))
        pc.setAttr("TempLocatorShape.localScaleY", (locatorSize / 1))
        pc.setAttr("TempLocatorShape.localScaleZ", (locatorSize / 1))

    if pc.objectType(SelectedControls[0]) == "transform":
        bbox = pc.exactWorldBoundingBox(SelectedControls[0])
        # Simple transforms
        locatorSizeX = bbox[3] - bbox[0]
        locatorSizeY = bbox[4] - bbox[1]
        locatorSizeZ = bbox[5] - bbox[2]
        locatorSize = (locatorSizeX + locatorSizeY + locatorSizeZ) / 3
        if pc.objExists("*ctlArmUpGimbalLf") or pc.objExists("*:*ctlArmUpGimbalLf"):
            pc.setAttr("TempLocatorShape.localScaleX", 0.6)
            pc.setAttr("TempLocatorShape.localScaleY", 0.6)
            pc.setAttr("TempLocatorShape.localScaleZ", 0.6)

        else:
            pc.setAttr("TempLocatorShape.localScaleX", (locatorSize / 1))
            pc.setAttr("TempLocatorShape.localScaleY", (locatorSize / 1))
            pc.setAttr("TempLocatorShape.localScaleZ", (locatorSize / 1))

    if pc.objExists("*MotionSystem*") or pc.objExists("*:*MotionSystem*"):
        SelectedControls[0] = SelectedControls[0] + "Shape"
        # AS
        bbox = pc.exactWorldBoundingBox(SelectedControls[0])
        locatorSizeX = bbox[3] - bbox[0]
        locatorSizeY = bbox[4] - bbox[1]
        locatorSizeZ = bbox[5] - bbox[2]
        locatorSize = (locatorSizeX + locatorSizeY + locatorSizeZ) / 3
        pc.setAttr("TempLocatorShape.localScaleX", (locatorSize / 1))
        pc.setAttr("TempLocatorShape.localScaleY", (locatorSize / 1))
        pc.setAttr("TempLocatorShape.localScaleZ", (locatorSize / 1))
