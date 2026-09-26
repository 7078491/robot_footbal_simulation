"""
基于对有利区域的计算找出可行的动态传球区域
通过向对手空当传球，队友跑合适位置的方式创造进攻机会
依据场地结构,设置静态权重
安全区与危险区计算
1.将全场切分为若干等大小矩形
2.分别取小矩形的中心，计算该时刻中心到每一台机器人的距离，加入列表
3.对双方的距离列表取出最小值比较
4.离我方更近是安全区，否则为危险区
有利区计算:
1.遍历所有对手，分别作出持球机与对方连线
2.作中垂线，找出中垂线近端
3.找出持球机与对手球门两角所成的三角形区域
4.找出中垂线近端区与三角形的交集区域作为有利区
ps:中垂线算法逻辑可行，但难以操作，改用划分小矩形网格的逻辑实现
"""
from PIL import ImageDraw
from robot_football_geomo_calcu import ds_theta_calcu
from robot_football_base import (LINE, HEIGHT, OPP_COLOR, OUR_COLOR,
                                 DANGER_COLOR, SAFE_COLOR, HOLDER, 
                                 BENEFIT_COLOR, SECT_LINE_COLOR, THREAT_COLOR)
from robot_football_field_draw import draw_lines
import math
# 基于位置反向获得索引
def set_index(best_points: list = None, mesh_dict: dict = None) -> dict:
    if not best_points:
        print("有利区为空！")
        return mesh_dict
    grid_state = mesh_dict["grid_state"]
    rows = mesh_dict["rows"]
    cols = mesh_dict["cols"]
    c_line = mesh_dict["c_line"]
    c_height = mesh_dict["c_height"]
    marked_count = 0
    for pos in best_points:
        x, y = pos
        col = int(x // c_line)
        row = int(y // c_height)
        # 边界检查
        if 0 <= row < rows and 0 <= col < cols:
            grid_state[row][col] = 2
            marked_count += 1
        else:
            print("给定点超出边界！")
    print(f"成功标记有利区：{marked_count}")
    return mesh_dict
# 绝对安全区与非安全区网格划分
def mesh_division(args_list: list = None, frame_locat_dict: dict = None, 
                  line: int = LINE, height: int = HEIGHT):
    # 处理我方视角的区域分布图,默认我方持球
    hol_team = "our"
    attack_color = OPP_COLOR
    our_pos_list = []
    opp_pos_list = []
    if args_list:
        # 找出持球队伍
        hol = args_list[HOLDER]
        hol_team = hol["holder.team"] if hol["holder.team"] else "our"
        if hol_team == "our":
            attack_color = OPP_COLOR
        elif hol_team == "opp":
            attack_color = OUR_COLOR
    if frame_locat_dict != None:
        for field, value in frame_locat_dict.items():
            if value != None:
                if field.startswith("our"):
                    our_pos_list.append(value)
                elif field.startswith("opp"):
                    opp_pos_list.append(value)
    # 行，列，安全区，非安全区初始化
    cols, rows = line // 25, height // 20
    c_line, c_height = line // cols, height // rows
    safe_points, dang_points = [], []
    best_points = set()
    threat_list = []
    # 初始化网格列表值为0，代表未更新
    grid_state = [[0 for _ in range(cols)] for _ in range(rows)]
    flat_pos = []
    for row in range(rows):
        for col in range(cols):
            # 网格左下右上角,获得网格中心
            left_x, top_y = col * c_line, row * c_height
            right_x, bot_y = (col+1) * c_line, (row+1) * c_height
            pos = [(left_x+right_x)/2,(top_y+bot_y)/2]
            flat_pos.append(pos)
            # 初始化最大
            min_opp_ds = float('inf')
            if opp_pos_list != None:
                for opp_pos in opp_pos_list:
                    ds1, *_ = ds_theta_calcu(pos, opp_pos)
                    if ds1 < min_opp_ds:
                        min_opp_ds = ds1
            min_our_ds = float('inf')
            if our_pos_list != None:
                for our_pos in our_pos_list:
                    ds2, *_ = ds_theta_calcu(pos, our_pos)
                    if ds2 < min_our_ds:
                        min_our_ds = ds2
            delta = min_our_ds - min_opp_ds
            if delta <= 0:
                # 将安全区赋值为1
                grid_state[row][col] = 1
                safe_points.append(pos)
            else:
                # 非安全区赋值为-1
                grid_state[row][col] = -1
                dang_points.append(pos)
    # 遍历安全区
    match hol_team:
        case "our":
            style = "有利"
            for pos in safe_points:
                # 计算持球方有利系数最高的区域
                benefit, ds = benefit_generate(pos, attack_color)
                if ds <= line*2/3:
                    threat_list.append((benefit, pos))
        case "opp":
            style = "威胁"
            for pos in dang_points:
                benefit, ds = benefit_generate(pos, attack_color)
                if ds <= line*2/3:
                    threat_list.append((benefit, pos))
        case _:
            style = "?"
            threat_list = []
    if 0 < len(threat_list) <= 25:
        for benefit, pos in threat_list:
            best_points.add(tuple(pos))
        print(f"系数最大的{style}区矩形中心数为:{len(threat_list)}, \n系数最大为:{threat_list[0][0]:.2f}")
    elif len(threat_list) > 25:
        # 取出25个系数最大的点作为有利区
        sorted_threat = sorted(threat_list, key = lambda x: x[0], reverse = True)
        top_25 = sorted_threat[:25]
        for benefit, pos in top_25:
            best_points.add(tuple(pos))
        print(f"前25个系数最大矩形中心的{style}系数最大值: {top_25[0][0]:.2f}")
    best_points = list(best_points)
    mesh_dict_0 = {
            "hol_team": hol_team,
            "cols": cols,
            "rows": rows,
            "c_line": c_line,
            "c_height": c_height,
            "flat_pos": flat_pos,
            "grid_state": grid_state
        }
    mesh_dict = set_index(best_points, mesh_dict_0)
    return best_points, mesh_dict, safe_points, dang_points
# 网格可视化区域,字典封装参数
def mesh_visual(img: any = None, mesh_dict: dict = None) -> any:
    if mesh_dict is None:
        print("网格数据未传入!")
        return img
    cols = mesh_dict["cols"]
    rows = mesh_dict["rows"]
    c_line = mesh_dict["c_line"]
    c_height = mesh_dict["c_height"]
    grid_state = mesh_dict["grid_state"]
    hol_team = mesh_dict["hol_team"]
    # 利用集合特性去重
    boundary_set = set()
    draw = ImageDraw.Draw(img)
    # 遍历网格(先纵后横)
    for row in range(rows):
        for col in range(cols):
            left_x, top_y = col * c_line, row * c_height
            right_x, bot_y = (col+1) * c_line, (row+1) * c_height
            if grid_state[row][col] == 1:
                # 安全区
                draw.rectangle([left_x, top_y, right_x, bot_y], fill = SAFE_COLOR)
            elif grid_state[row][col] == -1:
                # 非安全区
                draw.rectangle([left_x, top_y, right_x, bot_y], fill = DANGER_COLOR)
            elif grid_state[row][col] == 2:
                if hol_team == "our":
                    # 有利区
                    draw.rectangle([left_x, top_y, right_x, bot_y], fill = BENEFIT_COLOR)
                elif hol_team == "opp":
                    # 威胁区
                    draw.rectangle([left_x, top_y, right_x, bot_y], fill = THREAT_COLOR)
            # 边界绘制
            cur_state = grid_state[row][col]
            if col + 1 < cols:
                if grid_state[row][col+1] != cur_state:
                    line_x = (col + 1) * c_line
                    p1 = (line_x, top_y)
                    p2 = (line_x, bot_y)
                    # 元组，逐个元素比较，确保线段顺序正确
                    if p1[0] > p2[0] or (p1[0] == p2[0] and p1[1] > p2[1]):
                        boundary_set.add((p2, p1))
                    else:
                        boundary_set.add((p1, p2))
            if row + 1 < rows:
                if grid_state[row+1][col] != cur_state:
                    line_y = (row + 1) * c_height
                    p1 = (left_x, line_y)
                    p2 = (right_x, line_y)
                    if p1[0] > p2[0] or (p1[0] == p2[0] and p1[1] > p2[1]):
                        boundary_set.add((p2, p1))
                    else:
                        boundary_set.add((p1, p2))
    # 生成完整分界线列表存储
    # ps:bound是含有一堆线段列表的二维列表,用for循环解包
    boundary_lines = [[p1, p2] for p1, p2 in boundary_set]
    for bound in boundary_lines:
        draw_lines(img, bound, 3, 1, SECT_LINE_COLOR)
    print("区域情况已更新.")
    return img
# 有利区评定:权重系数表与调用
def benefit_generate(pos: list = None, opp_color: str = "red"):
    # 基于给定点到对方球门中点距离和角度赋予有利系数
    # ps:传入的是对手颜色，用于获取对方球门位置
    middle = goal(opp_color)
    def cal_L(ds: float):
        if ds is None or ds < 0:
            ds = 0.0
        points = [
        (0.0,   1.5),
        (30.0,  1.2),
        (60.0,  0.9),
        (90.0,  0.7),
        (120.0, 0.6),
        (150.0, 0.5),
        (180.0, 0.3),
        (210.0, 0.2),
        (240.0, 0.1)]
        if ds >= 240.0:
            return 0.1
        # 找到 ds 所在区间
        for i in range(len(points) - 1):
            d0, l0 = points[i]
            d1, l1 = points[i + 1]
            if d0 <= ds <= d1:
                t = (ds - d0) / (d1 - d0)
                return l0 + (l1 - l0) * t
        return 0.1
    def cal_A(abs_degree: float, opp_color: str):
        if abs_degree is None:
            abs_degree = 0.0
        abs_degree = abs(abs_degree)
        if abs_degree > 180.0:
            abs_degree = 360.0 - abs_degree
        if opp_color == "red":
            points = [
            (90.0,  0.2),
            (100.0, 0.4),
            (110.0, 0.5),
            (120.0, 0.7),
            (130.0, 0.8),
            (140.0, 0.9),
            (150.0, 1.1),
            (160.0, 1.3),
            (170.0, 1.4),
            (180.0, 1.5)]
            # 小于 90 视为超出正常范围，按最偏处理
            if abs_degree < 90.0:
                return 0.2
            if abs_degree > 180.0:
                return 1.5
        elif opp_color == "blue":
            points = [
            (0.0,  0.2),
            (10.0, 0.4),
            (20.0, 0.5),
            (30.0, 0.7),
            (40.0, 0.8),
            (50.0, 0.9),
            (60.0, 1.1),
            (70.0, 1.3),
            (80.0, 1.4),
            (90.0, 1.5)]
            if abs_degree < 0.0:
                return 0.2
            if abs_degree > 90.0:
                return 0.8
        else:
            return 0.2

    # 分段线性插值
        for i in range(len(points) - 1):
            a0, v0 = points[i]
            a1, v1 = points[i + 1]
            if a0 <= abs_degree <= a1:
                t = (abs_degree - a0) / (a1 - a0)
                return v0 + (v1 - v0) * t
        return points[-1][1]
    if pos is None:
        pos = [0, 0]
    ds, theta, *_ = ds_theta_calcu(pos, middle)
    # 函数返回点到对方球门中央的位置与角度权重
    # 基于机器人的位置，角度赋予权重，综合计算得到有利系数
    L = cal_L(ds)
    if theta is None:
        theta = 0.0
    degree = math.degrees(theta) % 360.0
    abs_degree = abs(degree)
    if abs_degree > 180.0:
        abs_degree = 360.0 - abs_degree
    A = cal_A(abs_degree, opp_color)
    pos_benefit = L * A
    pos_benefit = round(pos_benefit, 4)
    return pos_benefit, ds
# 找出进攻球员与对手球门夹角区域
def goal(opp_color: str = None, pos: list = None, 
         line: int = LINE, height: int = HEIGHT):
    if opp_color == "red":
        opp_up_goal = [round(line/256), round(height*5/12)]
        opp_low_goal = [round(line/256), round(height*7/12)]
    elif opp_color == "blue":
        opp_up_goal = [round(line*255/256), round(height*5/12)]
        opp_low_goal = [round(line*255/256), round(height*7/12)]
    middle = [(opp_low_goal[0]+opp_up_goal[0])/2, (opp_low_goal[1]+opp_up_goal[1])/2]
    if pos != None:
        goal_points = [pos, opp_low_goal, opp_up_goal]
        return middle, goal_points
    return middle
# 静态区域权重
def still_region_weights(pos: list, state: str, 
                         line: int = LINE, height: int = HEIGHT):
    x, y = pos
    # line1 = [(0.625*line, 0),(0.625*line, height)]
    # line2 = [(0.75*line, height),(0.75*line, 0)]
    # line3 = [(0.25*line, 0),(0.25*line, height)]
    # line4 = [(0.375*line, height),(0.375*line, 0)]
    # line5 = [(0, round(height/3)),(0.25*line, round(height/3))]
    # line6 = [(0, round(height*2/3)),(0.25*line, round(height*2/3))]
    # line7 = [(0.75*line, round(height/3)),(line, round(height/3))]
    # line8 = [(0.75*line, round(height*2/3)),(line, round(height*2/3))]
    # 四角
    corner = (0 <= x <= round(line/3) or
         round(line*2/3) <= x <= line) and (0 <= y <= round(height/3) or 
         round(height*2/3) <= y <= height)
    cor_center = [[round(line/6), round(height/6)], [round(line/6), round(height*5/6)], 
                  [round(line*5/6), round(height/6)], [round(line*5/6), round(height*5/6)]]
    # 两禁区
    goal = (0 <= x <= round(line/3) or
         round(line*2/3) <= x <= line) and (round(height/3) <= y <= round(height*2/3))
    goal_center = [[round(line/6), round(height/2)], [round(line*5/6), round(height/2)]]
    # 半场中间
    half_mid = (round(line/3) <= x <= round(line*3/8) or
         round(line*5/8) <= x <= round(line*2/3)) and (0 <= y <= height)
    half_mid_center = [[round(line*17/48), round(height/2)], [round(line*31/48), round(height/2)]]
    # 全场中线
    all_mid = (round(line*3/8) <= x <= round(line*5/8) and 0 <= y <= height)
    all_center = [round(line/2), round(height/2)]
    # 字典 = {"区域号": [进攻权重, 防守权重]}
    still_region_dict = {"corner":[2, -2],
                         "goal":[4, -1],
                         "half_mid":[3, -3],
                         "all_mid":[1, -4]}
    match state:
        case "进攻":
            if corner:
                name = "corner"
            elif goal:
                name = "goal"
            elif half_mid:
                name = "half_mid"
            elif all_mid:
                name = "all_mid"
            print(f"在{state}时({x:.1f}, {y:.1f})属于{name}区域,权重为{still_region_dict[name][0]}")
            return still_region_dict[name][0]
        case "防守":
            if corner:
                name = "corner"
            elif goal:
                name = "goal"
            elif half_mid:
                name = "half_mid"
            elif all_mid:
                name = "all_mid"
            print(f"在{state}时({x:.1f}, {y:.1f})属于{name}区域,权重为{still_region_dict[name][0]}")
            return still_region_dict[name][1]
        case _:
            print("未传入合法状态，无法返回权重")
            return None

    