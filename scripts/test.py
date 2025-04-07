import pymel.core as pc

objs = pc.selected()
position_list = []
for obj in objs:
    position = obj.getTranslation(space="world")
    position_list.append(position)
pc.polyCreateFacet(p=position_list)
