#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - Auto Limb Tool
#
# Follow @antCGi on Twitter For Updates and to Report Bugs
#           
# www.antcgi.com - www.youtube.com/antcgi
#
#-------------------------------------------------------------------------------------------------------------------------------------
#
# To use this tool -
#
# ~ Put the script into your \Documents\maya\scripts folder.
# ~ Restart Maya.
# ~ Create a new button on the shelf with this command -
#
# import antcgiQuickLimb
# antcgiQuickLimb.antcgiQuickLimbUI() 
#
# Check out the video to see how to use it - https://www.youtube.com/watch?v=phHdyhPaTRI
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.mel as mel
import maya.cmds as cmds
from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antCGiNewsUpdate():
    
    newsUpdate = "~ UI Changes\n~ Control Colours\n~ Foot Control Orientation\n~ Joint Orient Revised\n~ Roll Joints\n~ Hock Control Updates\n~ Save Previous Settings\n~ Bug Fixes\n"
    futureUpdates = "~ Auto Spine Rig\n~ Reverse Knee Support\n~ Arachnid Limb Support\n~ Tentacle Limb Support\n~ Node/Constraint/Matrix Options\n~ Soft IK\n~ Elbow & Knee Pinning\n~ Multiple Limb Support\n~ Space Swapping\n\n"

    cmds.scrollField ("antcgiNews", e=1, it=("               Version 3.0 Updates\n"), ip=0)      
    cmds.scrollField ("antcgiNews", e=1, it=("-"*46 + "\n"), ip=0)
    cmds.scrollField ("antcgiNews", e=1, it=newsUpdate, ip=0)
    cmds.scrollField ("antcgiNews", e=1, it=("-"*46 + "\n"), ip=0)
    
    cmds.scrollField ("antcgiNews", e=1, it=("                   Future Updates\n"), ip=0)      
    cmds.scrollField ("antcgiNews", e=1, it=("-"*46 + "\n"), ip=0)    
    cmds.scrollField ("antcgiNews", e=1, it=futureUpdates, ip=0)

    cmds.scrollField ("antcgiNews", e=1, it="                                Lots more to come!\n", ip=0)

    cmds.scrollField ("antcgiNews", e=1, it=("-"*46 + "\n"), ip=1)  
    cmds.scrollField ("antcgiNews", e=1, it=("       Limb Rigging Tool by @antCGi\n"), ip=1)

#---------------------------------------------------------------------------
# Store UI Values

def storeLimbUI(storeValue, *args):
        
    # Get a list of all the window controls
    antcgiUICtrlList = cmds.formLayout("autoLimbToolLayout", q=1, ca=1)

    for antcgiUICtrl in antcgiUICtrlList:

        controlTypeList = ["checkBox", "intField", "optionMenu", "textField", "floatField", "colorSliderGrp"]

        for controlType in controlTypeList:
            findType = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, ex=1)")
            
            if findType:
                if controlType == "textField":
                    getValue = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, tx=1)")
                elif controlType == "colorSliderGrp":
                    getValue = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, rgb=1)")
                else:
                    getValue = eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", q=1, v=1)")
                    
                if storeValue:
                    if controlType == "colorSliderGrp":
                        cmds.optionVar(sv=("antLimb_" + antcgiUICtrl + "_r", getValue[0]))
                        cmds.optionVar(sv=("antLimb_" + antcgiUICtrl + "_g", getValue[1]))
                        cmds.optionVar(sv=("antLimb_" + antcgiUICtrl + "_b", getValue[2]))
                    else:
                        cmds.optionVar(sv=("antLimb_" + antcgiUICtrl, getValue)) 
                else:
                    if controlType == "colorSliderGrp":
                        getCol_r = eval("cmds.optionVar(q=\"antLimb_" + antcgiUICtrl + "_r\")")
                        getCol_g = eval("cmds.optionVar(q=\"antLimb_" + antcgiUICtrl + "_g\")")
                        getCol_b = eval("cmds.optionVar(q=\"antLimb_" + antcgiUICtrl + "_b\")")                     
                    else:
                        getString = eval("cmds.optionVar(q=\"antLimb_" + antcgiUICtrl + "\")")                       
                    
                    if controlType == "textField":
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, tx=\"" + getString + "\")")
                    elif controlType == "optionMenu":
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, v=\"" + getString + "\")")
                        
                    elif controlType == "colorSliderGrp":
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, rgb=(" + getCol_r + ", " + getCol_g + ", " + getCol_b + "))")
                    else:
                        eval("cmds." + controlType + "(\"" + antcgiUICtrl + "\", e=1, v=" + getString + ")")
                break      
                            
#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiQuickLimbUI():
    # Window exists?
    if cmds.window ("autoLimbTool", ex=1): cmds.deleteUI ("autoLimbTool")

    # Create Window
    window = cmds.window ("autoLimbTool", t="Auto Limb Tool v3", w=200, h=330, mnb=0, mxb=0, s=0, cc=partial (storeLimbUI, 1))

    # Create a main layout
    mainLayout = cmds.formLayout("autoLimbToolLayout", numberOfDivisions=100)

    # Labels
    antcgiNews = cmds.scrollField ("antcgiNews", ed=0, ww=1, h=100, bgc=(0.1, 0.1, 0.1), fn="smallBoldLabelFont")

    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)
        
    limbLabel = cmds.text("limbLabel", label="Limb Type", align="left", h=20)
    sideLabel = cmds.text("sideLabel", label="Limb Side", align="left", h=20)

    orientLabel = cmds.text("primLabel", label="Joint Orient", align="left", h=20)
    footLabel = cmds.text("footLabel", label="Foot Orient", align="left", h=20)
    connectLabel = cmds.text("connectLabel", label="Connection", align="left", h=20)
         
    sizeLabel = cmds.text("sizeLabel", label="Scale Multi", align="left", h=20)

    # Headings
    extrasLabel = cmds.text("extrasLabel", label="Extra Options", align="left", h=20, fn="boldLabelFont")
    colorLabel = cmds.text("colorLabel", label="Control Colours", align="left", h=20, fn="boldLabelFont")
         
    # Input
    sizeInput = cmds.floatField("sizeInput", h=20, ann="Adjust control size.", v=1)      
    
    # Buttons
    button01 = cmds.button(w=150, h=25, l="[GO]", p=mainLayout, c=antcgiQuickLimb)

    # Separators
    separator01 = cmds.separator(h=5, p=mainLayout)
    separator02 = cmds.separator(h=5, p=mainLayout)
    separator03 = cmds.separator(h=5, p=mainLayout)
    separator04 = cmds.separator(h=5, p=mainLayout)

    # Checkbox
    stretchBox = cmds.checkBox("stretchBox", l="Stretch", h=20, ann="Add stretchiness to the limb.", v=1, en=1)
    volumePresBox = cmds.checkBox("volumePresBox", l="Volume", h=20, ann="Add volume preservations to the limb.", v=1, en=1)
    springSolverBox = cmds.checkBox("springSolverBox", l="Spring Solver", h=20, ann="Use a spring solver in the quadruped limb.", v=0, en=1)
         
    rollJointBox = cmds.checkBox("rollJointBox", l="Roll Joints", h=20, ann="Add roll joints to the limb.", v=0, en=1)
    softIKBox = cmds.checkBox("softIKBox", l="Soft IK", h=20, ann="Add soft IK to the limb.", v=0, en=0)
    kneePinBox = cmds.checkBox("kneePinBox", l="Pinning", h=20, ann="Add knee/elbow pinning to the limb.", v=0, en=0)
                   
    # Menu
    limbType = cmds.optionMenu("limbType", h=20, ann="What type of limb are you building?")

    cmds.menuItem (l="Biped Arm")
    cmds.menuItem (l="Biped Leg")
    cmds.menuItem (l="Biped Leg Rev", en=0)
    cmds.menuItem (l="Biped Spine", en=0)
    cmds.menuItem (d=1)
    cmds.menuItem (l="Quad Front")
    cmds.menuItem (l="Quad Rear")
    cmds.menuItem (l="Quad Spine", en=0)
    cmds.menuItem (d=1)
    cmds.menuItem (l="Arachnid Leg", en=0)
    cmds.menuItem (l="Tentacle", en=0)
                    
    # Menu
    limbSide = cmds.optionMenu("limbSide", h=20, ann="Which side are you building?")

    cmds.menuItem (l="Left")
    cmds.menuItem (l="Right")

    # Menu
    footOrient = cmds.optionMenu("footOrient", h=20, ann="How do you want the foot control orientating?")

    cmds.menuItem (l="Floor")
    cmds.menuItem (l="Joint")
    
    # Menu
    axisOrient = cmds.optionMenu("axisOrient", h=20, ann="Joint Orientation")

    cmds.menuItem (l="xyz - x primary")
    cmds.menuItem (l="yzx - y primary")
    cmds.menuItem (l="zxy - z primary")

    # Menu
    jntConnect = cmds.optionMenu("jntConnect", h=20, ann="Connction Type")

    cmds.menuItem (l="Constraint")
    cmds.menuItem (l="Node", en=0)
    cmds.menuItem (l="Matrix", en=0)

    leftColor = cmds.colorSliderGrp("leftColor", rgb=(1, 1, 0), cw2=(50, 0), ann="Left control colours.")
    midColor = cmds.colorSliderGrp("midColor", rgb=(0, 1, 0), cw2=(50, 0), ann="Middle control colours.")
    rightColor = cmds.colorSliderGrp("rightColor", rgb=(1, 0, 0), cw2=(50, 0), ann="Right control colours.")
               
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(antcgiNews, 'top', 5),
                                (antcgiNews, 'left', 5), (antcgiNews, 'right', 5), 
                                
                                (separator01, 'left', 5), (separator01, 'right', 5),    
                    
                                (limbLabel, 'left', 15),                   
                                (sideLabel, 'left', 15),
                                (orientLabel, 'left', 15),
                                (footLabel, 'left', 15),
                                (connectLabel, 'left', 15),
                                                                                                
                                (separator02, 'left', 5), (separator02, 'right', 5),  
                                  
                                (sizeLabel, 'left', 15), 
                                                                                                                                                    
                                (limbType, 'right', 15),
                                (axisOrient, 'right', 15),  
                                (sizeInput, 'right', 15),
                                (limbSide, 'right', 15),
                                (footOrient, 'right', 15),
                                (jntConnect, 'right', 15),
                                                                                                                                                                                                
                                (separator03, 'left', 5), (separator03, 'right', 5),                                                           
                                
                                (separator04, 'left', 5), (separator04, 'right', 5),     
                                (button01, 'bottom', 5), (button01, 'left', 5), (button01, 'right', 5),
                                ],
                                
                    attachControl=[(separator01, 'top', 5, antcgiNews), 
                                                             
                                   (limbLabel, 'top', 5, separator01),
                                   (sideLabel, 'top', 5, limbLabel),
                                   (orientLabel, 'top', 5, sideLabel),
                                   (footLabel, 'top', 5, orientLabel),
                                   (connectLabel, 'top', 5, footLabel),
                                                                                                         
                                   (limbType, 'top', 5, separator01),
                                   (limbSide, 'top', 5, limbType),
                                   (axisOrient, 'top', 5, limbSide),
                                   (footOrient, 'top', 5, axisOrient),
                                   (jntConnect, 'top', 5, footOrient),
                                                                                                         
                                   (separator02, 'top', 5, jntConnect),  
                                   (sizeLabel, 'top', 5, separator02),  
                                   (sizeInput, 'top', 5, separator02),
                                   
                                   (separator03, 'top', 5, sizeInput), 
                                   (extrasLabel, 'top', 5, separator03),

                                   (stretchBox, 'top', 5, extrasLabel),
                                   (volumePresBox, 'top', 5, extrasLabel),

                                   (springSolverBox, 'top', 5, stretchBox),
                                   (rollJointBox, 'top', 5, stretchBox),
                                   
                                   (softIKBox, 'top', 5, rollJointBox),
                                   
                                   (kneePinBox, 'top', 5, springSolverBox),

                                   (colorLabel, 'top', 5, kneePinBox),
                                   
                                   (leftColor, 'top', 5, colorLabel),
                                   (midColor, 'top', 5, colorLabel), (midColor, 'left', 5, leftColor),
                                   (rightColor, 'top', 5, colorLabel), (rightColor, 'left', 5, midColor),
                                    
                                   (separator04, 'top', 5, leftColor),                                   
                                   (linkText, 'top', 15, separator04),

                                   (button01, 'top', 15, linkText),
                                   ],
                                   
                    attachPosition=[(limbType, 'left', 0, 40),
                                    (limbSide, 'left', 0, 40),
                                    
                                    (axisOrient, 'left', 0, 40),
                                    (footOrient, 'left', 0, 40),
                                    (jntConnect, 'left', 0, 40),
                                    (sizeInput, 'left', 0, 40),

                                    (extrasLabel, 'left', 0, 35),
 
                                    (stretchBox, 'left', 0, 7),
                                    (volumePresBox, 'left', 0, 55),

                                    (springSolverBox, 'left', 0, 7),
                                    
                                    (rollJointBox, 'left', 0, 55),
                                    (softIKBox, 'left', 0, 55),
                                    
                                    (kneePinBox, 'left', 0, 7),

                                    (colorLabel, 'left', 0, 31),                                    
                                    (leftColor, 'left', 0, 10),
                                                                                                            
                                    (linkText, 'left', 0, 25),
                                   ]

                    )
       
    # Show Window
    cmds.showWindow (window)

    if (cmds.currentUnit (q=1, f=1)) == "centimeter": cmds.floatField("sizeInput", e=1, v=100)

    # Auto Fill
    if cmds.optionVar(ex="antLimb_stretchBox"):
        storeLimbUI(0) # Load
    else:
        storeLimbUI(1) # Store       

    antCGiNewsUpdate()
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Lock Specified Attributes

