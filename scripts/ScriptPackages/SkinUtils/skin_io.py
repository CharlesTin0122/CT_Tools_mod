import pickle
import json
import traceback
import maya.api.OpenMaya as om
import maya.api.OpenMayaAnim as oma
import pymel.core as pm
import pymel.core.nodetypes as nt
from Qt import QtWidgets


class SkinClusterIO(QtWidgets.QDialog):
    FILE_EXT = ".pSkin"
    FILE_JSON_EXT = ".jSkin"
    PACK_EXT = ".pSkinPack"

    _ui_instance = None

    def __init__(self, parent=None):
        if parent is None:
            parent = SkinClusterIO.maya_main_window()
        super().__init__(parent)

        self.setWindowTitle("Skin IO")
        self.setObjectName("skinIoWidget")
        self.setMinimumSize(200, 80)

        main_layout = QtWidgets.QVBoxLayout(self)
        import_btn = QtWidgets.QPushButton("Import skin")
        import_btn.released.connect(self.import_skin)
        export_btn = QtWidgets.QPushButton("Export skin")
        export_btn.released.connect(self.export_skin)
        main_layout.addWidget(import_btn)
        main_layout.addWidget(export_btn)

    @staticmethod
    def maya_main_window():
        app = QtWidgets.QApplication.instance()
        if app:
            for widget in app.topLevelWidgets():
                if widget.objectName() == "MayaWindow":
                    return widget
        return None

    @classmethod
    def show_ui(cls):
        if not cls._ui_instance:
            cls._ui_instance = cls()

        if cls._ui_instance.isHidden():
            cls._ui_instance.show()
        else:
            cls._ui_instance.raise_()
            cls._ui_instance.activateWindow()

    def collect_data(self, skinCluster_node: nt.SkinCluster, data: dict):
        """收集数据"""
        # 获取几何体DagPath和受蒙皮影响的组件（顶点）集合
        dag_path, components = self.get_geometry_components(skinCluster_node)
        # 获取影响权重
        self.collectInfluenceWeights(skinCluster_node, dag_path, components, data)
        # 获取双四元数和线性蒙皮的混合权重
        self.collectBlendWeights(skinCluster_node, dag_path, components, data)
        # 获取"skinningMethod", "normalizeWeights"
        for attr in ["skinningMethod", "normalizeWeights"]:
            data[attr] = skinCluster_node.attr(attr).get()
        data["skinClsName"] = skinCluster_node.name()

    def collectInfluenceWeights(
        self,
        skinCluster_node: nt.SkinCluster,
        dag_path: om.MDagPath,
        components: om.MObject,
        data: dict,
    ):
        """
                收集给定蒙皮簇的影响权重。
                Args:
                    dag_path (om.MDagPath): 几何体的dagPath.
                    components (om.MObject): skinCluster的蒙皮组件（顶点集合）.
                Returns:
                    None
                Notes:
                    权重的组织方式如下：对于每个顶点，权重为
                    根据影响对象以连续的顺序存储。
                    例如，对于顶点 0，权重为 [w0_j0, w0_j1, ...]；
                    对于顶点 1，权重为 [w1_j0, w1_j1, ...]。
                    权重存储在字典 {vtx_index:weight} 中，跳过 0 权重。
                    数据以以下格式写入：
                    dataDic[weights] = {
                    joint1: {0: 0.7, 2: 0.3},
                    joint2: {1: 0.5, 2: 0.5},
        ...}
        """
        weights, num_influence = self.get_current_weights(
            skinCluster_node, dag_path, components
        )
        # 获取获取所有影响对象DagPath数组
        skinCluster_fn = SkinClusterIO.get_skinCluster_fn(skinCluster_node.name())
        influences_paths: om.MDagPathArray = skinCluster_fn.influenceObjects()
        # 顶点数量总和 = 权重数量 / 影响（骨骼）数量，float做分母，避免整数除法可能导致的精度问题
        data["vertexCount"] = int(len(weights) / float(num_influence))
        # 计算每个影响对象的组件（顶点）数量
        component_num_perInfluence = int(len(weights) / num_influence)
        # 遍历影响对象数组
        for i in range(len(influences_paths)):
            influence_name = influences_paths[i].partialPathName()
            influence_name_without_namespace = pm.PyNode(
                influence_name
            ).stripNamespace()
            # 构建一个字典{vtx_index:weight},跳过0权重值
            influence_weights = {
                j: weights[j * num_influence + i]
                for j in range(component_num_perInfluence)
                if weights[j * num_influence + i] != 0
            }
            # 写入数据
            data["weights"][str(influence_name_without_namespace)] = influence_weights

    def collectBlendWeights(
        self,
        skinCluster_node: nt.SkinCluster,
        dag_path: om.MDagPath,
        components: om.MObject,
        data: dict,
    ):
        """
        获取blendWeights数据，双四元数蒙皮和线性蒙皮之间的混合权重.
        Args:
            dag_path (om.MDagPath): The DAG path of the geometry.
            components (om.MObject): The component selection (e.g., vertices).
        Returns:
            None
        """
        # 获取blendWeights数据
        skinCluster_fn = SkinClusterIO.get_skinCluster_fn(skinCluster_node.name())
        blend_weights: om.MDoubleArray = skinCluster_fn.getBlendWeights(
            dag_path, components
        )
        # 如果值不为零，则将索引和值作为键值对写入数据，精确到小数点后6位
        data["blendWeights"] = {
            index: round(blend_weights[index], 6)
            for index in range(len(blend_weights))
            if round(blend_weights[index], 6) != 0
        }

    def export_skin(self, file_path=None, objs=None, *args):
        if not objs:
            if pm.selected():
                objs = pm.selected()
            else:
                pm.displayWarning("Please Select One or more objects")
                return False
        # 顶层数据字典,self.data为"objDDic"的值
        pack_dict = {"objs": [], "objDDic": [], "bypassObj": []}
        # 如果没有提供路径参数，则选择一个
        if not file_path:
            f1 = f"jSkin ASCII (*{SkinClusterIO.FILE_JSON_EXT})"
            f2 = f";;pSkin Binary (*{SkinClusterIO.FILE_EXT})"
            f3 = ";;All Files (*.*)"
            file_filters = f1 + f2 + f3
            #  fileMode=0：表示保存模式,返回用户选择的文件路径（列表）
            file_path = pm.fileDialog2(fileMode=0, fileFilter=file_filters)
            if file_path:
                file_path = file_path[0]
            else:
                return False
        # 如果路径参数的扩展名不对，则直接返回
        if not file_path.endswith(SkinClusterIO.FILE_EXT) and not file_path.endswith(
            SkinClusterIO.FILE_JSON_EXT
        ):
            pm.displayWarning(f"Not valid file extension for: {file_path}")
            return
        # 遍历选择列表
        for obj in objs:
            # 获取skinCluster节点
            skinCluster_node = self.get_skin_cluster(obj)
            # 如果没有找到skincluster节点则报错
            if not skinCluster_node:
                pm.displayWarning(
                    f"{obj.name()}: Skiped because do not have skin cluster"
                )
                pass
            # 如果找到skincluster节点则收集数据
            else:
                # 创建蒙皮信息数据
                data = {
                    "weights": {},
                    "blendWeights": {},
                    "skinClsName": "",
                    "objName": "",
                    "nameSpace": "",
                    "vertexCount": 0,
                    "skinDataFormat": "compressed",
                }
                data["objName"] = obj.name()
                data["nameSpace"] = obj.namespace()

                self.collect_data(skinCluster_node, data)

                pack_dict["objs"].append(obj.name())
                pack_dict["objDDic"].append(data)

                name_skinCluster = skinCluster_node.name()
                num_influence = len(data["weights"].keys())
                num_points = data["vertexCount"]
                name_obj = obj.name()
                # 显示日志
                export_message = f"Exported skinCluster: {name_skinCluster}: ({num_influence} influences, {num_points} points), {name_obj}"
                pm.displayInfo(export_message)
        # 收集数据完成，保存数据
        if pack_dict["objs"]:
            # 如果路径名称扩展名为'.gSkin'，则使用Pickle库储存数据
            if file_path.endswith(SkinClusterIO.FILE_EXT):
                # 打开文件以二进制写入模式（"wb"）。
                with open(file_path, "wb") as fp:
                    # HIGHEST_PROTOCOL：使用最高协议版本进行序列化，以优化存储效率和兼容性。
                    pickle.dump(pack_dict, fp, pickle.HIGHEST_PROTOCOL)
            # 如果路径扩展名为'.jSkin'，使用json储存数据
            else:
                # 打开文件以文本写入模式（"w"）。
                with open(file_path, "w") as fp:
                    # sort_keys=True：按键排序，确保 JSON 输出的键顺序一致，便于比较或调试。
                    json.dump(pack_dict, fp, indent=4, sort_keys=True)
            # 表示文件保存成功，返回 True。
            return True

    def import_skin(self, file_path=None, *args):
        # 获取路径
        if not file_path:
            f1 = "export Skin (*{0} *{1})".format(
                SkinClusterIO.FILE_EXT, SkinClusterIO.FILE_JSON_EXT
            )
            f2 = ";;pSkin Binary (*{0});;jSkin ASCII  (*{1})".format(
                SkinClusterIO.FILE_EXT, SkinClusterIO.FILE_JSON_EXT
            )
            f3 = ";;All Files (*.*)"
            fileFilters = f1 + f2 + f3
            # fileMode=1:打开单个文件
            file_path = pm.fileDialog2(fileMode=1, fileFilter=fileFilters)
        if not file_path:
            raise RuntimeError("do nto get filePath")
        if not isinstance(file_path, str):
            file_path = file_path[0]
        pm.displayInfo(f"file_path: {file_path}")
        # 读取数据
        if file_path.endswith(SkinClusterIO.FILE_EXT):
            with open(file_path, "rb") as fp:
                data_pack = pickle.load(fp)
        else:
            with open(file_path, "r") as fp:
                data_pack = json.load(fp)
        # 迭代数据
        for data in data_pack["objDDic"]:
            #  使用一个skinDataFormat键来检查jSkin文件是否具有新的样式压缩格式
            compressed = False
            if "skinDataFormat" in data:
                if data["skinDataFormat"] == "compressed":
                    compressed = True
            try:
                skinCluster = False
                obj_name = data["objName"]
                obj_node = pm.PyNode(obj_name)
                assert isinstance(obj_node, nt.Transform)
                try:
                    # 获取形状节点
                    shapes = obj_node.getShapes(noIntermediate=True)
                    # 根据类型获取其组件数量
                    if isinstance(obj_node.getShape(), pm.nodetypes.Mesh):
                        mesh_vertices = pm.polyEvaluate(shapes, vertex=True)
                    elif isinstance(obj_node.getShape(), pm.nodetypes.NurbsSurface):
                        # if nurbs, count the cvs instead of the vertices.
                        mesh_vertices = sum([len(shape.cv) for shape in shapes])
                    elif isinstance(obj_node.getShape(), pm.nodetypes.NurbsCurve):
                        # meshVertices = sum([len(shape.cv) for shape in objShapes])
                        mesh_vertices = sum(1 for _ in shapes[0].cv)
                    else:
                        # TODO: Implement other skinnable objs like lattices.
                        mesh_vertices = 0

                    if compressed:
                        imported_vertics = data["vertexCount"]
                    else:
                        imported_vertics = len(data["blendWeights"])
                    if mesh_vertices != imported_vertics:
                        warning_message = "Vertex counts on {} do not match.{} != {}"
                        pm.displayWarning(
                            warning_message.format(
                                obj_name, mesh_vertices, imported_vertics
                            )
                        )
                        continue
                except Exception:
                    pass
                # 如果当前Mesh已经存在skin cluster，则获取skinCluster
                if self.get_skin_cluster(obj_node):
                    skinCluster = self.get_skin_cluster(obj_node)
                # 如果当前Mesh没有skinCluster，则创建skinCluster
                else:
                    try:
                        joints = list(data["weights"].keys())
                        skin_name = data["skinClsName"].replace("|", "")
                        # nw=2:后归一化（在操作完成后归一化）
                        skinCluster = pm.skinCluster(
                            joints,
                            obj_node,
                            toSelectedBones=True,
                            normalizeWeights=2,
                            name=skin_name,
                        )
                    except Exception:
                        scene_joints = set(
                            [pm.PyNode(x).name() for x in pm.ls(type="joint")]
                        )
                        not_found = []
                        for j in data["weights"].keys():
                            if j not in scene_joints:
                                not_found.append(str(j))
                        pm.displayWarning(
                            f"Object: {obj_name} skiped. can not found corresponding deformer for the following joints: {str(not_found)}"
                        )
                        continue
                if isinstance(skinCluster, list):
                    skinCluster = skinCluster[0]
                if skinCluster:
                    self.set_data(skinCluster, data, compressed)
                    print("Imported skin for: {}".format(obj_name))
            except Exception as e:
                traceback.print_exc()
                pm.displayWarning(e)

    def set_data(self, skinCluster, data, compressed):
        dagPath, components = self.get_geometry_components(skinCluster)
        self.set_influence_weight(skinCluster, dagPath, components, data, compressed)
        for attr in ["skinningMethod", "normalizeWeights"]:
            skinCluster.attr(attr).set(data[attr])
        self.set_blend_weights(skinCluster, dagPath, components, data, compressed)

    def set_influence_weight(self, skinCluster, dagPath, components, data, compressed):
        """为提供的蒙皮节点设置权重.
        Args:
            skinCls (PyNode): 蒙皮节点.
            dagPath (MDagPath): 几何体的dagPath.
            components (MObject): 蒙皮组件（顶点集合）.
            dataDic (dict): 蒙皮数据.
            compressed (bool): 是否压缩权重.
        """
        # 没有用到的导入信息
        unused_imports = []
        # 获取当前蒙皮节点的权重信息
        weights, num_influence = self.get_current_weights(
            skinCluster, dagPath, components
        )
        # 获取蒙皮函数集
        skin_fn = self.get_skinCluster_fn(skinCluster.name())
        # 获取影响对象DagPath列表
        influence_paths = skin_fn.influenceObjects()
        # 获取每个印象对象影响的点数量（几何体顶点数量）
        num_components_perInfluence = int(len(weights) / num_influence)

        # 获取影响对象映射(骨骼名称：索引)
        influence_map = {
            om.MFnDependencyNode(influence_paths[i].node()).name(): i
            for i in range(len(influence_paths))
        }
        # 遍历导入数据的权重列表: joint_name : weight_list
        for imported_influence, weight_val in data["weights"].items():
            # 根据导入数据的骨骼名称获取当前蒙皮的影响索引
            influence_index = influence_map.get(imported_influence)
            if influence_index is not None:
                if compressed:
                    # 遍历几何体顶点数量
                    for j in range(num_components_perInfluence):
                        # 字典的get方法，参数1：要获取值的键；参数2：当键不存在时返回的默认值
                        weight = weight_val.get(j, weight_val.get(str(j), 0.0))
                        # 设置权重值,weights是一个全局权重字典，需要计算权重索引位置
                        weights[j * num_influence + influence_index] = weight
                else:
                    for j, weight in enumerate(weight_val):
                        weights[j * num_influence + influence_index] = weight
            else:
                unused_imports.append(imported_influence)
        # 权重分配
        influence_indices = om.MIntArray()
        influence_indices.setLength(num_influence)
        for i in range(num_influence):
            influence_indices[i] = i
        """最终设置权重
        setWeights(
            shape, components, influences, weights, normalize=True, returnOldWeights=False
            ) -> None or MDoubleArray
        
        * shape       (MDagPath) - 几何体对象的MDagPath
        * components   (MObject) - 几何体对象的蒙皮组件（所有顶点）
        * influences (MIntArray) - 影响对象索引数组（骨骼）
        * weights (MDoubleArray) - 全部权重值
        * returnOldWeights(bool) - 是否返回就权重数据
        """
        skin_fn.setWeights(dagPath, components, influence_indices, weights, False)

    def set_blend_weights(self, skinCluster, dagPath, components, data, compressed):
        if compressed:
            # maya权重压缩会跳过0权重，如果key为空，则将其值设为0.0
            # json的key不能是整数，只能是unicode字符串 vtx[35]：0.69将是: u35: 0.69
            blendWeights = om.MDoubleArray(int(data["vertexCount"]))
            for key, value in data["blendWeights"].items():
                blendWeights[int(key)] = value
        else:
            # 没有被压缩，意味着所有0权重都存在， 向后兼容旧皮肤文件
            blendWeights = om.MDoubleArray(len(data["blendWeights"]))
            for i, val in enumerate(data["blendWeights"]):
                blendWeights[i] = val
        self.get_skinCluster_fn(skinCluster.name()).setBlendWeights(
            dagPath, components, blendWeights
        )

    @staticmethod
    def get_skin_cluster(obj: pm.nodetypes.Transform, first_sc: bool = False):
        """
        获取蒙皮节点
        Arguments:
            obj (pm.nodetypes.Transform): 要获取蒙皮节点的对象
            first_sc (bool, optional): 是否获取第一个蒙皮节点
        Returns:
            pm.nodetypes.SkinCluster: 蒙皮节点
        """
        skin_cluster = None  # 用于储存蒙皮节点
        try:
            # 如果节点的形状节点支持蒙皮
            if pm.nodeType(obj.getShape()) in ["mesh", "nurbsCurve", "nurbsSurface"]:
                # 遍历所有的形状节点
                for shape in obj.getShapes():
                    # 获取蒙皮节点
                    for sc in pm.listHistory(shape, type="skinCluster"):
                        assert isinstance(sc, pm.nodetypes.SkinCluster)
                        # 如果蒙皮节点关联的几何体为形状节点
                        if sc.getGeometry()[0] == shape:
                            # 变量赋值
                            skin_cluster = sc
                            # 如果“first_sc”参数为真，立刻返回当前蒙皮节点
                            # 如果参数为假：返回最后一个遍历到的蒙皮节点
                            # 一个Mesh上有可能有多个蒙皮节点，first_sc= False可获取最新的节点
                            if first_sc:
                                return skin_cluster
        except Exception:
            pm.displayWarning(f"{obj.name()} is not supported.")
        return skin_cluster

    @staticmethod
    def get_skinCluster_fn(skinCluster_name: str):
        """获取蒙皮节点函数集"""
        sel_list = om.MSelectionList()
        sel_list.add(skinCluster_name)
        skinCluster_obj = sel_list.getDependNode(0)
        return oma.MFnSkinCluster(skinCluster_obj)

    def get_geometry_components(self, skinCluster_node: nt.SkinCluster):
        # 获取与skin cluster连接的最近几何体
        geo_types = ["mesh", "nurbsSurface", "nurbsCurve"]
        for type in geo_types:
            # 找到与蒙皮节点连接的对应属性对象
            # 参数 et=True 表示精确类型匹配，t=t 指定几何体类型
            objs = skinCluster_node.listConnections(exactType=True, type=type)
            # 如果对象存在，获取其第一个形状节点名称
            if objs:
                geo_name = objs[0].getShape().name()
            # 获取几何体DagPath
            sel_list = om.MSelectionList()
            sel_list.add(geo_name)
            geo_dagpath = sel_list.getDagPath(0)
            # 获取几何体组件（所有顶点）
            mesh_fn = om.MFnMesh(geo_dagpath)  # 创建Mesh函数集
            # 创建单索引组件函数集
            components_fn = om.MFnSingleIndexedComponent()
            # 创建单索引组件对象（空顶点集合），类型为Mesh顶点组件，返回MObject
            components = components_fn.create(om.MFn.kMeshVertComponent)
            # 往这个组件对象里添加具体的顶点 ID。
            components_fn.addElements(range(mesh_fn.numVertices))
        # 返回
        return geo_dagpath, components

    def get_current_weights(
        self,
        skinCluster_node: nt.SkinCluster,
        dagPath: om.MDagPath,
        components: om.MObject,
    ):
        """
        获取当前顶点权重
        Parameters:
            skinCluster (pm.nodetypes.SkinCluster): The skin cluster node.
            dagPath (om.MDagPath): The DAG path of the geometry.
            components (om.MObject): The component selection (e.g., vertices).

        Returns:
            om.MDoubleArray: The current weights of the skin cluster.
        """
        # getWeights(shape, components) -> (MDoubleArray, int)
        # 返回权重数组和影响数量
        skinCluster_fn = SkinClusterIO.get_skinCluster_fn(skinCluster_node.name())
        # 根据提供的 几何体DagPath 和 组件顶点索引 计算权重列表，返回权重列表和影响数量
        weights, influence_num = skinCluster_fn.getWeights(dagPath, components)
        return weights, influence_num


if __name__ == "__main__":
    SkinClusterIO.show_ui()
