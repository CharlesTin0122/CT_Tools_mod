#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - Ribbon Tool
#
# Thanks for your support!
#           
# www.antcgi.com - www.youtube.com/antcgi
#
# import antcgiRibbon
# antcgiRibbon.antcgiRibbonUI() 
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
import pymel.core as pm
import maya.mel as mel

from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------    
# News

def antCGiRibbonNews():
    
    newsUpdate = "~ Updated for Maya 2022\n~ Added Simplify Ribbon Option\n~ Added Update Ribbon Option\n~ Ribbon Length Matches Joints\n~ Select Root Joint Only\n~ Bug Fixes\n"
    futureUpdates = "~ Automatic Ribbon Weighting\n~ Add Tween Controls to Poly Ribbons\n~ Controls Follow Ribbon Deformers\n\n"

    cmds.scrollField ("antcgiRibbonNews", e=1, it=("                Version 2.8 Updates\n"), ip=0)       
    cmds.scrollField ("antcgiRibbonNews", e=1, it=("-"*46 + "\n"), ip=0)
    cmds.scrollField ("antcgiRibbonNews", e=1, it=newsUpdate, ip=0)
    cmds.scrollField ("antcgiRibbonNews", e=1, it=("-"*46 + "\n"), ip=0)
    
    cmds.scrollField ("antcgiRibbonNews", e=1, it=("                    Future Updates\n"), ip=0)      
    cmds.scrollField ("antcgiRibbonNews", e=1, it=("-"*46 + "\n"), ip=0)    
    cmds.scrollField ("antcgiRibbonNews", e=1, it=futureUpdates, ip=0)

    cmds.scrollField ("antcgiRibbonNews", e=1, it="                               Lots more to come!\n", ip=0)

    cmds.scrollField ("antcgiRibbonNews", e=1, it=("-"*46 + "\n"), ip=1)  
    cmds.scrollField ("antcgiRibbonNews", e=1, it=("        Follow @antCGi for Updates\n"), ip=1)  

#-------------------------------------------------------------------------------------------------------------------------------------    
# Add Temperary Distance Node

def getTempDistance(startPos, endPos):
    cmds.shadingNode ("distanceBetween", au=1, n=(startPos + "_distnode"))

    cmds.connectAttr ((startPos + ".worldMatrix"), (startPos + "_distnode.inMatrix1"))
    cmds.connectAttr ((endPos + ".worldMatrix"), (startPos + "_distnode.inMatrix2"))
    cmds.connectAttr ((startPos + ".rotatePivotTranslate"), (startPos + "_distnode.point1"))
    cmds.connectAttr ((endPos + ".rotatePivotTranslate"), (startPos + "_distnode.point2"))

    return cmds.getAttr((startPos + "_distnode.distance"))

    cmds.delete((startPos + "_distnode"))
     
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Icon

def buildIcon(iconName, scale, *args):

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 

    pointsList = ([0.49949352081828996, -0.49965646741954789, 0.00011386882060004933],
            [-0.50050383972379531, -0.49965777484916379, 0.00025944578385106443],
            [-0.50050388864963413, 0.50034323886898902, -0.00011386824481751656],
            [0.49950191468729815, 0.50034278368308582, -0.0002594457838509534],
            [0.49949352081828996, -0.49965646741954789, 0.00011386882060004933]
            )
            
    cmds.curve (d=1, p=pointsList[0], n=iconName)

    for i in range(len(pointsList)):
        if i < (len(pointsList)-1):
            cmds.curve (iconName, a=1, p=pointsList[i+1])    

    cmds.setAttr ((iconName + ".scale"), scale, scale, scale)
   
    if jointOrient == "X":
        cmds.setAttr ((iconName + ".ry"), 90)
    elif jointOrient == "Y":
        cmds.setAttr ((iconName + ".rx"), 90)
        
    cmds.makeIdentity (iconName, a=1, t=1, r=1, s=1)
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Cleanup

