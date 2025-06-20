import sys

path = r"D:\CT_Tools_mod\scripts\ScriptPackages\jawUtils"
for module_name in sys.modules.keys():
    top_module = module_name.split(".")[0]
    if top_module == "jaw_utils":
        del sys.modules[module_name]
if path not in sys.path:
    sys.path.append(path)

import jaw_utils

jaw_utils.create_guides()
