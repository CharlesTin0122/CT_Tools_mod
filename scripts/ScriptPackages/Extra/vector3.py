import math


class Vector3:
    """三维向量"""

    def __init__(self, x=0.0, y=0.0, z=0.0):
        # 初始化向量
        self.x = x
        self.y = y
        self.z = z

    def __repr__(self):
        # 返回向量的字符串表示
        return f"Vector3({self.x}, {self.y}, {self.z})"

    def __add__(self, other):
        # 返回两个向量的和
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        # 返回两个向量的差
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        # 向量与标量相乘
        return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        # 向量与标量相除
        return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

    def zero(self):
        # 返回零向量
        return Vector3(0, 0, 0)

    def opposite(self):
        # 返回向量的反向
        return Vector3(-self.x, -self.y, -self.z)

    def length(self):
        # 返回向量的长度
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def normalize(self):
        # 将向量规范化（单位化）
        len = self.length()
        if len != 0:
            return self / len
        raise ValueError("Cannot normalize a zero-length vector")

    def dot(self, other):
        # 计算两个向量的点积
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        # 计算两个向量的叉积
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def angle_radians(self, other):
        # 计算两个向量的夹角（弧度制）
        dot_product = self.dot(other)
        len_self = self.length()
        len_other = other.length()
        if len_self == 0 or len_other == 0:
            raise ValueError("Cannot compute angle with zero-length vector")
        cos_theta = dot_product / (len_self * len_other)
        return math.acos(min(1, max(cos_theta, -1)))  # 确保cos_theta在[-1, 1]之间

    def angle_degrees(self, other):
        # 计算两个向量的夹角（度制）
        return math.degrees(self.angle(other))

    def distance(self, other):
        # 计算两点之间的距离
        return math.sqrt(
            (self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2
        )

    def to_list(self):
        return [self.x, self.y, self.z]

    def to_tuple(self):
        return (self.x, self.y, self.z)


if __name__ == "__main__":
    # 测试
    v1 = Vector3(1, 2, 3)
    v2 = Vector3(4, 5, 6)

    print(f"v1: {v1}")
    print(f"v2: {v2}")
    print(f"v1 + v2: {v1 + v2}")
    print(f"v1 - v2: {v1 - v2}")
    print(f"v1 * 3: {v1 * 3}")

    print(f"v1 length: {v1.length()}")
    print(f"v1 normalized: {v1.normalize()}")

    print(f"v1 zero: {v1.zero()}")
    print(f"v1 opposite: {v1.opposite()}")