def cleanRibbon(ribbonNme, matrixRibbon):

    if not cmds.objExists(ribbonNme + "_grp"):
        cmds.group(em=1, n=ribbonNme + "_grp")
        cmds.parent(ribbonNme, ribbonNme + "_grp")

    # Follicles
    if cmds.ls(ribbonNme + "_follicle_*"):
        if cmds.objExists(ribbonNme + "_follicles"):
            cmds.parent(cmds.ls(ribbonNme + "_follicle_*"), ribbonNme + "_follicles")
        else:        
            cmds.group(cmds.ls(ribbonNme + "_follicle_*"), n=ribbonNme + "_follicles")

        cmds.parent(ribbonNme + "_follicles", ribbonNme + "_grp")
        
    # Control joints
    if cmds.ls(ribbonNme + "_ctrljnt_*", type="joint"):
        if cmds.objExists(ribbonNme + "_ctrljnts"):
            cmds.parent(cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint"), ribbonNme + "_ctrljnts")
        else:        
            cmds.group(cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint"), n=ribbonNme + "_ctrljnts")

        cmds.parent(ribbonNme + "_ctrljnts", ribbonNme + "_grp")

    # Controls
    # if cmds.checkBox("contGroupInput", q=1, v=1):
    #     groupName = "_driver"
    # else:
    #     groupName = "_offset"        
    
    if cmds.ls(ribbonNme + "_control_*_offset"):
        if cmds.objExists(ribbonNme + "_controls"):
            cmds.parent(cmds.ls(ribbonNme + "_control_*_offset"), ribbonNme + "_controls")
        else:   
            cmds.group(cmds.ls(ribbonNme + "_control_*_offset"), n=ribbonNme + "_controls")

        cmds.parent(ribbonNme + "_controls", ribbonNme + "_grp")

    # Other Bits
    extraNodeList = (cmds.ls(ribbonNme + "_ikHandle_*") + cmds.ls(ribbonNme + "_tweak_*offset") + cmds.ls(ribbonNme + "_sine_*", tr=1) + cmds.ls(ribbonNme + "_twist_*", tr=1))

    for extraNode in extraNodeList:
        if not "Constraint" in extraNode: cmds.parent(extraNode, ribbonNme + "_grp")

    cmds.select(cl=1)
    antcgiStoreRibbonUI(1) 
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Store the ribbon data

def storeRibData(surface, spans, direction, orientation, endorient):

    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)

    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)

    cmds.addAttr (surface, ln="spans", at="long", dv=spans)
    cmds.setAttr ((surface + ".spans"), l=1)
    
    cmds.addAttr (surface, ln="RibbonName", dt="string")
    cmds.setAttr ((surface + ".RibbonName"), surface, type="string", l=1)

    cmds.addAttr (surface, ln="jointOrientMenu", dt="string")
    cmds.setAttr ((surface + ".jointOrientMenu"), jointOrient, type="string", l=1)
 
    cmds.addAttr (surface, ln="direction", dt="string")
    cmds.setAttr ((surface + ".direction"), direction, type="string", l=1)

    cmds.addAttr (surface, ln="orientation", at="double3")
    cmds.addAttr (surface, ln="orientationX", at="double", p="orientation")    
    cmds.addAttr (surface, ln="orientationY", at="double", p="orientation")       
    cmds.addAttr (surface, ln="orientationZ", at="double", p="orientation")       
    
    cmds.setAttr ((surface + ".orientation"), orientation[0], orientation[1], orientation[2], type="double3", l=1)

    cmds.addAttr (surface, ln="endorient", at="double3")
    cmds.addAttr (surface, ln="endorientX", at="double", p="endorient")    
    cmds.addAttr (surface, ln="endorientY", at="double", p="endorient")       
    cmds.addAttr (surface, ln="endorientZ", at="double", p="endorient")  
    
    cmds.setAttr ((surface + ".endorient"), endorient[0], endorient[1], endorient[2], type="double3", l=1)
                        
    cmds.addAttr (surface, ln="globalScaleInput", at="double", dv=globalScale)
    cmds.setAttr ((surface + ".globalScaleInput"), l=1)
         
    cmds.addAttr (surface, ln="jointOrientFlip", at="long", dv=jointFlip)
    cmds.setAttr ((surface + ".jointOrientFlip"), l=1)
    
    cmds.addAttr (surface, ln="resetJntInput", at="long", dv=resetJnt)
    cmds.setAttr ((surface + ".resetJntInput"), l=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Store the ribbon data

def convertToMatrix(*args):
    
    ribbonNme = cmds.textField("nameInput", q=1, tx=1)

    if not cmds.objExists(ribbonNme + "_follicle_01"): cmds.error("Follicles not found, make sure the name of the ribbon is correct.")

    ribbonJointList = cmds.ls(ribbonNme + "_joint_*", type="joint")

    # Get the data
    spans = cmds.getAttr ((ribbonNme + ".spans"))
    direction = cmds.setAttr ((ribbonNme + ".direction"))
    orientation = cmds.setAttr ((ribbonNme + ".orientation"))
    endorient = cmds.setAttr ((ribbonNme + ".endorient"))

    # Delete existing follicles
    for ribbonJoint in ribbonJointList:
        cmds.delete(ribbonJoint.replace("_joint_", "_follicle_"))

    cmds.select(cl=1)

    # Rebuild the joints    
    matrixConnect(ribbonNme, spans, direction, orientation, endorient, 1)  

#-------------------------------------------------------------------------------------------------------------------------------------
# Add Ribbon Jiggle

def addRibbonJiggle(surface, *args):

    doJiggle = cmds.checkBox("addJiggleInput", q=1, v=1)

    if doJiggle:
        cmds.deformer(surface, type="jiggle", n=surface + "_jiggle")
        cmds.connectAttr (("time1.outTime"), (surface + "_jiggle.currentTime"), f=1) 

        # Add Jiggle

        cmds.addAttr (surface, ln="muscleOptions", nn="--------", at="enum", en="MUSCLE", k=1)

        cmds.addAttr (surface, ln="Enable", at="enum", en="On:Off", k=1)
        cmds.addAttr(surface, ln="Amount", s=1, at="double", k=1, dv=0.9)
        cmds.addAttr(surface, ln="Flexability", s=1, at="double", k=1, dv=0.5)
        cmds.addAttr(surface, ln="Float", s=1, at="double", k=1, dv=0.5)   

        cmds.connectAttr ((surface + ".Enable"), (surface + "_jiggle.enable"), f=1)  
        cmds.connectAttr ((surface + ".Amount"), (surface + "_jiggle.jiggleWeight"), f=1)  
        cmds.connectAttr ((surface + ".Flexability"), (surface + "_jiggle.stiffness"), f=1)  
        cmds.connectAttr ((surface + ".Float"), (surface + "_jiggle.damping"), f=1)  

        cmds.select(cl=1)        
            
#-------------------------------------------------------------------------------------------------------------------------------------
# Add Ribbon Defromers

def addRibbonDeformers(surface, ribbonDir, *args):

    cmds.duplicate (surface, n=(surface + "_sine_bsh"))   # Sine BShape 
    cmds.duplicate (surface, n=(surface + "_twist_bsh"))  # Twist BShape

    # Setup Deformers
    sineDef = cmds.nonLinear((surface + "_sine_bsh"), typ="sine")    
    sineTwi = cmds.nonLinear((surface + "_twist_bsh"), typ="twist")

    if ribbonDir == "Horizontal":
        cmds.rotate (0, 0, 90, sineDef[1], sineTwi[1], r=1, os=1)

    cmds.rename (sineDef[0], (surface + "_sine_def"))
    cmds.rename (sineTwi[0], (surface + "_twist_def"))        
    cmds.rename (sineDef[1], (surface + "_sine_def_handle"))
    cmds.rename (sineTwi[1], (surface + "_twist_def_handle"))
    
    cmds.blendShape ((surface + "_sine_bsh"), (surface + "_twist_bsh"), surface, n=(surface + "_def_bsh"), foc=1)

    # Create attributes
    cmds.addAttr (surface, ln="deformOptions", nn="--------", at="enum", en="DEFORM", k=1)
        
    cmds.addAttr(surface, ln="Sine_Blend", s=1, at="double", min=0, max=1, k=1)
    cmds.addAttr(surface, ln="Twist_Blend", s=1, at="double", min=0, max=1, k=1)

    cmds.addAttr (surface, ln="sineOptions", nn="--------", at="enum", en="SINE", k=1)

    cmds.addAttr(surface, ln="Amplitude", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Wavelength", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Orientation", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Animate", s=1, at="double", k=1)

    cmds.addAttr (surface, ln="twistOptions", nn="--------", at="enum", en="TWIST", k=1)

    cmds.addAttr(surface, ln="Root", s=1, at="double", k=1)
    cmds.addAttr(surface, ln="Tip", s=1, at="double", k=1)   
                        
    cmds.connectAttr ((surface + ".Sine_Blend"), (surface + "_def_bsh." + surface + "_sine_bsh"), f=1)        
    cmds.connectAttr ((surface + ".Twist_Blend"), (surface + "_def_bsh." + surface + "_twist_bsh"), f=1) 

    cmds.connectAttr ((surface + ".Amplitude"), (surface + "_sine_def_handleShape.amplitude"), f=1) 
    cmds.connectAttr ((surface + ".Wavelength"), (surface + "_sine_def_handleShape.wavelength"), f=1) 
    cmds.connectAttr ((surface + ".Orientation"), (surface + "_sine_def_handle.rotateY"), f=1) 
    cmds.connectAttr ((surface + ".Animate"), (surface + "_sine_def_handleShape.offset"), f=1) 
                
    cmds.connectAttr ((surface + ".Root"), (surface + "_twist_def_handleShape.startAngle"), f=1)        
    cmds.connectAttr ((surface + ".Tip"), (surface + "_twist_def_handleShape.endAngle"), f=1)  

    cmds.setAttr (surface + "_sine_def.dropoff", 1)
    cmds.setAttr ((surface + ".Wavelength"), 2)

    cmds.select(cl=1)
                                    
#-------------------------------------------------------------------------------------------------------------------------------------
# Use UV Pin Instead of Follicles

def matrixConnect(surface, spans, direction, orientation, endorient, regenJoints):

    if regenJoints:
        globalScale = cmds.getAttr ((surface + ".globalScaleInput"))
        jointFlip = cmds.getAttr ((surface + ".jointOrientFlip"))
        resetJnt = cmds.getAttr ((surface + ".resetJntInput"))
        jointOrient = cmds.getAttr ((surface + ".jointOrientMenu"))
    else:
        globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
        jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
        jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
        resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)

    if jointFlip:
        flipJnt = 3
    else:
        flipJnt = 0

    surface = pm.PyNode(surface)
    
    for i in range(0, spans):

        if resetJnt and i == 0:
            normalAxis = 2
            tangentAxis = 1          
        else:
            if jointOrient == "X":
                normalAxis = 1+flipJnt
                tangentAxis = 3-flipJnt
            elif jointOrient == "Y":
                normalAxis = 2+flipJnt
                tangentAxis = 4-flipJnt       
            else:
                normalAxis = 0+flipJnt
                tangentAxis = 5-flipJnt    
        
        jointName = '_'.join((surface.name(),'joint', str(i+1).zfill(2)))
        newJoint = cmds.joint (rad=0.15*globalScale, n=jointName)

        cmds.shadingNode ("uvPin", au=1, n=(jointName + "_uvpin"))

        cmds.connectAttr ((jointName + "_uvpin.outputMatrix[0]"), (jointName + ".offsetParentMatrix"))
        cmds.connectAttr ((surface + "Shape.worldSpace"), (jointName + "_uvpin.deformedGeometry"))

        cmds.setAttr ((jointName + "_uvpin.coordinate[0].coordinateV"), 0.5)
        cmds.setAttr ((jointName + "_uvpin.coordinate[0].coordinateU"), (i/(spans - 1.0)))

        cmds.setAttr ((jointName + "_uvpin.normalAxis"), normalAxis)
        cmds.setAttr ((jointName + "_uvpin.tangentAxis"), tangentAxis)
                        
        if cmds.objExists("ribbon_joints"):
            cmds.parent(jointName, "ribbon_joints")
        else:
            cmds.group(jointName, n="ribbon_joints")

        cmds.select(cl=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Use Selected Ribbon

def useRibbon(*args):

    closedLoop = cmds.checkBox("ribbonLoop", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)

    selRibbonList = cmds.ls(sl=1)
    
    if selRibbonList:
        
        for selRibbon in selRibbonList:

            if not cmds.attributeQuery("jointOrientMenu", ex=1, n=selRibbon): cmds.error("Unable to update this ribbon, please use one generated with this tool.")
            
            spans = cmds.getAttr ((selRibbon + ".spans"))
            surface = cmds.getAttr ((selRibbon + ".RibbonName"))
            orientation = cmds.getAttr ((selRibbon + ".jointOrientMenu"))
            direction = cmds.getAttr ((selRibbon + ".direction"))
            
            orientation = (cmds.getAttr (selRibbon + ".orientationX"), cmds.getAttr (selRibbon + ".orientationY"), cmds.getAttr (selRibbon + ".orientationZ"))
            
            endorient = (cmds.getAttr (selRibbon + ".endorientX"), cmds.getAttr (selRibbon + ".endorientY"), cmds.getAttr (selRibbon + ".endorientZ"))
            
            globalScale = cmds.getAttr ((selRibbon + ".globalScaleInput"))
            jointOrientFlip = cmds.getAttr ((selRibbon + ".jointOrientFlip"))
            resetJntInput = cmds.getAttr ((selRibbon + ".resetJntInput"))

            # Check for existing follicles and controls
            if cmds.objExists(surface + "_skinCluster"):cmds.skinCluster(surface + "Shape", e=1, ub=1)
                   
            if cmds.objExists(surface + "_follicles"): cmds.delete(surface + "_follicles")
            if cmds.objExists(surface + "_ctrljnts"): cmds.delete(surface + "_ctrljnts")
            if cmds.objExists(surface + "_controls"): cmds.delete(surface + "_controls")
                        
            if cmds.objExists(surface + "_jiggle"):
                cmds.delete(surface + "_jiggle")

                cmds.deleteAttr(surface, at="muscleOptions")
                cmds.deleteAttr(surface, at="Enable")
                cmds.deleteAttr(surface, at="Amount")
                cmds.deleteAttr(surface, at="Flexability")
                cmds.deleteAttr(surface, at="Float")   

            if matrixRibbon:
                matrixConnect(surface, spans, direction, orientation, endorient, 0)
            else:            
                addFollicles(surface, spans, direction, orientation, endorient)            

            if closedLoop:        
                buildGenRibControls(surface, spans)
            else:
                buildCustomControls(surface, "", 1, matrixRibbon, spans, 0)

        cleanRibbon(surface, matrixRibbon)

        addRibbonJiggle(surface)

    else:
        cmds.error("Please select a ribbon to add follicles to.")
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Create Follicle Function

def addFollicles(surface, spans, direction, orientation, endorient):

    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)  
    surface = pm.PyNode(surface)

    # cmds.group(n=surface.replace("_ribbon", "").lower() + "_follicles", em=1)

    # if cmds.objExists("follicles"):
    #     cmds.parent(surface.replace("_ribbon", "").lower() + "_follicles", "follicles")
    # else:
    #     cmds.group(surface.replace("_ribbon", "").lower() + "_follicles", n="follicles")
   
    for i in range(0, spans):       
        follicleName = '_'.join((surface.name(),'follicle', str(i+1).zfill(2)))
        jointName = '_'.join((surface.name(),'joint', str(i+1).zfill(2)))
              
        follicle = pm.createNode('transform', n=follicleName, ss=1)
        follicleShape = pm.createNode('follicle', n=follicle.name()+'Shape', p=follicle, ss=1)

        surface.local >> follicleShape.inputSurface
        surface.worldMatrix[0] >> follicleShape.inputWorldMatrix
        follicleShape.outRotate >> follicle.rotate
        follicleShape.outTranslate >> follicle.translate
        follicle.inheritsTransform.set(False)

        follicleShape.parameterU.set(i/(spans - 1.0))
        follicleShape.parameterV.set(0.5)
                   
        jntPos = cmds.xform (str(follicle), q=True, ws=True, piv=True)
        newJoint = cmds.joint (rad=.05*globalScale, p=(jntPos[0], jntPos[1], jntPos[2]), n=jointName)

        cmds.parent (str(newJoint), str(follicle))

        cmds.matchTransform(str(newJoint), str(follicle), rot=1)

        if i == 0:
            cmds.rotate (endorient[0], endorient[1], endorient[2], str(newJoint), r=1, os=1, fo=1)
        else:
            cmds.rotate (orientation[0], orientation[1], orientation[2], str(newJoint), r=1, os=1, fo=1)            

        # cmds.parent(str(follicle), surface.replace("_ribbon", "").lower() + "_follicles")
            
    cmds.select(cl=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Build Ribbon Controls - Generated From Polys

def buildGenRibControls(ribbonNme, ribbonSpans):

    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    offsetControl = cmds.floatField("controlOffsetInput", q=1, v=1)
    ribbonRatio = cmds.optionMenu("controlRatioMenu", q=1, v=1)
    controlGroup = cmds.checkBox("contGroupInput", q=1, v=1)

    if "Alt" in ribbonRatio:
        spanNumber = 2
        ribbonRatio = ribbonRatio[0]
    else:
        spanNumber = 1
        
    colour = [0, 1, 0]

    if matrixRibbon:
        controlNormal = (0, 1, 0)
        moveAmount = (0, offsetControl*globalScale, 0)
    else:
        controlNormal = (0, 0, 1)
        moveAmount = (0, 0, offsetControl*globalScale)
        
    for i in range(1, ribbonSpans):

        if i == spanNumber:
            # Check if greater than 20
            if i < 10: spanNumber = "0" + str(i)
            if i >= 10: spanNumber = str(i)

            jointName =  (ribbonNme + "_joint_" + spanNumber)

            # Create Control Joints
            cmds.duplicate(jointName, n=jointName.replace("joint", "ctrljnt"))
            if not matrixRibbon: cmds.parent(jointName.replace("joint", "ctrljnt"), w=1)

            # Add Controls
            cmds.circle (nr=controlNormal, n=jointName.replace("joint", "control"), r=0.25*globalScale, s=12, ch=0)

            # Set the colour
            cmds.setAttr ((jointName.replace("joint", "control") + ".ove"), 1)

            cmds.setAttr((jointName.replace("joint", "control") + ".overrideRGBColors"), 1)
            cmds.setAttr ((jointName.replace("joint", "control") + ".overrideColorRGB"), colour[0], colour[1], colour[2])

            if controlGroup:
                cmds.group(jointName.replace("joint", "control"), n=jointName.replace("joint", "control") + "_offset")
                cmds.group(jointName.replace("joint", "control") + "_offset", n=jointName.replace("joint", "control") + "_driver")

                cmds.matchTransform(jointName.replace("joint", "control") + "_driver", jointName, pos=1, rot=1)
            else:
                cmds.group(jointName.replace("joint", "control"), n=jointName.replace("joint", "control") + "_offset")
                cmds.matchTransform(jointName.replace("joint", "control") + "_offset", jointName, pos=1, rot=1)

            cmds.parentConstraint(jointName.replace("joint", "control"), jointName.replace("joint", "ctrljnt"), mo=0)
            cmds.move(moveAmount[0], moveAmount[1], moveAmount[2], jointName.replace("joint", "control") + ".cv[0:11]", r=1, os=1)

            spanNumber = int(spanNumber) + int(ribbonRatio)

    ctrljntList = cmds.ls((ribbonNme + "_ctrljnt_*"), type="joint")
    cmds.skinCluster(ribbonNme, ctrljntList, dr=3, mi=2, n=(ribbonNme + "_skinCluster"))

#-------------------------------------------------------------------------------------------------------------------------------------
# Duplicate and reset joints position

def dupeJoint(source, target, newName, radius):

    cmds.duplicate(source, n=newName)
    cmds.matchTransform(newName, target, pos=1, rot=1)  
    cmds.makeIdentity (newName, a=1, t=0, r=1, s=1)

    cmds.joint(newName, e=1, rad=radius)

    childList = cmds.listRelatives(newName, f=1)
    
    if childList: cmds.delete(childList)
         
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Custom Ribbon Controls

def buildCustomControls(ribbonNme, jntList, genRibbon, matrixRibbon, ribbonDiv, quadLimbInput):

    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1)

    controlGroup = cmds.checkBox("contGroupInput", q=1, v=1)

    controlRatio = cmds.optionMenu("controlRatioMenu", q=1, v=1)
    snapToInput = cmds.checkBox("snapToInput", q=1, v=1)               
    ribbonLen = cmds.intField("lengthCount", q=1, v=1)
    ribbonLoop = cmds.checkBox("ribbonLoop", q=1, v=1)

    tweakCtrl = cmds.checkBox("twkControlsInput", q=1, v=1)
    angleCtrl = cmds.checkBox("angleControlsInput", q=1, v=1)

    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)

    offsetControl = cmds.floatField("controlOffsetInput", q=1, v=1)
    
    # Set colour
    if jntList:
        if "l_" in jntList[0].lower():
            colour = [1, 0, 0]
        elif "r_" in jntList[0].lower():
            colour = [0, 0, 1]
        else:
            colour = [0, 1, 0]
    else:
        colour = [0, 1, 0]
         
    if genRibbon:           
        limbDivisions = int(controlRatio)
    else:
        if quadLimbInput:
            limbDivisions = int(ribbonDiv/3)
        else:
            limbDivisions = int(ribbonDiv/2)
                
    jointNumber = 1
    cntrlJointList = []

    for i in range(1, ribbonDiv+1):
        if i == jointNumber or i == ribbonDiv:           
            if i < 10:
                buffer = "_0" + str(i)
            else:
                buffer = "_" + str(i)
                           
            dupeJoint((ribbonNme + "_joint" + buffer), (ribbonNme + "_joint" + buffer), (ribbonNme + "_ctrljnt" + buffer), 0.1*globalScale)

            if not matrixRibbon:
                cmds.parent((ribbonNme + "_ctrljnt" + buffer), w=1)

            # Create control
            # Set circle orientation
            moveAmount = (0, 0, offsetControl*globalScale)
                
            if genRibbon:
                controlOri = (0, 0, 1)
               
            elif jointOrient == "Z":
                controlOri = (0, 0, 1)
                
            elif jointOrient == "Y":
                controlOri = (0, 1, 0)
            else:
                controlOri = (1, 0, 0)   

            if matrixRibbon:
                controlOri = (0, 1, 0)
                moveAmount = (0, offsetControl*globalScale, 0)

            if resetJnt:
                if i == 1:
                    controlNormal = (0, 1, 0)
        
            cmds.circle (nr=controlOri, n=(ribbonNme + "_control" + buffer), r=0.25*globalScale, s=12, ch=0)
            
            # Set the colour
            cmds.setAttr ((ribbonNme + "_control" + buffer + ".ove"), 1)

            cmds.setAttr((ribbonNme + "_control" + buffer + ".overrideRGBColors"), 1)
            cmds.setAttr ((ribbonNme + "_control" + buffer + ".overrideColorRGB"), colour[0], colour[1], colour[2])

            if controlGroup:
                cmds.group((ribbonNme + "_control" + buffer), n=(ribbonNme + "_control" + buffer + "_driver"))
                cmds.group((ribbonNme + "_control" + buffer + "_driver"), n=(ribbonNme + "_control" + buffer + "_offset"))
            else:
                cmds.group((ribbonNme + "_control" + buffer), n=(ribbonNme + "_control" + buffer + "_offset"))
                
            cmds.matchTransform((ribbonNme + "_control" + buffer + "_offset"), (ribbonNme + "_ctrljnt" + buffer), pos=1, rot=1)

            cmds.parentConstraint((ribbonNme + "_control" + buffer), (ribbonNme + "_ctrljnt" + buffer), mo=0)
        
            jointNumber = jointNumber + limbDivisions

            if genRibbon: cmds.move(moveAmount[0], moveAmount[1], moveAmount[2], (ribbonNme + "_control" + buffer + ".cv[0:11]"), r=1, os=1)
            
            cntrlJointList.append((ribbonNme + "_ctrljnt" + buffer))

    if not genRibbon:
        if tweakCtrl: addTweakControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri)
        if angleCtrl: addAngleControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri)
    
    # Bind   
    cmds.skinCluster(ribbonNme, (cmds.ls(((ribbonNme + "_ctrljnt_*"), (ribbonNme + "_angle_*")), type="joint")), tsb=1, dr=10, n=(ribbonNme + "_skinCluster"))        

    # Snap to joints
    if jntList:
        if snapToInput:
            if quadLimbInput:
                limbJntCount = 4
            else:
                limbJntCount = 3     

            limbJointList = cmds.listRelatives(jntList[0], ad=1, type="joint")
            limbJointList.append(jntList[0])

            controlGrpList = cmds.ls((ribbonNme + "_control_*_offset"))
            controlGrpList.reverse()
            
            for i in range(limbJntCount):           
                cmds.matchTransform(controlGrpList[i], limbJointList[i], pos=1, rot=1)

