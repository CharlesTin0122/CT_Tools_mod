import numbers  # 引入 numbers 模块来检查是否为数字
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
        return True

    def __str__(self):
        """
        返回矩阵的字符串表示形式，以便于打印。
        """
        matrix_str = ""
        for row in self.data:
            # 使用格式化字符串确保对齐,宽度是8位，精确到小数点后两位
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
        # 情况1: 标量乘法 (e.g., matrix * 3)
        if isinstance(other, numbers.Number):  # 检查other是否为数字
            result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(3):
                for j in range(3):
                    result_data[i][j] = self.data[i][j] * other
            return Matrix3x3(result_data)

        # 情况2: 矩阵乘法
        if isinstance(other, Matrix3x3):
            result_data = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
            for i in range(3):  # 遍历结果矩阵的每一行
                for j in range(3):  # 遍历结果矩阵的每一列
                    for k in range(3):  # 遍历计算当前[i][j]位置的值
                        # 这一步是：将self的第i行第k列 × other的第k行第j列，累加到结果中
                        # R[i][j] = A[i][0]*B[0][j] + A[i][1]*B[1][j] + A[i][2]*B[2][j]
                        result_data[i][j] += self.data[i][k] * other.data[k][j]
            return Matrix3x3(result_data)

        # 不支持的类型
        raise TypeError(f"不支持 Matrix3x3 和 {type(other).__name__} 之间的乘法。")

    def __rmul__(self, other):
        """
        重载右乘法运算符 '*'，用于处理标量在前的情况 (e.g., 3 * matrix)。
        """
        # 这个方法会调用常规的 __mul__ 方法，避免代码重复。
        return self.__mul__(other)

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
        是静态方法 (static method)。静态方法是定义在类中的函数，但它不依赖于任何特定的实例（即它不需要 self 参数）。
        这非常适合创建像旋转矩阵这样的“工厂”函数，因为它的目的就是生成一个新的矩阵，而不是修改一个已有的矩阵。

        :param axis: 旋转轴，必须是 'x', 'y', 或 'z' (不区分大小写)。
        :param angle_rad: 旋转角度，以弧度为单位。
        :return: 一个代表旋转的 Matrix3x3 对象。
        """
        c = math.cos(angle_rad)
        s = math.sin(angle_rad)

        axis = axis.lower()  # 转换为小写以支持 'X', 'Y', 'Z'

        if axis == "x":
            return Matrix3x3([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == "y":
            return Matrix3x3([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        elif axis == "z":
            return Matrix3x3([[c, -s, 0], [s, c, 0], [0, 0, 1]])
        else:
            raise ValueError("旋转轴必须是 'x', 'y', 或 'z'")

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
        # 1. 确保法向量是一个单位向量（长度为1）
        nx, ny, nz = normal_vector
        length_sq = nx**2 + ny**2 + nz**2

        if length_sq == 0:
            raise ValueError("法向量不能是零向量。")

        # 如果长度不是1，则进行归一化
        if abs(length_sq - 1.0) > 1e-9:  # 使用一个小的容差来比较浮点数
            length = math.sqrt(length_sq)
            nx /= length
            ny /= length
            nz /= length

        # 2. 计算投影矩阵 P = I - n * n^T
        #    其中 I是单位矩阵, n是单位法向量, n^T是n的转置
        #    n * n^T (外积) 计算如下:
        #    [[nx*nx, nx*ny, nx*nz],
        #     [ny*nx, ny*ny, ny*nz],
        #     [nz*nx, nz*ny, nz*nz]]

        #    投影矩阵 P 的元素为:
        #    P_ij = delta_ij - n_i * n_j   (其中 delta_ij 是克罗内克δ)

        data = [
            [1 - nx * nx, -nx * ny, -nx * nz],
            [-ny * nx, 1 - ny * ny, -ny * nz],
            [-nz * nx, -nz * ny, 1 - nz * nz],
        ]

        return Matrix3x3(data)


# --- 使用示例 ---
if __name__ == "__main__":
    # 创建一个旋转矩阵
    rotation_matrix = Matrix3x3.create_rotation_matrix("y", math.pi / 2)
