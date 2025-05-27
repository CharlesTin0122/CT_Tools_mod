#-------------------------------------------------------------------------------------------------------------------------------------
# antCGi - IK <> FK Matching Tool
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
# import antcgiIKFKMatch
# antcgiIKFKMatch.antcgiIKFKMatchUI() 
#
# Check out the video to see how to use it - https://www.youtube.com/watch?v=7R_0omGY-Ms
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
from functools import partial

#-------------------------------------------------------------------------------------------------------------------------------------   
# Match Positions

def matchPos(destination, source):

    print ("Matching > " + destination + " to " + source)
 
    cmds.matchTransform(source, destination, pos=1, rot=1)

#-------------------------------------------------------------------------------------------------------------------------------------    
# Add IK Elbow/Knee Reference Locator

def addRefLoc(*args):

    # Get side
    side = cmds.optionMenu("matchSideMenu", q=1, v=1)

    if side == "Left":
        prefix = "l_"
    else:
        prefix = "r_"
        
    # Get names
    ik_elbow = prefix + cmds.textField("ik_elbow_jnt_input", q=1, tx=1)  

    # Controls
    fk_elbow = prefix + cmds.textField("fk_elbow_jnt_input", q=1, tx=1)
    ik_elbow_ctrl = prefix.upper() + cmds.textField("ik_elbow_ctrl_input", q=1, tx=1)

    fk_elbow_locator = ik_elbow_ctrl + "_ref_locator"

    # Add Pole Vector Locator

    if not cmds.objExists(fk_elbow_locator):        
        cmds.spaceLocator(n=fk_elbow_locator)
        
        matchPos(ik_elbow_ctrl, fk_elbow_locator)
        cmds.parent(fk_elbow_locator, fk_elbow)

#-------------------------------------------------------------------------------------------------------------------------------------    
# Match IK to FK

def autoFillUI(armleg, doWhat, *args):

    # If first time ran, use default values.

    if not cmds.optionVar(ex="antcgiIKFK_fk_sh_" + armleg + "_ctrl"):
        if armleg == "arm":
            shoulder = "shoulder"
            elbow = "elbow"
            wrist = "wrist"
            
            humerus = "humerus"
            radius = "radius"
            wrist = "wrist"

        if armleg == "leg":
            shoulder = "hip"
            elbow = "knee"
            wrist = "ankle"        

            humerus = "femur"
            radius = "tibia"
            wrist = "ankle"
            
        cmds.textField("fk_shoulder_ctrl_input", e=1, tx=shoulder + "_FK_ctrl")
        cmds.textField("fk_elbow_ctrl_input", e=1, tx=elbow + "_FK_ctrl")     
        cmds.textField("fk_wrist_ctrl_input", e=1, tx=wrist + "_FK_ctrl")

        cmds.textField("fk_shoulder_jnt_input", e=1, tx=humerus + "_fk")
        cmds.textField("fk_elbow_jnt_input", e=1, tx=radius + "_fk")     
        cmds.textField("fk_wrist_jnt_input", e=1, tx=wrist + "_fk")

        cmds.textField("ik_shoulder_jnt_input", e=1, tx=humerus + "_ik")
        cmds.textField("ik_elbow_jnt_input", e=1, tx=radius + "_ik")     
        cmds.textField("ik_wrist_jnt_input", e=1, tx=wrist + "_ik")

        cmds.textField("ik_elbow_ctrl_input", e=1, tx=armleg + "_pv_ctrl")    
        cmds.textField("ik_wrist_ctrl_input", e=1, tx=armleg + "_IK_ctrl")

        storeLoad(armleg, "store")

    else:
        storeLoad(armleg, doWhat)

