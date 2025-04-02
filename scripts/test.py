import pymel.core as pm

objs = pm.selected()
position_list = []
for obj in objs:
    position = obj.getTranslation(space="world")
    position_list.append(position)
pm.polyCreateFacet(p=position_list)
