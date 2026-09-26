"""
规则库：
    动作优先级判断标准
        1.本机位置/朝向"
        2.足球位置/速度/方向
        3.敌我双方分布
            3.1 敌方位置列表
            3.2 我方位置列表
    规则列表
        1.进攻时，若我方机器人带球进入射门范围且无敌方遮挡，
          射门
        2.防守时，若敌方机器人带球越过中线接近我方球门，
          在敌人与我方球门间且离敌方最近的机器人尝试抢断
        3.
----------------------------------------
动作序列与概率
逻辑示例:
1. 传球
    条件:机器人持球,目标传球方向与朝向夹角小于45度,
        传球对象处于有利区且传球路线无遮挡
    执行:进攻情况:传球到进攻权重尽量大的指定区域内
        防守情况:传球到防守权重尽量大的指定区域内
    概率:
2. 防守
    条件:敌方持球越过半场,机器人在敌方与我方球门之间,距离无条件限制
    执行:第一优先:直接阻断持球者与我方球门的连线,已满足则执行第二优先
        第二优先:切断敌方可能的传球路线
    概率:
3. 带球
    条件:机器人持球,最近的敌方离自己距离大于24或无队友处于有利区内
    执行:进攻情况:带球到进攻权重尽量大的指定区域内
        防守情况:带球到防守权重尽量大的指定区域内
    概率:
4. 射门
    条件:机器人持球,离对手球门较近或进入指定范围,且无敌方遮挡,处于有利区内
    执行:选定角度射门
    概率:
5. 抢断
    条件:敌方持球,我方在敌方与我方球门之间,且离敌方最近
    执行:在满足切断敌方与我方球门连线条件下,前逼尝试抢断
        抢断成功必要条件:机器人离足球距离不大于10且足球在自己朝向90度范围内
        成功率: 0.3 * k
    概率:
简化处理:
    1,2共同条件:机器人正前方有遮挡
1. 左移
    执行: 机器人向左侧移动指定长度像素
2. 右移
    执行: 机器人向右侧移动指定长度像素
3. 保持距离
    条件:对手持球
    执行: 机器人与对手保持指定距离
4. 退守
    条件:机器人在对手,球和己方球门连线上
    执行:机器人向后退指定长度像素  
5. 控场
    条件:机器人防守状态,对手有至少俩人
    执行:mid_1 = 最近俩人中点
        mid_2 = 球与mid_1中点
        跑向mid_2
"""
from robot_football_rule_base import rules_choose
from robot_football_base import (LINE, HEIGHT, OUR_COLOR, OPP_COLOR,
                                rules_dict, our_conditions, opp_conditions)
# 初始化阵型，选择战术
# 函数返回(初始，基本)阵型和路线点列表，传球序列
def choose_strategy(color: str = None, strategy: str = None, 
                    line: int = LINE, height: int = HEIGHT):
    # 战术库：从前向后，从上到下排序
    # 所有阵型均按照机器人编号1-5排序
    if color == OUR_COLOR:
        match strategy:
            case "漏斗阵":
# ps: 有触发条件后面再补，基本阵型不考虑守门员(4人)
# 战术A:均衡,2-2-1阵型
# 左------上------右
#     1(持球)
#          3
#               5
#          4
#     2
# 前------下------后
                our_ori_format = [[line*2/3, height*3/8], 
[line*2/3, height*5/8], [line*5/6, height*5/12], 
[line*5/6, height*7/12], [line*61/64, height/2]]
                our_bas_format = [[line*2/3, height*3/8], 
[line*2/3, height*5/8], [line*5/6, height*5/12], 
[line*5/6, height*7/12]]
# 行进路线(len = 8)
                r1 = [(0.64*line, 0.36*height), (0.59*line, 0.36*height), 
(0.52*line, 0.34*height), (0.46*line, 0.29*height), 
(0.47*line, 0.20*height), (0.55*line, 0.20*height), 
(0.54*line, 0.26*height), (0.45*line, 0.33*height)]
                r2 = [(0.63*line, 0.60*height), (0.60*line, 0.56*height), 
(0.54*line, 0.56*height), (0.48*line, 0.52*height), 
(0.53*line, 0.47*height), (0.60*line, 0.50*height), 
(0.57*line, 0.68*height), (0.50*line, 0.76*height)]
                r3 = [(0.81*line, 0.36*height), (0.76*line, 0.31*height), 
(0.78*line, 0.26*height), (0.81*line, 0.19*height), 
(0.74*line, 0.13*height), (0.73*line, 0.31*height), 
(0.72*line, 0.39*height), (0.67*line, 0.46*height)]
                r4 = [(0.81*line, 0.58*height), (0.77*line, 0.60*height), 
(0.73*line, 0.66*height), (0.69*line, 0.63*height), 
(0.65*line, 0.58*height), (0.68*line, 0.56*height), 
(0.73*line, 0.57*height), (0.71*line, 0.60*height)]
                r5 = [(0.92*line, 0.48*height), (0.89*line, 0.44*height), 
(0.88*line, 0.39*height), (0.87*line, 0.44*height), 
(0.87*line, 0.49*height), (0.87*line, 0.54*height), 
(0.85*line, 0.52*height), (0.89*line, 0.49*height)]
                our_forward_points = [r1, r2, r3, r4, r5]
