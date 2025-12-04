
#Title: blendShapeTransfer_complete.py
#Author: Noah Schnapp
#LinkedIn: https://www.linkedin.com/in/wnschnapp/
#Youtube: http://www.youtube.com/WilliamNoahSchnapp

####################
####################
#...Import Commands
####################
####################

import maya.cmds as cmds
import maya.mel as mel

####################
####################

#...SCRIPT EDITOR USE
dirpath = r'REPLACE_WITH_YOUR_DIRECTORY_PATH'
'''
dirpath = r'REPLACE_WITH_YOUR_DIRECTORY_PATH'
import sys 
import imp 
sys.path.insert(0, dirpath) 
import blendShapeTransfer_complete 
reload(blendShapeTransfer_complete)
blendShapeTransfer_complete.run_dev()
'''
####################

def run_dev():

	#...name file
	filepath = '%s/00_example.mb'%dirpath
	#...open scene
	cmds.file(filepath, o=True, f=True)
	#...setLayout
	mel.eval('setNamedPanelLayout "layout_user";')
	#...rename scene for testing
	cmds.file(rename='untitled')
	#...transfer
	meshA = 'mesh_head'
	meshB = 'mesh_elf'
	transfer_blendShapeTrgts(meshA, meshB)

	return True

def transfer_blendShapeTrgts(meshA, meshB):

	#...check if meshA and meshB are same point count
	if len(cmds.ls('%s.vtx[*]'%meshA, flatten=True)) == len(cmds.ls('%s.vtx[*]'%meshB, flatten=True)):
		#...print
		print('')
		print('WARNING: Same topo detected between "%s" and "%s"! Running Same Topo BlendShape Transfer!'%(meshA,meshB))

		#...run action
		transfer_blendShapeTrgtsSameTopo(meshA, meshB)
	#...else
	else:
		#...print
		print('')
		print('WARNING: Different topo detected between "%s" and "%s"! Running Diff Topo BlendShape Transfer!'%(meshA,meshB))
		#...run action
		transfer_blendShapeTrgtsDiffTopo(meshA, meshB)

	return True

def transfer_blendShapeTrgtsSameTopo(meshA, meshB):

	#...vars
	grp_trgt = 'grp_trgt'
	grp_output = 'grp_%s'%meshB.replace('mesh_','')

	#...create new trgt grp
	cmds.createNode('transform', n=grp_output)

	#...get trgts
	trgt_Array = [t for t in cmds.listRelatives(grp_trgt, c=True)]
	trgt_ArrayTemp = trgt_Array[::]
	trgt_ArrayTemp.append(meshB)
	#...create blendShapes
	blendShape_meshA = 'blendShape_%s'%meshA
	cmds.blendShape(trgt_ArrayTemp, meshA, 
					name = blendShape_meshA,
					weight = (len(trgt_Array),1), 
					frontOfChain = True,
					tc=False)	

	#...cycle trgts
	for trgt in trgt_Array:
		#...turn on
		cmds.setAttr('%s.%s'%(blendShape_meshA, trgt), 1)
		#...duplicate blendshapes
		trgtNew = '%s__OUTPUT'%trgt
		cmds.duplicate(meshA, n=trgtNew)
		#...turn off
		cmds.setAttr('%s.%s'%(blendShape_meshA, trgt), 0)
		#...show
		cmds.setAttr('%s.v'%trgtNew, True)
		#...parent
		cmds.parent(trgtNew, grp_output)
		#...rename
		cmds.rename(trgtNew, trgt)
	#...clean scene
	cmds.delete(blendShape_meshA)
	cmds.delete(meshA, ch=True)
	#...create new grp_trgt
	grp_trgtNew = cmds.group(cmds.listRelatives(grp_output, children=True, path=True), n=grp_trgt)
	#...hide grp_trgt
	cmds.hide(grp_trgtNew)
	#...duplicate meshB
	meshNew = '%s__OUTPUT'%meshA
	cmds.duplicate(meshB, n=meshNew)
	cmds.parent(meshNew, grp_output)
	cmds.rename(meshNew, meshA)
	#...print success
	print('='*100)
	print('SUCCESS: Transfered The Following BlendShape Trgts from "%s" to "%s"!'%(meshA, meshB))
	print('-'*100)
	for trgt in trgt_Array:
		print(trgt)
	print('='*100)
	print('')

	return True

