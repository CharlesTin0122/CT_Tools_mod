#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - Blendshape Rigging Tool
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
# import antcgiConnectBS
# antcgiConnectBS.antcgiConnectBS_UI() 
#
# Check out the video to see how to use it - https://www.youtube.com/watch?v=QhkT_U5S9x8
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
from functools import partial

def updateBSAttr(*args):

    cmds.optionMenu("bsAttr_Y", e=1, dai=1)
    cmds.optionMenu("bsAttr_X", e=1, dai=1)
    cmds.optionMenu("bsAttr_Z", e=1, dai=1)
        
    bsNodeName = cmds.optionMenu("bsNode", q=1, v=1)

    if bsNodeName != "None":
        bsAttributeList = cmds.listAttr ((bsNodeName + ".w"), m=1)

        for bsAttribute in bsAttributeList:
            cmds.menuItem(p="bsAttr_Y", l=bsAttribute)
            cmds.menuItem(p="bsAttr_X", l=bsAttribute)
            cmds.menuItem(p="bsAttr_Z", l=bsAttribute)
    else:
        cmds.menuItem(p="bsAttr_Y", l="None")
        cmds.menuItem(p="bsAttr_X", l="None")
        cmds.menuItem(p="bsAttr_Z", l="None")

                    
#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiConnectBS_UI():
    # Window exists?
    if cmds.window ("BSRigTool", ex=1): cmds.deleteUI ("BSRigTool")

    # Create Window
    window = cmds.window ("BSRigTool", t="Blendshape Rigging Tool v1.5", w=325, h=310, mnb=0, mxb=0, s=0)

    # Create a main layout
    mainLayout = cmds.formLayout(numberOfDivisions=100)

    # Labels
    mainText = cmds.text("mainText", label="Blendshape Rigging Tool by @antCGi", align="left", h=20)
    thanksText = cmds.text("thanksText", label="Thanks for your support!", align="left", h=20)
    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)
    helpText = cmds.text(l='<a href="https://www.youtube.com/watch?v=QhkT_U5S9x8/?q=HTML+link">[?]</a>', hl=True)
        
    bsNodeLabel = cmds.text("limbLabel", label="BlendShape Node", align="left", h=20)
    bsYLabel = cmds.text("bsYLabel", label="Y Driven BlendShape", align="left", h=20)
    bsXLabel = cmds.text("bsXLabel", label="X Driven BlendShape", align="left", h=20)
    bsZLabel = cmds.text("bsZLabel", label="Z Driven BlendShape", align="left", h=20)
        
    connectXBox = cmds.checkBox("connectXBox", l="Connect X", align="left", h=20, v=1)
    connectYBox = cmds.checkBox("connectYBox", l="Connect Y", align="left", h=20, v=1)
    connectZBox = cmds.checkBox("connectZBox", l="Connect Z", align="left", h=20, v=1)
         
    multiplierLabel = cmds.text("multiplierLabel", label="Scale Multiplier", align="left", h=20)

    # Input
    multiplierInput = cmds.floatField("multiplierInput", h=20, ann="Adjust control size.", v=100)      
    
    # Buttons
    button01 = cmds.button(w=150, h=25, l="[GO]", p=mainLayout, c=antcgiConnectBS)

    # Separators
    separator01 = cmds.separator(h=5, p=mainLayout)
    separator02 = cmds.separator(h=5, p=mainLayout)
    separator03 = cmds.separator(h=5, p=mainLayout)
        
    # Menu
    bsNode = cmds.optionMenu("bsNode", h=20, ann="Primary Blend Shape Node?", cc=updateBSAttr)

    blendShapeNodeList = cmds.ls(type="blendShape")

    if blendShapeNodeList:
        for blendShapeNode in blendShapeNodeList:
            cmds.menuItem (l=blendShapeNode)
    else:
        cmds.menuItem (l="None")        

    # Menu
    bsAttr_Y = cmds.optionMenu("bsAttr_Y", h=20, ann="Which shape is driven by the Y axis?")
    bsAttr_X = cmds.optionMenu("bsAttr_X", h=20, ann="Which shape is driven by the X axis?")
    bsAttr_Z = cmds.optionMenu("bsAttr_Z", h=20, ann="Which shape is driven by the Z axis?")

    # cmds.menuItem (l="None")
              
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(mainText, 'top', 5), (helpText, 'top', 10),

                                (separator01, 'left', 5), (separator01, 'right', 5),    
                    
                                (bsNodeLabel, 'left', 25),                   
                                (bsYLabel, 'left', 25),  
                                (bsXLabel, 'left', 25), 
                                (bsZLabel, 'left', 25), 
                                (multiplierLabel, 'left', 25),  
                                                                                                                                                    
                                (bsNode, 'right', 25),
                                (connectXBox, 'right', 25),  
                                (connectYBox, 'left', 25),
                                (connectZBox, 'left', 25),
                                (multiplierInput, 'right', 25),
                                (bsAttr_Y, 'right', 25),
                                (bsAttr_X, 'right', 25),
                                (bsAttr_Z, 'right', 25),
                                                                                                                                                                                                
                                (separator02, 'left', 5), (separator02, 'right', 5),
                                (separator03, 'left', 5), (separator03, 'right', 5),                                 
                                                                                           
                                (button01, 'bottom', 5), (button01, 'left', 5), (button01, 'right', 5),
                                ],
                                
                    attachControl=[(helpText, 'left', 5, mainText),
                        
                                   (thanksText, 'top', 5, mainText),
                                   (separator01, 'top', 5, thanksText),                           
                                   (bsNodeLabel, 'top', 5, separator01),
                                   (bsYLabel, 'top', 5, bsNodeLabel),
                                   (bsXLabel, 'top', 5, bsYLabel),
                                   (bsZLabel, 'top', 5, bsXLabel),
                                   
                                   (separator02, 'top', 5, bsAttr_Z),
                                                                                                                                                                                                    
                                   (connectZBox, 'top', 5, separator02),                                                           
                                   (connectYBox, 'top', 5, separator02),
                                   (connectXBox, 'top', 5, separator02),

                                   (multiplierLabel, 'top', 5, connectYBox),  
                                                                                                                                 
                                   (bsNode, 'top', 5, separator01),
                                   (bsAttr_Y, 'top', 5, bsNode),
                                   (bsAttr_X, 'top', 5, bsAttr_Y),
                                   (bsAttr_Z, 'top', 5, bsAttr_X),

                                   (multiplierInput, 'top', 5, connectYBox),
                                   
                                   (separator03, 'top', 5, multiplierInput),                                   
                                   (linkText, 'top', 5, separator03),
                                   ],
                                   
                    attachPosition=[(mainText, 'left', 0, 20),
                                    (thanksText, 'left', 0, 30),
                                    (bsNode, 'left', 0, 50),
                                    (bsAttr_Y, 'left', 0, 50),
                                    (bsAttr_X, 'left', 0, 50),                                    
                                    (bsAttr_Z, 'left', 0, 50),
                                     
                                    (connectYBox, 'left', 0, 7),
                                    (connectXBox, 'left', 0, 40),
                                    (connectZBox, 'left', 0, 71),

                                    (multiplierInput, 'left', 0, 50),
                                    (linkText, 'left', 0, 34),
                                   ]

                    )
       
    # Show Window
    cmds.showWindow (window)

    updateBSAttr()  
    