def storeLoad(armleg, doWhat, *args):
    
        if doWhat == "store":
            cmds.optionVar(sv=("antcgiIKFK_fk_sh_" + armleg + "_ctrl", cmds.textField("fk_shoulder_ctrl_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_fk_el_" + armleg + "_ctrl", cmds.textField("fk_elbow_ctrl_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_fk_wr_" + armleg + "_ctrl", cmds.textField("fk_wrist_ctrl_input", q=1, tx=1)))

            cmds.optionVar(sv=("antcgiIKFK_fk_sh_" + armleg + "_jnt", cmds.textField("fk_shoulder_jnt_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_fk_el_" + armleg + "_jnt", cmds.textField("fk_elbow_jnt_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_fk_wr_" + armleg + "_jnt", cmds.textField("fk_wrist_jnt_input", q=1, tx=1)))

            cmds.optionVar(sv=("antcgiIKFK_ik_sh_" + armleg + "_jnt", cmds.textField("ik_shoulder_jnt_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_ik_el_" + armleg + "_jnt", cmds.textField("ik_elbow_jnt_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_ik_wr_" + armleg + "_jnt", cmds.textField("ik_wrist_jnt_input", q=1, tx=1)))

            cmds.optionVar(sv=("antcgiIKFK_ik_el_" + armleg + "_ctrl", cmds.textField("ik_elbow_ctrl_input", q=1, tx=1)))
            cmds.optionVar(sv=("antcgiIKFK_ik_wr_" + armleg + "_ctrl", cmds.textField("ik_wrist_ctrl_input", q=1, tx=1)))
        else:
            cmds.textField("fk_shoulder_ctrl_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_sh_" + armleg + "_ctrl"))
            cmds.textField("fk_elbow_ctrl_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_el_" + armleg + "_ctrl"))
            cmds.textField("fk_wrist_ctrl_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_wr_" + armleg + "_ctrl"))

            cmds.textField("fk_shoulder_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_sh_" + armleg + "_jnt"))
            cmds.textField("fk_elbow_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_el_" + armleg + "_jnt"))
            cmds.textField("fk_wrist_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_fk_wr_" + armleg + "_jnt"))

            cmds.textField("ik_shoulder_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_ik_sh_" + armleg + "_jnt"))
            cmds.textField("ik_elbow_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_ik_el_" + armleg + "_jnt"))
            cmds.textField("ik_wrist_jnt_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_ik_wr_" + armleg + "_jnt"))

            cmds.textField("ik_elbow_ctrl_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_ik_el_" + armleg + "_ctrl"))
            cmds.textField("ik_wrist_ctrl_input", e=1, tx=cmds.optionVar(q="antcgiIKFK_ik_wr_" + armleg + "_ctrl")) 
                
#-------------------------------------------------------------------------------------------------------------------------------------    
# Match IK to FK

def matchIKFK(whichWay, *args):

    # Get side
    side = cmds.optionMenu("matchSideMenu", q=1, v=1)

    if side == "Left":
        prefix = "l_"
    else:
        prefix = "r_"        
        
    # Get names
    fk_shoulder_ctrl = prefix.upper() + cmds.textField("fk_shoulder_ctrl_input", q=1, tx=1)  
    fk_elbow_ctrl = prefix.upper() + cmds.textField("fk_elbow_ctrl_input", q=1, tx=1)  
    fk_wrist_ctrl = prefix.upper() + cmds.textField("fk_wrist_ctrl_input", q=1, tx=1)  

    ik_shoulder = prefix + cmds.textField("ik_shoulder_jnt_input", q=1, tx=1)  
    ik_elbow = prefix + cmds.textField("ik_elbow_jnt_input", q=1, tx=1)  
    ik_wrist = prefix + cmds.textField("ik_wrist_jnt_input", q=1, tx=1)  

    # Controls
    fk_shoulder = prefix + cmds.textField("fk_shoulder_jnt_input", q=1, tx=1)  
    fk_elbow = prefix + cmds.textField("fk_elbow_jnt_input", q=1, tx=1)
    fk_wrist = prefix + cmds.textField("fk_wrist_jnt_input", q=1, tx=1)

    ik_arm_ctrl = prefix.upper()  + cmds.textField("ik_wrist_ctrl_input", q=1, tx=1)
    ik_elbow_ctrl = prefix.upper() + cmds.textField("ik_elbow_ctrl_input", q=1, tx=1)

    fk_elbow_locator = ik_elbow_ctrl + "_ref_locator"

    # Check the names
    found = 0

    nameCheckList = [fk_shoulder_ctrl, fk_elbow_ctrl, fk_wrist_ctrl, ik_shoulder, ik_elbow, ik_wrist,
                    fk_shoulder, fk_elbow, fk_wrist, ik_arm_ctrl, ik_elbow_ctrl]

    for name in nameCheckList:
        if cmds.objExists(name):
            print (" > Checking " + name + " - Found")
            found = found + 1
        else:
            print (" > Checking " + name + " ! Not Found - Check names match!")

    if found == 11:
        # Do matching
        if cmds.objExists(fk_elbow_locator):
            if whichWay == "IKFK":
                matchPos(fk_wrist, ik_arm_ctrl)
                matchPos(fk_elbow_locator, ik_elbow_ctrl)
                
            if whichWay == "FKIK":
            
                matchPos(ik_shoulder, fk_shoulder_ctrl)
                matchPos(ik_elbow, fk_elbow_ctrl)
                matchPos(ik_wrist, fk_wrist_ctrl)
        else:
            cmds.error("No reference locator detected, please create one at the bind pose.")
    else:
        cmds.error("Some names didn't match, please check the script editor for details.")


