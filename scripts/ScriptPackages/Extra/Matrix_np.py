import numpy as np
import numbers
import math


class Matrix4x4:
    """
    用于表示和操作 4x4 齐次矩阵的类（行优先存储，使用 NumPy），支持基本的矩阵运算（加、减、乘）、
    向量乘法、行列式计算、矩阵求逆、转置以及创建旋转、缩放、平移和投影矩阵。
    适用于 3D 几何变换、计算机图形学等场景。矩阵采用行优先存储，变换顺序为 M1 @ M2 @ v（先应用 M2，再应用 M1）。
    平移分量位于第四行，适用于左乘列向量（M @ v）。
    """

    def __init__(self, data=None):
        """
        初始化一个 4x4 矩阵（行优先）。
        如果没有提供数据，则创建一个所有元素都为 0 的矩阵。
        :param data: 一个 4x4 的列表/NumPy 数组，例如：[[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
        """
        if data is None:
            self.data = np.zeros((4, 4), dtype=np.float64)
        else:
            # 转换为 NumPy 数组并验证
            if isinstance(data, np.ndarray):
                data = data.tolist()  # 转换为列表以统一验证
            if self._is_valid_matrix(data):
                self.data = np.array(data, dtype=np.float64)
            else:
                raise ValueError(
                    "提供的输入数据必须是一个 4x4 的列表或 NumPy 数组，且元素必须是数字。"
                )

    def _is_valid_matrix(self, data):
        """检查输入数据是否为有效的 4x4 矩阵，且元素为数字。"""
        if not isinstance(data, list) or len(data) != 4:
            return False
        for row in data:
            if not isinstance(row, list) or len(row) != 4:
                return False
            for elem in row:
                if not isinstance(elem, numbers.Number):
                    return False
        return True

    def __str__(self):
        """
        返回矩阵的字符串表示形式，确保对齐（行优先）。
        """
        max_width = max(len(f"{elem:.2f}") for row in self.data for elem in row)
        matrix_str = ""
        for row in self.data:
            matrix_str += " ".join(f"{elem:>{max_width}.2f}" for elem in row) + "\n"
        return matrix_str

    def __add__(self, other):
        """矩阵加法（行优先）。"""
        if not isinstance(other, Matrix4x4):
            raise TypeError("只能将一个矩阵与另一个矩阵相加。")
        return Matrix4x4(self.data + other.data)

    def __sub__(self, other):
        """矩阵减法（行优先）。"""
        if not isinstance(other, Matrix4x4):
            raise TypeError("只能从一个矩阵中减去另一个矩阵。")
        return Matrix4x4(self.data - other.data)

    def __mul__(self, other):
        """
        矩阵乘法或标量乘法（行优先）。
        :param other: 另一个 Matrix4x4 对象或标量（int/float）。
        :return: 新的 Matrix4x4 对象。
        """
        if isinstance(other, (int, float)):
            return Matrix4x4(self.data * other)
        if isinstance(other, Matrix4x4):
            return Matrix4x4(np.dot(self.data, other.data))
        raise TypeError(f"不支持 Matrix4x4 和 {type(other).__name__} 之间的乘法。")

    def __rmul__(self, other):
        """右乘法（标量 * 矩阵，行优先）。"""
        return self.__mul__(other)

    def multiply_vector(self, vector):
        """
        用该矩阵乘以一个 4 维列向量（齐次坐标，行优先，M @ v）。
        :param vector: 包含 4 个数字的列表或元组。
        :return: 包含 4 个元素的结果列表。
        """
        if not isinstance(vector, (list, tuple, np.ndarray)) or len(vector) != 4:
            raise ValueError("向量必须是一个包含 4 个元素的列表、元组或 NumPy 数组。")
        if not all(isinstance(elem, (int, float)) for elem in vector):
            raise ValueError("向量元素必须是数字。")
        vector = np.array(vector, dtype=np.float64)
        result = np.dot(self.data, vector)
        return result.tolist()

    def determinant(self):
        """
        计算 4x4 矩阵的行列式（行优先）。
        :return: 行列式的值（float）。
        """
        return float(np.linalg.det(self.data))

    def inverse(self):
        """
        计算矩阵的逆矩阵（行优先）。
        :return: 新的 Matrix4x4 对象，表示逆矩阵。
        """
        det = self.determinant()
        if abs(det) < 1e-9:
            raise ValueError("矩阵不可逆（行列式接近零）。")
        return Matrix4x4(np.linalg.inv(self.data))

    def transpose(self):
        """返回矩阵的转置（行优先）。"""
        return Matrix4x4(np.transpose(self.data))

    def __eq__(self, other):
        """比较两个矩阵是否相等（考虑浮点误差，行优先）。"""
        if not isinstance(other, Matrix4x4):
            return False
        return np.allclose(self.data, other.data, atol=1e-9)

    @staticmethod
    def identity():
        """创建 4x4 单位矩阵（行优先）。"""
        return Matrix4x4(np.eye(4, dtype=np.float64))

    @staticmethod
    def zero():
        """创建 4x4 零矩阵（行优先）。"""
        return Matrix4x4(np.zeros((4, 4), dtype=np.float64))

    @staticmethod
    def create_rotation_matrix(axis, angle_rad):
        """
        创建一个绕指定轴旋转的 4x4 旋转矩阵（行优先，M @ v）。
        :param axis: 旋转轴 ('x', 'y', 'z')，不区分大小写。
        :param angle_rad: 旋转角度（弧度）。
        :return: Matrix4x4 对象。
        """
        if not isinstance(angle_rad, (int, float)):
            raise TypeError("旋转角度必须是数字（弧度）。")
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)
        axis = axis.lower()
        if axis == "x":
            data = [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]
        elif axis == "y":
            data = [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]
        elif axis == "z":
            data = [[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        else:
            raise ValueError("旋转轴必须是 'x', 'y', 或 'z'")
        return Matrix4x4(np.array(data, dtype=np.float64))

    @staticmethod
    def create_scale_matrix(scale_x, scale_y, scale_z):
        """
        创建一个 4x4 缩放矩阵（行优先）。
        :param scale_x: X 轴缩放因子。
        :param scale_y: Y 轴缩放因子。
        :param scale_z: Z 轴缩放因子。
        :return: Matrix4x4 对象。
        """
        if not all(isinstance(s, (int, float)) for s in (scale_x, scale_y, scale_z)):
            raise TypeError("缩放因子必须是数字。")
        data = [
            [scale_x, 0, 0, 0],
            [0, scale_y, 0, 0],
            [0, 0, scale_z, 0],
            [0, 0, 0, 1],
        ]
        return Matrix4x4(np.array(data, dtype=np.float64))

    @staticmethod
    def create_translation_matrix(tx, ty, tz):
        """
        创建一个 4x4 平移矩阵（行优先，平移分量在第四行）。
        :param tx: X 轴平移量。
        :param ty: Y 轴平移量。
        :param tz: Z 轴平移量。
        :return: Matrix4x4 对象。
        """
        if not all(isinstance(t, (int, float)) for t in (tx, ty, tz)):
            raise TypeError("平移量必须是数字。")
        data = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [tx, ty, tz, 1]]
        return Matrix4x4(np.array(data, dtype=np.float64))

    @staticmethod
    def create_projection_matrix(normal_vector):
        """
        创建一个正交投影矩阵，用于将点投影到由法向量定义的平面上（行优先）。
        :param normal_vector: 包含 3 个数字的列表或元组，表示法向量。
        :return: Matrix4x4 对象。
        """
        if (
            not isinstance(normal_vector, (list, tuple, np.ndarray))
            or len(normal_vector) != 3
        ):
            raise ValueError("法向量必须是一个包含 3 个元素的列表、元组或 NumPy 数组。")
        if not all(isinstance(elem, (int, float)) for elem in normal_vector):
            raise ValueError("法向量元素必须是数字。")
        n = np.array(normal_vector, dtype=np.float64)
        length = np.sqrt(np.sum(n**2))
        if length == 0:
            raise ValueError("法向量不能是零向量。")
        n = n / length  # 归一化
        # 投影矩阵：P = I - n @ n.T
        I = np.eye(3, dtype=np.float64)
        n_outer = np.outer(n, n)
        proj_3x3 = I - n_outer
        # 扩展到 4x4
        data = np.eye(4, dtype=np.float64)
        data[:3, :3] = proj_3x3
        return Matrix4x4(data)


if __name__ == "__main__":
    # 测试矩阵初始化和打印
    m1 = Matrix4x4([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]])
    print("Matrix m1:")
    print(m1)

    # 测试加法
    m2 = Matrix4x4.identity()
    print("Identity matrix m2:")
    print(m2)
    print("m1 + m2:")
    print(m1 + m2)

    # 测试减法
    print("m1 - m2:")
    print(m1 - m2)

    # 测试矩阵乘法
    print("m1 * m2:")
    print(m1 * m2)

    # 测试标量乘法
    print("m1 * 2:")
    print(m1 * 2)

    # 测试向量乘法
    vector = [1, 2, 3, 1]
    print(f"m1 * vector {vector}:")
    print(m1.multiply_vector(vector))

    # 测试行列式
    print(f"Determinant of m1: {m1.determinant():.2f}")

    # 测试逆矩阵
    rotation_matrix = Matrix4x4.create_rotation_matrix("y", math.pi / 2)
    print("Rotation matrix (y-axis, π/2):")
    print(rotation_matrix)
    print("Inverse of rotation matrix:")
    print(rotation_matrix.inverse())

    # 测试转置
    print("Transpose of m1:")
    print(m1.transpose())

    # 测试单位矩阵和零矩阵
    print("Zero matrix:")
    print(Matrix4x4.zero())
    print("Identity matrix:")
    print(Matrix4x4.identity())

    # 测试缩放矩阵
    scale_matrix = Matrix4x4.create_scale_matrix(2, 3, 4)
    print("Scale matrix (2, 3, 4):")
    print(scale_matrix)

    # 测试平移矩阵
    translation_matrix = Matrix4x4.create_translation_matrix(1, 2, 3)
    print("Translation matrix (1, 2, 3):")
    print(translation_matrix)
    print(f"Translation matrix * vector {vector}:")
    print(translation_matrix.multiply_vector(vector))  # 应为 [2, 4, 6, 1]

    # 测试投影矩阵
    projection_matrix = Matrix4x4.create_projection_matrix([1, 0, 0])
    print("Projection matrix (normal [1, 0, 0]):")
    print(projection_matrix)

    # 测试相等性
    print("m2 == identity:", m2 == Matrix4x4.identity())

    # 测试行优先变换顺序（先平移，再旋转）
    print("Testing transformation order (translate then rotate):")
    translate = Matrix4x4.create_translation_matrix(1, 0, 0)
    rotate_y = Matrix4x4.create_rotation_matrix("y", math.pi / 2)
    combined = rotate_y * translate  # 行优先：先应用 translate，再应用 rotate_y
    vector = [0, 0, 0, 1]
    result = combined.multiply_vector(vector)
    print(f"Combined matrix (rotate_y * translate):")
    print(combined)
    print(f"Transformed vector {vector}: {result}")  # 应为 [0, 0, -1, 1]