def lockdownAttr(name, doTranslate, doRotate, doScale, doVisibility, doReference):

        if doTranslate:
            cmds.setAttr ((name + ".tx"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".ty"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".tz"), l=1, k=0, cb=0)
                        
        if doRotate:
            cmds.setAttr ((name + ".rx"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".ry"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".rz"), l=1, k=0, cb=0)

        if doScale:
            cmds.setAttr ((name + ".sx"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".sy"), l=1, k=0, cb=0)
            cmds.setAttr ((name + ".sz"), l=1, k=0, cb=0)

        if doVisibility:
            cmds.setAttr ((name + ".v"), l=1, k=0, cb=0)

        if doReference:            
            cmds.setAttr ((name + ".overrideEnabled"), 1)
            cmds.setAttr ((name + ".overrideDisplayType"), 2)     

#-------------------------------------------------------------------------------------------------------------------------------------    
# Build Stretch Nodes

def add_distanceNodes(ribbonName, scaleJointRoot):
    scaleSkeletonList = cmds.listRelatives(scaleJointRoot, ad=1, type="joint")
    scaleSkeletonList.insert(len(scaleSkeletonList), scaleJointRoot)

    scaleSkeletonList.reverse()    

    distNodeCount = []
    scaleJointCount = len(scaleSkeletonList)

    if not scaleJointCount%2:
        includeLastJoint = 1
    else:
        includeLastJoint = 0
    
    # Build distance nodes for each section
    for i in range(scaleJointCount):

        if i is not scaleJointCount-1:
            cmds.shadingNode ("distanceBetween", au=1, n=(scaleSkeletonList[i] + "_distnode"))
            
            cmds.connectAttr ((scaleSkeletonList[i] + ".worldMatrix"), (scaleSkeletonList[i] + "_distnode.inMatrix1"))
            cmds.connectAttr ((scaleSkeletonList[i+1] + ".worldMatrix"), (scaleSkeletonList[i] + "_distnode.inMatrix2"))
            cmds.connectAttr ((scaleSkeletonList[i] + ".rotatePivotTranslate"), (scaleSkeletonList[i] + "_distnode.point1"))
            cmds.connectAttr ((scaleSkeletonList[i+1] + ".rotatePivotTranslate"), (scaleSkeletonList[i] + "_distnode.point2"))

            if i%2:
                cmds.shadingNode ("addDoubleLinear", au=1, n=(scaleSkeletonList[i] + "_full_distnode"))        

                cmds.connectAttr ((scaleSkeletonList[i-1] + "_distnode.distance"), (scaleSkeletonList[i] + "_full_distnode.input1"))
                cmds.connectAttr ((scaleSkeletonList[i] + "_distnode.distance"), (scaleSkeletonList[i] + "_full_distnode.input2"))

                distNodeCount.append((scaleSkeletonList[i] + "_full_distnode"))
                
        elif includeLastJoint:
            cmds.shadingNode ("addDoubleLinear", au=1, n=(scaleSkeletonList[i] + "_full_distnode"))        
            cmds.connectAttr ((scaleSkeletonList[i-1] + "_distnode.distance"), (scaleSkeletonList[i] + "_full_distnode.input1"))
            distNodeCount.append((scaleSkeletonList[i] + "_full_distnode"))            

    if len(distNodeCount) > 1:
        cmds.shadingNode ("addDoubleLinear", au=1, n=(ribbonName.lower() + "_stretch_full_distnode"))        

        cmds.connectAttr ((distNodeCount[0] + ".output"), (ribbonName.lower() + "_stretch_full_distnode.input1"))
        cmds.connectAttr ((distNodeCount[1] + ".output"), (ribbonName.lower() + "_stretch_full_distnode.input2"))

        outPutNode = (ribbonName.lower() + "_stretch_full_distnode")
    else:
        outPutNode = distNodeCount[0]   

    cmds.shadingNode ("distanceBetween", au=1, n=(scaleSkeletonList[0] + "_stretch_distnode"))
    cmds.shadingNode ("plusMinusAverage", au=1, n=(scaleSkeletonList[0] + "_stretch_adjust"))
    
    cmds.connectAttr ((scaleSkeletonList[0] + ".worldMatrix"), (scaleSkeletonList[0] + "_stretch_distnode.inMatrix1"))
    cmds.connectAttr ((ribbonName + "_stretchEndPos_loc.worldMatrix"), (scaleSkeletonList[0] + "_stretch_distnode.inMatrix2"))
    cmds.connectAttr ((scaleSkeletonList[0] + ".rotatePivotTranslate"), (scaleSkeletonList[0] + "_stretch_distnode.point1"))
    cmds.connectAttr ((ribbonName + "_stretchEndPos_loc.rotatePivotTranslate"), (scaleSkeletonList[0] + "_stretch_distnode.point2"))    

    cmds.shadingNode ("multiplyDivide", au=1, n=(ribbonName + "_scaleFactor"))
    cmds.shadingNode ("condition", au=1, n=(ribbonName + "_condition"))

    cmds.setAttr ((ribbonName + "_scaleFactor.operation"), 2)
    cmds.setAttr ((ribbonName + "_condition.secondTerm"), 1)
    cmds.setAttr ((ribbonName + "_condition.operation"), 5)
    cmds.setAttr ((ribbonName + "_condition.colorIfTrueR"), 1)

    cmds.connectAttr ((scaleSkeletonList[0] + "_stretch_distnode.distance"), (ribbonName + "_scaleFactor.input1X"), f=1)
    
    cmds.connectAttr ((outPutNode + ".output"), (scaleSkeletonList[0] + "_stretch_adjust.input1D[0]"), f=1)
    cmds.connectAttr ((scaleSkeletonList[0] + "_stretch_adjust.output1D"), (ribbonName + "_scaleFactor.input2X"), f=1)
    
    cmds.connectAttr ((ribbonName + "_scaleFactor.outputX"), (ribbonName + "_condition.firstTerm"), f=1)

    return outPutNode, (scaleSkeletonList[0] + "_stretch_distnode") 

    
#---------------------------------------------------------------------------
# Build Icons/Controls