#-------------------------------------------------------------------------------------------------------------------------------------    
# Main UI

def antcgiIKFKMatchUI():
    # Window exists?
    if cmds.window ("IKFKMatch", ex=1): cmds.deleteUI ("IKFKMatch")

    # Create Window
    window = cmds.window ("IKFKMatch", t="IK<>FK Matching Tool v1.5", w=275, h=400, mnb=0, mxb=0, s=1)

    # Create a main layout
    mainLayout = cmds.formLayout(numberOfDivisions=100)

    # Labels
    mainText = cmds.text("mainText", label="IK<>FK Matching Tool by @antCGi", align="left", h=20)
    thanksText = cmds.text("thanksText", label="Thanks for your support!", align="left", h=20)
    linkText = cmds.text(l='<a href="http://YouTube.com/antCGi/?q=HTML+link">YouTube.com/antCGi.</a>', hl=True)
    helpText = cmds.text(l='<a href="https://www.youtube.com/watch?v=7R_0omGY-Ms/?q=HTML+link">[?]</a>', hl=True)

    # Headings
    fk_ctrls_label = cmds.text("fk_ctrls_label", label="FK Controls", align="left", h=20, fn="boldLabelFont")
    fk_jnts_label = cmds.text("fk_jnts_label", label="FK Joints", align="left", h=20, fn="boldLabelFont")

    ik_ctrls_label = cmds.text("ik_ctrls_label", label="IK Controls", align="left", h=20, fn="boldLabelFont")
    ik_jnts_label = cmds.text("ik_jnts_label", label="IK Joints", align="left", h=20, fn="boldLabelFont")
    
    # FK Controls
    fk_shoulder_ctrl_label = cmds.text("fk_shoulder_ctrl_label", label="Shoulder", align="left", h=20, w=60)
    fk_shoulder_ctrl_input = cmds.textField("fk_shoulder_ctrl_input", w=120, h=20, ann="Shoulder Control Name.")      

    fk_elbow_ctrl_label = cmds.text("fk_elbow_ctrl_label", label="Elbow", align="left", h=20, w=60)
    fk_elbow_ctrl_input = cmds.textField("fk_elbow_ctrl_input", w=120, h=20, ann="Elbow Control Name.")     

    fk_wrist_ctrl_label = cmds.text("fk_wrist_ctrl_label", label="Wrist", align="left", h=20, w=60)
    fk_wrist_ctrl_input = cmds.textField("fk_wrist_ctrl_input", w=120, h=20, ann="Wrist Control Name.")  

    # FK Joints
    fk_shoulder_jnt_input = cmds.textField("fk_shoulder_jnt_input", w=120, h=20, ann="Shoulder Joint Name.")    
    fk_elbow_jnt_input = cmds.textField("fk_elbow_jnt_input", w=120, h=20, ann="Elbow Joint Name.")    
    fk_wrist_jnt_input = cmds.textField("fk_wrist_jnt_input", w=120, h=20, ann="Wrist Joint Name.")    

    # FK Controls
    ik_elbow_ctrl_input = cmds.textField("ik_elbow_ctrl_input", w=120, h=20, ann="Elbow Joint Name.")
    ik_wrist_ctrl_input = cmds.textField("ik_wrist_ctrl_input", w=120, h=20, ann="Wrist Joint Name.")  
    
    # IK Joints
    ik_shoulder_ctrl_label = cmds.text("ik_shoulder_ctrl_label", label="Shoulder", align="left", h=20, w=60)
    ik_shoulder_jnt_input = cmds.textField("ik_shoulder_jnt_input", w=120, h=20, ann="Shoulder Joint Name.")    
    
    ik_elbow_ctrl_label = cmds.text("ik_elbow_ctrl_label", label="Elbow", align="left", h=20, w=60)
    ik_elbow_jnt_input = cmds.textField("ik_elbow_jnt_input", w=120, h=20, ann="Elbow Joint Name.")
    
    ik_wrist_ctrl_label = cmds.text("ik_wrist_ctrl_label", label="Wrist", align="left", h=20, w=60)
    ik_wrist_jnt_input = cmds.textField("ik_wrist_jnt_input", w=120, h=20, ann="Wrist Joint Name.")   

    # Side Menu
    matchSideLabel = cmds.text("matchSideLabel", label="Side", align="left", h=20)
    matchSideMenu = cmds.optionMenu("matchSideMenu", h=20, ann="Side.")

    cmds.menuItem (l="Left")
    cmds.menuItem (l="Right")
                    
    # Buttons
    button01 = cmds.button(w=80, h=25, l="[IK > FK]", p=mainLayout, c=partial (matchIKFK, "IKFK"))
    button02 = cmds.button(w=80, h=25, l="[FK > IK]", p=mainLayout, c=partial (matchIKFK, "FKIK"))

    button03 = cmds.button(w=100, h=25, l="[Add Reference Locator]", p=mainLayout, c=addRefLoc)

    storeNamesLabel = cmds.text("storeNamesLabel", label="Store Names", align="left", h=20)
 
    button04 = cmds.button(w=60, h=20, l="[ ARM ]", p=mainLayout, c=partial (autoFillUI, "arm", "store"), ann="Store the arm names.")
    button05 = cmds.button(w=60, h=20, l="[ LEG ]", p=mainLayout, c=partial (autoFillUI, "leg", "store"), ann="Store the leg names.")  

    loadNamesLabel = cmds.text("loadNamesLabel", label="Load Names", align="left", h=20)
 
    button06 = cmds.button(w=60, h=20, l="[ ARM ]", p=mainLayout, c=partial (autoFillUI, "arm", "load"), ann="Load the arm names.")
    button07 = cmds.button(w=60, h=20, l="[ LEG ]", p=mainLayout, c=partial (autoFillUI, "leg", "load"), ann="Load the leg names.")  

    # Separators
    separator01 = cmds.separator(h=5, p=mainLayout)
    separator02 = cmds.separator(h=5, p=mainLayout)
    separator03 = cmds.separator(h=5, p=mainLayout)    
    separator04 = cmds.separator(h=5, p=mainLayout)  
                    
    cmds.formLayout(mainLayout, edit=True,
                    attachForm=[(mainText, 'top', 5), (helpText, 'top', 10),

                                (separator01, 'left', 5), (separator01, 'right', 5),    

                                (fk_shoulder_ctrl_label, 'left', 15), 
                                (fk_shoulder_jnt_input, 'right', 15),

                                (fk_elbow_ctrl_label, 'left', 15), 
                                (fk_elbow_jnt_input, 'right', 15),
                                
                                (fk_wrist_ctrl_label, 'left', 15), 
                                (fk_wrist_jnt_input, 'right', 15),
 
                                (separator02, 'left', 5), (separator02, 'right', 5),  
                                
                                (ik_shoulder_ctrl_label, 'left', 15),
                                (ik_shoulder_jnt_input, 'right', 15), 
                                                                                                 
                                (ik_elbow_ctrl_label, 'left', 15),
                                (ik_elbow_jnt_input, 'right', 15),
                                                                 
                                (ik_wrist_ctrl_label, 'left', 15),                      
                                (ik_wrist_jnt_input, 'right', 15),
                                
                                (matchSideLabel, 'left', 15),
                                                                                                                                                                                                                                                                
                                (separator03, 'left', 5), (separator03, 'right', 5),                                                           

                                (button05, 'right', 15),
                                (button07, 'right', 15),
                                
                                (separator04, 'left', 5), (separator04, 'right', 5),

                                (button01, 'bottom', 5), (button01, 'left', 5),
                                (button02, 'bottom', 5), (button02, 'right', 5),
                                (button03, 'bottom', 5),
                                ],
                                
                    attachControl=[(helpText, 'left', 5, mainText),
                        
                                   (thanksText, 'top', 5, mainText),
                                   (separator01, 'top', 5, thanksText),                           

                                   (fk_ctrls_label, 'top', 5, separator01), 
                                   (fk_jnts_label, 'top', 5, separator01), 

                                   (fk_shoulder_ctrl_label, 'top', 5, fk_ctrls_label),

                                   (fk_shoulder_ctrl_input, 'top', 5, fk_ctrls_label),
                                   (fk_shoulder_ctrl_input, 'left', 10, fk_shoulder_ctrl_label),

                                   (fk_elbow_ctrl_label, 'top', 5, fk_shoulder_ctrl_input),

                                   (fk_elbow_ctrl_input, 'top', 5, fk_shoulder_ctrl_input),
                                   (fk_elbow_ctrl_input, 'left', 10, fk_elbow_ctrl_label),

                                   (fk_wrist_ctrl_label, 'top', 5, fk_elbow_ctrl_input),

                                   (fk_wrist_ctrl_input, 'top', 5, fk_elbow_ctrl_input),
                                   (fk_wrist_ctrl_input, 'left', 10, fk_wrist_ctrl_label),

                                   
                                   (fk_shoulder_jnt_input, 'top', 5, fk_ctrls_label),
                                   (fk_elbow_jnt_input, 'top', 5, fk_shoulder_jnt_input),
                                   (fk_wrist_jnt_input, 'top', 5, fk_elbow_jnt_input),
                                                                                                         
                                   (fk_shoulder_jnt_input, 'left', 10, fk_shoulder_ctrl_input),
                                   (fk_elbow_jnt_input, 'left', 10, fk_elbow_ctrl_input),
                                   (fk_wrist_jnt_input, 'left', 10, fk_wrist_ctrl_input),

                                   (separator02, 'top', 5, fk_wrist_ctrl_input), 
                                   
                                   (ik_ctrls_label, 'top', 5, separator02), 
                                   (ik_jnts_label, 'top', 5, separator02), 

                                   (ik_shoulder_ctrl_label, 'top', 5, ik_jnts_label),                                   
                                   (ik_elbow_ctrl_label, 'top', 5, ik_shoulder_ctrl_label),
                                   (ik_wrist_ctrl_label, 'top', 5, ik_elbow_ctrl_label),

                                   (ik_elbow_ctrl_input, 'top', 5, ik_shoulder_ctrl_label),
                                   (ik_elbow_ctrl_input, 'left', 10, ik_elbow_ctrl_label),

                                   (ik_wrist_ctrl_input, 'top', 5, ik_elbow_ctrl_input),
                                   (ik_wrist_ctrl_input, 'left', 10, ik_wrist_ctrl_label),


                                   (ik_shoulder_jnt_input, 'top', 5, ik_jnts_label),
                                   (ik_shoulder_jnt_input, 'left', 10, ik_elbow_ctrl_input),
                                   
                                   (ik_elbow_jnt_input, 'top', 5, ik_shoulder_ctrl_label),
                                   (ik_elbow_jnt_input, 'left', 10, ik_elbow_ctrl_input),

                                   (ik_wrist_jnt_input, 'top', 5, ik_elbow_jnt_input),
                                   (ik_wrist_jnt_input, 'left', 10, ik_wrist_ctrl_input),

                                   (separator03, 'top', 5, ik_wrist_jnt_input),
                                   
                                   (matchSideLabel, 'top', 17, separator03),                                  
                                   (matchSideMenu, 'top', 17, separator03),  

                                   (storeNamesLabel, 'top', 5, separator03),
                                   (loadNamesLabel, 'top', 5, storeNamesLabel),
                                                                         
                                   (button04, 'top', 5, separator03),
                                   (button05, 'top', 5, separator03),   

                                   (button06, 'top', 5, button04),
                                   (button07, 'top', 5, button05), 
                                                                                                                                                                            
                                   (separator04, 'top', 5, button07),  
                                                                                                                                                                          
                                   (linkText, 'top', 5, separator04),
                                   ],
                                   
                    attachPosition=[(mainText, 'left', 0, 26),
                                    (thanksText, 'left', 0, 34),
 
                                    (fk_ctrls_label, 'left', 0, 31),
                                    (fk_jnts_label, 'left', 0, 71),

                                    (ik_ctrls_label, 'left', 0, 31),
                                    (ik_jnts_label, 'left', 0, 71),
                                                                        
                                    (fk_shoulder_ctrl_input, 'right', 0, 50),
                                    (fk_elbow_ctrl_input, 'right', 0, 50),
                                    (fk_wrist_ctrl_input, 'right', 0, 50),

                                    (ik_elbow_ctrl_input, 'right', 0, 50),
                                    (ik_wrist_ctrl_input, 'right', 0, 50),
 
                                    (matchSideMenu, 'left', 0, 15),
                                    
                                    (storeNamesLabel, 'left', 0, 45),
                                    (loadNamesLabel, 'left', 0, 45),
                                                                        
                                    (button04, 'left', 0, 65),
                                    (button06, 'left', 0, 65),
                                                                                                                                                                                    
                                    (linkText, 'left', 0, 36),
 
                                    (button01, 'right', 0, 25),
                                    (button02, 'left', 0, 75),
                                    (button03, 'left', 0, 25), (button03, 'right', 0, 75),
                                   ]

                    )
       
    # Show Window
    cmds.showWindow (window)
    
    storeLoad("arm", "load")
