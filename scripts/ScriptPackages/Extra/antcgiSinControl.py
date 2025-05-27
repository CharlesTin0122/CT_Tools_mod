#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - Joint Arc Tool
#
# Thanks for your support!
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
# import antcgiSinControl
# antcgiSinControl.antcgiSinControlUI() 
#
# Check out the video to see how to use it - https://www.youtube.com/watch?v=hnzfeDQY0oM
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds

#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiSinControlUI():
    # Window exists?
    if cmds.window ("sinControlUI", ex=1): cmds.deleteUI ("sinControlUI")

    # Create Window
    window = cmds.window ("sinControlUI", t="Joint Arc Tool v1.5", w=275, h=350, mnb=0, mxb=0, s=0)

    # Create a main layout
    mainLayout = cmds.formLayout(numberOfDivisions=100)

    # Labels
    mainText = cmds.text("mainText", label="Joint Arc Tool by @antCGi", align="left", h=20)
    thanksText = cmds.text("thanksText", label="Thanks for your support!", align="left", h=20)
    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)
    helpText = cmds.text(l='<a href="https://www.youtube.com/watch?v=hnzfeDQY0oM/?q=HTML+link">[?]</a>', hl=True)
        
    primLabel = cmds.text("primLabel", label="Primary Axis", align="left", h=20)
    secLabel = cmds.text("secLabel", label="Secondary Axis", align="left", h=20)
    upLabel = cmds.text("upLabel", label="Up Axis", align="left", h=20)

    input01Label = cmds.text("input01Label", label="Horizontal", align="left", h=20)
    input02Label = cmds.text("input02Label", label="Vertical", align="left", h=20)
    input03Label = cmds.text("input03Label", label="Movement", align="left", h=20)
             
    # Buttons
    button01 = cmds.button(w=150, h=25, l="[GO]", p=mainLayout, c=antcgiSinControl)

    # Separators
    separator01 = cmds.separator(h=5, p=mainLayout)
    separator02 = cmds.separator(h=5, p=mainLayout)
    separator03 = cmds.separator(h=5, p=mainLayout)
        
    # Menu
    primAxis = cmds.optionMenu("primAxis", h=20, ann="Which axis is pointing down the joint?")

    cmds.menuItem (l="X")
    cmds.menuItem (l="Y")
    cmds.menuItem (l="Z")

    # Menu
    secAxis = cmds.optionMenu("secAxis", h=20, ann="Which axis is pointing forwards?")

    cmds.menuItem (l="X")
    cmds.menuItem (l="Y")
    cmds.menuItem (l="Z")

    # Menu
    upAxis = cmds.optionMenu("upAxis", h=20, ann="Which axis is pointing up?")

    cmds.menuItem (l="X")
    cmds.menuItem (l="Y")
    cmds.menuItem (l="Z")
 
    # Checkbox
    invertYChk = cmds.checkBox("invertYChk", l="Invert Y-Axis", h=20, ann="Invert the Y Axis?", v=0)    

    # Inputs
    input01Horizontal = cmds.floatField("input01Horizontal", h=20, ann="Horizontal gradient movement.", v=0) 
    input02Vertical = cmds.floatField("input02Vertical", h=20, ann="Vertical gradient movement.", v=-0) 
    input03Movement = cmds.floatField("input03Movement", h=20, ann="Overall movement.", v=10) 
                        
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(mainText, 'top', 5), (helpText, 'top', 10),

                                (separator01, 'left', 5), (separator01, 'right', 5),    
 
                                (primLabel, 'left', 25),  
                                (secLabel, 'left', 25),  
                                (upLabel, 'left', 25),  
                                                                                                                                                    
                                (primAxis, 'right', 25),  
                                (secAxis, 'right', 25),
                                (upAxis, 'right', 25),
                                                                                                                                
                                (separator02, 'left', 5), (separator02, 'right', 5),
                                
                                (input01Label, 'left', 25), (input01Horizontal, 'right', 25),                                   
                                (input02Label, 'left', 25), (input02Vertical, 'right', 25),                                   
                                (input03Label, 'left', 25), (input03Movement, 'right', 25),

                                (separator03, 'left', 5), (separator03, 'right', 5),
                                                                                           
                                (button01, 'bottom', 5), (button01, 'left', 5), (button01, 'right', 5),
                                ],
                                
                    attachControl=[(helpText, 'left', 5, mainText),
                        
                                   (thanksText, 'top', 5, mainText),
                                   (separator01, 'top', 5, thanksText),                           
                                                       
                                   (primLabel, 'top', 5, separator01),                        
                                   (secLabel, 'top', 5, primLabel),  
                                   (upLabel, 'top', 5, secLabel),  
                                                                                                                                 
                                   (primAxis, 'top', 5, separator01),
                                   (secAxis, 'top', 5, primAxis),
                                   (upAxis, 'top', 5, secAxis),
                                   (invertYChk, 'top', 5, upAxis),                                   
                                   (separator02, 'top', 5, invertYChk),
                                   
                                   (input01Label, 'top', 5, separator02),
                                   (input02Label, 'top', 5, input01Label),
                                   (input03Label, 'top', 5, input02Label),
                                                                                                           
                                   (input01Horizontal, 'top', 5, separator02),  
                                   (input02Vertical, 'top', 5, input01Horizontal),
                                   (input03Movement, 'top', 5, input02Vertical),
                                     
                                   (separator03, 'top', 5, input03Movement),                                                                                                                                                                               
                                   (linkText, 'top', 5, separator03),
                                   ],
                                   
                    attachPosition=[(mainText, 'left', 0, 24),
                                    (thanksText, 'left', 0, 25),
                                    (primAxis, 'left', 0, 50),
                                    (secAxis, 'left', 0, 50),
                                    (upAxis, 'left', 0, 50),
                                    (invertYChk, 'left', 0, 35),
                                    
                                    (input01Horizontal, 'left', 0, 50),                                    
                                    (input02Vertical, 'left', 0, 50),   
                                    (input03Movement, 'left', 0, 50),   
                                                                                                            
                                    (linkText, 'left', 0, 30),
                                   ]

                    )
       
    # Show Window
    cmds.showWindow (window)
    
    # Update Boxes
    cmds.optionMenu("primAxis", e=1, v="Z")
    cmds.optionMenu("secAxis", e=1, v="X")    
    cmds.optionMenu("upAxis", e=1, v="Y")  
        
