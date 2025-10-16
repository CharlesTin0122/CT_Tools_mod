from collections import defaultdict

import maya.cmds as cmds
import maya.api.OpenMaya as om

# Returns Error Tuple
#     "uv": {}, [UUID] : [... uvId]
#     "vertex": {},[UUID] : [... vertexId ]
#     "edge" : {},[UUID] : [... edgeId ]
#     "polygon": {}, -> [UUID] : [... polygonId ]
#     "nodes" : [] -> [... nodes UUIDs]


# Internal Utility Functions
def _getNodeName(uuid):
    """
    Returns the name of the node with the given UUID

    :param uuid: UUID of the node
    :type uuid: str
    :return: Name of the node or None if the node does not exist
    :rtype: str or None
    """
    nodeName = cmds.ls(uuid, uuid=True)
    if nodeName:
        return nodeName[0]
    return None


# Functions to be imported
def trailingNumbers(nodes, _):
    """
    Returns a list of nodes with names that end with a digit.

    :param nodes: UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes with names that end with a digit
    :rtype: tuple of (str, list of str)
    """
    trailingNumbers = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName and nodeName[-1].isdigit():
            trailingNumbers.append(node)
    return "nodes", trailingNumbers


def duplicatedNames(nodes, _):
    """
    Returns a list of nodes with names that have duplicates.

    :param nodes: UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes with names that have duplicates
    :rtype: tuple of (str, list of str)
    """
    nodesByShortName = defaultdict(list)
    for node in nodes:
        nodeName = _getNodeName(node)
        name = nodeName.rsplit("|", 1)[-1]
        nodesByShortName[name].append(node)
    invalid = []
    for name, shortNameNodes in nodesByShortName.items():
        if len(shortNameNodes) > 1:
            invalid.extend(shortNameNodes)
    return "nodes", invalid


def namespaces(nodes, _):
    """
    Returns a list of nodes with names that contain a namespace (i.e. have a ":" in their name)

    :param nodes: UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes with names that contain a namespace
    :rtype: tuple of (str, list of str)
    """
    namespaces = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName and ":" in nodeName:
            namespaces.append(node)
    return "nodes", namespaces


def shapeNames(nodes, _):
    """
    Returns a list of nodes with names that do not end with "Shape" when split by "|"

    :param nodes: UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes with names that do not end with "Shape" when split by "|"
    :rtype: tuple of (str, list of str)
    """
    shapeNames = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if nodeName:
            new = nodeName.split("|")
            shape = cmds.listRelatives(nodeName, shapes=True)
            if shape:
                shapename = new[-1] + "Shape"
                if shape[0] != shapename:
                    shapeNames.append(node)
    return "nodes", shapeNames