#-------------------------------------------------------------------------------------------------------------------------------------
# Add Angle Controls

def addAngleControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri, *args):

    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
       
    for i in range(len(cntrlJointList)-1):
        dupeJoint(cntrlJointList[i], cntrlJointList[i], (cntrlJointList[i].replace("_ctrljnt_", "_angle_")), 0.25*globalScale)
        dupeJoint(cntrlJointList[i], cntrlJointList[i+1], (cntrlJointList[i].replace("_ctrljnt_", "_angletip_")), 0.25*globalScale)

        cmds.parent((cntrlJointList[i].replace("_ctrljnt_", "_angletip_")), (cntrlJointList[i].replace("_ctrljnt_", "_angle_")))
        cmds.parent((cntrlJointList[i].replace("_ctrljnt_", "_angle_")), cntrlJointList[i])

        cmds.ikHandle( n=(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_")), sol="ikRPsolver", sj=(cntrlJointList[i].replace("_ctrljnt_", "_angle_")), ee=(cntrlJointList[i].replace("_ctrljnt_", "_angletip_")) )

        cmds.setAttr(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_") + ".poleVector", 0, 0, 0, type="double3")
        cmds.setAttr(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_") + ".rotate", 0, 0, 0, type="double3")
        
        # cmds.ikHandle( n=(cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_")), sol="ikSCsolver", sj=(cntrlJointList[i].replace("_ctrljnt_", "_angle_")), ee=(cntrlJointList[i].replace("_ctrljnt_", "_angletip_")) )

        cmds.pointConstraint(cntrlJointList[i+1], cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_"), mo=1)
        # cmds.connectAttr ((cntrlJointList[i+1] + ".translate"), (cntrlJointList[i].replace("_ctrljnt_", "_ikHandle_") + ".translate"), f=1)
                        
#-------------------------------------------------------------------------------------------------------------------------------------
# Add Tweak Controls

def addTweakControls(ribbonNme, cntrlJointList, quadLimbInput, controlOri, *args):

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1)  
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)

    if jointOrient == "X":
        controlUp = (0, 1, 0)
    elif jointOrient == "Y":
        controlUp = (0, 0, 1)
    else:
        controlUp = (1, 0, 0)

    if cmds.checkBox("jointOrientFlip", q=1, v=1):
        controlOri = (controlOri[0]*-1, controlOri[1]*-1, controlOri[2]*-1)        
            
    if quadLimbInput:
        tweakCount = 3
    else:
        tweakCount = 2
        
    for i in range(tweakCount):
        buildIcon((ribbonNme + "_tweak_" + str(i)), 0.5*globalScale)

        dupeJoint(cntrlJointList[i], cntrlJointList[i], (cntrlJointList[i] + "_tweak"), 0.1*globalScale)

        # Set the colour
        cmds.setAttr ((ribbonNme + "_tweak_" + str(i) + ".ove"), 1)

        cmds.setAttr((ribbonNme + "_tweak_" + str(i) + ".overrideRGBColors"), 1)
        cmds.setAttr ((ribbonNme + "_tweak_" + str(i) + ".overrideColorRGB"), 0, 1, 1)

        cmds.group((ribbonNme + "_tweak_" + str(i)), n=(ribbonNme + "_tweak_" + str(i) + "_aim"))
        cmds.group((ribbonNme + "_tweak_" + str(i) + "_aim"), n=(ribbonNme + "_tweak_" + str(i) + "_offset"))
        
        cmds.matchTransform((ribbonNme + "_tweak_" + str(i) + "_offset"), cntrlJointList[i+1], rot=1)

        cmds.pointConstraint(cntrlJointList[i], cntrlJointList[i+1], (ribbonNme + "_tweak_" + str(i) + "_offset"), mo=0)

        cmds.aimConstraint( cntrlJointList[i], (ribbonNme + "_tweak_" + str(i) + "_aim"), w=1, aim=controlOri, u=controlUp, wu=controlUp, wut="objectrotation", wuo=(cntrlJointList[i]), mo=0 ) 

        cmds.parentConstraint((ribbonNme + "_tweak_" + str(i)), (cntrlJointList[i] + "_tweak"), mo=0)
            
#-------------------------------------------------------------------------------------------------------------------------------------
# Build Custom Ribbon

def custRibbon(*args):

    # Get the dimensions
    globalScale = cmds.floatField("globalScaleInput", q=1, v=1)
    
    ribbonDir = cmds.optionMenu("ribbonDirMenu", q=1, v=1)
    ribbonOri = cmds.optionMenu("ribbonOrientMenu", q=1, v=1)
    ribbonDiv = cmds.intField("divisCount", q=1, v=1)    
    ribbonLen = cmds.intField("lengthCount", q=1, v=1) 
    ribbonNme = cmds.textField("nameInput", q=1, tx=1) 

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)

    addCrease = cmds.checkBox("addCreaseInput", q=1, v=1)
    addControls = cmds.checkBox("controlsInput", q=1, v=1)

    snapToInput = cmds.checkBox("snapToInput", q=1, v=1)

    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    quadLimbInput = cmds.checkBox("quadLimbInput", q=1, v=1)

    addDeformers = cmds.checkBox("addDeformInput", q=1, v=1)

    resetJnt = cmds.checkBox("resetJntInput", q=1, v=1)

    if quadLimbInput:
        limbJntCount = 4
    else:
        limbJntCount = 3
        
    jntRoot = cmds.ls(sl=1, ap=1, type="joint")

    if snapToInput:
        if not jntRoot:        
            cmds.error("Please select the root joint of the limb if you want to snap the controls to it.")

    if cmds.objExists(ribbonNme): cmds.error("A ribbon with that name already exists, choose another name.")

    # Get the leg length
    if jntRoot:                
        limbJointList = cmds.listRelatives(jntRoot[0], ad=1, type="joint")
        limbJointList.append(jntRoot[0])

        ribbonLen = 0.0
        
        for i in range(limbJntCount-1):           
            ribbonLen = ribbonLen + getTempDistance(limbJointList[i], limbJointList[i+1])
   
    lengthRatio = 0.15

    # Ribbon Pointing X
    if ribbonOri == "X": planeAxis = [1, 0, 0]

    # Ribbon Pointing Y
    if ribbonOri == "Y": planeAxis = [0, 1, 0]

    # Ribbon Pointing Z
    if ribbonOri == "Z": planeAxis = [0, 0, 1]

    if jointFlip:    
        if jointOrient == "X":
            ribbonJointOrient = [-90, 0, 0]
            endJointOrient = [0, 0, -90]   
        elif jointOrient == "Y":
            ribbonJointOrient = [0, 180, -90]
            endJointOrient = [0, 0, -90]   
        else:
            ribbonJointOrient = [0, 90, 0]        
            endJointOrient = [0, 0, -90] 
    else:
        if jointOrient == "X":
            ribbonJointOrient = [-90, -180, 0]
            endJointOrient = [0, 0, -90]   
        elif jointOrient == "Y":
            ribbonJointOrient = [0, 0, 90]
            endJointOrient = [0, 0, -90]              
        else:
            ribbonJointOrient = [0, -90, 0]       
            endJointOrient = [0, 0, -90]  

    if not resetJnt:
        endJointOrient = ribbonJointOrient      
            
    if not quadLimbInput:
        multi = 2
        baseDivisions = 5
    else:
        multi = 3
        baseDivisions = 7
        
    for i in range(1, ribbonDiv):
        baseDivisions = baseDivisions + multi
                  
    cmds.nurbsPlane(w=ribbonLen, d=3, u=baseDivisions-1, v=1, lr=lengthRatio, ax=planeAxis, ch=0, n=ribbonNme)

    if ribbonDir == "Vertical":
        cmds.setAttr ((ribbonNme + ".rotate" + ribbonOri), 90)
        cmds.makeIdentity (ribbonNme, a=1, t=0, r=1, s=1)

    # Add a crease to help knee/elbow bending
    if addCrease:
        if quadLimbInput:
            cmds.insertKnotSurface((ribbonNme + ".u[0.325]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.340]"), ch=0, nk=7, add=1, ib=0, rpo=1)

            cmds.insertKnotSurface((ribbonNme + ".u[0.660]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.675]"), ch=0, nk=7, add=1, ib=0, rpo=1)
        else:
            cmds.insertKnotSurface((ribbonNme + ".u[0.495]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            cmds.insertKnotSurface((ribbonNme + ".u[0.505]"), ch=0, nk=7, add=1, ib=0, rpo=1)
            
    cmds.select(cl=1)

    if addDeformers:
        addRibbonDeformers(ribbonNme, ribbonDir)    
        addRibbonJiggle(ribbonNme)

    if matrixRibbon:
        matrixConnect(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient, 0)
    else:
        storeRibData(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient)
        addFollicles(ribbonNme, baseDivisions, ribbonDir.lower(), ribbonJointOrient, endJointOrient)   

    if addControls: buildCustomControls(ribbonNme, jntRoot, 0, matrixRibbon, baseDivisions, quadLimbInput)

    cleanRibbon(ribbonNme, matrixRibbon)

#-------------------------------------------------------------------------------------------------------------------------------------
# Build Polygon Selection Ribbon

def storeEdges(whichSide, *args):

    cmds.polyToCurve(f=2, dg=3, usm=0, n=("temp" + whichSide + "curve"))
    cmds.button((whichSide + "Button"), e=1, en=0)

    if cmds.objExists("tempinnercurve") and cmds.objExists("tempoutercurve"):
        cmds.button("polyRibbonButton", e=1, en=1)  

    cmds.select(cl=1)
              
def polyRibbon(*args):

    jntList = []

    jointOrient = cmds.optionMenu("jointOrientMenu", q=1, v=1) 
    jointFlip = cmds.checkBox("jointOrientFlip", q=1, v=1)
    normalFlip = cmds.checkBox("flipRibbonNormals", q=1, v=1)

    ribbonNme = cmds.textField("nameInput", q=1, tx=1)
    addControls = cmds.checkBox("controlsInput", q=1, v=1)

    closedLoop = cmds.checkBox("ribbonLoop", q=1, v=1)

    matrixRibbon = cmds.checkBox("mtrxRibbonInput", q=1, v=1)
    reduceCurve = cmds.checkBox("reduceRibbonSpans", q=1, v=1)

    if cmds.objExists(ribbonNme): cmds.error("A ribbon with that name already exists, choose another name.")
    
    if jointFlip:
        invert = -1
    else:
        invert = 1

    if reduceCurve:
        spanCount = cmds.getAttr("tempinnercurve.spans")
        
        cmds.rebuildCurve("tempinnercurve", rpo=1, rt=0, s=spanCount/2, ch=1)
        cmds.rebuildCurve("tempoutercurve", rpo=1, rt=0, s=spanCount/2, ch=1)

    if normalFlip:
        cmds.loft("tempinnercurve", "tempoutercurve", r=0, ch=0, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=1, n=ribbonNme) 
    else:
        cmds.loft("tempinnercurve", "tempoutercurve", r=0, ch=0, u=1, c=0, ar=1, d=1, ss=1, rn=0, po=0, rsn=1, n=ribbonNme)       
        
    ribbonDiv = cmds.getAttr(ribbonNme + ".spansU")

    ribbonJointOrient = [0, 0, 0]    
    endJointOrient = [0, 0, 0]    

    cmds.select(cl=1)

    if matrixRibbon:
        matrixConnect(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient, 0)
    else:
        storeRibData(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient)
        addFollicles(ribbonNme, ribbonDiv+1, "horizontal", ribbonJointOrient, endJointOrient)  

    cmds.delete("tempoutercurve", "tempinnercurve")
    
    cmds.button("polyRibbonButton", e=1, en=0)   
    cmds.button("outerButton", e=1, en=1)
    cmds.button("innerButton", e=1, en=1)      

    if addControls:
        if closedLoop:        
            buildGenRibControls(ribbonNme, ribbonDiv+1)
        else:
            buildCustomControls(ribbonNme, jntList, ribbonDiv+1, matrixRibbon, ribbonDiv+1, 0)

    cleanRibbon(ribbonNme, matrixRibbon)

    addRibbonJiggle(ribbonNme)

#-------------------------------------------------------------------------------------------------------------------------------------    
# Update the UI

def snapTo(*args):
   
    if cmds.checkBox("controlsInput", q=1, v=1):
        cmds.checkBox("snapToInput", e=1, en=1)        
        cmds.text("snapToLabel", e=1, en=1)

        cmds.checkBox("twkControlsInput", e=1, en=1)        
        cmds.text("twkControlsLabel", e=1, en=1)

        cmds.checkBox("angleControlsInput", e=1, en=1)        
        cmds.text("angleControlsLabel", e=1, en=1)         

        cmds.checkBox("addDeformInput", e=1, en=1)        
        cmds.text("addDeformLabel", e=1, en=1)  
    else:
        cmds.checkBox("snapToInput", e=1, en=0, v=0)
        cmds.text("snapToLabel", e=1, en=0) 

        cmds.checkBox("twkControlsInput", e=1, en=0, v=0)        
        cmds.text("twkControlsLabel", e=1, en=0)

        cmds.checkBox("angleControlsInput", e=1, en=0, v=0)        
        cmds.text("angleControlsLabel", e=1, en=0) 

        cmds.checkBox("addDeformInput", e=1, en=0)        
        cmds.text("addDeformLabel", e=1, en=0)  

#-------------------------------------------------------------------------------------------------------------------------------------    
# Store Layout

def antcgiStoreRibbonUI(storeValue, *args):
        
    # Get a list of all the window controls
    antcgiUICtrlList = cmds.formLayout("antcgiRibbonForm", q=1, ca=1)

    for antcgiUICtrl in antcgiUICtrlList:

        controlTypeList = ["checkBox", "intField", "optionMenu", "textField", "floatField"]

        for controlType in controlTypeList:
            findType = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, ex=1)")
            
            if findType:
                if controlType == "textField":
                    getValue = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, tx=1)")
                else:
                    getValue = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, v=1)")
                    
                if storeValue:
                    cmds.optionVar(sv=("antRib_" + antcgiUICtrl, getValue))                
                else:
                    getString = eval("cmds.optionVar(q=\"antRib_" + antcgiUICtrl + "\")")
                    
                    if controlType == "textField":
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, tx=\"" + getString + "\")")
                    elif controlType == "optionMenu":
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, v=\"" + getString + "\")")
                    else:
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, v=" + getString + ")")
                break

    # Also store the news section layout
    if storeValue:  
        cmds.optionVar(sv=("antRib_news", cmds.frameLayout("newsFrame", q=1, cl=1)))
    else:
        if cmds.optionVar(q="antRib_news") == "True":
            cmds.frameLayout("newsFrame", e=1, cl=1)

            cmds.window ("antcgiRibbonTool", e=1, h=300)
        else:
            cmds.frameLayout("newsFrame", e=1, cl=0)
            
