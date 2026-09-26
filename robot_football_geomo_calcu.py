"""
专门存放几何运算的函数
用于基本阵型与特定点的相关计算
"""
import math
import random
"""
判断传球条件
1.遍历安全区矩形
2.基于有利系数从高向低排序
3.在有利区选出理论传球位置I
4.过每个对手作持球机与位置I的连线垂线,按距离确定是否可以截获
5.如果可以,那么不传球;否则传球
x0, y0 = ball_pos
min_ds = float('inf')
for x, y in all_robot:
    dx = x0 - x
    dy = y0 - y
    ds = math.sqrt(dx ** 2 + dy ** 2)
    theta = math.atan2(dy, dx)
    if ds < min_ds:
        min_ds = ds
"""
# 距离和角度计算
def ds_theta_calcu(A: list, B: list):
    if A is None or B is None:
        print("输入格式有误!")
        return 0, 0, (0, 0)
    x1, y1 = A
    x2, y2 = B
    dx = x2 - x1
    dy = y2 - y1
    ds = math.sqrt(dx ** 2 + dy ** 2)
    theta = math.atan2(dy, dx)
    return ds, theta, (dx, dy)

# 包围盒中心选点法
def center_choose(points: list = None):
    if not points:
        print("未输入坐标点！")
        return None
    max_x = min_x = points[0][0]
    max_y = min_y = points[0][1]
    for x, y in points[1:]:
        if x > max_x:
            max_x = x
        elif x < min_x:
            min_x = x
        if y > max_y:
            max_y = y
        elif y < min_y:
            min_y = y    
    cx = (min_x + max_x) / 2
    cy = (min_y + max_y) / 2
    return (cx, cy)

# 随机选点法
def random_choose(points: list):
    if points:
        n = len(points)
        p = 1 / n
        pro = [p for _ in range(len(points))]
        point_list = random.choices(points, weights = pro, k = 1)
        return point_list[0]

# 用于实现4人基本阵型变幻
def format_shift(frame: int = 0, ori_format: list = None, 
                 K: float = 1.0, A: float = 0.0):
    # ps:阵型中心位置需要更新，后续补充此逻辑
    x1, y1 = ori_format[0]
    x2, y2 = ori_format[1]
    x3, y3 = ori_format[2] 
    x4, y4 = ori_format[3]
    x0 = (x1 + x2 + x3 + x4) / 4
    y0 = (y1 + y2 + y3 + y4) / 4
    # 横纵偏移量
    diff_1 = [x1 - x0, y1 - y0]
    diff_2 = [x2 - x0, y2 - y0]
    diff_3 = [x3 - x0, y3 - y0]
    diff_4 = [x4 - x0, y4 - y0]
    diff_list = [diff_1, diff_2, diff_3, diff_4]
    if frame >= 1:
        bas_format = []
        # 放缩，旋转变换
        for dx, dy in diff_list:
            rad = math.hypot(dx, dy)
            new_rad = K * rad
            theta = math.atan2(dy, dx)
            alpha = theta + A
            new_dx = new_rad * math.cos(alpha)
            new_dy = new_rad * math.sin(alpha)
            x = x0 + new_dx
            y = y0 + new_dy
            bas_format.append((x, y))
        print("阵型更新成功，已返回新位置")
    else:
        print("机器人未离开初始位置，阵型更新失败")
        return None
    return bas_format