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
    range_switch = anim_utils.IkFkTransfer()

    switch_control = ui_host.name()
    blend_attr = _get_switch_node_attrs(ui_host.name(), "_blend")[0]

    root = _find_rig_root(ui_host.name())

    criteria = blend_attr.replace("_blend", "") + "_id*_ctl_cnx"
    component_ctl = cmds.listAttr(switch_control, ud=True, string=criteria) or []
    if component_ctl:
        ik_list = []
        ikRot_list = []
        fk_list = []
        upv_list = []

        for com_list in component_ctl:
            # set the initial val for the blend attr in each iteration
            ik_controls, fk_controls = get_ik_fk_controls_by_role(
                switch_control, com_list
            )
            ik_list.append(ik_controls["ik_control"])
            if ik_controls["ik_rot"]:
                ikRot_list.append(ik_controls["ik_rot"])
            upv_list.append(ik_controls["pole_vector"])
            fk_list = fk_list + fk_controls

        range_switch.execute(
            model=root,
            ikfk_attr=blend_attr,
            uihost=pm.PyNode(switch_control).stripNamespace(),
            fks=fk_list,
            ik=ik_list,
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
