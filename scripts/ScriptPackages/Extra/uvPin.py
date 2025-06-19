import maya.cmds as mc


def createUVPin(
    name=None,
    components=[0],
    tangentAxis=1,
    normalAxis=0,
    uvSet="map1",
    normalizeIsoparms=True,
    output=2,
    exTransform=[],
):
    """
    Creates UVPin-constrained Locators or Objects on specified objects and components.
    Args:
        name (str): Name of the NURBS surface or mesh.
        components (list): List of components (e.g., vertices for mesh, CVs for NURBS).
        tangentAxis (int): 0=X, 1=Y, 2=Z, 3=-X, 4=-Y, 5=-Z.
        normalAxis (int): 0=X, 1=Y, 2=Z, 3=-X, 4=-Y, 5=-Z.
        uvSet (str): UV set name (default: "map1").
        normalizeIsoparms (bool): Normalize UV coordinates.
        output (int): 0=Existing Transform, 1=New Transform, 2=New Locator, 3=Matrix.
        exTransform (list): List of existing transforms to constrain.
    """
    # Check if the object is a valid NURBS surface or mesh
    shapes = mc.listRelatives(name, c=True, s=True)
    if not shapes:
        mc.error("No shapes found for the provided object.")

    shape = shapes[0]
    typ = mc.objectType(shape)

    # Define attributes based on object type
    if typ == "nurbsSurface":
        componentPrefix = ".cv"
        cAttr = ".create"
        cAttr2 = ".worldSpace[0]"
    elif typ == "mesh":
        componentPrefix = ".vtx"
        cAttr = ".inMesh"
        cAttr2 = ".worldMesh[0]"
    else:
        mc.error("Object must be a Mesh or NURBS surface.")

    # Create UVPin node
    uvPinNode = mc.createNode("uvPin")

    # Connect the surface to the UVPin node
    mc.connectAttr(f"{shape}{cAttr2}", f"{uvPinNode}.deformedGeometry")

    # Create locators if output is set to 2
    locators = []
    if output == 2:
        for i, comp in enumerate(components):
            loc = mc.spaceLocator(n=f"uvPin_loc_{i + 1}")[0]
            locators.append(loc)
            mc.connectAttr(f"{uvPinNode}.outputMatrix[{i}]", f"{loc}.matrix")

    # Set UV coordinates
    for i, comp in enumerate(components):
        if typ == "nurbsSurface":
            uv = comp if isinstance(comp, list) else [0, 0]
            mc.setAttr(f"{uvPinNode}.coordinate[{i}].coordinateU", uv[0])
            mc.setAttr(f"{uvPinNode}.coordinate[{i}].coordinateV", uv[1])

    # Set tangent and normal axes
    mc.setAttr(f"{uvPinNode}.tangentAxis", tangentAxis)
    mc.setAttr(f"{uvPinNode}.normalAxis", normalAxis)
    mc.setAttr(f"{uvPinNode}.normalizeIsoparms", normalizeIsoparms)

    return uvPinNode, locators


# Example usage
surface = "ribbonSurface"  # Replace with your NURBS surface name
components = [
    [0.0, 0.5],
    [0.25, 0.5],
    [0.5, 0.5],
    [0.75, 0.5],
    [1.0, 0.5],
]  # UV coordinates
uvPinNode, locators = createUVPin(name=surface, components=components, output=2)

# Create joints and bind them to the surface
joints = []
for i in range(10):  # Create 10 bind joints
    jnt = mc.joint(
        name=f"bind_jnt_{i + 1}", position=(i * 0.1, 0, 0)
    )  # Adjust position as needed
    joints.append(jnt)

# Bind NURBS surface to joints
mc.select(surface, joints)
mc.skinCluster(toSelectedBones=True, maximumInfluences=3, skinMethod=0)

# Constrain joints to locators
for i, jnt in enumerate(joints):
    if i < len(locators):
        mc.parentConstraint(locators[i], jnt, maintainOffset=True)