def triangles(_, SLMesh):
    """
    Returns a list of polygon IDs that are triangles (i.e. have 3 edges)

    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a list of UUIDs of polygons that are triangles
    :rtype: tuple of (str, list of str)
    """
    triangles = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) == 3:
                triangles[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", triangles


def ngons(_, SLMesh):
    """
    Returns a dictionary of ngons (polygons with more than 4 edges)

    :param _:
    :param SLMesh:
    :return: A dictionary of ngons (polygons with more than 4 edges)
        "polygon": {}, [UUID] : [... ngonId ]
    :rtype: dict
    """
    ngons = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) > 4:
                ngons[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", ngons


def hardEdges(_, SLMesh):
    """
    Returns a dictionary of hard edges (edges that are not smooth and not on the boundary)

    :param _:
    :param SLMesh:
    :return: A dictionary of hard edges (edges that are not smooth and not on the boundary)
        "edge": {}, [UUID] : [... hardEdgeId ]
    :rtype: dict
    """
    hardEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.isSmooth is False and edgeIt.onBoundary() is False:
                hardEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", hardEdges


def lamina(_, SLMesh):
    """
    Returns a dictionary of lamina faces (faces that are marked as lamina)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of polygons that are lamina to their corresponding polygon IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    lamina = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            laminaFaces = faceIt.isLamina()
            if laminaFaces is True:
                lamina[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", lamina


def zeroAreaFaces(_, SLMesh):
    """
    Returns a dictionary of zero area faces (faces that have an area of 0 or less)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of polygons that are zero area to their respective polygon IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    zeroAreaFaces = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            faceArea = faceIt.getArea()
            if faceArea <= 0.00000001:
                zeroAreaFaces[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", zeroAreaFaces


def zeroLengthEdges(_, SLMesh):
    """
    Returns a dictionary of zero length edges (edges that have a length of 0 or less)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("edge") and a dictionary of UUIDs of edges that are zero length to their respective edge IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    zeroLengthEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.length() <= 0.00000001:
                zeroLengthEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", zeroLengthEdges


def selfPenetratingUVs(transformNodes, _):
    """
    Returns a dictionary of self penetrating UVs (UVs that are overlapping with each other)

    :param transformNodes: A list of transform nodes to check
    :type transformNodes: list of str
    :param _: Unused parameter
    :type _: None
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of polygons that are self penetrating to their respective polygon IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    selfPenetratingUVs = defaultdict(list)
    for node in transformNodes:
        nodeName = _getNodeName(node)
        shapes = cmds.listRelatives(
            nodeName, shapes=True, type="mesh", noIntermediate=True
        )
        if shapes:
            overlapping = cmds.polyUVOverlap("{}.f[*]".format(shapes[0]), oc=True)
            if overlapping:
                formatted = [
                    overlap.split("{}.f[".format(shapes[0]))[1][:-1]
                    for overlap in overlapping
                ]
                selfPenetratingUVs[node].extend(formatted)
    return "polygon", selfPenetratingUVs


def noneManifoldEdges(_, SLMesh):
    """
    Returns a dictionary of none manifold edges (edges that are connected to more than 2 faces)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("edge") and a dictionary of UUIDs of edges that are none manifold to their respective edge IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    noneManifoldEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                noneManifoldEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", noneManifoldEdges


def openEdges(_, SLMesh):
    """
    Returns a dictionary of open edges (edges that are connected to less than 2 faces)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("edge") and a dictionary of UUIDs of edges that are open to their respective edge IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    openEdges = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                openEdges[uuid].append(edgeIt.index())
            edgeIt.next()
        selIt.next()
    return "edge", openEdges


def poles(_, SLMesh):
    """
    Returns a dictionary of poles (vertices that are connected to more than 5 edges)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("vertex") and a dictionary of UUIDs of vertices that are poles to their respective vertex IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    poles = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        vertexIt = om.MItMeshVertex(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not vertexIt.isDone():
            if vertexIt.numConnectedEdges() > 5:
                poles[uuid].append(vertexIt.index())
            vertexIt.next()
        selIt.next()
    return "vertex", poles


def starlike(_, SLMesh):
    """
    Returns a dictionary of non-starlike polygons (polygons that are not starlike)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of polygons that are not starlike to their respective polygon IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    noneStarlike = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not polyIt.isDone():
            if polyIt.isStarlike() is False:
                noneStarlike[uuid].append(polyIt.index())
            polyIt.next()
        selIt.next()
    return "polygon", noneStarlike


def missingUVs(_, SLMesh):
    """
    Returns a dictionary of faces that are missing UVs

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of faces that are missing UVs to their respective face IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    missingUVs = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            if faceIt.hasUVs() is False:
                missingUVs[uuid].append(faceIt.index())
            faceIt.next()
        selIt.next()
    return "polygon", missingUVs


def uvRange(_, SLMesh):
    """
    Returns a dictionary of UVs that are outside of the range 0-10 for U and V coordinates

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("uv") and a dictionary of UUIDs of UVs that are outside of the range to their respective UV IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    uvRange = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if Us[i] < 0 or Us[i] > 10 or Vs[i] < 0:
                uvRange[uuid].append(i)
        selIt.next()
    return "uv", uvRange


def onBorder(_, SLMesh):
    """
    Returns a dictionary of UVs that are on the border of the UV range (i.e. U or V coordinates are integers)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("uv") and a dictionary of UUIDs of UVs that are on the border to their respective UV IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    onBorder = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        mesh = om.MFnMesh(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        Us, Vs = mesh.getUVs()
        for i in range(len(Us)):
            if abs(int(Us[i]) - Us[i]) < 0.00001 or abs(int(Vs[i]) - Vs[i]) < 0.00001:
                onBorder[uuid].append(i)
        selIt.next()
    return "uv", onBorder


def crossBorder(_, SLMesh):
    """
    Returns a dictionary of polygons that have UVs that cross the border of the UV range (i.e. U or V coordinates are integers)

    :param _:
    :param SLMesh: UUID of the mesh to check
    :type SLMesh: str
    :return: A tuple containing a string indicating the type of nodes ("polygon") and a dictionary of UUIDs of polygons that have UVs that cross the border to their respective polygon IDs
    :rtype: tuple of (str, dict of (str, list of int))
    """
    crossBorder = defaultdict(list)
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        fn = om.MFnDependencyNode(selIt.getDagPath().node())
        uuid = fn.uuid().asString()
        while not faceIt.isDone():
            U, V = set(), set()
            try:
                UVs = faceIt.getUVs()
                (
                    Us,
                    Vs,
                ) = (
                    UVs[0],
                    UVs[1],
                )
                for i in range(len(Us)):
                    uAdd = int(Us[i]) if Us[i] > 0 else int(Us[i]) - 1
                    vAdd = int(Vs[i]) if Vs[i] > 0 else int(Vs[i]) - 1
                    U.add(uAdd)
                    V.add(vAdd)
                if len(U) > 1 or len(V) > 1:
                    crossBorder[uuid].append(faceIt.index())
                faceIt.next()
            except:
                cmds.warning("Face " + str(faceIt.index()) + " has no UVs")
                faceIt.next()
        selIt.next()
    return "polygon", crossBorder


def unfrozenTransforms(nodes, _):
    """
    Returns a list of nodes that have unfrozen transforms

    :param nodes: A list of UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes that have unfrozen transforms
    :rtype: tuple of (str, list of str)
    """
    unfrozenTransforms = []
    for node in nodes:
        nodeName = _getNodeName(node)
        translation = cmds.xform(nodeName, q=True, worldSpace=True, translation=True)
        rotation = cmds.xform(nodeName, q=True, worldSpace=True, rotation=True)
        scale = cmds.xform(nodeName, q=True, worldSpace=True, scale=True)
        if (
            translation != [0.0, 0.0, 0.0]
            or rotation != [0.0, 0.0, 0.0]
            or scale != [1.0, 1.0, 1.0]
        ):
            unfrozenTransforms.append(node)
    return "nodes", unfrozenTransforms


def layers(nodes, _):
    """
    Returns a list of nodes that are connected to a display layer

    :param nodes: A list of UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes that are connected to a display layer
    :rtype: tuple of (str, list of str)
    """
    layers = []
    for node in nodes:
        nodeName = _getNodeName(node)
        layer = cmds.listConnections(nodeName, type="displayLayer")
        if layer:
            layers.append(node)
    return "nodes", layers


def shaders(transformNodes, _):
    """
    Returns a list of nodes that have shaders other than the initialShadingGroup

    :param transformNodes: A list of UUIDs of transform nodes to check
    :type transformNodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes that have shaders other than the initialShadingGroup
    :rtype: tuple of (str, list of str)
    """
    shaders = []
    for node in transformNodes:
        nodeName = _getNodeName(node)
        shape = cmds.listRelatives(nodeName, shapes=True, fullPath=True)
        if cmds.nodeType(shape) == "mesh" and shape:
            shadingGrps = cmds.listConnections(shape, type="shadingEngine")
            if shadingGrps[0] != "initialShadingGroup":
                shaders.append(node)
    return "nodes", shaders


def history(nodes, _):
    """
    Returns a list of nodes that have a history larger than 1
    (i.e. they have been modified by a tool or a script)

    :param nodes: A list of UUIDs of nodes to check
    :type nodes: list of str
    :return: A tuple containing a string indicating the type of nodes ("nodes") and a list of UUIDs of nodes that have a history larger than 1
    :rtype: tuple of (str, list of str)
    """
    history = []
    for node in nodes:
        nodeName = _getNodeName(node)
        shape = cmds.listRelatives(nodeName, shapes=True, fullPath=True)
        if shape and cmds.nodeType(shape[0]) == "mesh":
            historySize = len(cmds.listHistory(shape))
            if historySize > 1:
                history.append(node)
    return "nodes", history


def uncenteredPivots(nodes, _):
    """
    Checks if the pivot of the given nodes are not centered (i.e. not at [0, 0, 0]).

    Parameters
    ----------
    nodes : list
        A list of node IDs to check.

    Returns
    -------
    tuple
        A tuple containing the name of the node type and a list of node IDs with uncentered pivots.
    """
    uncenteredPivots = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if cmds.xform(nodeName, q=1, ws=1, rp=1) != [0, 0, 0]:
            uncenteredPivots.append(node)
    return "nodes", uncenteredPivots


def emptyGroups(nodes, _):
    """
    Finds all empty groups in a given list of nodes.

    :param nodes: A list of nodes to check.
    :type nodes: list
    :return: A tuple containing the type of the result and a list of nodes that are empty groups.
    :rtype: tuple
    """
    emptyGroups = []
    for node in nodes:
        nodeName = _getNodeName(node)
        if not cmds.listRelatives(nodeName, ad=True):
            emptyGroups.append(node)
    return "nodes", emptyGroups


def parentGeometry(transformNodes, _):
    """
    Finds all transform nodes that have a parent node that has a mesh node as a child.

    :param transformNodes: A list of transform nodes.
    :type transformNodes: list
    :return: A tuple containing the type of the result and a list of transform nodes that have a parent node with a mesh node as a child.
    :rtype: tuple
    """
    parentGeometry = []
    for node in transformNodes:
        nodeName = _getNodeName(node)
        parents = cmds.listRelatives(nodeName, p=True, fullPath=True)
        if parents:
            for parent in parents:
                children = cmds.listRelatives(parent, fullPath=True)
                for child in children:
                    if cmds.nodeType(child) == "mesh":
                        parentGeometry.append(node)
    return "nodes", parentGeometry