def build_RigIcon(iconType, iconName, colour, scale, orientation):

    # globalScale = cmds.intField("globalScaleInput", q=1, v=1)
    
    if colour == "Red":
        colour = [1, 0, 0]
    elif colour == "Blue":
        colour = [0, 0, 1]
    elif colour == "Yellow":
        colour = [1, 1, 0]
    elif colour == "Green":
        colour = [0, 1, 0]
    elif colour == "Black":
        colour = [0, 0, 0]
                        
    if orientation == "X":
        rotAxis = ".rotateX"
    if orientation == "Z":
        rotAxis = ".rotateZ"
                          
    if iconType == "Translate":
        pointsList = ([-0.50014558208710158, 1.1105462817953031e-16, 6.0257540429130064e-16],
                [-0.30008734925226305, 6.6632776907718638e-17, 0.20005823283484037],
                [-0.30008734925226305, 6.6632776907718638e-17, 0.10002911641742132],
                [-0.099962118478249914, 2.2196049104972174e-17, 0.099962118478251122],
                [-0.10002911641742046, 2.2210925635906089e-17, 0.30008734925226116],
                [-0.20005823283484206, 4.4421851271812431e-17, 0.30008734925226116],
                [0, 0, 0.50014558208710236],
                [0.20005823283484078, -4.4421851271812148e-17, 0.30008734925226116],
                [0.10002911641742046, -2.2210925635906089e-17, 0.30008734925226116],
                [0.099962118478249914, -2.2196049104972174e-17, 0.099962118478251122],
                [0.30008734925225883, -6.6632776907717701e-17, 0.10002911641742132],
                [0.30008734925225883, -6.6632776907717701e-17, 0.20005823283484037],
                [0.50014558208710158, -1.1105462817953031e-16, 6.0257540429130064e-16],
                [0.30008734925225883, -6.6632776907717701e-17, -0.20005823283484059],
                [0.30008734925225883, -6.6632776907717701e-17, -0.10002911641742018],
                [0.099962118478249914, -2.2196049104972174e-17, -0.099962118478249429],
                [0.10002911641742046, -2.2210925635906089e-17, -0.30008734925226116],
                [0.20005823283484078, -4.4421851271812148e-17, -0.30008734925226116],
                [0, 0, -0.50014558208710236],
                [-0.20005823283484206, 4.4421851271812431e-17, -0.30008734925226116],
                [-0.10002911641742046, 2.2210925635906089e-17, -0.30008734925226116],
                [-0.099962118478249914, 2.2196049104972174e-17, -0.099962118478249429],
                [-0.30008734925226305, 6.6632776907718638e-17, -0.10002911641742018],
                [-0.30008734925226305, 6.6632776907718638e-17, -0.20005823283484059],
                [-0.50014558208710158, 1.1105462817953031e-16, 6.0257540429130064e-16]
                )
                
        cmds.curve (d=1, p=pointsList[0], n=iconName)

        for i in range(len(pointsList)):
            if i < (len(pointsList)-1):
                cmds.curve (iconName, a=1, p=pointsList[i+1])
                
    if iconType == "Point":
        pointsList = ([-0.50034994073483507, -0.00152424931426448, 0.35455152544687402],
                [0.0013416437945424355, 0.50015894964716101, 0.35481523768071371],
                [0.50009062278004079, 0.0014112767983053321, 0.35491807433836609],
                [0, 0, -0.53556469863508738],
                [-0.0015976249628304477, -0.50027701982201966, 0.35465436251126342],
                [-0.50034994073483507, -0.00152424931426448, 0.35455152544687402],
                [0, 0, -0.53556469863508738],
                [0, 0, -0.53556469863508738],
                [0, 0, -0.53556469863508738],
                [0, 0, -0.53556469863508738],
                [0.0013416437945424355, 0.50015894964716101, 0.35481523768071371],
                [0.50009051225258583, 0.0014112567120969769, 0.35491807429471212],
                [0.50009062278004079, 0.0014112767983053321, 0.35491807433836609],
                [-0.0015976249628304477, -0.50027701982201966, 0.35465436251126342]
                )
                
        cmds.curve (d=1, p=pointsList[0], n=iconName)

        for i in range(len(pointsList)):
            if i < (len(pointsList)-1):
                cmds.curve (iconName, a=1, p=pointsList[i+1])                

        cmds.rotate (0, 180, 0, r=1, os=1)
                
    if iconType == "Rotate":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.6, s=12)

        cmds.select ((iconName + ".cv[0]"), r=1)
        cmds.select ((iconName + ".cv[2]"), add=1)
        cmds.select ((iconName + ".cv[4]"), add=1)        
        cmds.select ((iconName + ".cv[6]"), add=1)        
        cmds.select ((iconName + ".cv[8]"), add=1)        
        cmds.select ((iconName + ".cv[10]"), add=1)        
                                
        cmds.scale (0.5, 0.5, 0.5, r=1, ocp=1)

    if iconType == "Circle":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.5, s=12)

    if iconType == "Cube":
        pointsList = ([0.49949352081828996, -0.49965646741954789, 0.50328983824071771],
                [0.49934400608651491, -0.50002955640749192, -0.49669244817327646],
                [0.49935240467804698, 0.4999694046672008, -0.49703337181054147],
                [0.49950191468729815, 0.50034278368308582, 0.50291652363626671],
                [0.49949352081828996, -0.49965646741954789, 0.50328983824071771],
                [-0.50050383972379531, -0.49965777484916379, 0.50343541520396873],
                [-0.50065028582985005, -0.50003088904426218, -0.49661468934922276],
                [-0.5006503300331675, 0.49996983464596256, -0.49695561241069885],
                [-0.50050388864963413, 0.50034323886898902, 0.50306210117530015],
                [0.49950191468729815, 0.50034278368308582, 0.50291652363626671],
                [0.49935240467804698, 0.4999694046672008, -0.49703337181054147],
                [-0.5006503300331675, 0.49996983464596256, -0.49695561241069885],
                [-0.50065028582985005, -0.50003088904426218, -0.49661468934922276],
                [0.49934400608651491, -0.50002955640749192, -0.49669244817327646],
                [0.49949352081828996, -0.49965646741954789, 0.50328983824071771],
                [-0.5005037491930191, -0.49965764410620322, 0.50343541514217149],
                [-0.50050383972379531, -0.49965777484916379, 0.50343541520396873],
                [-0.50050388864963413, 0.50034323886898902, 0.50306210117530015]
                )

        cmds.curve (d=1, p=pointsList[0], n=iconName)

        for i in range(len(pointsList)):
            if i < (len(pointsList)-1):
                cmds.curve (iconName, a=1, p=pointsList[i+1])
                
    if iconType == "IKHandle":
        pointsListA = ([-7.1382756976404347e-16, 1.1108536880093235e-16, -0.50028402553819296],
                [-0.31876615676753811, 7.0780305342917757e-17, -0.31876615676753428],
                [-0.50028402553819373, 0, 1.110853688009325e-16],
                [-0.318766156767538, -7.0780305342917757e-17, 0.31876615676753434],
                [-4.9165683216217886e-16, -1.1108536880093235e-16, 0.50028402553819296],
                [0.31876615676753201, -7.0780305342917757e-17, 0.31876615676753428],
                [0.50028402553819373, 0, -1.110853688009325e-16],
                [0.31876615676753189, 7.0780305342917757e-17, -0.31876615676753434],
                [-7.1382756976404347e-16, 1.1108536880093235e-16, -0.50028402553819296]
                )

        pointsListB = ([0.30719697801356827, 9.6465531701909973e-17, -0.30719697801356916],
                [-3.9882920891183316e-15, 6.1009819481423129e-17, -0.38857469280865742],
                [-0.30719697801356927, 0, -0.30719697801356921],
                [-0.38857469280865758, -6.1009819481423129e-17, -3.9371601392578399e-15],
                [-0.30719697801356904, -9.6465531701909973e-17, 0.30719697801356838],
                [-6.3914937325614286e-16, -6.1009819481423129e-17, 0.38857469280865281],
                [0.30719697801356927, 0, 0.30719697801356921],
                [0.38857469280865281, 6.1009819481423129e-17, -7.6697924790737145e-16],
                [0.30719697801356827, 9.6465531701909973e-17, -0.30719697801356916]
                )
                        
        cmds.curve (d=1, p=pointsListA[0], n=iconName)

        for i in range(len(pointsListA)):
            if i < (len(pointsListA)-1):
                cmds.curve (iconName, a=1, p=pointsListA[i+1])    

        cmds.curve (d=1, p=pointsListB[0], n=(iconName + "_inner"))

        for i in range(len(pointsListB)):
            if i < (len(pointsListB)-1):
                cmds.curve ((iconName + "_inner"), a=1, p=pointsListB[i+1])  
                
        cmds.parent ((cmds.listRelatives (iconName + "_inner")), iconName, s=1, r=1)
        
        cmds.rotate (0, -90, 0, iconName, r=1, fo=1)
        cmds.makeIdentity (iconName, a=1, r=1)

        cmds.delete ((iconName + "_inner"))

    if iconType == "Slider":
        pointsList = ([-2.2283155692144308e-16, -6.0453498292630366e-16, -0.50177205835889982],
                [-4.4566311384289685e-17, -0.20070882334355969, -0.30106323501534193],
                [-8.9132622768577792e-17, -0.10035441167178098, -0.30106323501534193],
                [1.7826524553715413e-16, -0.10035441167178098, 0.30106323501533772],
                [2.2283155692144229e-16, -0.20070882334355969, 0.30106323501533772],
                [2.2283155692144362e-16, -6.0453498292630366e-16, 0.50177205835889982],
                [4.4566311384287713e-17, 0.20070882334355994, 0.30106323501533772],
                [8.9132622768576424e-17, 0.10035441167177984, 0.30106323501533772],
                [-1.7826524553715551e-16, 0.10035441167177984, -0.30106323501534193],
                [-2.2283155692144422e-16, 0.20070882334355994, -0.30106323501534193],
                [-2.2283155692144308e-16, -6.0453498292630366e-16, -0.50177205835889982]
                )
                
        cmds.curve (d=1, p=pointsList[0], n=iconName)

        for i in range(len(pointsList)):
            if i < (len(pointsList)-1):
                cmds.curve (iconName, a=1, p=pointsList[i+1])    

        cmds.rotate (0, -90, 0, iconName, r=1, fo=1)
        cmds.makeIdentity (iconName, a=1, r=1)

    if iconType == "FKLabel":
        pointsListA = ([-0.37276455904025763, 0.38125594817812219, -0.0019004885689956341],
                [-0.37276455904025763, 0.65197291497280763, -0.0019004885689956341],
                [-0.15941631946163998, 0.65197291497280763, -0.0019004885689956341],
                [-0.15941631946163998, 0.71965214890603457, -0.0019004885689956341],
                [-0.37276455904025763, 0.71965214890603457, -0.0019004885689956341],
                [-0.37276455904025763, 0.92268988176749311, -0.0019004885689956341],
                [-0.1189673929634345, 0.92268988176749311, -0.0019004885689956341],
                [-0.1189673929634345, 0.99036908463894235, -0.0019004885689956341],
                [-0.45736360922223573, 0.99036908463894235, -0.0019004885689956341],
                [-0.45736360922223573, 0.38125594817812219, -0.0019004885689956341],
                [-0.37276455904025763, 0.38125594817812219, -0.0019004885689956341]
                )

        pointsListB = ([0.084070308836246332, 0.38125594817812219, -0.0019003563829690928],
                [0.084070308836246332, 0.68991031037198147, -0.0019003563829690928],
                [0.34632738303744504, 0.38125594817812219, -0.0019003563829690928],
                [0.45736360922223573, 0.38125594817812219, -0.0019003563829690928],
                [0.1796408137725205, 0.70048516834839547, -0.0019003563829690928],
                [0.41691471378580802, 0.99036908463894235, -0.0019003563829690928],
                [0.32940759785047158, 0.99036908463894235, -0.0019003563829690928],
                [0.084070308836246332, 0.69070341074241259, -0.0019003563829690928],
                [0.084070308836246332, 0.99036908463894235, -0.0019003563829690928],
                [-0.00052874134573177578, 0.99036908463894235, -0.0019003563829690928],
                [-0.00052874134573177578, 0.38125594817812219, -0.0019003563829690928],
                [0.084070308836246332, 0.38125594817812219, -0.0019003563829690928]
                )
                        
        cmds.curve (d=1, p=pointsListA[0], n=iconName)

        for i in range(len(pointsListA)):
            if i < (len(pointsListA)-1):
                cmds.curve (iconName, a=1, p=pointsListA[i+1])    

        cmds.curve (d=1, p=pointsListB[0], n=(iconName + "_inner"))

        for i in range(len(pointsListB)):
            if i < (len(pointsListB)-1):
                cmds.curve ((iconName + "_inner"), a=1, p=pointsListB[i+1])  
                
        cmds.parent ((cmds.listRelatives (iconName + "_inner")), iconName, s=1, r=1)
        
        cmds.rotate (0, -90, 0, iconName, r=1, fo=1)
        cmds.makeIdentity (iconName, a=1, r=1)

        cmds.delete ((iconName + "_inner"))

    if iconType == "Arrow":
        pointsList = ([-9.1931988995664767e-17, -2.8759696960856863e-16, 0.49615556213233214],
                [0.42772031218304501, -2.8759696960856863e-16, -0.068435249949287166],
                [0.1411477030204048, -2.8759696960856863e-16, -0.068435249949287208],
                [0.14114770302040489, -2.8759696960856863e-16, -0.49615556213233214],
                [-0.14114770302040483, -2.8759696960856863e-16, -0.49615556213233225],
                [-0.14114770302040489, -2.8759696960856863e-16, -0.068435249949287236],
                [-0.42772031218304507, -2.8759696960856863e-16, -0.068435249949287263],
                [-9.1931988995664767e-17, -2.8759696960856863e-16, 0.49615556213233214]
                )
                
        cmds.curve (d=1, p=pointsList[0], n=iconName)

        for i in range(len(pointsList)):
            if i < (len(pointsList)-1):
                cmds.curve (iconName, a=1, p=pointsList[i+1])    

        cmds.makeIdentity (iconName, a=1, r=1)
        
    if iconType == "Global":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.5, s=12)

        for x in range(8):
            pointsList = ([-0.023940681939395029, 0, 0.5631832622276296],
                [-0.023940681939395067, 0, 0.75200189936704354],
                [-0.038743440873048901, 0, 0.75200189936704354],
                [-0.0091379230057411342, 0, 0.79006613662501024],
                [0.021524934785399154, 0, 0.75200189936704354],
                [0.0067221758517452199, 0, 0.75200189936704354],
                [0.0067221758517452199, 0, 0.5631832622276296],
                [-0.023940681939395029, 0, 0.5631832622276296]       
                )
                    
            cmds.curve (d=1, p=pointsList[0], n=(iconName+ str(x)))

            for i in range(len(pointsList)):
                if i < (len(pointsList)-1):
                    cmds.curve ((iconName + str(x)), a=1, p=pointsList[i+1]) 

            cmds.rotate (0, (45 * x), 0, (iconName + str(x)), r=1, fo=1)
            cmds.makeIdentity ((iconName + str(x)), a=1, r=1)
            cmds.parent ((cmds.listRelatives ((iconName + str(x)), s=1)), iconName, s=1, r=1)
            
            cmds.delete ((iconName + str(x)))
            
            cmds.rotate (0, -90, 0, iconName, r=1, fo=1)
            
    if iconType == "IKLabel":
        pointsListA = ([-0.27672412079123787, 0.38125594817812219, 0.0019003563829691206],
                [-0.27672412079123787, 0.99036908463894235, 0.0019003563829691206],
                [-0.36132317097321598, 0.99036908463894235, 0.0019003563829691206],
                [-0.36132317097321598, 0.38125594817812219, 0.0019003563829691206],
                [-0.27672412079123787, 0.38125594817812219, 0.0019003563829691206]
                )

        pointsListB = ([-0.031386878369679128, 0.38125594817812219, 0.0019004885689956341],
                [-0.031386878369679128, 0.68991031037198147, 0.0019004885689956341],
                [0.23087016476974187, 0.38125594817812219, 0.0019004885689956341],
                [0.34190645307808798, 0.38125594817812219, 0.0019004885689956341],
                [0.064183626566595042, 0.70048516834839547, 0.0019004885689956341],
                [0.30145749551810486, 0.99036908463894235, 0.0019004885689956341],
                [0.21395037958276841, 0.99036908463894235, 0.0019004885689956341],
                [-0.031386878369679128, 0.69070341074241259, 0.0019004885689956341],
                [-0.031386878369679128, 0.99036908463894235, 0.0019004885689956341],
                [-0.11598592855165724, 0.99036908463894235, 0.0019004885689956341],
                [-0.11598592855165724, 0.38125594817812219, 0.0019004885689956341],
                [-0.031386878369679128, 0.38125594817812219, 0.0019004885689956341]
                )
                        
        cmds.curve (d=1, p=pointsListA[0], n=iconName)

        for i in range(len(pointsListA)):
            if i < (len(pointsListA)-1):
                cmds.curve (iconName, a=1, p=pointsListA[i+1])    

        cmds.curve (d=1, p=pointsListB[0], n=(iconName + "_inner"))

        for i in range(len(pointsListB)):
            if i < (len(pointsListB)-1):
                cmds.curve ((iconName + "_inner"), a=1, p=pointsListB[i+1])  
                
        cmds.parent ((cmds.listRelatives (iconName + "_inner")), iconName, s=1, r=1)
        
        cmds.rotate (0, -90, 0, iconName, r=1, fo=1)
        cmds.makeIdentity (iconName, a=1, r=1)

        cmds.delete ((iconName + "_inner"))

    if iconType == "Paw":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.5, s=12)
        cmds.move (0, 0, -0.25, ((iconName + ".cv[5:6]"), (iconName + ".cv[8:9]")), r=1, os=1, wd=1)
 
        cmds.circle (nr=(0, 1, 0), n=(iconName + "_pad2"), r=0.5, s=6)
        cmds.scale (0.3, 1, 0.5, (iconName + "_pad2"), r=1, ocp=1)
        cmds.move (0.2, 0, 0.775, (iconName + "_pad2"), r=1, os=1, wd=1)
 
        cmds.duplicate((iconName + "_pad2"), n=(iconName + "_pad1"))
        cmds.move (0.35, 0, -0.3, (iconName + "_pad1"), r=1, os=1, wd=1)
 
        cmds.duplicate((iconName + "_pad2"), n=(iconName + "_pad3"))
        cmds.move (-0.4, 0, 0, (iconName + "_pad3"), r=1, os=1, wd=1)

        cmds.duplicate((iconName + "_pad1"), n=(iconName + "_pad4"))
        cmds.move (-1.1, 0, 0, (iconName + "_pad4"), r=1, os=1, wd=1)

        cmds.makeIdentity ((iconName + "_pad1"), (iconName + "_pad2"), (iconName + "_pad3"), (iconName + "_pad4"), a=1, r=1, t=1, s=1)

        cmds.parent ((cmds.listRelatives (iconName + "_pad1")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_pad2")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_pad3")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_pad4")), iconName, s=1, r=1)

        cmds.delete ((iconName + "_pad1"), (iconName + "_pad2"), (iconName + "_pad3"), (iconName + "_pad4")) 

        cmds.scale (0.1, 0.1, 0.1, iconName, r=1, ocp=1)

        cmds.makeIdentity (iconName, s=1)

    if iconType == "Foot":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.5, s=12)
        cmds.scale (1, 1, 1.8, iconName, r=1, ocp=1)
        cmds.move (0.2, 0, 0, (iconName + ".cv[3:5]"), r=1, os=1, wd=1)
        cmds.move (0.15, 0, 0, (iconName + ".cv[4]"), r=1, os=1, wd=1)
        cmds.move (0.10, 0, 0, (iconName + ".cv[8]"), r=1, os=1, wd=1)
        cmds.move (-0.16, 0, 0, ((iconName + ".cv[10:11]"), (iconName + ".cv[5:6]")), r=1, os=1, wd=1)

        cmds.circle (nr=(0, 1, 0), n=(iconName + "_toe1"), r=0.5, s=6)
        cmds.scale (0.23, 0.93, 0.33, (iconName + "_toe1"), r=1, ocp=1)
        cmds.move (-0.4, 0, 1.01, (iconName + "_toe1"), r=1, os=1, wd=1)
        cmds.rotate (0, -10, 0, (iconName + "_toe1"), r=1, os=1)

        cmds.duplicate((iconName + "_toe1"), n=(iconName + "_toe2"))
        cmds.move (0.23, 0, 0.07, (iconName + "_toe2"), r=1, os=1, wd=1)
        cmds.scale (0.8, 0.8, 0.8, (iconName + "_toe2"), r=1, ocp=1)
        cmds.rotate (0, 10, 0, (iconName + "_toe2"), r=1, os=1)

        cmds.duplicate((iconName + "_toe2"), n=(iconName + "_toe3"))
        cmds.move (0.2, 0, 0.01, (iconName + "_toe3"), r=1, os=1, wd=1)
        cmds.scale (0.9, 0.9, 0.9, (iconName + "_toe3"), r=1, ocp=1)
        cmds.rotate (0, 4, 0, (iconName + "_toe3"), r=1, os=1)

        cmds.duplicate((iconName + "_toe3"), n=(iconName + "_toe4"))
        cmds.move (0.2, 0, -0.03, (iconName + "_toe4"), r=1, os=1, wd=1)
        cmds.scale (0.9, 0.9, 0.9, (iconName + "_toe4"), r=1, ocp=1)
        cmds.rotate (0, 4, 0, (iconName + "_toe4"), r=1, os=1)

        cmds.duplicate((iconName + "_toe4"), n=(iconName + "_toe5"))
        cmds.move (0.15, 0, -0.12, (iconName + "_toe5"), r=1, os=1, wd=1)
        cmds.scale (0.9, 0.9, 0.9, (iconName + "_toe5"), r=1, ocp=1)
        cmds.rotate (0, 4, 0, (iconName + "_toe5"), r=1, os=1)

        cmds.makeIdentity (iconName, (iconName + "_toe1"), (iconName + "_toe2"), (iconName + "_toe3"), (iconName + "_toe4"), (iconName + "_toe5"), a=1, r=1, t=1, s=1)

        cmds.parent ((cmds.listRelatives (iconName + "_toe1")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_toe2")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_toe3")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_toe4")), iconName, s=1, r=1)
        cmds.parent ((cmds.listRelatives (iconName + "_toe5")), iconName, s=1, r=1)

        cmds.delete ((iconName + "_toe1"), (iconName + "_toe2"), (iconName + "_toe3"), (iconName + "_toe4"), (iconName + "_toe5")) 

        cmds.scale (0.1, 0.1, 0.1, iconName, r=1, ocp=1)

        cmds.makeIdentity (iconName, s=1)

    if iconType == "LollyPop":
        cmds.circle (nr=(1, 0, 0), n=iconName, r=0.5, s=12)
        cmds.move (0, 1.5, 0, iconName, r=1, os=1, wd=1)
        cmds.makeIdentity (iconName, a=1, r=1, t=1)

        cmds.curve (d=1, p=[(0, 0, 0), (0, 1, 0)], n=(iconName + "_stick"))
                               
        cmds.parent ((cmds.listRelatives (iconName + "_stick")), iconName, s=1, r=1)
        cmds.xform (iconName, piv=(0, 0, 0))        
        
        cmds.delete ((iconName + "_stick"))               
                     
    cmds.setAttr ((iconName + ".ove"), 1)

    cmds.setAttr((iconName + ".overrideRGBColors"), 1)
    cmds.setAttr ((iconName + ".overrideColorRGB"), colour[0], colour[1], colour[2])
    
    cmds.setAttr ((iconName + ".scale"), scale, scale, scale)
   
    if orientation != "Y":
        cmds.setAttr ((iconName + rotAxis), 90)
        
    cmds.makeIdentity (iconName, a=1, t=1, r=1, s=1)
    cmds.controller (iconName)
        
    cmds.delete (iconName, ch=1)
    cmds.select (cl=1)
    
#---------------------------------------------------------------------------
# Add Joint & Orient

def addOrientJoint(jointName, jointPosName, roOrder, *orientOffset):
    
    getPosPoint = cmds.xform(jointPosName, q=1, ws=1, piv=1)
    cmds.joint (p=(getPosPoint[0], getPosPoint[1], getPosPoint[2]), roo=roOrder, n=jointName.lower())
    
    cmds.orientConstraint (jointPosName, jointName.lower(), w=1, n="tmpOC"); cmds.delete("tmpOC")
    cmds.rotate (orientOffset[0], orientOffset[1], orientOffset[2], (jointName.lower() + ".rotateAxis"), a=1, os=1, fo=1)
    
    cmds.joint (jointName.lower(), e=1, zso=1)
    cmds.makeIdentity (jointName.lower(), a=1, t=0, r=1, s=0)
   
#---------------------------------------------------------------------------
# Main Procedure

def antcgiQuickLimb(*args):

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Setup Variables

    quadFront = 0
    quadRear = 0
    
    jointChainList = cmds.ls(sl=1, type="joint")

    if not jointChainList:
        cmds.error("Select the three, or four main joints of the limb.")

    limbType = cmds.optionMenu("limbType", q=1, v=1).lower()
    jntOrient = cmds.optionMenu("axisOrient", q=1, v=1)
    footOrient = cmds.optionMenu("footOrient", q=1, v=1)
    
    limbSide = cmds.optionMenu("limbSide", q=1, v=1)

    doStretch = cmds.checkBox("stretchBox", q=1, v=1)
    doVPres = cmds.checkBox("volumePresBox", q=1, v=1)
    doSpring = cmds.checkBox("springSolverBox", q=1, v=1)
    doRoll = cmds.checkBox("rollJointBox", q=1, v=1)
            
    scaleMultiply = cmds.floatField("sizeInput", q=1, v=1)  

    if limbSide == "Left":
        iconColour = cmds.colorSliderGrp("leftColor", q=1, rgb=1)
    else:
        iconColour = cmds.colorSliderGrp("rightColor", q=1, rgb=1)

    midIconColour = cmds.colorSliderGrp("midColor", q=1, rgb=1)

    if "Front" in cmds.optionMenu("limbType", q=1, v=1): quadFront = 1
    if "Rear" in cmds.optionMenu("limbType", q=1, v=1): quadRear = 1

    # Use Spring Solver?
    
    if doSpring:
        # Initialize Spring Solver
        mel.eval("ikSpringSolver")
        solverType = "ikSpringSolver"
    else:
        solverType = "ikRPsolver"
        
    pvValue = 1
                  
    if limbType == "biped arm":
        limbType = "arm"
        midPoint = "elbow"
        pvValue = -1
        
    elif limbType == "biped leg":
        limbType = "leg"
        midPoint = "knee"

    elif limbType == "quad rear":
        limbType = "leg_rear"
        midPoint = "tibia"

    elif limbType == "quad front":
        limbType = "leg_front"
        midPoint = "tibia"
        pvValue = -1

        pvValue = -1

        if limbType is "arm":
            pvValue = 1

    pvMoveAmount = [0, 0, 0]
    pvDistAdjust = [0, 0, 0]
        
    getPrefix = jointChainList[0][0:2]
    limbName = getPrefix + limbType

    rootJoint = jointChainList[0] 
    endJoint = jointChainList[-1]

    # Setup IK Control Icon

    if limbType == "leg_rear":
        ikControlIcon = "Paw"
        ikControlScale = 0.1
    elif limbType == "leg_front":
        ikControlIcon = "Paw"
        ikControlScale = 0.1
    elif limbType == "leg":
        ikControlIcon = "Foot"
        ikControlScale = 0.125
    else:
        ikControlIcon = "IKHandle"
        ikControlScale = 0.2

    # Setup Control Orientation

    primAxis = jntOrient[0].capitalize()
    ikControlOrient = jntOrient[0].capitalize()
    fkControlOrient = jntOrient[0].capitalize()
            
    if limbType is "arm":
        if "xyz" in jntOrient:
            ikControlOrient = jntOrient[2].capitalize()
            fkControlOrient = jntOrient[2].capitalize()

        elif "yzx" in jntOrient:
            ikControlOrient = jntOrient[0].capitalize()
            fkControlOrient = jntOrient[0].capitalize()
            
        else:
            ikControlOrient = jntOrient[1].capitalize()
            fkControlOrient = jntOrient[1].capitalize()
    else:
        if "xyz" in jntOrient:
            ikControlOrient = jntOrient[1].capitalize()
            fkControlOrient = jntOrient[2].capitalize()
            
        elif "zxy" in jntOrient:
            ikControlOrient = jntOrient[2].capitalize()
            fkControlOrient = jntOrient[1].capitalize()
                                              
    cmds.select(cl=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Hierachy

    if not cmds.objExists("connection_lines"):

        rigName = "xxx_rig_grp"

        cmds.group (em=1, n=rigName)
        cmds.group (em=1, n="controls", p=rigName)
        
        cmds.group (em=1, n="DO_NOT_TOUCH", p=rigName)
        cmds.group (em=1, n="root_grp", p="controls")

        cmds.group (em=1, n="export_skeleton", p="DO_NOT_TOUCH")
        cmds.group (em=1, n="geometry", p="DO_NOT_TOUCH")

        cmds.group (em=1, n="export_geometry", p="geometry")
        cmds.group (em=1, n="template_geometry", p="geometry")
        cmds.group (em=1, n="proxy_geometry", p="geometry")
        cmds.group (em=1, n="basecage_geometry", p="geometry")
        cmds.group (em=1, n="blendshapes", p="geometry")
            
        cmds.group (em=1, n="rig_deformers", p="DO_NOT_TOUCH")
        cmds.group (em=1, n="rig_systems", p="DO_NOT_TOUCH")
        cmds.group (em=1, n="visual_aids", p="DO_NOT_TOUCH")
        cmds.group (em=1, n="connection_lines", p="visual_aids")
    
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Setup The Scene
 
    if not cmds.objExists("scene_direction"): 
        
        build_RigIcon("Arrow", "scene_direction", "Black", 2*scaleMultiply, "Y")
        build_RigIcon("Global", "root_ctrl", midIconColour, 1*scaleMultiply, "Y")
        build_RigIcon("Arrow", "root_joint_ctrl", "Black", 1*scaleMultiply, "Y")

        cmds.parent ("scene_direction", "controls")
        cmds.parent ("root_joint_ctrl", "controls")
        cmds.parent ("root_ctrl", "root_grp")
        
        cmds.makeIdentity ("root_joint_ctrl", a=1, t=0, r=1, s=0)
        
        cmds.addAttr ("root_ctrl", ln="tweakOptions", nn="-----", at="enum", en="TWEAK")
        cmds.setAttr ("root_ctrl.tweakOptions", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Body_Tweak", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Body_Tweak", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Arm_Tweak", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Arm_Tweak", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Leg_Tweak", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Leg_Tweak", e=1, k=0, cb=1)
        
        cmds.addAttr ("root_ctrl", ln="RigOptions", nn="-----", at="enum", en="VISIBILITY")
        cmds.setAttr ("root_ctrl.RigOptions", e=1, k=0, cb=1)    

        cmds.addAttr ("root_ctrl", ln="Body_Controls", at="enum", en="Hide:Show", dv=1)
        cmds.setAttr ("root_ctrl.Body_Controls", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Face_Controls", at="enum", en="Hide:Show", dv=1)
        cmds.setAttr ("root_ctrl.Face_Controls", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Twist_Controls", at="enum", en="Hide:Show", dv=1)
        cmds.setAttr ("root_ctrl.Twist_Controls", e=1, k=0, cb=1)
                
        cmds.addAttr ("root_ctrl", ln="Geometry", at="enum", en="Hide:Show", dv=1)
        cmds.setAttr ("root_ctrl.Geometry", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Blendshapes", at="enum", en="Hide:Show", dv=0)
        cmds.setAttr ("root_ctrl.Blendshapes", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="lockOptions", nn="-----", at="enum", en="LOCK")
        cmds.setAttr ("root_ctrl.lockOptions", e=1, k=0, cb=1)  

        cmds.addAttr ("root_ctrl", ln="ExportGeometry", at="enum", en="Unlocked:Wireframe:Locked", dv=2)
        cmds.setAttr ("root_ctrl.ExportGeometry", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="RigDebug", nn="-----", at="enum", en="DEBUG")
        cmds.setAttr ("root_ctrl.RigDebug", e=1, k=0, cb=1)
        
        cmds.addAttr ("root_ctrl", ln="Rig_Systems", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Rig_Systems", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Rig_Deformers", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Rig_Deformers", e=1, k=0, cb=1)
        
        cmds.addAttr ("root_ctrl", ln="Skeleton", at="enum", en="Hide:Show")
        cmds.setAttr ("root_ctrl.Skeleton", e=1, k=0, cb=1)

        cmds.addAttr ("root_ctrl", ln="Rig_Connection", at="enum", en="Normal:HasNoEffect:Blocking")
        cmds.setAttr ("root_ctrl.Rig_Connection", e=1, k=0, cb=1)

        cmds.setAttr ("root_ctrl.visibility", e=1, k=0, cb=1)
        
        cmds.connectAttr ("root_ctrl.Rig_Deformers", "rig_deformers.visibility", f=1)     
        cmds.connectAttr ("root_ctrl.Rig_Systems", "rig_systems.visibility", f=1) 

        cmds.connectAttr ("root_ctrl.Geometry", "export_geometry.visibility", f=1) 
        cmds.connectAttr ("root_ctrl.Blendshapes", "blendshapes.visibility", f=1) 
            
        cmds.connectAttr ("root_ctrl.Body_Controls", "connection_lines.visibility", f=1) 

        cmds.connectAttr ("root_ctrl.scale", "rig_systems.scale", f=1)
                            
        cmds.setAttr ("scene_direction.overrideDisplayType", 2)   
    
     
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Joints

    for jointChain in jointChainList:
        addOrientJoint((jointChain + "_fk"), jointChain, "xyz", 0, 0, 0)

    cmds.select(cl=1)

    for jointChain in jointChainList:
        addOrientJoint((jointChain + "_ik"), jointChain, "xyz", 0, 0, 0)  

    cmds.select(cl=1)

    for jointChain in jointChainList:
        addOrientJoint((jointChain + "_stretch"), jointChain, "xyz", 0, 0, 0)  

    cmds.select(cl=1)

    # Set Prefered Angle
    cmds.joint((rootJoint + "_fk"), e=1, spa=1, ch=1)
    cmds.joint((rootJoint + "_ik"), e=1, spa=1, ch=1)
    cmds.joint((rootJoint + "_stretch"), e=1, spa=1, ch=1)
    
    if quadRear:
        for jointChain in jointChainList:
            addOrientJoint((jointChain + "_driver"), jointChain, "xyz", 0, 0, 0)
 
        cmds.joint((rootJoint + "_driver"), e=1, spa=1, ch=1)

        # Connect driver scale to ik - for stretchiness
        for jointChain in jointChainList:
            cmds.connectAttr ((jointChain + "_driver.scale"), (jointChain + "_ik.scale"), f=1)
        
    cmds.select(cl=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add Roll & Twist Joints
    
    if doRoll:
        # Add Twist Joints
        cmds.duplicate(rootJoint, n=rootJoint + "_twist", po=1)
        cmds.duplicate(endJoint, n=endJoint + "_twist", po=1)

        cmds.parent(rootJoint + "_twist", rootJoint)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Connect to main joints

    for jointChain in jointChainList:
        cmds.parentConstraint ((jointChain + "_ik"), (jointChain + "_fk"), jointChain, w=1, mo=0)  

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add Controls

    # Root

    build_RigIcon ("LollyPop", (limbName + "_root_ctrl"), "Blue", 0.1*scaleMultiply, "X")
    cmds.group(em=1, n=(limbName + "_root_ctrl_offset"))

    cmds.parent ((limbName + "_root_ctrl"), (limbName + "_root_ctrl_offset"))
    cmds.matchTransform((limbName + "_root_ctrl_offset"), rootJoint, pos=1)

    # Add group for the limb

    cmds.group(em=1, n=(limbName + "_grp"))
    cmds.pointConstraint (rootJoint, (limbName + "_grp"), n="tmpPC"); cmds.delete ("tmpPC")

    # IK

    build_RigIcon (ikControlIcon, (limbName + "_IK_ctrl"), iconColour, ikControlScale*scaleMultiply, ikControlOrient)
    cmds.group ((limbName + "_IK_ctrl"), n=(limbName + "_IK_ctrl_offset"))

    anklePivot = cmds.xform (endJoint, q=True, ws=True, piv=True)

    if "leg" in limbType:
        cmds.matchTransform((limbName + "_IK_ctrl_offset"), endJoint, rot=1, pos=1)

        if footOrient == "Floor":
            cmds.parent((limbName + "_IK_ctrl"), w=1)
            cmds.setAttr((limbName + "_IK_ctrl.ty"), 0)
            cmds.xform (limbName + "_IK_ctrl", os=1, ro=(0, 0, 0))
            cmds.parent (limbName + "_IK_ctrl", limbName + "_IK_ctrl_offset")
        else:
            if limbSide == "Right":
                cmds.xform (limbName + "_IK_ctrl", os=1, ro=(90, 90, 0))
            else:
                cmds.xform (limbName + "_IK_ctrl", os=1, ro=(-90, 90, 0))
                                
        if limbSide == "Right":
            cmds.scale (-1, 1, 1, (limbName + "_IK_ctrl"), r=1, ocp=1)

        cmds.makeIdentity ((limbName + "_IK_ctrl"), a=1, t=1, r=1, s=1)
        cmds.xform ((limbName + "_IK_ctrl"), ws=1, piv=(anklePivot[0], anklePivot[1], anklePivot[2]))
    else:
        cmds.matchTransform((limbName + "_IK_ctrl_offset"), endJoint, rot=1, pos=1)

    if quadRear or quadFront:
        cmds.ikHandle (n=(limbName + "_knee_ikHandle"), sol="ikRPsolver", ccv=0, sj=(rootJoint + "_ik"), ee=(jointChainList[2] + "_ik"))
        cmds.ikHandle (n=(limbName + "_hock_ikHandle"), sol="ikSCsolver", ccv=0, sj=(jointChainList[2] + "_ik"), ee=(endJoint + "_ik"))

        if cmds.objExists("root_ctrl"):
            cmds.connectAttr ("root_ctrl.Rig_Systems", (limbName + "_knee_ikHandle.visibility"), f=1)  
            cmds.connectAttr ("root_ctrl.Rig_Systems", (limbName + "_hock_ikHandle.visibility"), f=1) 
                   
        cmds.group((limbName + "_knee_ikHandle"), n=(limbName + "_knee_control"))
        cmds.group((limbName + "_knee_control"), n=(limbName + "_knee_control_offset"))
        
        cmds.xform (((limbName + "_knee_control"), (limbName + "_knee_control_offset")), ws=1, piv=(anklePivot[0], anklePivot[1], anklePivot[2]))
        
        cmds.parent((limbName + "_knee_control_offset"), (limbName + "_hock_ikHandle"), (limbName + "_IK_ctrl"))
        
    else:
        cmds.ikHandle (n=(limbName + "_ikHandle"), sol="ikRPsolver", ccv=0, sj=(rootJoint + "_ik"), ee=(endJoint + "_ik"))
        cmds.parent((limbName + "_ikHandle"), (limbName + "_IK_ctrl"))

        if cmds.objExists("root_ctrl"):
            cmds.connectAttr ("root_ctrl.Rig_Systems", (limbName + "_ikHandle.visibility"), f=1)  
            
    if quadRear:
        cmds.parent((limbName + "_knee_control_offset"), (jointChainList[2] + "_driver"))
        cmds.parent((limbName + "_hock_ikHandle"), (endJoint + "_driver"))
        
        cmds.ikHandle (n=(limbName + "_driver_ikHandle"), sol=solverType, ccv=0, sj=(rootJoint + "_driver"), ee=(endJoint + "_driver"))
                        
        cmds.parent((limbName + "_driver_ikHandle"), (limbName + "_IK_ctrl"))

        if cmds.objExists("root_ctrl"):
            cmds.connectAttr ("root_ctrl.Rig_Systems", (limbName + "_driver_ikHandle.visibility"), f=1)  
    
    cmds.orientConstraint ((limbName + "_IK_ctrl"), (endJoint + "_ik"), w=1, mo=1)

    # FK
    for i in range(len(jointChainList)):
        build_RigIcon ("Circle", (jointChainList[i] + "_FK_ctrl"), "Yellow", 0.15*scaleMultiply, fkControlOrient)
        cmds.group ((jointChainList[i] + "_FK_ctrl"), n=(jointChainList[i] + "_FK_ctrl_offset"))    

        cmds.matchTransform((jointChainList[i] + "_FK_ctrl_offset"), (jointChainList[i] + "_fk"), rot=1, pos=1)

        cmds.parentConstraint ((jointChainList[i] + "_FK_ctrl"), (jointChainList[i] + "_fk"), w=1, mo=0)
        
        if i > 0:
            cmds.parent((jointChainList[i] + "_FK_ctrl_offset"), (jointChainList[i-1] + "_FK_ctrl"))            

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Pole Vector

    pvControlRotate = [0, 0, 0]

    if "xyz" in jntOrient:
        if limbSide == "Right": pvValue = pvValue*-1

        pvMoveAmount[1] = (0.25*pvValue)*scaleMultiply
        pvControlRotate = [90*pvValue, 0, 0]

    elif "yzx" in jntOrient:

        if limbSide == "Right": pvValue = pvValue*-1
        if limbType == "arm" and limbSide == "Right": pvControlRotate = [180, 0, 0]
        if limbType == "leg" and limbSide == "Left": pvControlRotate = [0, 180, 0]            
        if quadRear and limbSide == "Left": pvControlRotate = [0, 180, 0]              
        if quadFront and limbSide == "Right": pvValue = pvValue*-1
    
        pvMoveAmount[2] = (0.25*pvValue)*scaleMultiply

    else:
        if limbSide == "Right": pvValue = pvValue*-1

        pvMoveAmount[0] = (0.25*pvValue)*scaleMultiply
        pvControlRotate = [0, -90*pvValue, 0]

        if limbType == "arm": pvControlRotate = [0, 0, 90*pvValue]
                        
    cmds.spaceLocator (n=(limbName + "_pvStartPoint_loc"))

    cmds.matchTransform((limbName + "_pvStartPoint_loc"), (jointChainList[1] + "_ik"), rot=1, pos=1)
    cmds.move(pvMoveAmount[0], pvMoveAmount[1], pvMoveAmount[2], (limbName + "_pvStartPoint_loc"), r=1, os=1)

    cmds.duplicate ((limbName + "_pvStartPoint_loc"), n=(limbName + "_pvEndPoint_loc"))
    
    cmds.parent ((limbName + "_pvStartPoint_loc"), (rootJoint + "_fk"))
    cmds.parent ((limbName + "_pvEndPoint_loc"), (rootJoint + "_ik"))        

    cmds.shadingNode ("distanceBetween", au=1, n=(limbName + "_pvMove_distnode"))

    cmds.connectAttr ((limbName + "_pvStartPoint_loc.worldMatrix"), (limbName + "_pvMove_distnode.inMatrix1"))
    cmds.connectAttr ((limbName + "_pvEndPoint_loc.worldMatrix"), (limbName + "_pvMove_distnode.inMatrix2"))
    cmds.connectAttr ((limbName + "_pvStartPoint_loc.rotatePivotTranslate"), (limbName + "_pvMove_distnode.point1"))
    cmds.connectAttr ((limbName + "_pvEndPoint_loc.rotatePivotTranslate"), (limbName + "_pvMove_distnode.point2"))

    #
    
    build_RigIcon ("Point", (limbName + "_" + midPoint + "_ctrl"), iconColour, 0.1*scaleMultiply, ikControlOrient)
    cmds.group ((limbName + "_" + midPoint + "_ctrl"), n=(limbName + "_" + midPoint + "_ctrl_offset"))
    cmds.xform ((limbName + "_" + midPoint + "_ctrl_offset"), ws=1, piv=(0, 0, 0))
    
    cmds.rotate (pvControlRotate[0], pvControlRotate[1], pvControlRotate[2], (limbName + "_" + midPoint + "_ctrl"), r=1, os=1, fo=1)

    cmds.matchTransform((limbName + "_" + midPoint + "_ctrl_offset"), (jointChainList[1] + "_ik"), rot=1, pos=1)
    cmds.makeIdentity ((limbName + "_" + midPoint + "_ctrl"), a=1, t=1, r=1, s=1)

    if quadRear:
        cmds.poleVectorConstraint ((limbName + "_" + midPoint + "_ctrl"), (limbName + "_driver_ikHandle"), w=1)
    elif quadFront:
        cmds.poleVectorConstraint ((limbName + "_" + midPoint + "_ctrl"), (limbName + "_knee_ikHandle"), w=1)
    else:
        cmds.poleVectorConstraint ((limbName + "_" + midPoint + "_ctrl"), (limbName + "_ikHandle"), w=1)
 
    cmds.matchTransform((limbName + "_" + midPoint + "_ctrl_offset"), (limbName + "_pvStartPoint_loc"), rot=1, pos=1)

    # Set PV Position
    getPVEndLocation = cmds.xform ((limbName + "_pvEndPoint_loc"), q=True, ws=True, piv=True)
    cmds.xform ((limbName + "_" + midPoint + "_ctrl_offset"), ws=1, t=(getPVEndLocation[0], getPVEndLocation[1], getPVEndLocation[2]))

    getDistance = cmds.getAttr((limbName + "_pvMove_distnode.distance"))

    if "xyz" in jntOrient:
        pvDistAdjust[1] = getDistance*pvValue
    elif "yzx" in jntOrient:
        pvDistAdjust[2] = getDistance*pvValue  
    else:
        pvDistAdjust[0] = getDistance*pvValue  
        
    cmds.move (pvDistAdjust[0], pvDistAdjust[1], pvDistAdjust[2], (limbName + "_" + midPoint + "_ctrl_offset"), r=1, os=1, wd=1)

    # Make limb follow root

    cmds.parentConstraint ((limbName + "_root_ctrl"), (limbName + "_grp"), w=1, mo=1) 
    cmds.parentConstraint ((limbName + "_root_ctrl"), (rootJoint + "_FK_ctrl_offset"), w=1, mo=1) 

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Hock Control

    if quadFront or quadRear:
        build_RigIcon ("Cube", (limbName + "_hock_ctrl"), iconColour, 0.1*scaleMultiply, ikControlOrient)
        cmds.group ((limbName + "_hock_ctrl"), n=(limbName + "_hock_ctrl_offset"))
        
        cmds.parent((limbName + "_hock_ctrl_offset"), (limbName + "_root_ctrl"))

        cmds.matchTransform((limbName + "_hock_ctrl_offset"), jointChainList[2], pos=1)

        cmds.shadingNode ("multiplyDivide", au=1, n=(limbName + "_hock_multi"))
        
        cmds.connectAttr ((limbName + "_hock_ctrl.translate"), (limbName + "_hock_multi.input1"), f=1)        
        cmds.connectAttr ((limbName + "_hock_multi.outputZ"), (limbName + "_knee_control.rotateX"), f=1)
        cmds.connectAttr ((limbName + "_hock_multi.outputX"), (limbName + "_knee_control.rotateZ"), f=1) 

        cmds.setAttr((limbName + "_hock_multi.input2X"), -2.5)
        cmds.setAttr((limbName + "_hock_multi.input2Z"), 2.5)

        if quadFront:
            cmds.parentConstraint ((limbName + "_IK_ctrl"), (limbName + "_hock_ctrl_offset"), w=1, sr=("x", "y", "z"), mo=1) 
        else:
            cmds.pointConstraint ((limbName + "_IK_ctrl"), (limbName + "_hock_ctrl_offset"), w=1, mo=1)             
            
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add New Attributes to the IK Control

    cmds.addAttr ((limbName + "_IK_ctrl"), ln="FK_IK_Switch", at="double", min=0, max=1, dv=0)

    cmds.addAttr ((limbName + "_IK_ctrl"), ln="Stretchiness", at="double", min=0, max=1, dv=0)
    cmds.setAttr ((limbName + "_IK_ctrl.Stretchiness"), e=1, keyable=1)

    cmds.addAttr ((limbName + "_IK_ctrl"), ln="StretchType", at="enum", en="Full:Stretch Only:Squash Only:")
    cmds.setAttr ((limbName + "_IK_ctrl.StretchType"), e=1, keyable=1)
   
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add IK FK Blend Visibility

    cmds.shadingNode ("reverse", au=1, n=(limbName + "_fkik_reverse"))

    cmds.connectAttr ((limbName + "_IK_ctrl.FK_IK_Switch"), (limbName + "_fkik_reverse.inputX"), f=1)       
    cmds.connectAttr ((limbName + "_IK_ctrl.FK_IK_Switch"), (limbName + "_IK_ctrl_offset.visibility"), f=1)         
    cmds.connectAttr ((limbName + "_fkik_reverse.outputX"), (rootJoint + "_FK_ctrl_offset.visibility"), f=1)

    cmds.connectAttr ((limbName + "_IK_ctrl.FK_IK_Switch"), (limbName + "_" + midPoint + "_ctrl_offset.visibility"), f=1) 

    if quadFront or quadRear:
        cmds.connectAttr ((limbName + "_IK_ctrl.FK_IK_Switch"), (limbName + "_hock_ctrl_offset.visibility"), f=1) 
        
        
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add IK FK Switcher

    build_RigIcon ("Slider", (limbName + "_ctrl"), "Blue", 0.1*scaleMultiply, "Y")
    build_RigIcon ("FKLabel", (limbName + "_ik_label"), "Blue", 0.05*scaleMultiply, "Y")
    build_RigIcon ("IKLabel", (limbName + "_fk_label"), "Blue", 0.05*scaleMultiply, "Y")

    cmds.parent ((limbName + "_ik_label"), (limbName + "_fk_label"), (limbName + "_ctrl"))   
    cmds.pointConstraint (endJoint, (limbName + "_ctrl"), w=1, n="tmppc"); cmds.delete ("tmppc")

    cmds.setAttr ((limbName + "_fk_label.rotateY"), 90)
    cmds.setAttr ((limbName + "_ik_label.rotateY"), 90)

    cmds.select(cl=1)

    if limbType == "arm": pvValue = 1
    if limbSide == "Right": pvValue = -1
    if limbSide == "Left" and quadFront: pvValue = 1
            
    cmds.move ((0.1*scaleMultiply)*pvValue, 0.1*scaleMultiply, 0, (limbName + "_ctrl"), wd=1, r=1, os=1)

    cmds.makeIdentity ((limbName + "_ctrl"), a=1, t=1, r=1, s=1)

    cmds.addAttr ((limbName + "_ctrl"), ln="FK_IK_Switch", at="double", min=0, max=1, dv=0)
    cmds.setAttr ((limbName + "_ctrl.FK_IK_Switch"), e=1, keyable=1)

    cmds.connectAttr ((limbName + "_ctrl.FK_IK_Switch"), (limbName + "_IK_ctrl.FK_IK_Switch"), f=1)   
    cmds.connectAttr ((limbName + "_ctrl.FK_IK_Switch"), (limbName + "_fk_label.visibility"), f=1)         
    cmds.connectAttr ((limbName + "_fkik_reverse.outputX"), (limbName + "_ik_label.visibility"), f=1)

    cmds.setAttr ((limbName + "_ctrl.FK_IK_Switch"), 1)

    cmds.addAttr ((limbName + "_ctrl"), ln="Volume_Offset", at="double", dv=-0.5)
    cmds.setAttr ((limbName + "_ctrl.Volume_Offset"), e=1, keyable=1)

    cmds.pointConstraint (endJoint, (limbName + "_ctrl"), w=1, mo=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Connect Constraints

    for jointChain in jointChainList:
        getConstraint = cmds.listConnections(jointChain, type="parentConstraint")[0]
        getWeights = cmds.parentConstraint (getConstraint, q=1, wal=1)

        cmds.connectAttr ((limbName + "_ctrl.FK_IK_Switch"), (getConstraint + "." + getWeights[0]), f=1)  
        cmds.connectAttr ((limbName + "_fkik_reverse.outputX"), (getConstraint + "." + getWeights[1]), f=1) 

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Add PV Lines

    cmds.curve (d=1, p=([0,0,0], [0,0,1]), n=(limbName + "_slider_line"))

    cmds.cluster ((limbName + "_slider_line.cv[0]"), n=(limbName + "_slider_line_Start"))
    cmds.cluster ((limbName + "_slider_line.cv[1]"), n=(limbName + "_slider_line_end"))
                  
    cmds.parentConstraint (endJoint, (limbName + "_slider_line_StartHandle"), w=1, n="tempClusterPCA")                              
    cmds.parentConstraint ((limbName + "_ctrl"), (limbName + "_slider_line_endHandle"), w=1, n="tempClusterPCB") 
    cmds.delete ("tempClusterPCA", "tempClusterPCB")

    cmds.parent ((limbName + "_slider_line_StartHandle"), endJoint)
    cmds.parent ((limbName + "_slider_line_endHandle"), (limbName + "_ctrl"))

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Make Stretchy

    if doStretch:
        cmds.spaceLocator (n=(limbName + "_stretchEndPos_loc"))
        
        cmds.matchTransform((limbName + "_stretchEndPos_loc"), endJoint, rot=1, pos=1)
        cmds.parent((limbName + "_stretchEndPos_loc"), (limbName + "_IK_ctrl"))

        grabDistNode = add_distanceNodes(limbName, (rootJoint + "_stretch"))

        cmds.setAttr((limbName + "_condition.operation"), 2)

        for i in range(len(jointChainList)-1):
            if quadRear:
                cmds.connectAttr ((limbName + "_condition.outColorR"), (jointChainList[i] + "_driver.scale" + primAxis), f=1)
            else:
                cmds.connectAttr ((limbName + "_condition.outColorR"), (jointChainList[i] + "_ik.scale" + primAxis), f=1)

        # Add the ability to turn the stretchiness off
        cmds.shadingNode ("blendColors", au=1, n=(limbName + "_blendColors"))
        cmds.setAttr ((limbName + "_blendColors.color2"), 1, 0, 0, type="double3")

        cmds.connectAttr ((limbName + "_scaleFactor.outputX"), (limbName + "_blendColors.color1R"), f=1)
        cmds.connectAttr ((limbName + "_blendColors.outputR"), (limbName + "_condition.colorIfTrueR"), f=1)

        cmds.setAttr ((limbName + "_blendColors.blender"), 1)

        # Wire Up The Attributes
        cmds.setAttr ((limbName + "_IK_ctrl.Stretchiness"), 1)
        cmds.connectAttr ((limbName + "_IK_ctrl.Stretchiness"), (limbName + "_blendColors.blender"), f=1)

        cmds.setAttr ((limbName + "_IK_ctrl.StretchType"), 0)
        cmds.setAttr ((limbName + "_condition.operation"), 1) # Not Equal

        cmds.setDrivenKeyframe ((limbName + "_condition.operation"), cd=(limbName + "_IK_ctrl.StretchType"))

        cmds.setAttr ((limbName + "_IK_ctrl.StretchType"), 1)
        cmds.setAttr ((limbName + "_condition.operation"), 3) # Greater or Equal

        cmds.setDrivenKeyframe ((limbName + "_condition.operation"), cd=(limbName + "_IK_ctrl.StretchType"))

        cmds.setAttr ((limbName + "_IK_ctrl.StretchType"), 2)
        cmds.setAttr ((limbName + "_condition.operation"), 5) # Less or Equal

        cmds.setDrivenKeyframe ((limbName + "_condition.operation"), cd=(limbName + "_IK_ctrl.StretchType"))

        cmds.setAttr ((limbName + "_IK_ctrl.StretchType"), 1)

    #-------------------------------------------------------------------------------------------------------------------------------------        
    # Add Volume Preservation

    if doVPres:
        # Create the main multiply divide node which will calculate the volume
        cmds.shadingNode( "multiplyDivide", au=1, n=limbName + "_volume")    

        # Set the operation to Power
        cmds.setAttr(limbName + "_volume.operation", 3)    
        cmds.setAttr(limbName + "_volume.input2X", -1)
            
        # Connect the main stretch value to the volume node
        cmds.connectAttr((limbName + "_condition.outColorR"), limbName + "_volume.input1X", f=1 ) 
        
        # Connect to the main volume attribute
        cmds.connectAttr( (limbName + "_ctrl.Volume_Offset"), (limbName + "_volume.input2X"), f=1 )   

        for i in range(len(jointChainList)):
            
            axesList = ("X", "Y", "Z")
            
            for axes in axesList:
                if axes != primAxis:
                    cmds.connectAttr (limbName + "_volume.outputX", jointChainList[i] + ".scale" + axes, f=1)

    #---------------------------------------------------------------------------------    
    # Add Roll Joints & Systems  

    if doRoll:
        
        # Setup variables
        twistControlOrient = jntOrient[0].capitalize()

        if "yzx" in jntOrient:
            twistControlRotate = [0, 0, 0]
        else:
            twistControlRotate = [0, 90, 0]
                    
        rollMoveAmount = [pvMoveAmount[0]*-0.25, pvMoveAmount[1]*-0.25, pvMoveAmount[2]*-0.25]
        
        if limbType == "arm" or quadFront:
            rollMoveAmount = [pvMoveAmount[0]*0.25, pvMoveAmount[1]*0.25, pvMoveAmount[2]*0.25]  

        # Create the main roll and follow joints
        cmds.duplicate(jointChainList[0], n=jointChainList[0] + "_follow", po=1)
        cmds.duplicate(jointChainList[0], n=jointChainList[0] + "_follow_tip", po=1)

        cmds.pointConstraint (jointChainList[0], jointChainList[1] , (jointChainList[0] + "_follow_tip"), w=1, n="tmpPC")                              
        cmds.delete ("tmpPC")

        cmds.parent((jointChainList[0] + "_follow_tip"), (jointChainList[0] + "_follow"))

        #---------------------------------------------------------------------------------    
        # Upper arm & leg systems

        # Now move them out
        cmds.move( rollMoveAmount[0], rollMoveAmount[1], rollMoveAmount[2], (jointChainList[0] + "_follow"), r=1, os=1, wd=1 )
            
        # Create the aim locator which the femur roll joint will always follow
        cmds.spaceLocator( n=(jointChainList[0] + "_roll_aim") )

        # Move it to the root joint and parent it to the follow joint so it moves with it
        cmds.matchTransform((jointChainList[0] + "_roll_aim"), (jointChainList[0] + "_follow") )   

        # Move the locator out too
        cmds.move( rollMoveAmount[0], rollMoveAmount[1], rollMoveAmount[2], (jointChainList[0] + "_roll_aim"), r=1, os=1, wd=1 )
        
        # Upper Aim
        if limbSide == "Right": pvValue = -1

        # Setup upper aim constraints
        if "xyz" in jntOrient:
            aimV = (1*pvValue, 0, 0)
            upV = (0, -1*pvValue, 0) 
        elif "yzx" in jntOrient:
            aimV = (0, 1*pvValue, 0)
            upV = (0, 0, -1*pvValue)         
        else:
            aimV = (0, 0, 1*pvValue)
            upV = (-1*pvValue, 0, 0)   
               
        cmds.aimConstraint( jointChainList[1], jointChainList[0] + "_twist", w=1, aim=aimV, u=upV, wut="object", wuo=jointChainList[0] + "_roll_aim", mo=1 ) 

        # Add an ik handle so the follow joints, follow the leg
        cmds.ikHandle( n=(limbName + "_follow_ikHandle"), sol="ikRPsolver", sj=(jointChainList[0] + "_follow"), ee=(jointChainList[0] + "_follow_tip") )

        # Now move it to the fibula and parent it too
        cmds.parent( (limbName + "_follow_ikHandle"), jointChainList[1])    
        cmds.matchTransform((limbName + "_follow_ikHandle"), jointChainList[1]) 

        # Also reset the pole vector to stop the limb twisting
        cmds.setAttr ((limbName + "_follow_ikHandle.poleVector"), 0, 0, 0, type="double3")

        # Create icon
        build_RigIcon ("Slider", (jointChainList[0] + "_twist_ctrl"), iconColour, 0.1*scaleMultiply, twistControlOrient)
        cmds.rotate (twistControlRotate[0], twistControlRotate[1], twistControlRotate[2], jointChainList[0] + "_twist_ctrl", r=1, os=1, fo=1)

        cmds.group (jointChainList[0] + "_twist_ctrl", n=jointChainList[0] + "_twist_ctrl_offset")

        cmds.matchTransform(jointChainList[0] + "_twist_ctrl_offset", jointChainList[0] + "_roll_aim")
        cmds.makeIdentity (jointChainList[0] + "_twist_ctrl", a=1, r=1)

        cmds.parentConstraint (jointChainList[0] + "_follow", jointChainList[0] + "_twist_ctrl_offset", w=1, mo=1)
        cmds.parent (jointChainList[0] + "_roll_aim", jointChainList[0] + "_twist_ctrl")

        cmds.connectAttr("root_ctrl.Twist_Controls", (jointChainList[0] + "_twist_ctrl" + ".visibility"), f=1 )
        cmds.connectAttr("root_ctrl.Rig_Systems", (jointChainList[0] + "_roll_aim" + ".visibility"), f=1 )

        #---------------------------------------------------------------------------------    
        # Lower arm & leg systems  
           
        # Create the aim locator which the metacarpus roll joint will always follow
        cmds.spaceLocator( n=(endJoint + "_roll_aim") )    
        
        # Move it to the ankle joint and parent it to ankle joint too
        cmds.matchTransform(endJoint + "_roll_aim", endJoint)    
        cmds.parent(endJoint + "_roll_aim", endJoint)    
        
        #Also move it out to the side
        cmds.move( rollMoveAmount[0], rollMoveAmount[1], rollMoveAmount[2], (endJoint + "_roll_aim"), r=1, os=1, wd=1 )

        # Setup upper aim constraints
        if "xyz" in jntOrient:
            aimV = (-1*pvValue, 0, 0)
        elif "yzx" in jntOrient:
            aimV = (0, -1*pvValue, 0)
        else:
            aimV = (0, 0, -1*pvValue)

        # Make the ankle joint aim at the metatarsus joint, but also keep looking at the aim locator for reference
        cmds.aimConstraint( jointChainList[-2], endJoint + "_twist", w=1, aim=aimV, u=upV, wut="object", wuo=(endJoint + "_roll_aim"), mo=1 ) 
         
        # Create icon      
        build_RigIcon ("Slider", endJoint + "_twist_ctrl", iconColour, 0.1*scaleMultiply, twistControlOrient)
        cmds.rotate (twistControlRotate[0], twistControlRotate[1], twistControlRotate[2], endJoint + "_twist_ctrl", r=1, os=1, fo=1)
        
        cmds.group (endJoint + "_twist_ctrl", n=endJoint + "_twist_ctrl_offset")
        cmds.matchTransform(endJoint + "_twist_ctrl_offset", endJoint + "_roll_aim")
        
        cmds.parentConstraint (endJoint, endJoint + "_twist_ctrl_offset", w=1, mo=1)
        cmds.parent (endJoint + "_roll_aim", endJoint + "_twist_ctrl")

        cmds.connectAttr (endJoint + ".translate" + primAxis, endJoint + "_twist.translate" + primAxis, f=1)
       
        cmds.select(cl=1)

        cmds.connectAttr("root_ctrl.Twist_Controls", (endJoint + "_twist_ctrl" + ".visibility"), f=1 )
        cmds.connectAttr("root_ctrl.Rig_Systems", (endJoint + "_roll_aim" + ".visibility"), f=1 )
        
    #-------------------------------------------------------------------------------------------------------------------------------------        
    # Cleanup

    # Hierachy
    cmds.parent((rootJoint + "_ik"), (rootJoint + "_fk"), (rootJoint + "_stretch"), (limbName + "_grp"))
    cmds.parent((limbName + "_grp"), "rig_systems")
    cmds.parent((limbName + "_slider_line"), "connection_lines")

    cmds.parent((limbName + "_ctrl"), (limbName + "_root_ctrl_offset"), (limbName + "_" + midPoint + "_ctrl_offset"), "root_ctrl")
    cmds.parent((rootJoint + "_FK_ctrl_offset"), (limbName + "_IK_ctrl_offset"), "root_ctrl")

    if quadRear:
        cmds.parent((rootJoint + "_driver"), (limbName + "_grp"))

    if quadFront or quadRear:
        lockdownAttr((limbName + "_hock_ctrl"), 0, 1, 1, 1, 0)  

    if doRoll:
        cmds.parent (jointChainList[0] + "_twist_ctrl_offset", endJoint + "_twist_ctrl_offset", "root_ctrl")
        cmds.parent( (jointChainList[0] + "_follow"), (limbName + "_grp") ) 
          
    # Visibility
    if doStretch:
        cmds.setAttr((limbName + "_stretchEndPos_loc.visibility"), 0)
        lockdownAttr((limbName + "_stretchEndPos_loc"), 1, 1, 1, 1, 1)
        
    cmds.setAttr((limbName + "_slider_line_StartHandle.visibility"), 0)
    cmds.setAttr((limbName + "_slider_line_endHandle.visibility"), 0)
        
    # Remove
    cmds.delete((limbName + "_pvStartPoint_loc"), (limbName + "_pvEndPoint_loc"))

    # Lock
    for jointChain in jointChainList:
        lockdownAttr((jointChain + "_FK_ctrl"), 0, 0, 1, 1, 0)

    lockdownAttr((limbName + "_slider_line"), 1, 1, 1, 1, 1)
    lockdownAttr((limbName + "_ik_label"), 1, 1, 1, 1, 1)
    lockdownAttr((limbName + "_fk_label"), 1, 1, 1, 1, 1)

    lockdownAttr((limbName + "_slider_line_StartHandle"), 1, 1, 1, 1, 1)
    lockdownAttr((limbName + "_slider_line_endHandle"), 1, 1, 1, 1, 1)

    lockdownAttr((limbName + "_ctrl"), 1, 1, 1, 1, 0)
    lockdownAttr((limbName + "_IK_ctrl"), 0, 0, 1, 1, 0)
    lockdownAttr((limbName + "_root_ctrl"), 0, 0, 1, 1, 0)

    lockdownAttr("scene_direction", 1, 1, 1, 1, 1)
    lockdownAttr("root_joint_ctrl", 1, 1, 1, 1, 1)
    
    offsetGroupList = cmds.ls("*_offset")

    for offsetGroup in offsetGroupList:
        lockdownAttr(offsetGroup, 1, 1, 1, 1, 0)
        
    cmds.select(cl=1) 
               