#-------------------------------------------------------------------------------------------------------------------------------------           
# Expiration Date

def expCheck():
    expCheck = cmds.date(sd=1)
    expDay = "30"
    
    expDate = "06/" + expDay

    today = expCheck.split("/")
    daysLeft = int(expDay) - int(today[1])

    if expCheck == expDate:
        cmds.error("The Ribbon Tool BETA has Expired - Please download a new version from www.antcgi.com/store.")
    else:
        print (str(daysLeft) + " days left before the beta expires.")

    return daysLeft
                
#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiRibbonUI():

    mayaVersion = cmds.about(v=1)
    # daysLeft = expCheck()
    
    # Window exists?
    if cmds.window ("antcgiRibbonTool", ex=1): cmds.deleteUI ("antcgiRibbonTool")

    # Create Window
    window = cmds.window ("antcgiRibbonTool", t="Ribbon Tool v2.8", w=225, mnb=0, mxb=0, s=1, cc=partial(antcgiStoreRibbonUI, 1))

    # Create a main layout
    mainLayout = cmds.formLayout("antcgiRibbonForm", numberOfDivisions=100)

    # Create the news frame
    newsFrame = cmds.frameLayout("newsFrame", label='News & Updates', cll=1, cl=0, bv=0, cc=partial(cmds.window, "antcgiRibbonTool", e=1, h=200))
    newsLayout = cmds.formLayout("newsLayout", numberOfDivisions=100, bgc=(0.2, 0.2, 0.2) )

    # Feed
    antcgiRibbonNews = cmds.scrollField ("antcgiRibbonNews", ed=0, ww=1, h=100, bgc=(0.1, 0.1, 0.1), fn="smallBoldLabelFont")
    
    separator03 = cmds.separator(h=10, vis=0)
   
    cmds.setParent(mainLayout)

    # Labels
    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)

    # Separators
    separator01 = cmds.separator(h=5, p=mainLayout)
    separator02 = cmds.separator(h=15, p=mainLayout)
    separator03 = cmds.separator(h=15, p=mainLayout)
    separator04 = cmds.separator(h=15, p=mainLayout)
    separator05 = cmds.separator(h=15, p=mainLayout, vis=0)
                
    # Buttons
    button01 = cmds.button("polyRibbonButton", h=25, l="Generate Ribbon", ann="Generate the ribbon using the guide curves.", p=mainLayout, c=polyRibbon, en=0)
    button02 = cmds.button("polyCustomButton", h=25, l="Build Custom Ribbon", p=mainLayout, c=custRibbon)    
    
    button03 = cmds.button("outerButton", h=25, l="Outer Edges", ann="Create the outer guide curve.", p=mainLayout, c=partial (storeEdges, "outer")) 
    button04 = cmds.button("innerButton", h=25, l="Inner Edges", ann="Create the inner guide curve.", p=mainLayout, c=partial (storeEdges, "inner"))

    button05 = cmds.button("convMatrix", h=25, l="Convert Follicles > Matrix", ann="Convert follicles to matrix nodes.", p=mainLayout, c=convertToMatrix)   
    button06 = cmds.button("updateRibbon", h=25, l="Update Selected Ribbon", ann="Rebuild the follicles and controls on the selected ribbon.", p=mainLayout, c=useRibbon)  
    
    # Ratio Menu
    controlRatioLabel = cmds.text("controlRatioLabel", label="Control Ratio", align="left", h=20)
    controlRatioMenu = cmds.optionMenu("controlRatioMenu", h=20, ann="How many joints do you want between each control?")

    cmds.menuItem (l="1")
    cmds.menuItem (l="2")
    cmds.menuItem (l="2 Alt")
    cmds.menuItem (l="3")
    cmds.menuItem (l="4")            
    cmds.menuItem (l="5")
    
    # Direction Menu
    ribbonDirLabel = cmds.text("ribbonDirLabel", label="Direction", align="left", h=20)
    ribbonDirMenu = cmds.optionMenu("ribbonDirMenu", h=20, w=104, ann="Do you want the ribbon to be horizontal or vertical?")

    cmds.menuItem (l="Vertical")
    cmds.menuItem (l="Horizontal")

    # Ribbon Orientation Menu
    ribbonOrientLabel = cmds.text("ribbonOrientLabel", label="Orientation", align="left", h=20)
    ribbonOrientMenu = cmds.optionMenu("ribbonOrientMenu", w=20, h=20, ann="The orientation of the ribbon using the world axis.")

    cmds.menuItem (l="X", en=0)
    cmds.menuItem (l="Y", en=0)
    cmds.menuItem (l="Z")

    # Joint Orientation Menu
    jointOrientLabel = cmds.text("jointOrientLabel", label="Joint Orient", align="left", h=20)
    jointOrientMenu = cmds.optionMenu("jointOrientMenu", h=20, ann="Which joint axis points down the joint?")

    cmds.menuItem (l="Z")
    cmds.menuItem (l="X")
    cmds.menuItem (l="Y")

    # Headings
    globalLabel = cmds.text("globalLabel", label="Global Settings", align="left", h=20, fn="boldLabelFont")
    customLabel = cmds.text("customLabel", label="Custom Ribbon", align="left", h=20, fn="boldLabelFont")
    polyLabel = cmds.text("polyLabel", label="Generate Ribbon From Surface", align="left", h=20, fn="boldLabelFont")
    
    # Checkbox
    jointOrientFlip = cmds.checkBox("jointOrientFlip", l="Invert", h=20, ann="Point the axis towards the ribbon instead of away?", v=0)
    flipRibbonNormals = cmds.checkBox("flipRibbonNormals", l="Flip Normals", h=15, ann="Flips the ribbon so the normals point the opposite way.", v=0)
    reduceRibbonSpans = cmds.checkBox("reduceRibbonSpans", l="Simplify Ribbon", h=15, ann="Halves the amount of spans in the ribbon.", v=0)
        
    addCreaseLabel = cmds.text("addCreaseLabel", label="Crease/s", align="left", h=15)
    addCreaseInput = cmds.checkBox("addCreaseInput", l="", h=15, ann="Add a crease at the mid-points?", v=0)

    controlsLabel = cmds.text("controlsLabel", label="Add Controls", align="left", h=15)    
    controlsInput = cmds.checkBox("controlsInput", l="", h=15, ann="Add basic controls to the ribbon?", v=0, cc=snapTo)

    contGroupLabel = cmds.text("contGroupLabel", label="Driver Group", align="left", h=15)    
    contGroupInput = cmds.checkBox("contGroupInput", l="", h=15, ann="Add an extra group to help with additional controls?", v=0)

    twkControlsLabel = cmds.text("twkControlsLabel", label="Tweak Controls", align="left", h=15, en=0)    
    twkControlsInput = cmds.checkBox("twkControlsInput", l="", h=15, ann="Add tweak controls to the ribbon?", en=0, v=0)

    angleControlsLabel = cmds.text("angleControlsLabel", label="Angle Controls", align="left", h=15, en=0)    
    angleControlsInput = cmds.checkBox("angleControlsInput", l="", h=15, ann="Add angle controls to the ribbon?", en=0, v=0)
    
    ribbonLoop = cmds.checkBox("ribbonLoop", l="Closed Loop", w=98, h=15, ann="Is it a closed ribbon?", v=0)
 
    snapToLabel = cmds.text("snapToLabel", label="Snap To Joints", align="left", h=15, en=0)       
    snapToInput = cmds.checkBox("snapToInput", l="", h=15, ann="Snap the controls to the joints?", en=0, v=0)
    
    mtrxRibbonLabel = cmds.text("mtrxRibbonLabel", label="Matrix Ribbon", align="left", h=15)    
    mtrxRibbonInput = cmds.checkBox("mtrxRibbonInput", l="", h=15, ann="Use matrix connections instead of follicles? [Maya 2020+ Only]", v=0)

    quadLimbLabel = cmds.text("quadLimbLabel", label="Three Joint Limb", align="left", h=15)  
    quadLimbInput = cmds.checkBox("quadLimbInput", l="", h=15, ann="Create a ribbon for a limb with three joints (Dog Leg).", v=0)

    resetJntLabel = cmds.text("resetJntLabel", label="Reset End Joint", align="left", h=15)
    resetJntInput = cmds.checkBox("resetJntInput", l="", h=15, ann="Makes the end joint match the world space orientation.", v=0)

    addDeformLabel = cmds.text("addDeformLabel", label="Add Deformers", align="left", h=15)
    addDeformInput = cmds.checkBox("addDeformInput", l="", h=15, ann="Add twist and sine deformers.", v=0)

    addJiggleLabel = cmds.text("addJiggleLabel", label="Add Jiggle", align="left", h=15)
    addJiggleInput = cmds.checkBox("addJiggleInput", l="", h=15, ann="Use dynamics to add a wobble to the ribbon.", v=0)

    # Scene Units   
    scaleUnits = cmds.text("scaleUnits", label=(cmds.currentUnit (q=1, f=1)) + "\s", align="left", h=20, en=1)

    if cmds.currentUnit (q=1, f=1) == "centimeter":
        defValue = 20
    else:
        defValue = 1
               
    # Input
    globalScale = cmds.text("globalScale", label="Overall Scale", align="left", h=20)
    globalScaleInput = cmds.floatField("globalScaleInput", h=20, w=50, pre=2, ann="Overall size of the scene - Use to make the ribbon and joints larger or smaller.", v=defValue)
    
    divisLabel = cmds.text("divisLabel", label="Mid Joints", align="left", h=20)
    divisCount = cmds.intField("divisCount", h=20, ann="Amount of joints between each control.", v=1)

    lengthLabel = cmds.text("lengthLabel", label="Length", align="left", h=20)
    lengthCount = cmds.intField("lengthCount", h=20, ann="Length of the ribbon.", v=10)

    nameLabel = cmds.text("nameLabel", label="Ribbon Name", align="left", h=20)
    nameInput = cmds.textField("nameInput", h=20, w=50, ann="Name of the ribbon.", tx="RibbonName")

    controlOffsetLabel = cmds.text("controlOffsetLabel", label="Control Offset", align="left", h=20)
    controlOffsetInput = cmds.floatField("controlOffsetInput", h=20, w=50, pre=2, ann="The distance the control is away from the joints.", v=0)
                
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(newsFrame, 'left', 5),  (newsFrame, 'top', 5), (newsFrame, 'right', 5),
                    
                                (separator01, 'left', 5), (separator01, 'right', 5),    

                                (globalScale, 'left', 15),
 
                                (nameLabel, 'left', 15), (nameInput, 'right', 15),

                                (mtrxRibbonLabel, 'left', 15),
                                (controlsInput, 'right', 15),

                                (addJiggleLabel, 'left', 15),
                                                              
                                (separator02, 'left', 5), (separator02, 'right', 5),
                                (button01, 'left', 5), (button01, 'right', 5), 
                                (button06, 'left', 5), (button06, 'right', 5), 
                                                                
                                (separator03, 'left', 5), (separator03, 'right', 5),
                                
                                (flipRibbonNormals, 'left', 10),
                                (reduceRibbonSpans, 'left', 10),
                                (controlRatioLabel, 'left', 10), (controlRatioMenu, 'right', 10),
                                (controlOffsetLabel, 'left', 10), (controlOffsetInput, 'right', 10),
                                
                                (divisLabel, 'left', 10),
                                (lengthCount, 'right', 10),

                                (ribbonDirLabel, 'left', 10), (ribbonDirMenu, 'right', 10),
                                (ribbonOrientLabel, 'left', 10), (ribbonOrientMenu, 'right', 10),
                                
                                (jointOrientLabel, 'left', 10),

                                (addCreaseLabel, 'left', 10),
                                (snapToLabel, 'left', 10),

                                (twkControlsLabel, 'left', 10),
                                (angleControlsInput, 'right', 10),

                                (addDeformLabel, 'left', 10),

                                (resetJntInput, 'right', 10),
                                (quadLimbInput, 'right', 10),

                                (contGroupInput, 'right', 15),
                                                                                                                                                                                                
                                (button03, 'left', 5),
                                (button04, 'right', 5),
                                (button02, 'left', 5), (button02, 'right', 5),

                                (separator04, 'left', 5), (separator04, 'right', 5),
                                (button05, 'left', 5), (button05, 'right', 5),
                                (separator05, 'left', 5), (separator05, 'right', 5), 

                                (linkText, 'bottom', 15),
                                ],
                                
                    attachControl=[(separator01, 'top', 5, newsFrame),
                                   (globalLabel, 'top', 5, separator01),                      
                                   (globalScale, 'top', 5, globalLabel), 
                                   (globalScaleInput, 'top', 5, globalLabel), 
                                   (scaleUnits, 'top', 5, globalLabel), 
 
                                   (nameLabel, 'top', 5, scaleUnits),
                                   (nameInput, 'top', 5, scaleUnits),

                                   (mtrxRibbonLabel, 'top', 5, nameLabel),
                                   (mtrxRibbonInput, 'top', 5, nameLabel),
 
                                   (controlsLabel, 'top', 5, nameLabel), 
                                   (controlsInput, 'top', 5, nameLabel),

                                   (contGroupLabel, 'top', 5, controlsLabel), 
                                   (contGroupInput, 'top', 5, controlsLabel),

                                   (addJiggleInput, 'top', 5, mtrxRibbonInput),                                   
                                   (addJiggleLabel, 'top', 5, mtrxRibbonInput),
                                                                                                       
                                   (separator02, 'top', 1, addJiggleInput), 

                                   (polyLabel, 'top', 1, separator02),

                                   (button03, 'top', 5, polyLabel),   
                                   (button04, 'top', 5, polyLabel),
                                   
                                   (flipRibbonNormals, 'top', 10, button04),
                                   (ribbonLoop, 'top', 10, button04),

                                   (reduceRibbonSpans, 'top', 10, flipRibbonNormals),
                                   
                                   (controlRatioLabel, 'top', 5, reduceRibbonSpans),
                                   (controlRatioMenu, 'top', 5, reduceRibbonSpans),

                                   (controlOffsetLabel, 'top', 5, controlRatioLabel),
                                   (controlOffsetInput, 'top', 5, controlRatioMenu),
                                   
                                   (button01, 'top', 5, controlOffsetLabel),                                  
                                                                                                                                                                                                                     
                                   (button06, 'top', 1, button01),                                   

                                   (separator03, 'top', 1, button06), 
                                     
                                   (customLabel, 'top', 1, separator03),
                                   
                                   (divisLabel, 'top', 5, customLabel),
                                   (divisCount, 'top', 5, customLabel), (divisCount, 'right', 10, lengthLabel),

                                   (lengthLabel, 'top', 5, customLabel),
                                   (lengthCount, 'top', 5, customLabel), (lengthCount, 'left', 10, lengthLabel),

                                   (ribbonDirLabel, 'top', 5, lengthLabel),
                                   (ribbonDirMenu, 'top', 5, lengthLabel),

                                   (ribbonOrientLabel, 'top', 5, ribbonDirLabel),
                                   (ribbonOrientMenu, 'top', 5, ribbonDirLabel), (ribbonOrientMenu, 'left', 18, ribbonOrientLabel),

                                   (jointOrientLabel, 'top', 5, ribbonOrientLabel),
                                   
                                   (jointOrientMenu, 'top', 5, ribbonOrientLabel),
                                   (jointOrientFlip, 'top', 5, ribbonOrientLabel), (jointOrientFlip, 'left', 10, jointOrientMenu),
                                   
                                   (addCreaseLabel, 'top', 10, jointOrientMenu),
                                   (addCreaseInput, 'top', 10, jointOrientMenu),

                                   (resetJntLabel, 'top', 10, jointOrientMenu),
                                   (resetJntInput, 'top', 10, jointOrientMenu),
                                                                                                        
                                   (snapToLabel, 'top', 5, addCreaseLabel),                                   
                                   (snapToInput, 'top', 5, addCreaseLabel),

                                   (twkControlsInput, 'top', 5, snapToInput), 
                                   (twkControlsLabel, 'top', 5, snapToInput),

                                   (angleControlsInput, 'top', 5, snapToInput), 
                                   (angleControlsLabel, 'top', 5, snapToInput),

                                   (quadLimbLabel, 'top', 5, resetJntLabel),                                   
                                   (quadLimbInput, 'top', 5, resetJntLabel),

                                   (addDeformLabel, 'top', 5, twkControlsInput), 
                                   (addDeformInput, 'top', 5, twkControlsInput),

                                   (button02, 'top', 10, addDeformLabel),
                                                                                                         
                                   (separator04, 'top', 5, button02),
                                   (button05, 'top', 5, separator04),
                                   (separator05, 'top', 5, button05),                                  

                                   (linkText, 'top', 5, separator05), 
                                   ],
                                   
                    attachPosition=[(globalLabel, 'left', 0, 32),
                                    (polyLabel, 'left', 0, 15),

                                    (globalScaleInput, 'left', 0, 42),
                                    (scaleUnits, 'left', 0, 65),

                                    (nameInput, 'left', 0, 42),

                                    (mtrxRibbonInput, 'left', 0, 43),
                                    (addJiggleInput, 'left', 0, 43),
                                    (controlsLabel, 'left', 0, 53),
                                    (contGroupLabel, 'left', 0, 53),
                                    
                                    (button03, 'right', 0, 50),
                                    (button04, 'left', 0, 50),

                                    (customLabel, 'left', 0, 32),
                                    (controlRatioMenu, 'left', 0, 50),

                                    (ribbonLoop, 'left', 0, 50),
                                    (controlOffsetInput, 'left', 0, 50),
                                    
                                    (divisCount, 'left', 0, 35),

                                    (lengthLabel, 'left', 0, 58),
 
                                    (ribbonDirMenu, 'left', 0, 35),
                                    
                                    (ribbonOrientMenu, 'left', 0, 35),                                    
                                    (jointOrientMenu, 'left', 0, 35),
                                    
                                    (addCreaseInput, 'left', 0, 42),
                                    (snapToInput, 'left', 0, 42),
                                    (addDeformInput, 'left', 0, 42),
                                                                        
                                    (resetJntLabel, 'left', 0, 51),
                                    (quadLimbLabel, 'left', 0, 51),
                                    
                                    (twkControlsInput, 'left', 0, 42),
                                    (angleControlsLabel, 'left', 0, 51),
                                    
                                    (contGroupLabel, 'left', 0, 53),
                                                                                                                                                                                                                                                                                                                                                                                                                                        
                                    (linkText, 'left', 0, 30),
                                   ]
                    )

    cmds.formLayout(newsLayout, edit=True,
                    attachForm=[(antcgiRibbonNews, 'top', 5),
                                (antcgiRibbonNews, 'left', 5), (antcgiRibbonNews, 'right', 5), 

                                ],
                    )       
    # Show Window
    cmds.showWindow (window)
    
    # Update UI

    cmds.optionMenu("ribbonOrientMenu", e=1, v="Z")

    if cmds.objExists("tempinnercurve"):
        cmds.button("innerButton", e=1, en=0) 

    if cmds.objExists("tempoutercurve"):
        cmds.button("outerButton", e=1, en=0) 
    
    if cmds.objExists("tempinnercurve") and cmds.objExists("tempoutercurve"):
        cmds.button("polyRibbonButton", e=1, en=1)

    if int(mayaVersion) < 2020:
        cmds.checkBox("mtrxRibbonInput", e=1, v=0, en=0)        
        cmds.button("convMatrix", e=1, en=0)           
        
    antCGiRibbonNews()
    
    # Auto fill
    if cmds.optionVar(ex=("antRib_globalScaleInput")):    
        antcgiStoreRibbonUI(0)
        snapTo()
    else:
        antcgiStoreRibbonUI(1)  