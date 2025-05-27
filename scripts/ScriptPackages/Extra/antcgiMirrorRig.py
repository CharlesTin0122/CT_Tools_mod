#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - Mirror Rig Tool
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
# import antcgiMirrorRig
# antcgiMirrorRig.antcgiMirrorRigUI() 
#
# Check out the video to see how to use it - https://www.youtube.com/watch?v=GdexRVl9XBU
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel
from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------    
# Mirror Joints

def antcgiMirrorJnts(*args):
    cmds.mirrorJoint(myz=1, mb=1, sr=("l_", "r_"))

#-------------------------------------------------------------------------------------------------------------------------------------    
# Mirror Controls

def antcgiMirrorCntrls(*args):
    cmds.group(n="antcgi_left")
    
    cmds.xform("antcgi_left", piv=(0, 0, 0))
    
    cmds.duplicate("antcgi_left", rr=1, n="antcgi_right")
    cmds.scale( -1, 1, 1, "antcgi_right", r=1)
    
    cmds.select(hi=1)

    mel.eval ('searchReplaceNames "l_" "r_" "selected"')
 
    right_grps = cmds.listRelatives("antcgi_right")
    cmds.select(hi=1)
    
    cmds.checkBox("trans_box", e=1, v=1)    
    cmds.checkBox("rot_box", e=1, v=1)    
    cmds.checkBox("scale_box", e=1, v=1)
    cmds.checkBox("viz_box", e=1, v=1)
    
    antcgiLockUnlock("unlock")
    
    cmds.ungroup("antcgi_left", "antcgi_right")
    cmds.makeIdentity(right_grps, apply=1, t=0, r=0, s=1, n=0, pn=1)    

    cmds.select(cl=1)
    
#-------------------------------------------------------------------------------------------------------------------------------------    
# Lock/Unlock

def antcgiLockUnlock(whichWay, *args):

    if whichWay == "lock":
        locked = 1
        keyable = 0
    elif whichWay == "unlock":
        locked = 0
        keyable = 1
            
    selList = cmds.ls(sl=1, ap=1, tr=1)    

    for sel in selList:
        if cmds.checkBox("trans_box", q=1, v=1):
            cmds.setAttr((sel + ".tx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".ty"), k=keyable, l=locked)
            cmds.setAttr((sel + ".tz"), k=keyable, l=locked)

        if cmds.checkBox("rot_box", q=1, v=1):
            cmds.setAttr((sel + ".rx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".ry"), k=keyable, l=locked)
            cmds.setAttr((sel + ".rz"), k=keyable, l=locked)
            
        if cmds.checkBox("scale_box", q=1, v=1):
            cmds.setAttr((sel + ".sx"), k=keyable, l=locked)
            cmds.setAttr((sel + ".sy"), k=keyable, l=locked)
            cmds.setAttr((sel + ".sz"), k=keyable, l=locked)
            
        if cmds.checkBox("viz_box", q=1, v=1):                                    
            cmds.setAttr((sel + ".v"), k=keyable, l=locked)
                            
#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiMirrorRigUI():
    # Window exists?
    if cmds.window ("antcgiMirRig", ex=1): cmds.deleteUI ("antcgiMirRig")

    # Create Window
    window = cmds.window ("antcgiMirRig", t="Rig Mirroring Tool v1.5", w=200, h=350, mnb=0, mxb=0, s=1)

    # Create a main layout
    mainLayout = cmds.formLayout(numberOfDivisions=100)

    # Labels
    mainText = cmds.text("mainText", label="Rig Mirroring Tool by @antCGi", align="left", h=20)
    thanksText = cmds.text("thanksText", label="Thanks for your support!", align="left", h=20)
    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)
    helpText = cmds.text(l='<a href="https://www.youtube.com/watch?v=GdexRVl9XBU/?q=HTML+link">[?]</a>', hl=True)

    # Separators
    separator01 = cmds.separator(h=15, p=mainLayout)
    separator02 = cmds.separator(h=15, p=mainLayout)
    separator03 = cmds.separator(h=15, p=mainLayout)
        
    # Buttons
    button01 = cmds.button(w=80, h=25, l="Mirror Selected Joints +X to -X", p=mainLayout, c=antcgiMirrorJnts)
    button02 = cmds.button(w=80, h=25, l="Mirror Selected Controls +X to -X", p=mainLayout, c=antcgiMirrorCntrls)    
    
    button03 = cmds.button(h=25, l="Lock", p=mainLayout, c=partial (antcgiLockUnlock, "lock")) 
    button04 = cmds.button(h=25, l="Unlock", p=mainLayout, c=partial (antcgiLockUnlock, "unlock")) 

    # Headings
    lockAttr_label = cmds.text("lockAttr_label", label="Lock/Unlock Attributes", align="left", h=20, fn="boldLabelFont")
    
    trans_box = cmds.checkBox("trans_box", label="Translate", align="left", h=20)
    rot_box = cmds.checkBox("rot_box", label="Rotate", align="left", h=20)
    scale_box = cmds.checkBox("scale_box", label="Scale", align="left", h=20)
    viz_box = cmds.checkBox("viz_box", label="Visibility", align="left", h=20)
                            
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(mainText, 'top', 5), (helpText, 'top', 10),
                                (separator01, 'left', 5), (separator01, 'right', 5),    

                                (button01, 'left', 5), (button01, 'right', 5), 
                                (button02, 'left', 5), (button02, 'right', 5), 
                                
                                (separator02, 'left', 5), (separator02, 'right', 5),

                                (button03, 'left', 5),
                                (button04, 'right', 5),

                                (separator03, 'left', 5), (separator03, 'right', 5),
                                
                                (linkText, 'bottom', 15), 
                                ],
                                
                    attachControl=[(helpText, 'left', 5, mainText),
                                   (thanksText, 'top', 5, mainText),
                                   (separator01, 'top', 5, thanksText),                           

                                   (button01, 'top', 5, separator01),                                                                                                                                               
                                   (button02, 'top', 5, button01), 
                                   (separator02, 'top', 5, button02),                                   
                                     
                                   (lockAttr_label, 'top', 1, separator02),
                                                                                                        
                                   (trans_box, 'top', 2, lockAttr_label),
                                   (rot_box, 'top', 2, trans_box),
                                   (scale_box, 'top', 2, rot_box),
                                   (viz_box, 'top', 2, scale_box),

                                   (button03, 'top', 10, viz_box),    
                                   (button04, 'top', 10, viz_box),    
                                                                                                         
                                   (separator03, 'top', 5, button04),
                                   ],
                                   
                    attachPosition=[(mainText, 'left', 0, 11),
                                    (thanksText, 'left', 0, 19),

                                    (lockAttr_label, 'left', 0, 20),
                                    
                                    (trans_box, 'left', 0, 33),
                                    (rot_box, 'left', 0, 33),
                                    (scale_box, 'left', 0, 33),
                                    (viz_box, 'left', 0, 33),

                                    (button03, 'right', 0, 50),
                                    (button04, 'left', 0, 50),
                                                                                                                                                 
                                    (linkText, 'left', 0, 25),
                                   ]

                    )
       
    # Show Window
    cmds.showWindow (window) 