import numbers
import math


class Matrix3x3:
    """一个用于表示和操作3x3矩阵的类。"""

    def __init__(self, data=None):
        """
        初始化一个3x3矩阵。
        如果没有提供数据，则创建一个所有元素都为0的矩阵。
        :param data: 一个3x3的列表的列表，例如：[[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        """
        if data is None:
            self.data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        elif self._is_valid_matrix(data):
            self.data = data
        else:
            raise ValueError("提供的输入数据必须是一个3x3的列表的列表。")

    def _is_valid_matrix(self, data):
        """检查输入数据是否为有效的3x3列表的列表。"""
        if not isinstance(data, list) or len(data) != 3:
            return False
        for row in data:
            if not isinstance(row, list) or len(row) != 3:
                return False
            for elem in row:
                if not isinstance(elem, numbers.Number):
                    return False
        return True

    def __str__(self):
        """
        返回矩阵的字符串表示形式，以便于打印。
        """
        matrix_str = ""
        for row in self.data:
            matrix_str += " ".join(f"{elem:8.2f}" for elem in row) + "\n"
        return matrix_str

    def __add__(self, other):
        """
        重载加法运算符 '+'。
        :param other: 另一个Matrix3x3对象。
        :return: 一个新的Matrix3x3对象，它是两者之和。
        """
        if not isinstance(other, Matrix3x3):
            raise TypeError("只能将一个矩阵与另一个矩阵相加。")

        result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                result_data[i][j] = self.data[i][j] + other.data[i][j]
        return Matrix3x3(result_data)

    def __sub__(self, other):
        """
        重载减法运算符 '-'。
        :param other: 另一个Matrix3x3对象。
        :return: 一个新的Matrix3x3对象，它是两者之差。
        """
        if not isinstance(other, Matrix3x3):
            raise TypeError("只能从一个矩阵中减去另一个矩阵。")

        result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                result_data[i][j] = self.data[i][j] - other.data[i][j]
        return Matrix3x3(result_data)

    def __mul__(self, other):
        """
        重载乘法运算符 '*'。
        可以处理矩阵-矩阵乘法和矩阵-标量乘法。
        :param other: 另一个Matrix3x3对象或一个标量（int或float）。
        :return: 一个新的Matrix3x3对象。
        """
        if isinstance(other, numbers.Number):
            return self._scalar_multiply(other)
        if isinstance(other, Matrix3x3):
            result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(3):
                for j in range(3):
                    for k in range(3):
                        result_data[i][j] += self.data[i][k] * other.data[k][j]
            return Matrix3x3(result_data)
        raise TypeError(f"不支持 Matrix3x3 和 {type(other).__name__} 之间的乘法。")

    def __rmul__(self, other):
        """
        重载右乘法运算符 '*'，用于处理标量在前的情况 (e.g., 3 * matrix)。
        """
        if isinstance(other, numbers.Number):
            return self._scalar_multiply(other)
        raise TypeError(f"不支持 {type(other).__name__} 和 Matrix3x3 之间的乘法。")

    def _scalar_multiply(self, scalar):
        """执行标量乘法。"""
        result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        for i in range(3):
            for j in range(3):
                result_data[i][j] = self.data[i][j] * scalar
        return Matrix3x3(result_data)

    def multiply_vector(self, vector):
        """
        用该矩阵乘以一个列向量。
        :param vector: 一个包含3个数字的列表或元组，代表一个列向量。
        :return: 一个包含3个元素的结果列表。
        """
        if not isinstance(vector, (list, tuple)) or len(vector) != 3:
            raise ValueError("向量必须是一个包含3个元素的列表或元组。")

        result_vector = [0, 0, 0]
        for i in range(3):
            for j in range(3):
                result_vector[i] += self.data[i][j] * vector[j]
        return result_vector

    def determinant(self):
        """
        计算并返回矩阵的行列式。
        对于3x3矩阵 [[a, b, c], [d, e, f], [g, h, i]]
        行列式 = a(ei - fh) - b(di - fg) + c(dh - eg)
        :return: 行列式的值 (float或int)。
        """
        a, b, c = self.data[0]
        d, e, f = self.data[1]
        g, h, i = self.data[2]

        det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
        return det

    @staticmethod
    def create_rotation_matrix(axis, angle_rad):
        """
        创建一个绕指定轴旋转的3D旋转矩阵。
        :param axis: 旋转轴，必须是 'x', 'y', 或 'z' (不区分大小写)。
        :param angle_rad: 旋转角度，以弧度为单位。
        :return: 一个代表旋转的 Matrix3x3 对象。
        """
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)

        axis = axis.lower()
        if axis not in ["x", "y", "z"]:
            raise ValueError(f"无效的旋转轴 '{axis}'。必须是 'x', 'y' 或 'z'。")

        if axis == "x":
            return Matrix3x3([[1, 0, 0], [0, c, -房], [0, s, c]])
        elif axis == "y":
            return Matrix3x3([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == "z":
            return Matrix3x3([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    @staticmethod
    def create_scale_matrix(scale_x, scale_y, scale_z):
        """创建一个缩放矩阵

        Args:
            scale_x (float): X轴缩放
            scale_y (float): Y轴缩放
            scale_z (float): Z轴缩放

        Returns:
            matrix3x3: 缩放矩阵
        """
        return Matrix3x3([[scale_x, 0, 0], [0, scale_y, 0], [0, 0, scale_z]])

    @staticmethod
    def create_projection_matrix(normal_vector):
        """
        创建一个正交投影矩阵，用于将点投影到由法向量定义的平面上。

        :param normal_vector: 一个定义平面的法向量，例如 [x, y, z]。
        :return: 一个代表投影的 Matrix3x3 对象。
        """
        if not isinstance(normal_vector, (list, tuple)) or len(normal_vector) != 3:
            raise ValueError("法向量必须是一个包含3个元素的列表或元组。")

        nx, ny, nz = normal_vector
        length_sq = nx**2 + ny**2 + nz**2

        if length_sq == 0:
            raise ValueError("法向量不能是零向量。")

        if not math.isclose(length_sq, 1.0, rel_tol=1e-6):
            length = math.sqrt(length_sq)
            nx /= length
            ny /= length
            nz /= length

        data = [
            [1 - nx * nx, -nx * ny, -nx * nz],
            [-ny * nx, 1 - ny * ny, -ny * nz],
            [-nz * nx, -nz * ny, 1 - nz * nz],
        ]

        return Matrix3x3(data)

    @staticmethod
    def create_reflection_matrix(normal_vector):
        """
        创建一个绕指定平面（由法向量定义）的反射矩阵。
        反射矩阵公式：R = I - 2 * n * n^T，其中I是单位向量， n 是平面法向量，n^T是向量转置
        外积 n * n^T：这是法向量 n 与其转置 n^T 的矩阵乘法，结果是一个 3x3 矩阵，表示投影到法向量方向的变换。

        :param normal_vector: 一个定义反射平面的法向量，例如 [x, y, z]。
        :return: 一个代表反射的 Matrix3x3 对象。
        """
        if not isinstance(normal_vector, (list, tuple)) or len(normal_vector) != 3:
            raise ValueError("法向量必须是一个包含3个元素的列表或元组。")

        nx, ny, nz = normal_vector
        length_sq = nx**2 + ny**2 + nz**2

        if length_sq == 0:
            raise ValueError("法向量不能是零向量。")

        if not math.isclose(length_sq, 1.0, rel_tol=1e-6):
            length = math.sqrt(length_sq)
            nx /= length
            ny /= length
            nz /= length

        # 反射矩阵公式：R = I - 2 * n * n^T
        data = [
            [1 - 2 * nx * nx, -2 * nx * ny, -2 * nx * nz],
            [-2 * ny * nx, 1 - 2 * ny * ny, -2 * ny * nz],
            [-2 * nz * nx, -2 * nz * ny, 1 - 2 * nz * nz],
        ]

        return Matrix3x3(data)

    @staticmethod
    def create_shear_matrix(axis, shear_axis, shear_factor):
        """
        创建一个沿指定轴的剪切矩阵。
        例如，沿 x 轴剪切，y 方向受 x 影响：y' = y + shear_factor * x。

        :param axis: 剪切的主轴，'x', 'y', 或 'z' (不区分大小写)。
        :param shear_axis: 受影响的轴，'x', 'y', 或 'z'，且不能与主轴相同。
        :param shear_factor: 剪切因子（float）。
        :return: 一个代表剪切的 Matrix3x3 对象。
        """
        axis = axis.lower()
        shear_axis = shear_axis.lower()

        if axis not in ["x", "y", "z"] or shear_axis not in ["x", "y", "z"]:
            raise ValueError("轴必须是 'x', 'y' 或 'z'。")
        if axis == shear_axis:
            raise ValueError("剪切轴不能与主轴相同。")

        data = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # 单位矩阵
        if axis == "x":
            if shear_axis == "y":
                data[1][0] = shear_factor  # y' = y + shear_factor * x
            elif shear_axis == "z":
                data[2][0] = shear_factor  # z' = z + shear_factor * x
        elif axis == "y":
            if shear_axis == "x":
                data[0][1] = shear_factor  # x' = x + shear_factor * y
            elif shear_axis == "z":
                data[2][1] = shear_factor  # z' = z + shear_factor * y
        elif axis == "z":
            if shear_axis == "x":
                data[0][2] = shear_factor  # x' = x + shear_factor * z
            elif shear_axis == "y":
                data[1][2] = shear_factor  # y' = y + shear_factor * z

        return Matrix3x3(data)


# --- 使用示例 ---
if __name__ == "__main__":
    # 创建两个矩阵
    m1 = Matrix3x3([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    m2 = Matrix3x3([[9, 8, 7], [6, 5, 4], [3, 2, 1]])

    # 测试加法
    print("矩阵加法:")
    print(m1 + m2)

    # 测试标量乘法
    print("标量乘法 (m1 * 2):")
    print(m1 * 2)

    # 测试矩阵乘法
    print("矩阵乘法:")
    print(m1 * m2)

    # 测试向量乘法
    vector = [1, 2, 3]
    print("向量乘法:", m1.multiply_vector(vector))

    # 测试行列式
    print("行列式:", m1.determinant())

    # 测试旋转矩阵
    rotation_matrix = Matrix3x3.create_rotation_matrix("y", math.pi / 2)
    print("Y轴旋转矩阵 (90度):")
    print(rotation_matrix)

    # 测试缩放矩阵
    scale_matrix = Matrix3x3.create_scale_matrix(2, 3, 4)
    print("缩放矩阵:")
    print(scale_matrix)

    # 测试投影矩阵
    projection_matrix = Matrix3x3.create_projection_matrix([1, 0, 0])
    print("投影矩阵 (法向量 [1, 0, 0]):")
    print(projection_matrix)

    # 测试反射矩阵
    reflection_matrix = Matrix3x3.create_reflection_matrix([1, 0, 0])
    print("反射矩阵 (法向量 [1, 0, 0]):")
    print(reflection_matrix)

    # 测试剪切矩阵
    shear_matrix = Matrix3x3.create_shear_matrix("x", "y", 2.0)
    print("剪切矩阵 (沿 x 轴，y 方向，因子 2.0):")
    print(shear_matrix)
