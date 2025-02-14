import maya.cmds as cmds
import pymel.core as pm

for i in range(10):
    cmds.polyCube()
    pm.polySphere()