# 触发条件
                return our_ori_format, our_bas_format, our_forward_points
            case "锋矢阵":
# 战术B:进攻,3-1-1阵型
# 左------上------右
#     2(持球)
#   1     4     5
#     3
# 前------下------后
                our_ori_format = [[line*5/8, height/2], 
[line*3/4, height*3/8], [line*3/4, height*5/8], 
[line*5/6, height/2], [line*61/64, height/2]]
                our_bas_format = [[line*5/8, height/2], 
[line*3/4, height*3/8], [line*3/4, height*5/8], 
[line*5/6, height/2]]
                r1 = [(0.64*line, 0.36*height), (0.59*line, 0.36*height), 
(0.52*line, 0.34*height), (0.46*line, 0.29*height), 
(0.47*line, 0.20*height), (0.55*line, 0.20*height), 
(0.54*line, 0.26*height), (0.45*line, 0.33*height)]
                r2 = [(0.63*line, 0.60*height), (0.60*line, 0.56*height), 
(0.54*line, 0.56*height), (0.48*line, 0.52*height), 
(0.53*line, 0.47*height), (0.60*line, 0.50*height), 
(0.57*line, 0.68*height), (0.50*line, 0.76*height)]
                r3 = [(0.81*line, 0.36*height), (0.76*line, 0.31*height), 
(0.78*line, 0.26*height), (0.81*line, 0.19*height), 
(0.74*line, 0.13*height), (0.73*line, 0.31*height), 
(0.72*line, 0.39*height), (0.67*line, 0.46*height)]
                r4 = [(0.81*line, 0.58*height), (0.77*line, 0.60*height), 
(0.73*line, 0.66*height), (0.69*line, 0.63*height), 
(0.65*line, 0.58*height), (0.68*line, 0.56*height), 
(0.73*line, 0.57*height), (0.71*line, 0.60*height)]
                r5 = [(0.92*line, 0.48*height), (0.89*line, 0.44*height), 
(0.88*line, 0.39*height), (0.87*line, 0.44*height), 
(0.87*line, 0.49*height), (0.87*line, 0.54*height), 
(0.85*line, 0.52*height), (0.89*line, 0.49*height)]
                our_forward_points = [r1, r2, r3, r4, r5]
                return our_ori_format, our_bas_format, our_forward_points
            case "铁锅阵":
# 左------上------右
#     1(持球)
#          3
#               
#          4
#     2
# 前------下------后
                our_ori_format = [[line*2/3, height*3/8], [line*2/3, height*5/8], 
[line*5/6, height*5/12], [line*5/6, height*7/12]]
                our_bas_format = [[line*2/3, height*3/8], [line*2/3, height*5/8], 
[line*5/6, height*5/12], [line*5/6, height*7/12]]
                our_forward_points = []
                return our_ori_format, our_bas_format, our_forward_points
            case "双人成行":
# 2机练习
# 左------------右
#     1  
#
#     2
# 前------------后
                our_ori_format = [[line*3/4, height*3/8], 
                                  [line*3/4, height*5/8]]
                our_bas_format = [[line*3/4, height*3/8], 
                                  [line*3/4, height*5/8]]
                r1 = [(0.71*line, 0.36*height), 
(0.65*line, 0.33*height), (0.54*line, 0.31*height), 
(0.44*line, 0.30*height), (0.33*line, 0.34*height), 
(0.25*line, 0.41*height), (0.19*line, 0.37*height),
(0.17*line, 0.34*height), (0.14*line, 0.33*height)]
                r2 = [(0.71*line, 0.63*height), 
(0.66*line, 0.66*height), (0.59*line, 0.61*height), 
(0.53*line, 0.61*height), (0.44*line, 0.65*height), 
(0.36*line, 0.68*height), (0.26*line, 0.68*height), 
(0.21*line, 0.62*height), (0.16*line, 0.57*height)]
                our_forward_points = [r1, r2]
                return our_ori_format, our_bas_format, our_forward_points
            case _:
                print("未输入合法战术类型！")
                return None
    elif color == OPP_COLOR:
        match strategy:
            case "锋矢阵":
# 对手: 1-3-1阵型
# 左------------------右
#            2
#    5     4      1
#            3
# 后------------------前
                opp_ori_format = [[line*3/8, height/2], 
[line/4, height*3/8], [line/4, height*5/8], 
[line*11/48, height/2], [line/12, height/2]]
                opp_bas_format = []
