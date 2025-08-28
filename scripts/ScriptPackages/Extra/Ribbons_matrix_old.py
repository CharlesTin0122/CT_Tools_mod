import pymel.core as pm

"""
Author: Chris Lesage, https://rigmarolestudio.com
A script snippet for pinning an object to a nurbs surface in Autodesk Maya.
This results in a surface pin, much like a follicle, but I've found
follicles to be less stable, sometimes flipping since Maya 2018 or so. Details in this thread:
https://tech-artists.org/t/flipping-follicles-in-ribbon-ik/11022/10?u=clesage
sourceObj is an optional parameter. If you pass a PyNode object, it will place the "follicle"
as close to the object as possible. Otherwise, you can specify U and V coordinates.
"""


def pin_to_surface(oNurbs, sourceObj=None, uPos=0.5, vPos=0.5):
    """
        这个功能替代了我以前用毛囊的用途。
        它将一个物体固定在表面的 UV 坐标上。
        在少数情况下，毛囊可能会翻转和抖动。这似乎解决了这个问题

        1. oNurbs 是你想要固定的表面。
        传递一个 PyNode 变换、NurbsSurface 或有效的字符串名称。
        2. sourceObj是一个可选的参考变换。如果指定,UV坐标将尽可能放置。否则,指定U和V坐标。
    传递一个PyNode变换、形状节点或有效的字符串名称。
        3. uPos和vPos可以指定,默认为0.5。
    """

    # TODO: Can I support polygons?
    # Parse whether it is a nurbsSurface shape or transform
    if type(oNurbs) == str and pm.objExists(oNurbs):
        oNurbs = pm.PyNode(oNurbs)
    if type(oNurbs) == pm.nodetypes.Transform:
        pass
    elif type(oNurbs) == pm.nodetypes.NurbsSurface:
        oNurbs = oNurbs.getTransform()
    elif type(oNurbs) == list:
        pm.warning("Specify a NurbsSurface, not a list.")
        return False
    else:
        pm.warning("Invalid surface object specified.")
        return False

    pointOnSurface = pm.createNode("pointOnSurfaceInfo")
    oNurbs.getShape().worldSpace.connect(pointOnSurface.inputSurface)
    # follicles remap from 0-1, but closestPointOnSurface must take minMaxRangeV into account
    paramLengthU = oNurbs.getShape().minMaxRangeU.get()
    paramLengthV = oNurbs.getShape().minMaxRangeV.get()

    if sourceObj:
        # Place the follicle at the position of the sourceObj
        # Otherwise use the UV coordinates passed in the function
        if isinstance(sourceObj, str) and pm.objExists(sourceObj):
            sourceObj = pm.PyNode(sourceObj)
        if isinstance(sourceObj, pm.nodetypes.Transform):
            pass
        elif isinstance(sourceObj, pm.nodetypes.Shape):
            sourceObj = sourceObj.getTransform()
        elif type(sourceObj) == list:
            pm.warning("sourceObj should be a transform, not a list.")
            return False
        else:
            pm.warning("Invalid sourceObj specified.")
            return False
        oNode = pm.createNode("closestPointOnSurface", n="ZZZTEMP")
        oNurbs.worldSpace.connect(oNode.inputSurface, force=True)
        oNode.inPosition.set(sourceObj.getTranslation(space="world"))
        uPos = oNode.parameterU.get()
        vPos = oNode.parameterV.get()
        pm.delete(oNode)

    pName = "{}_foll#".format(oNurbs.name())
    result = pm.spaceLocator(n=pName).getShape()
    result.addAttr("parameterU", at="double", keyable=True, dv=uPos)
    result.addAttr("parameterV", at="double", keyable=True, dv=vPos)
    # set min and max ranges for the follicle along the UV limits.
    result.parameterU.setMin(paramLengthU[0])
    result.parameterV.setMin(paramLengthV[0])
    result.parameterU.setMax(paramLengthU[1])
    result.parameterV.setMax(paramLengthV[1])
    result.parameterU.connect(pointOnSurface.parameterU)
    result.parameterV.connect(pointOnSurface.parameterV)

    # Compose a 4x4 matrix
    mtx = pm.createNode("fourByFourMatrix")
    outMatrix = pm.createNode("decomposeMatrix")
    mtx.output.connect(outMatrix.inputMatrix)
    outMatrix.outputTranslate.connect(result.getTransform().translate)
    outMatrix.outputRotate.connect(result.getTransform().rotate)

    """
    Thanks to kiaran at https://forums.cgsociety.org/t/rotations-by-surface-normal/1228039/4
    # Normalize these vectors
    [tanu.x, tanu.y, tanu.z, 0]
    [norm.x, norm.y, norm.z, 0]
    [tanv.x, tanv.y, tanv.z, 0]
    # World space position
    [pos.x, pos.y, pos.z, 1]
    """

    pointOnSurface.normalizedTangentUX.connect(mtx.in00)
    pointOnSurface.normalizedTangentUY.connect(mtx.in01)
    pointOnSurface.normalizedTangentUZ.connect(mtx.in02)
    mtx.in03.set(0)

    pointOnSurface.normalizedNormalX.connect(mtx.in10)
    pointOnSurface.normalizedNormalY.connect(mtx.in11)
    pointOnSurface.normalizedNormalZ.connect(mtx.in12)
    mtx.in13.set(0)

    pointOnSurface.normalizedTangentVX.connect(mtx.in20)
    pointOnSurface.normalizedTangentVY.connect(mtx.in21)
    pointOnSurface.normalizedTangentVZ.connect(mtx.in22)
    mtx.in23.set(0)

    pointOnSurface.positionX.connect(mtx.in30)
    pointOnSurface.positionY.connect(mtx.in31)
    pointOnSurface.positionZ.connect(mtx.in32)
    mtx.in33.set(1)

    return result


if __name__ == "__main__":
    """
    Here are some examples of how to use the pin_to_surface.py script.
    """

    # make a nurbsPlane
    oNurbs = pm.nurbsPlane(n="nurbsPlane1")

    # You can specify the nurbsSurface by string, PyNode transform or PyNode shape.
    pin_to_surface("nurbsPlane1", uPos=0.5, vPos=0.5)
    pin_to_surface(pm.PyNode("nurbsPlane1"), uPos=0.5, vPos=0.5)

    # To place a range of "follicles", just loop over U or V or both.
    # Make sure to multiply by the U or V range of your surface. UV does not always go 0 to 1.
    paramLengthU = oNurbs.getShape().minMaxRangeU.get()

    numberOfFollicles = 20
    for i in range(numberOfFollicles):
        uPos = (i / float(numberOfFollicles - 1)) * paramLengthU[1]
        pin_to_surface("nurbsPlane1", uPos=uPos, vPos=0.5)

    # Make a locator and place it somewhere near your surface
    oLoc = pm.spaceLocator(n="positionLocator")

    # If you specify sourceObj in the function, it will place the follicle
    # as close as possible to your sourceObj. It can be any transform.
    # You can use this feature to place follicles near the joints of a rig, for example.
    pin_to_surface(pm.PyNode("nurbsPlane1"), sourceObj=oLoc)
