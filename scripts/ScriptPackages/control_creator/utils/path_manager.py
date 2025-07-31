import maya.cmds as cmds
from pathlib import Path


class PathManager:
    """管理脚本和控制器形状的路径，缓存结果以提高性能"""

    _script_dir = None
    _control_shapes_dir = None

    @classmethod
    def get_script_directory(cls):
        """获取脚本所在目录，优先使用 __file__，否则使用 Maya 用户脚本目录"""
        if cls._script_dir is None:
            try:
                cls._script_dir = Path(__file__).resolve().parent
            except NameError:
                cls._script_dir = Path(cmds.internalVar(userScriptDir=True))
        return cls._script_dir

    @classmethod
    def get_control_shapes_dir(cls, subfolder="control_shapes"):
        """获取控制器形状目录"""
        if cls._control_shapes_dir is None:
            cls._control_shapes_dir = cls.get_script_directory() / subfolder
        return cls._control_shapes_dir

    @classmethod
    def set_control_shapes_dir(cls, new_path):
        """设置自定义控制器形状目录"""
        if not isinstance(new_path, Path):
            new_path = Path(new_path)
        if new_path.is_dir():
            cls._control_shapes_dir = new_path
            return True
        return False