# 行进路线(len = 8)
                r1 = [(0.41*line, 0.48*height), (0.46*line, 0.44*height), 
(0.48*line, 0.38*height), (0.52*line, 0.43*height), 
(0.49*line, 0.49*height), (0.50*line, 0.47*height), 
(0.50*line, 0.50*height), (0.56*line, 0.51*height)]
                r2 = [(0.28*line, 0.38*height), (0.31*line, 0.34*height), 
(0.34*line, 0.32*height), (0.38*line, 0.31*height), 
(0.41*line, 0.35*height), (0.47*line, 0.32*height), 
(0.51*line, 0.35*height), (0.47*line, 0.36*height)]
                r3 = [(0.29*line, 0.64*height), (0.33*line, 0.67*height), 
(0.39*line, 0.69*height), (0.43*line, 0.64*height), 
(0.49*line, 0.65*height), (0.45*line, 0.70*height), 
(0.47*line, 0.73*height), (0.52*line, 0.69*height)]
                r4 = [(0.24*line, 0.50*height), (0.27*line, 0.47*height), 
(0.30*line, 0.44*height), (0.36*line, 0.44*height), 
(0.37*line, 0.47*height), (0.35*line, 0.50*height), 
(0.33*line, 0.53*height), (0.34*line, 0.56*height)]
                r5 = [(0.11*line, 0.53*height), (0.15*line, 0.48*height), 
(0.18*line, 0.44*height), (0.14*line, 0.44*height), 
(0.12*line, 0.47*height), (0.14*line, 0.53*height), 
(0.12*line, 0.59*height), (0.07*line, 0.56*height)]
                opp_forward_points = [r1, r2, r3, r4, r5]
                return opp_ori_format, opp_bas_format, opp_forward_points
            case "铁锅阵":
# 左------上------右
#         1
#      3
#               
#      4
#         2
# 后------下------前
                opp_ori_format = [[line/3, height*3/8], [line/3, height*5/8], 
[line/6, height*5/12], [line/6, height*7/12]]
                opp_bas_format = []
                opp_forward_points = []
                return opp_ori_format, opp_bas_format, opp_forward_points
            case "双人成行":
# 2机练习
# 左------------右
#     1  
#
#     2
# 后------------前
                opp_ori_format = [[line/4, height*3/8], 
                                  [line/4, height*5/8]]
                r1 = [(0.28*line, 0.38*height), 
(0.37*line, 0.41*height), (0.43*line, 0.35*height)]
                r2 = [(0.31*line, 0.58*height), 
(0.37*line, 0.63*height), (0.40*line, 0.58*height)]
                opp_bas_format = []
                opp_forward_points = [r1, r2]
                return opp_ori_format, opp_bas_format, opp_forward_points
            case "单机模式":
                opp_pos = [line/12, height/2]
                opp_forward_points = [
(0.10*line, 0.46*height), (0.15*line, 0.41*height), 
(0.18*line, 0.38*height), (0.18*line, 0.42*height), 
(0.18*line, 0.47*height), (0.16*line, 0.49*height), 
(0.14*line, 0.58*height), (0.14*line, 0.61*height), 
(0.17*line, 0.66*height), (0.19*line, 0.61*height)]
                return opp_pos, opp_forward_points
            case _:
                print("未输入合法战术类型！")
                return None
# 战术选择逻辑封装(一次性)
def strategy_generate():
    # 获取阵型,路线:用*_舍弃多余的解包(unpack)返回值
    our_strategy_style = input("输入我方采取的战术阵型(可选:漏斗阵,铁锅阵,双人成行,锋矢阵): ")
    opp_strategy_style = input("输入对方采取的战术阵型(可选:铁锅阵,双人成行,锋矢阵,单机模式): ")
    our_strategy = choose_strategy(OUR_COLOR, our_strategy_style)  
    opp_strategy = choose_strategy(OPP_COLOR, opp_strategy_style)
    if our_strategy is None or opp_strategy is None:
        print("战术获取失败！")
        return None
    our_ori_format, our_bas_format, our_forward_points = our_strategy
    opp_ori_format, opp_bas_format, opp_forward_points = opp_strategy
    if our_ori_format:
        for i, pos in enumerate(our_ori_format):
            if not isinstance(pos, tuple):
                pos = tuple(pos)
            our_forward_points[i] = [pos] + our_forward_points[i]
    if opp_ori_format:
        for i, pos in enumerate(opp_ori_format):
            if not isinstance(pos, tuple):
                pos = tuple(pos)
            opp_forward_points[i] = [pos] + opp_forward_points[i]
    our_points = our_forward_points
    opp_points = opp_forward_points
    our_rules = rules_choose([], "our", our_conditions, rules_dict, our_strategy_style)
    opp_rules = rules_choose([], "opp", opp_conditions, rules_dict, opp_strategy_style)
    return {
        "our_rules": our_rules,
        "opp_rules": opp_rules,
        "our_points": our_points,
        "opp_points": opp_points,
        "our_bas_format": our_bas_format,
        "opp_bas_format": opp_bas_format
    }