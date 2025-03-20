from mgear.core import anim_utils
from mgear.core.dagmenu import (
    _list_rig_roots,
    _find_rig_root,
    _get_switch_node_attrs,
    get_ik_fk_controls_by_role,
)
import pymel.core as pm
import maya.cmds as cmds


def range_switch_exec(ui_host, switchTo, onlyKeyframes, start_frame, end_frame):
    """Wrapper function to call mGears range fk/ik switch function

    Args:
        list: callback from menuItem
    """

    # instance for the range switch util
    range_switch = anim_utils.IkFkTransfer()

    switch_control = ui_host.name()
    blend_attr = _get_switch_node_attrs(ui_host.name(), "_blend")[0]
    # blend attriute extension _blend, _switch or other
    # blend_attr_ext = args[2]

    # the gets root node for the given control
    # this assumes the rig is root is a root node.
    # But it's common practice to reference rigs into the scene
    # and use the reference group function to group incoming scene data.
    # Instead swap to _find_rig_root that will
    # do the same thing but account for potential parent groups.
    # root = cmds.ls(args[0], long=True)[0].split("|")[1]

    root = _find_rig_root(ui_host.name())

    # ik_controls, fk_controls = _get_controls(switch_control, blend_attr)
    # search criteria to find all the components sharing the blend
    if "_Switch" in blend_attr:
        criteria = "*_id*_ctl_cnx"
    else:
        criteria = blend_attr.replace("_blend", "") + "_id*_ctl_cnx"
    #     component_ctl = [x for x in component_ctl if "leg" in x or "arm" in x]
    component_ctl = cmds.listAttr(switch_control, ud=True, string=criteria) or []
    if component_ctl:
        # ik_list = []
        # fk_list = []
        # NOTE: with the new implemantation provably ikRot_list and upc_list
        # are not needed anymore since the controls will be passed with the
        #  ik_controls_complete_dict and fk_controls_complete_list
        ikRot_list = []
        upv_list = []

        ik_controls_complete_dict = {}
        fk_controls_complete_list = []
        for i, comp_ctl_list in enumerate(component_ctl):
            ik_controls, fk_controls = get_ik_fk_controls_by_role(
                switch_control, comp_ctl_list
            )
            fk_controls_complete_list = fk_controls_complete_list + fk_controls
            filtered_ik_controls = {
                k: v for k, v in ik_controls.items() if v is not None
            }
            ik_controls_complete_dict.update(filtered_ik_controls)

        ik_controls_complete_list = list(ik_controls_complete_dict.values())

        range_switch.execute(
            model=root,
            ikfk_attr=blend_attr,
            uihost=pm.PyNode(switch_control).stripNamespace(),
            fks=fk_controls_complete_list,
            ik=ik_controls_complete_list,
            upv=upv_list,
            ikRot=ikRot_list,
            startFrame=start_frame,
            endFrame=end_frame,
            onlyKeyframes=onlyKeyframes,
            switchTo=switchTo,
        )


if __name__ == "__main__":
    sel = pm.ls(sl=True)[0]
    range_switch_exec(
        sel,
        switchTo="ik",
        onlyKeyframes=False,
        start_frame=int(pm.playbackOptions(query=True, min=True)),
        end_frame=int(pm.playbackOptions(query=True, max=True)),
    )


from mgear.core import anim_utils

range_switch = anim_utils.IkFkTransfer()
range_switch.execute(
    model="rig",
    ikfk_attr="leg_blend",
    uihost="legUI_L0_ctl",
    fks=["leg_L0_fk0_ctl", "leg_L0_fk1_ctl", "leg_L0_fk2_ctl"],
    ik=["leg_L0_ik_ctl", "leg_L0_upv_ctl"],
    upv=[],
    ikRot=[],
    startFrame=0,
    endFrame=100,
    onlyKeyframes=False,
    switchTo="ik",
)