def transfer_blendShapeTrgtsDiffTopo(meshA, meshB):
		
	#...vars
	grp_trgt = 'grp_trgt'
	grp_output = 'grp_%s'%meshB.replace('mesh_','')
	meshAXferOld = meshA.replace('mesh_','trgt_')+'_xfer'
	meshAXfer = meshA+'_xfer'
	meshBXfer = meshB.replace('mesh_','trgt_')+'_xfer'

	#...create new trgt grp
	cmds.createNode('transform', n=grp_output)

	#...get trgts
	trgt_Array = [t for t in cmds.listRelatives(grp_trgt, c=True)]

	#...create blendShape with [trgts] to meshA
	blendShape_meshA = 'blendShape_%s'%meshA
	cmds.blendShape(trgt_Array, meshA, 
					name = blendShape_meshA,
					frontOfChain = True,
					tc=False)	

	#...duplicate meshAXfer >> meshAXferDrv
	cmds.duplicate(meshAXferOld, n=meshAXfer)
	cmds.parent(meshAXfer, w=True)

	#...wrap to xferPose- create the wrap point to point relationship with a xferDrv mesh, 
	#...later to be transferred to "like" neutral meshB to receive delta movement
	cmds.select(meshBXfer, meshAXfer,r=1)
	cmds.CreateWrap()
	wrapOld = cmds.listConnections('%s.worldMatrix[0]'%cmds.listRelatives(meshBXfer, c=True)[0], plugs=True)[0].split('.')[0]
	wrap = 'wrap_xfer'
	cmds.rename(wrapOld,wrap)

	#...create blendshape between meshA and meshAXfer
	blendShape_xfer = 'blendShape_xfer'
	cmds.blendShape(meshA, meshAXfer, 
					name = blendShape_xfer,
					weight = (0,1), 
					frontOfChain = True,
					tc=False)	

	#...duplicate meshBXfer
	meshBInMeshATrgtCycler = 'meshBInMeshATrgtCycler'
	cmds.duplicate(meshBXfer, n=meshBInMeshATrgtCycler)

	#...create blendShape with [meshBXfer, meshB] to meshBInMeshATrgtCycler 
	blendShape_meshBInMeshATrgtCycler = 'blendShape_%s'%meshBInMeshATrgtCycler
	cmds.blendShape([meshBXfer, meshB], meshBInMeshATrgtCycler, 
					name = blendShape_meshBInMeshATrgtCycler,
					weight = ([0,1],[1,1]), 
					frontOfChain = True,
					tc=False)	

	#...cycle trgts
	for trgt in trgt_Array:
		#...turn on
		cmds.setAttr('%s.%s'%(blendShape_meshA, trgt), 1)
		#...duplicate blendshapes
		trgtNew = '%s__OUTPUT'%trgt
		cmds.duplicate(meshBInMeshATrgtCycler, n=trgtNew)
		#...turn off
		cmds.setAttr('%s.%s'%(blendShape_meshA, trgt), 0)
		#...show
		cmds.setAttr('%s.v'%trgtNew, True)
		#...parent
		cmds.parent(trgtNew, grp_output)
		cmds.rename(trgtNew, trgt)
		
	#...clean scene
	cmds.delete(meshA, ch=True)
	cmds.delete(wrap)
	cmds.delete(meshAXfer)
	cmds.delete(meshBInMeshATrgtCycler)

	#...create new grp_trgt
	grp_trgtNew = cmds.group(cmds.listRelatives(grp_output, children=True, path=True), n=grp_trgt)

	#...hide grp_trgt
	cmds.hide(grp_trgtNew)

	#...duplicate meshB
	meshNew = '%s__OUTPUT'%meshA
	cmds.duplicate(meshB, n=meshNew)
	cmds.parent(meshNew, grp_output)
	cmds.rename(meshNew, meshA)

	#...print success
	print('='*100)
	print('SUCCESS: Transfered The Following BlendShape Trgts from "%s" to "%s"!'%(meshA, meshB))
	print('-'*100)
	for trgt in trgt_Array:
		print(trgt)
	print('='*100)
	print('')


	return True
