import math


class Quaternion:
    """四元数类，用于表示和处理三维空间中的旋转"""

    def __init__(self, w, x, y, z):
        """初始化四元数，w为实部，x,y,z为虚部"""
        self.w = float(w)
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __str__(self):
        """返回四元数的字符串表示"""
        return f"{self.w} + {self.x}i + {self.y}j + {self.z}k"

    def __add__(self, other):
        """四元数加法"""
        return Quaternion(
            self.w + other.w, self.x + other.x, self.y + other.y, self.z + other.z
        )

    def __mul__(self, other):
        """四元数乘法"""
        w = self.w * other.w - self.x * other.x - self.y * other.y - self.z * other.z
        x = self.w * other.x + self.x * other.w + self.y * other.z - self.z * other.y
        y = self.w * other.y - self.x * other.z + self.y * other.w + self.z * other.x
        z = self.w * other.z + self.x * other.y - self.y * other.x + self.z * other.w
        return Quaternion(w, x, y, z)

    def conjugate(self):
        """返回四元数的共轭"""
        return Quaternion(self.w, -self.x, -self.y, -self.z)

    def norm(self):
        """计算四元数的模长"""
        return math.sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        """返回归一化的四元数"""
        n = self.norm()
        if n == 0:
            raise ValueError("无法归一化零四元数")
        return Quaternion(self.w / n, self.x / n, self.y / n, self.z / n)

    @staticmethod
    def from_axis_angle(axis, angle):
        """从轴-角表示创建四元数
        参数:
            axis: 旋转轴（列表或元组 [x, y, z]）
            angle: 旋转角度（弧度）
        """
        # 归一化旋转轴
        ax, ay, az = axis
        mag = math.sqrt(ax**2 + ay**2 + az**2)
        if mag == 0:
            raise ValueError("旋转轴不能为零向量")
        ax, ay, az = ax / mag, ay / mag, az / mag
        # 计算四元数
        half_angle = angle / 2
        w = math.cos(half_angle)
        sin_half = math.sin(half_angle)
        x, y, z = ax * sin_half, ay * sin_half, az * sin_half
        return Quaternion(w, x, y, z).normalize()

    def to_rotation_matrix(self):
        """将四元数转换为3x3旋转矩阵"""
        w, x, y, z = self.w, self.x, self.y, self.z
        return [
            [1 - 2 * y * y - 2 * z * z, 2 * x * y - 2 * w * z, 2 * x * z + 2 * w * y],
            [2 * x * y + 2 * w * z, 1 - 2 * x * x - 2 * z * z, 2 * y * z - 2 * w * x],
            [2 * x * z - 2 * w * y, 2 * y * z + 2 * w * x, 1 - 2 * x * x - 2 * y * y],
        ]

    def rotate_vector(self, vector):
        """使用四元数旋转三维向量
        参数:
            vector: 要旋转的向量（列表或元组 [x, y, z]）
        """
        # 将向量转换为纯四元数 (w=0)
        v_x, v_y, v_z = vector
        v_quat = Quaternion(0, v_x, v_y, v_z)
        # 计算旋转: q * v * q^-1
        q_conj = self.conjugate()
        result = self * v_quat * q_conj
        return [result.x, result.y, result.z]

    def to_axis_angle(self):
        """将四元数转换为轴-角表示
        返回:
            axis: 旋转轴（列表 [x, y, z]）
            angle: 旋转角度（弧度）
        """
        q = self.normalize()
        angle = 2 * math.acos(q.w)
        if abs(angle) < 1e-10:  # 无旋转
            return [1, 0, 0], 0.0
        s = math.sqrt(1 - q.w**2)
        if s < 1e-10:  # 避免除零
            return [1, 0, 0], angle
        axis = [q.x / s, q.y / s, q.z / s]
        return axis, angle

    @staticmethod
    def slerp(q1, q2, t):
        """球面线性插值（SLERP）从q1到q2
        参数:
            q1: 起始四元数
            q2: 终止四元数
            t: 插值参数，范围 [0, 1]
        """
        # 确保输入四元数为单位四元数
        q1 = q1.normalize()
        q2 = q2.normalize()

        # 计算点积
        dot = q1.w * q2.w + q1.x * q2.x + q1.y * q2.y + q1.z * q2.z

        # 处理 q2 和 -q2 表示相同旋转的情况
        if dot < 0:
            q2 = Quaternion(-q2.w, -q2.x, -q2.y, -q2.z)
            dot = -dot

        # 如果四元数几乎相同，直接返回线性插值
        if dot > 0.9995:
            result = Quaternion(
                q1.w + t * (q2.w - q1.w),
                q1.x + t * (q2.x - q1.x),
                q1.y + t * (q2.y - q1.y),
                q1.z + t * (q2.z - q1.z),
            )
            return result.normalize()

        # 计算插值角度
        theta = math.acos(dot)
        sin_theta = math.sin(theta)

        # 计算插值权重
        s1 = math.sin((1 - t) * theta) / sin_theta
        s2 = math.sin(t * theta) / sin_theta

        # 插值
        result = Quaternion(
            s1 * q1.w + s2 * q2.w,
            s1 * q1.x + s2 * q2.x,
            s1 * q1.y + s2 * q2.y,
            s1 * q1.z + s2 * q2.z,
        )
        return result.normalize()


# 示例用法
if __name__ == "__main__":
    # 创建绕 z 轴旋转 90 度的四元数
    q1 = Quaternion.from_axis_angle([0, 0, 1], math.pi / 2)
    print(f"q1: {q1}")

    # 创建绕 z 轴旋转 180 度的四元数
    q2 = Quaternion.from_axis_angle([0, 0, 1], math.pi)
    print(f"q2: {q2}")

    # 旋转向量 [1, 0, 0]
    v = [1, 0, 0]
    rotated_v = q1.rotate_vector(v)
    print(f"旋转后的向量: {rotated_v}")

    # 转换为旋转矩阵
    R = q1.to_rotation_matrix()
    print(f"旋转矩阵:\n{R}")

    # 转换为轴-角表示
    axis, angle = q1.to_axis_angle()
    print(f"旋转轴: {axis}, 角度: {angle} 弧度")

    # SLERP 插值 (t=0.5)
    q_interp = Quaternion.slerp(q1, q2, 0.5)
    print(f"SLERP 插值 (t=0.5): {q_interp}")
