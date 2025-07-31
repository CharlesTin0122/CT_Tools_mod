from importlib import reload
from control_creator.ui import control_creator_ui

reload(control_creator_ui)
control_creator_ui.show_control_creator_ui()
