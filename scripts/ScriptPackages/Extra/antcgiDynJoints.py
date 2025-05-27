#-------------------------------------------------------------------------------------------
#
# antCGi - Add IK, FK and Dynamics functionality to a joint chain
#
#-------------------------------------------------------------------------------------------------------------------------------------
#
# To use this tool -
#
# ~ Put the script into your \Documents\maya\scripts folder.
# ~ Restart Maya.
# ~ Create a new button on the shelf with this script -
#
# import antcgiDynJoints
# antcgiDynJoints.antcgiDynJointsUI()
#
#-------------------------------------------------------------------------------------------------------------------------------------

import maya.cmds as cmds
import maya.mel as mel

#---------------------------------------------------------------------------------    
# Make the joints dynamic

def antcgiDynJoints(*args):

    globalName = cmds.textField("systemName", q=1, tx=1)
    addDynamics = cmds.checkBox("addDynamics", q=1, v=1)
    conScale = cmds.floatField("conScaleInput", q=1, v=1)

    rootJoint = cmds.ls(sl=1, type="joint")
    
    if not rootJoint: cmds.error("Please select the root joint.")

    if len(rootJoint) > 1: cmds.error("Please only select one joint.") 
    
    jointChainList = cmds.listRelatives(type="joint", ad=1)

    jointChainList.reverse()
    jointChainList.insert(0, rootJoint[0])

    midJoint = jointChainList[int(len(jointChainList)/2)]

    cmds.select(cl=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Joints

    for jointChain in jointChainList:
        addOrientJoint((jointChain + "_fk"), jointChain, "xyz", 0, 0, 0)

    cmds.select(cl=1)

    for jointChain in jointChainList:
        addOrientJoint((jointChain + "_ik"), jointChain, "xyz", 0, 0, 0) 

    # Connect to main joints

    for jointChain in jointChainList:
        cmds.parentConstraint ((jointChain.lower() + "_ik"), (jointChain.lower() + "_fk"), jointChain, w=1, mo=0) 

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Controls

    # Add IK FK Switcher

    build_RigIcon ("Slider", (globalName + "_ctrl"), "Blue", conScale*4, "Y")
    build_RigIcon ("FKLabel", (globalName + "_ik_label"), "Black", conScale*2, "Y")
    build_RigIcon ("IKLabel", (globalName + "_fk_label"), "Black", conScale*2, "Y")

    cmds.parent ((globalName + "_ik_label"), (globalName + "_fk_label"), (globalName + "_ctrl"))   
    cmds.matchTransform((globalName + "_ctrl"), rootJoint, pos=1)

    cmds.setAttr ((globalName + "_fk_label.rotateY"), 90)
    cmds.setAttr ((globalName + "_ik_label.rotateY"), 90)

    cmds.move (0, 10, 0, (globalName + "_ctrl"), wd=1, r=1, os=1)

    cmds.addAttr ((globalName + "_ctrl"), ln="FK_IK_Switch", at="double", min=0, max=1, dv=0)
    cmds.setAttr ((globalName + "_ctrl.FK_IK_Switch"), e=1, keyable=1)

    if addDynamics:
        cmds.addAttr ((globalName + "_ctrl"), ln="dynDivider", nn="----------", at="enum", en="DYNAMICS:")
        cmds.setAttr ((globalName + "_ctrl.dynDivider"), e=1, cb=1, keyable=0)

        cmds.addAttr ((globalName + "_ctrl"), ln="Simulation", at="double", min=0, max=1, dv=0)
        cmds.setAttr ((globalName + "_ctrl.Simulation"), e=1, keyable=1)

        cmds.addAttr ((globalName + "_ctrl"), ln="Follow_Pose", at="double", min=0, max=1, dv=0)
        cmds.setAttr ((globalName + "_ctrl.Follow_Pose"), e=1, keyable=1)

    cmds.pointConstraint (rootJoint, (globalName + "_ctrl"), w=1, mo=1)
    
    # FK & Dynamic
    conColour = "Yellow"

    if addDynamics:
        conType = ("_fk", "_dyn")
    else:
        conType = ("_fk", )
        
    for con in conType:

        if con == "_dyn": conColour = "Green"
    
        for i in range(len(jointChainList)):

            build_RigIcon ("Circle", (jointChainList[i] + con + "_ctrl"), conColour, conScale*3, "Z")
                        
            cmds.group ((jointChainList[i] +  con + "_ctrl"), n=(jointChainList[i] +  con + "_ctrl_offset"))    
            cmds.xform ((jointChainList[i] +  con + "_ctrl_offset"), ws=1, piv=(0, 0, 0))
              
            cmds.matchTransform((jointChainList[i] +  con + "_ctrl_offset"), jointChainList[i].lower() + "_fk", rot=1, pos=1)
            
            if con == "_fk":
                cmds.parentConstraint ((jointChainList[i] +  con + "_ctrl"), jointChainList[i].lower() + con, w=1, mo=0)
            
            if i > 0:
                cmds.parent((jointChainList[i] + con + "_ctrl_offset"), (jointChainList[i-1] + con + "_ctrl"))    

    # IK
    ikContList = (jointChainList[0] + "_ik_ctrl", jointChainList[-1] + "_ik_ctrl", midJoint + "_ik_ctrl")

    for ikCont in ikContList:
        build_RigIcon ("IKHandle", ikCont, "Red", conScale*4, "Z")
        cmds.group (ikCont, n=ikCont + "_offset")

        cmds.matchTransform((ikCont + "_offset"), ikCont.replace("_ik_ctrl", ""), rot=1, pos=1)

    cmds.select(cl=1)

    # Adjust hierachy
    cmds.group ((jointChainList[0] + "_ik_ctrl_offset"), (jointChainList[-1] + "_ik_ctrl_offset"), (midJoint + "_ik_ctrl_offset"), n=globalName + "_ik_controls")
    cmds.group (em=1, n=globalName + "_ctrljnts")

    if addDynamics:
        cmds.group (em=1, n=globalName + "_dynamics")
        cmds.group (em=1, n=globalName + "_deformers")
        cmds.group (em=1, n=globalName + "_follicles")
        
    # Add IK FK Blend Visibility
    cmds.shadingNode ("reverse", au=1, n=(globalName + "_fkik_reverse"))

    cmds.connectAttr ((globalName + "_ctrl.FK_IK_Switch"), (globalName + "_fkik_reverse.inputX"), f=1)       
    cmds.connectAttr ((globalName + "_fkik_reverse.outputX"), (jointChainList[0] + "_fk_ctrl_offset.visibility"), f=1)
    cmds.connectAttr ((globalName + "_fkik_reverse.outputX"), (globalName + "_ik_label.visibility"), f=1)
    
    cmds.connectAttr ((globalName + "_ctrl.FK_IK_Switch"), (midJoint + "_ik_ctrl_offset.visibility"), f=1)  
    cmds.connectAttr ((globalName + "_ctrl.FK_IK_Switch"), (jointChainList[0] + "_ik_ctrl_offset.visibility"), f=1) 
    cmds.connectAttr ((globalName + "_ctrl.FK_IK_Switch"), (jointChainList[-1] + "_ik_ctrl_offset.visibility"), f=1) 
    cmds.connectAttr ((globalName + "_ctrl.FK_IK_Switch"), (globalName + "_fk_label.visibility"), f=1) 
    
    # Connect Constraints

    constBlend(jointChainList, "", (globalName + "_ctrl.FK_IK_Switch"), (globalName + "_fkik_reverse.outputX"))
    
    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Control Joints

    contJntList = (jointChainList[0], midJoint, jointChainList[-1])

    for contJnt in contJntList:
        addOrientJoint((contJnt.lower() + "_ctrljnt"), contJnt, "xyz", 0, 0, 0)

        cmds.parent((contJnt.lower() + "_ctrljnt"), (globalName + "_ctrljnts"))

        if cmds.objExists((contJnt + "_ik_ctrl")):
            cmds.parentConstraint ((contJnt + "_ik_ctrl"), (contJnt.lower() + "_ctrljnt"), w=1, mo=0)

        cmds.select(cl=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Build Curves

    # Create curve for ik spline
    rootPivot = cmds.xform (jointChainList[0], q=True, ws=True, piv=True)

    if len(jointChainList) > 3:
        cmds.curve (d=3, p=(rootPivot[0], rootPivot[1], rootPivot[2]), n=globalName + "_ik_curve")
    else:
        cmds.curve (d=2, p=(rootPivot[0], rootPivot[1], rootPivot[2]), n=globalName + "_ik_curve")
    
    # cmds.curve (globalName + "_ik_curve", a=1, p=(endPivot[0], endPivot[1], endPivot[2]))

    for i in range(1, len(jointChainList)):       
        pointPivot = cmds.xform (jointChainList[i], q=True, ws=True, piv=True)
        cmds.curve (globalName + "_ik_curve", a=1, p=(pointPivot[0], pointPivot[1], pointPivot[2]))

    if addDynamics:
        cmds.duplicate(globalName + "_ik_curve", n=globalName + "_ik_dynamic_curve")

    # Create IK spline handle
    cmds.ikHandle (n=globalName + "_ikHandle", sol="ikSplineSolver", ccv=0, roc=1, pcv=0, sj=jointChainList[0].lower() + "_ik", ee=jointChainList[-1].lower() + "_ik", c=globalName + "_ik_curve")
    
    # Bind to control joints
    cmds.skinCluster((jointChainList[0].lower() + "_ctrljnt", midJoint.lower() + "_ctrljnt", jointChainList[-1].lower() + "_ctrljnt"), globalName + "_ik_curve", tsb=1, dr=10, mi=3, n=globalName + "_ik_curve_skinCluster")

    # Setup roll and twist
    cmds.shadingNode ("plusMinusAverage", au=1, n=globalName + "_uppertwist_pma")   
    cmds.shadingNode ("multiplyDivide", au=1, n=globalName + "_uppercomp_mult") 

    cmds.setAttr(globalName + "_uppercomp_mult.input2X", -1)

    cmds.connectAttr (jointChainList[0] + "_ik_ctrl.rotateX", globalName + "_ikHandle.roll", f=1)    
    cmds.connectAttr (globalName + "_ikHandle.roll", globalName + "_uppercomp_mult.input1X", f=1)

    cmds.connectAttr (jointChainList[-1] + "_ik_ctrl.rotateX", globalName + "_uppertwist_pma.input1D[0]", f=1)
    cmds.connectAttr (globalName + "_uppercomp_mult.outputX", globalName + "_uppertwist_pma.input1D[1]", f=1)
       
    cmds.connectAttr (globalName + "_uppertwist_pma.output1D", globalName + "_ikHandle.twist", f=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Make stretchy & global scale

    cmds.shadingNode ("curveInfo", au=1, n=globalName + "_ik_curveinfo")    
    cmds.shadingNode ("multiplyDivide", au=1, n=globalName + "_ik_scaleFactor")    
    
    cmds.connectAttr (cmds.listRelatives(globalName + "_ik_curve", c=1, s=1)[0] + ".worldSpace[0]", globalName + "_ik_curveinfo.inputCurve", f=1)
    cmds.connectAttr (globalName + "_ik_curveinfo.arcLength", globalName + "_ik_scaleFactor.input1X", f=1)

    cmds.setAttr(globalName + "_ik_scaleFactor.input2X", cmds.getAttr(globalName + "_ik_scaleFactor.input1X"))
    cmds.setAttr(globalName + "_ik_scaleFactor.operation", 2)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Volume preservation
    
    # Create the main multiply divide node which will calculate the volume
    cmds.shadingNode( "multiplyDivide", au=1, n=globalName + "_ik_volume")    

    # Set the operation to Power
    cmds.setAttr(globalName + "_ik_volume.operation", 3)    
    cmds.setAttr(globalName + "_ik_volume.input2X", -1)
        
    # Connect the main stretch value to the volume node
    cmds.connectAttr(globalName + "_ik_scaleFactor.outputX", globalName + "_ik_volume.input1X", f=1 ) 
    
    # Connect to the joints

    for i in range(len(jointChainList)-1):
        cmds.connectAttr (globalName + "_ik_scaleFactor.outputX", jointChainList[i].lower() + "_ik.scaleX", f=1)
        cmds.connectAttr (globalName + "_ik_scaleFactor.outputX", jointChainList[i] + ".scaleX", f=1)

        cmds.connectAttr (globalName + "_ik_volume.outputX", jointChainList[i] + ".scaleY", f=1)
        cmds.connectAttr (globalName + "_ik_volume.outputX", jointChainList[i] + ".scaleZ", f=1)

    #-------------------------------------------------------------------------------------------------------------------------------------    
    # Make Dynamic

    if addDynamics:
        cmds.select(globalName + "_ik_dynamic_curve", r=1)
        mel.eval('makeCurvesDynamic 2 { "0", "0", "1", "1", "0"}')

        dynFollicle = cmds.listRelatives(globalName + "_ik_dynamic_curve", p=1)[0]
        dynFollicleShape = cmds.listRelatives(dynFollicle, s=1)[0]

        hairSystemList = cmds.listConnections(dynFollicleShape)

        for hairSystem in hairSystemList:
            if "hairSystem" in hairSystem:
                hairSystemShape = cmds.listRelatives(hairSystem, c=1)[0]

        # Release the tip
        cmds.setAttr(dynFollicleShape + ".pointLock", 1) 

        # Connect IK
        dynCurveConnections = cmds.listConnections(dynFollicleShape, sh=1)    

        for dynCurve in dynCurveConnections:
            if "curveShape" in dynCurve:
                outputCurve = cmds.listRelatives(dynCurve, p=1)[0]

        # Update Names
        cmds.rename(dynFollicle, globalName + "_follicle")
        cmds.rename(outputCurve, globalName + "_output_curve")
            
        # Create blendshape
        cmds.blendShape(globalName + "_output_curve", globalName + "_ik_curve", n=globalName + "_bshape")
        cmds.connectAttr (globalName + "_ctrl.Simulation", globalName + "_bshape." + globalName + "_output_curve", f=1)

        cmds.connectAttr ((globalName + "_ctrl.Simulation"), (jointChainList[0] + "_dyn_ctrl_offset.visibility"), f=1) 

        cmds.connectAttr ((globalName + "_ctrl.Simulation"), (globalName + "_fkik_reverse.inputY"), f=1) 
        cmds.connectAttr ((globalName + "_fkik_reverse.outputY"), (globalName + "_ik_controls.visibility"), f=1)

        cmds.connectAttr ((globalName + "_ctrl.Follow_Pose"), (hairSystemShape + ".startCurveAttract"), f=1) 

        # Add clusters
        curveCVs = cmds.getAttr(globalName + "_ik_dynamic_curve.cp", s=1)
     
        for i in range(curveCVs):
            cmds.cluster(globalName + "_ik_dynamic_curve.cv[" + str(i) + "]", n=globalName + "_cluster_" + str(i))
            cmds.parent(globalName + "_cluster_" + str(i) + "Handle", jointChainList[i] + "_dyn_ctrl")

        # Update hierachy
        cmds.parent((globalName + "_ik_dynamic_curve"), (globalName + "_output_curve"), (globalName + "_ik_curve"), (globalName + "_ikHandle"), (globalName + "_deformers"))
        cmds.parent(cmds.listRelatives(hairSystemShape, p=1)[0], (globalName + "_dynamics"))
        cmds.parent((globalName + "_follicle"), (globalName + "_follicles"))

    # Lock
    for con in conType:   
        for i in range(len(jointChainList)):
            lockdownAttr((jointChainList[i] + con + "_ctrl"), 0, 0, 1, 1, 0)
            lockdownAttr((jointChainList[i] + con + "_ctrl_offset"), 1, 1, 1, 1, 0)

    lockdownAttr((jointChainList[-1] + "_ik_ctrl"), 0, 0, 1, 1, 0)
    lockdownAttr((jointChainList[-1] + "_ik_ctrl_offset"), 1, 1, 1, 1, 0)

    lockdownAttr((midJoint + "_ik_ctrl"), 0, 0, 1, 1, 0)
    lockdownAttr((midJoint + "_ik_ctrl_offset"), 1, 1, 1, 1, 0)

    lockdownAttr((globalName + "_ctrl"), 1, 1, 1, 1, 0)
    lockdownAttr((globalName + "_ik_label"), 1, 1, 1, 1, 1)
    lockdownAttr((globalName + "_fk_label"), 1, 1, 1, 1, 1)
    
    cmds.select(cl=1)

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
                            
#---------------------------------------------------------------------------
# Constraint Blend

def constBlend(nodeList, side, sourceAttr, destAttr, *args):

    for node in nodeList:       
        getConstraint = cmds.listConnections(node + side, type="parentConstraint")[0]
        getWeights = cmds.parentConstraint (getConstraint, q=1, wal=1)

        cmds.connectAttr (sourceAttr, (getConstraint + "." + getWeights[0]), f=1)  
        cmds.connectAttr (destAttr, (getConstraint + "." + getWeights[1]), f=1) 

#---------------------------------------------------------------------------
# Add Joint & Orient

def addOrientJoint(jointName, jointPosName, roOrder, *orientOffset):

    conScale = cmds.floatField("conScaleInput", q=1, v=1)
    
    getPosPoint = cmds.xform(jointPosName, q=1, ws=1, piv=1)
    cmds.joint (p=(getPosPoint[0], getPosPoint[1], getPosPoint[2]), rad=conScale, roo=roOrder, n=jointName.lower())
    
    cmds.orientConstraint (jointPosName, jointName.lower(), w=1, n="tmpOC"); cmds.delete("tmpOC")
    cmds.rotate (orientOffset[0], orientOffset[1], orientOffset[2], (jointName.lower() + ".rotateAxis"), a=1, os=1, fo=1)
    
    cmds.joint (jointName.lower(), e=1, zso=1)
    cmds.makeIdentity (jointName.lower(), a=1, t=0, r=1, s=0)

#---------------------------------------------------------------------------
# Build Icons/Controls

def build_RigIcon(iconType, iconName, colour, scale, orientation):
    
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
                          
    if iconType == "Circle":
        cmds.circle (nr=(0, 1, 0), n=iconName, r=0.5, s=12)
               
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

#---------------------------------------------------------------------------------    
# Create the UI

def antcgiDynJointsUI():
    
    # First we check if the window exists and if it does, delete it
    if cmds.window("antcgiDynJointsUI", ex=1): cmds.deleteUI ("antcgiDynJointsUI")

    # Create the window
    window = cmds.window("antcgiDynJointsUI", t="Dynamic Joints v2.1", w=200, h=100, mnb=0, mxb=0, s=0)
 
    # Create the main layout
    mainLayout = cmds.formLayout (nd=100)

    # Text
    systemName = cmds.textField("systemName", h=20, tx="Simulation_Name", ann="Dynamics Systems Name")

    conScaleLabel = cmds.text("conScaleLabel", label="Control Scale", align="left", h=20)
    conScaleInput = cmds.floatField("conScaleInput", h=20, w=50, pre=2, ann="Overall size of the controls.", v=1)
        
    # Buttons
    button01 = cmds.button(l="Make Dynamic", h=50, c=antcgiDynJoints)

    # Checkboxes
    addDynamics = cmds.checkBox("addDynamics", l="Include Dynamics", h=20, ann="Include dynamics?", v=1)
     
    # Adjust layout
    cmds.formLayout(mainLayout, e=1,
                    attachForm = [(systemName, 'top', 5), (systemName, 'left', 5), (systemName, 'right', 5),

                                  (conScaleLabel, 'left', 20),
                                  (addDynamics, 'left', 25),
                                  
                                  (button01, 'bottom', 5), (button01, 'left', 5), (button01, 'right', 5)
                    
                    ],              
                                  
                    attachControl = [(conScaleLabel, 'top', 5, systemName),
                                     (conScaleInput, 'top', 5, systemName), (conScaleInput, 'left', 5, conScaleLabel), 
                                     (addDynamics, 'top', 5, conScaleLabel),  
                                     (button01, 'top', 5, addDynamics),             
                    ],
    
    )
        
    # Show the window
    cmds.showWindow(window)    
  