#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiSinControl(*args):

    selectionList = cmds.ls(sl=1)

    if not selectionList:
        cmds.error("Select the control and the tip joint.")

    control = selectionList[0]
    attrControl = selectionList[0]
    endJoint = selectionList[1]
    rootJoint = cmds.listRelatives(endJoint, p=1, type="joint")[0]

    primAxis = cmds.optionMenu("primAxis", q=1, v=1)
    secAxis = cmds.optionMenu("secAxis", q=1, v=1)
    upAxis = cmds.optionMenu("upAxis", q=1, v=1)

    invertY = cmds.checkBox("invertYChk", q=1, v=1)

    horizontalValue = cmds.floatField("input01Horizontal", q=1, v=1)
    verticalValue = cmds.floatField("input02Vertical", q=1, v=1)
    movementValue = cmds.floatField("input03Movement", q=1, v=1)
        
    # Create Locator
    
    cmds.spaceLocator(n=(control + "_loc"))
    cmds.group ((control + "_loc"), n=(control + "_loc_offset"))

    if cmds.objExists("head_ctrl"):
        if ("lower" in attrControl):
            cmds.parent((control + "_loc_offset"), "jaw_ctrl")
        else:
            cmds.parent((control + "_loc_offset"), "head_ctrl")

    cmds.pointConstraint(endJoint, (control + "_loc"), mo=0, n="tmpPC")
    cmds.delete("tmpPC")
 
    cmds.makeIdentity ((control + "_loc"), a=1, t=1, r=0, s=1)

    cmds.setAttr((control + "_loc.scale"), 0.01, 0.01, 0.01)

    control = (control + "_loc")

    # Add main rotation control to the root joint
    # We first add the rotation so the joint follows the control

    cmds.shadingNode ("multiplyDivide", au=1, n=(control + "_orient_multi"))

    cmds.connectAttr ((control + ".translate"), (control + "_orient_multi.input1"))
    
    cmds.connectAttr ((control + "_orient_multi.output" + upAxis), (rootJoint + ".rotate" + secAxis))
    
    cmds.connectAttr ((control + "_orient_multi.outputX"), (rootJoint + ".rotate" + upAxis))

    cmds.setAttr((control + "_orient_multi.input2X"), 550)
    cmds.setAttr((control + "_orient_multi.input2Y"), 550)

    # Create the curve
    # We need to move the z translation in and out to create the curve

    # initial multiply divide node to get movement

    cmds.shadingNode ("multiplyDivide", au=1, n=(endJoint + "_trans_multi"))

    cmds.connectAttr ((control + ".translateX"), (endJoint + "_trans_multi.input1" + secAxis))
    cmds.connectAttr ((control + ".translateX"), (endJoint + "_trans_multi.input2" + secAxis))

    cmds.connectAttr ((control + ".translateY"), (endJoint + "_trans_multi.input1" + upAxis))
    cmds.connectAttr ((control + ".translateY"), (endJoint + "_trans_multi.input2" + upAxis))

    # Need to add a plus minus average for the offset

    cmds.shadingNode ("plusMinusAverage", au=1, n=(endJoint + "_offset_pma"))

    cmds.connectAttr ((endJoint + "_trans_multi.output" + secAxis), (endJoint + "_offset_pma.input1D[0]"))
    cmds.connectAttr ((endJoint + "_trans_multi.output" + upAxis), (endJoint + "_offset_pma.input1D[1]"))
    cmds.connectAttr ((control + ".translateZ"), (endJoint + "_offset_pma.input1D[2]"))
        
    cmds.setAttr((endJoint + "_offset_pma.input1D[3]"), cmds.getAttr((endJoint + ".translate" + primAxis)))

    # Invert the value

    cmds.shadingNode ("multiplyDivide", au=1, n=(endJoint + "_invert_reverse"))

    cmds.connectAttr ((endJoint + "_offset_pma.output1D"), (endJoint + "_invert_reverse.input1" + secAxis))
    cmds.setAttr((endJoint + "_invert_reverse.input2" + secAxis), -1)

    cmds.setAttr((endJoint + "_offset_pma.operation"), 2)

    # Add the ability to adjust the gradient

    cmds.shadingNode ("multiplyDivide", au=1, n=(endJoint + "_gradient_multi"))

    cmds.connectAttr ((control + ".translateX"), (endJoint + "_gradient_multi.input1" + secAxis))
    cmds.connectAttr ((control + ".translateY"), (endJoint + "_gradient_multi.input1" + upAxis))
    
    cmds.connectAttr ((endJoint + "_gradient_multi.output" + secAxis), (endJoint + "_trans_multi.input2" + secAxis), f=1)
    cmds.connectAttr ((endJoint + "_gradient_multi.output" + upAxis), (endJoint + "_trans_multi.input2" + upAxis), f=1)

    # Add controls

    cmds.addAttr (attrControl, ln="GRADIENT", at="enum", en="----------")
    cmds.setAttr ((attrControl + ".GRADIENT"), e=1, k=0, cb=1)

    cmds.addAttr (attrControl, ln="Horizontal", at="double", dv=horizontalValue)
    cmds.addAttr (attrControl, ln="Vertical", at="double", dv=verticalValue)
    
    cmds.addAttr (attrControl, ln="TIP", at="enum", en="----------")
    cmds.setAttr ((attrControl + ".TIP"), e=1, k=0, cb=1)   
    
    cmds.addAttr (attrControl, ln="Offset", at="double")
    cmds.addAttr (attrControl, ln="Movement", at="double", dv=movementValue)

    cmds.setAttr ((attrControl + ".Horizontal"), e=1, keyable=1)
    cmds.setAttr ((attrControl + ".Vertical"), e=1, keyable=1)
    cmds.setAttr ((attrControl + ".Movement"), e=1, keyable=1)
    cmds.setAttr ((attrControl + ".Offset"), e=1, keyable=1)

    cmds.connectAttr ((attrControl + ".Horizontal"), (endJoint + "_gradient_multi.input2" + secAxis))
    cmds.connectAttr ((attrControl + ".Vertical"), (endJoint + "_gradient_multi.input2" + upAxis))
    
    cmds.connectAttr ((attrControl + ".Offset"), (endJoint + "_offset_pma.input1D[3]"))

    cmds.connectAttr ((attrControl + ".Movement"), (control + "_orient_multi.input2" + secAxis))

    cmds.setAttr((attrControl + ".Offset"), cmds.getAttr((endJoint + ".translate" + primAxis)))

    # Add Y flip
    if invertY:
        cmds.shadingNode ("reverse", au=1, n=(endJoint + "_orient_reverse"))

        cmds.connectAttr ((attrControl + ".Movement"), (endJoint + "_orient_reverse.input" + secAxis))
        cmds.connectAttr ((endJoint + "_orient_reverse.output" + secAxis), (control + "_orient_multi.input2" + upAxis))

    cmds.connectAttr ((endJoint + "_invert_reverse.output" + secAxis), (endJoint + ".translate" + primAxis))
        
    # Connect control to locator
    cmds.pointConstraint(attrControl, control, mo=1)
    
    cmds.select(cl=1)