#-------------------------------------------------------------------------------------------------------------------------------------
# Lock Specified Attributes

def antcgiConnectBS(*args):

    offsetOptions = 0
    X_Multi = 0
    Y_Multi = 0    
    Z_Multi = 0
    
    controlName = cmds.ls(sl=1)[0]

    # Check if attributes exist
    
    attrCheckList = cmds.listAttr(controlName, ud=1)

    connectCheck = cmds.listConnections(controlName, type="multiplyDivide")

    if connectCheck:
        for connect in connectCheck:
            if "bsMulti" in connect: cmds.warning("Control already connected.")

    if attrCheckList:
        for attrCheck in attrCheckList:
            if attrCheck == "offsetOptions": offsetOptions = 1
            if attrCheck == "X_Multi": X_Multi = 1
            if attrCheck == "Y_Multi": Y_Multi = 1
            if attrCheck == "Z_Multi": Z_Multi = 1

    if not offsetOptions:
        cmds.addAttr (controlName, ln="offsetOptions", nn="-----", at="enum", en="OFFSET")
        cmds.setAttr ((controlName + ".offsetOptions"), e=1, k=0, cb=1)

    bsNodeName = cmds.optionMenu("bsNode", q=1, v=1)
    
    bsAttrName_Y = cmds.optionMenu("bsAttr_Y", q=1, v=1)
    bsAttrName_X = cmds.optionMenu("bsAttr_X", q=1, v=1)
    bsAttrName_Z = cmds.optionMenu("bsAttr_Z", q=1, v=1)
        
    doY = cmds.checkBox("connectYBox", q=1, v=1)
    doX = cmds.checkBox("connectXBox", q=1, v=1)
    doZ = cmds.checkBox("connectZBox", q=1, v=1)
    
    multiAmount = cmds.floatField("multiplierInput", q=1, v=1)

    cmds.shadingNode ("multiplyDivide", au=1, n=(controlName.lower() + "_bsMulti"))

    if doY:
        if not Y_Multi:
            cmds.connectAttr ((controlName + ".ty"), (controlName.lower() + "_bsMulti.input1Y"), f=1)
            cmds.connectAttr ((controlName.lower() + "_bsMulti.outputY"), (bsNodeName + "." + bsAttrName_Y), f=1)

            cmds.addAttr (controlName, ln=("Y_Multi"), at="double", dv=multiAmount)
            cmds.setAttr ((controlName + ".Y_Multi"), e=1, keyable=1)

            cmds.connectAttr ((controlName + ".Y_Multi"), (controlName.lower() + "_bsMulti.input2Y"), f=1)        

    if doX:
        if not X_Multi:
            cmds.connectAttr ((controlName + ".tx"), (controlName.lower() + "_bsMulti.input1X"), f=1)
            cmds.connectAttr ((controlName.lower() + "_bsMulti.outputX"), (bsNodeName + "." + bsAttrName_X), f=1)

            cmds.addAttr (controlName, ln=("X_Multi"), at="double", dv=multiAmount)
            cmds.setAttr ((controlName + ".X_Multi"), e=1, keyable=1)

            cmds.connectAttr ((controlName + ".X_Multi"), (controlName.lower() + "_bsMulti.input2X"), f=1)   
 
    if doZ:
        if not Z_Multi:
            cmds.connectAttr ((controlName + ".tz"), (controlName.lower() + "_bsMulti.input1Z"), f=1)
            cmds.connectAttr ((controlName.lower() + "_bsMulti.outputZ"), (bsNodeName + "." + bsAttrName_Z), f=1)

            cmds.addAttr (controlName, ln=("Z_Multi"), at="double", dv=multiAmount)
            cmds.setAttr ((controlName + ".Z_Multi"), e=1, keyable=1)

            cmds.connectAttr ((controlName + ".Z_Multi"), (controlName.lower() + "_bsMulti.input2Z"), f=1) 
        
    cmds.select(controlName, r=1)         
        