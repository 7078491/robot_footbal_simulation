"""
数据的更新与处理
策略对应的位置处理器函数集成
"""
from robot_football_rule_base import actions
from robot_football_section_calcu import benefit_generate
from robot_football_geomo_calcu import ds_theta_calcu
from robot_football_base import (ENV_TEAM, ENV_ID,
                                 ENV_VX, ENV_VY, ENV_X, ENV_Y, 
                                 ENV_HAVEBALL, ENV, HOLDER, OUR,
                                 OPP, OUR_COLOR, OPP_COLOR,
                                 LINE, HEIGHT, OURGOAL, OPPGOAL, 
                                 ROBOT_V, BALL_DS, DT,
                                 ACTION_NAME, ACTION_OBJECTS, 
                                 ACTION_POSITIONS, ACTION_VELOCITIES)
import math
"""
我方采用默认系,阵地在右向左进攻
对方坐标系翻转180度
(x = |x - LINE|, y = |y - HEIGHT|)
(vx = - vx, vy = - vy)
"""
# 分速度计算
def rob_vel_calcu(A: list = None, B: list = None, 
                  ROBOT_V: int = ROBOT_V) -> list[float, float]:
    tup = ds_theta_calcu(A, B)
    if tup:
        theta = tup[1]
        v = ROBOT_V
        if theta is not None:
            vx = v * math.cos(theta)
            vy = v * math.sin(theta)
            vx = round(vx, 2)
            vy = round(vy, 2)
            return [vx, vy]
    return [0, 0]
# 沿线推算机器人位置与速度,返回所在位置的段索引
def rob_update(frame: int = 0, points: list = None, 
               DT: float = DT, ROBOT_V: int = ROBOT_V):
    if not points or len(points) < 2:
        return None
    if not isinstance(points, list):
        try:
            points = list(points)
        except (TypeError, ValueError):
            return None
    # 计算当前机器人经过距离
    n_ds = 0   
    # ps:可以考虑截取若干帧的距离来算
    s = ROBOT_V * frame * DT / 2
    seg_n = len(points) - 1
    # 给定路径段数为n
    for seg_idx in range(seg_n):
        x1, y1 = points[seg_idx]
        x2, y2 = points[seg_idx + 1]
        dx = x2 - x1
        dy = y2 - y1
        ds = math.sqrt(dx ** 2 + dy ** 2)
        v = rob_vel_calcu(points[seg_idx], points[seg_idx + 1])
        # 逐次累加轨迹各段长
        n_ds_0 = n_ds
        n_ds += ds
        if n_ds_0 <= s < n_ds:
            delta = n_ds - s
            alpha = 1 - delta / ds
            x = x1 + alpha * dx
            y = y1 + alpha * dy
            x = round(x, 2)
            y = round(y, 2)
            return seg_idx, [x, y], v
        elif s == n_ds:
            next = points[seg_idx + 1]
            return seg_idx, list(next), v
    if s >= n_ds:
        last = points[-1]
        return seg_n - 1, list(last), [0, 0]
    elif s == 0:
        first = points[0]
        return 0, list(first), [0, 0]
    return None
# 时序速度与位置表更新
def loc_vel_update(frame: int = 0, DT: float = DT, 
                 frame_locat_dict: dict = None, 
                 frame_veloc_dict: dict = None,
                 strategy_dict: dict = None,
                 ball_pos: list = None,
                 ball_v: list = None,
                 act_list: list = None):
    # 边界检查函数
    def in_boundary(pos: list = None, 
                    line: int = LINE, height: int = HEIGHT) -> tuple:
        if pos != None and len(pos) == 2:
            x, y = pos
            if 0 <= x <= line and 0 <= y <= height:
                return True, [x, y]
            else:
                x0 = max(0, min(x, line))
                y0 = max(0, min(y, height))
                return False, [x0, y0]
        return False, [0, 0]
    if frame_locat_dict is None:
        frame_locat_dict = {
    "our_1": None,
    "our_2": None,
    "our_3": None,
    "our_4": None,
    "our_5": None,
    "opp_1": None,
    "opp_2": None,
    "opp_3": None,
    "opp_4": None,
    "opp_5": None,
    "ball": None,
    "frame": 0}
    if frame_veloc_dict is None:
        frame_veloc_dict = {
    "our_1": None,
    "our_2": None,
    "our_3": None,
    "our_4": None,
    "our_5": None,
    "opp_1": None,
    "opp_2": None,
    "opp_3": None,
    "opp_4": None,
    "opp_5": None,
    "ball": None}
    print(f"\n 目前时刻数为{frame}, \n")
    # 实际路线存储
    points_list = []
    rules_hit_dict = {    
    "our_1": False,
    "our_2": False,
    "our_3": False,
    "our_4": False,
    "our_5": False,
    "opp_1": False,
    "opp_2": False,
    "opp_3": False,
    "opp_4": False,
    "opp_5": False,
    "ball": False,
    "frame": 0}
    # 蓝5 红5 球
    if act_list:
        # 格式：act = [name, [team_rid...], [(x, y)...], [(vx, vy)...]]
        # 接收动作链返回的数据并更新
        for act in act_list:
            if act and len(act) >= 4:
                # 接收第n帧的位置和用于生成n+1帧位置的速度，
                # 二者结合得到n+1帧的位置
                name = act[ACTION_NAME]
                obj_list = act[ACTION_OBJECTS]
                pos_list = act[ACTION_POSITIONS]
                vel_list = act[ACTION_VELOCITIES]
                if name in actions: 
                    for i, field in enumerate(obj_list):
                        x, y = pos_list[i]
                        vx, vy = vel_list[i]
                        x0 = x + vx * DT 
                        y0 = y + vy * DT
                        x0 = round(x0, 1)
                        y0 = round(y0, 1)
                        pos0 = (x0, y0)
                        tup = None
                        tup = in_boundary(pos0)
                        if tup[0]:
                            pos0 = tup[1]
                        else:
                            pos0 = tup[1]
                            vel_list[i] = (0, 0)
                        if field in frame_locat_dict:
                            frame_locat_dict[field] = pos0
                        if field in rules_hit_dict:
                            rules_hit_dict[field] = True 
    if strategy_dict:
        our_points = strategy_dict["our_points"]
        opp_points = strategy_dict["opp_points"]
    our_n_list = [0 for _ in range(5)]
    opp_n_list = [0 for _ in range(5)]
    # 位置
    for field in frame_locat_dict.keys():
        if field == "frame":
            # 更新帧数并跳过
            frame_locat_dict[field] = frame
            rules_hit_dict[field] = frame
            continue
        elif rules_hit_dict[field] == True:
            # 规则触发时舍弃预设数据
            continue
        elif field == "ball":
            frame_locat_dict[field] = ball_pos
        elif "_" in field:
            rid = field.split('_')[-1]
            idx = int(rid) - 1
            tup0 = None
            if field.startswith("our"):
                # ps:后面要专门设计每种战术对应的位置更新函数
                if idx < len(our_points):
                    # tup0 = (n, pos, v)的元组
                    tup0 = rob_update(frame, our_points[idx], DT)
                    if tup0 and len(tup0) == 3:
                        our_n_list[idx] = tup0[0]
                        # tup是(bool, pos)的元组,检查是否越界
                        tup = in_boundary(tup0[1])
                        if tup[0]:
                            tup0[1][0] = tup[1][0]  
                            tup0[1][1] = tup[1][1]
            elif field.startswith("opp"):
                if idx < len(opp_points):
                    tup0 = rob_update(frame, opp_points[idx], DT)
                    if tup0 and len(tup0) == 3:
                        opp_n_list[idx] = tup0[0]
                        tup = in_boundary(tup0[1])
                        if tup[0]:
                            tup0[1][0] = tup[1][0]  
                            tup0[1][1] = tup[1][1]
            if tup0 and len(tup0) >= 2:
                frame_locat_dict[field] = tup0[1]
            else:
                frame_locat_dict[field] = None
    # 速度  
    for field in frame_veloc_dict.keys():
        if rules_hit_dict[field] == True:
            continue
        elif field == "ball":
            frame_veloc_dict[field] = ball_v
        else:
            rid = field.split('_')[-1]
            idx = int(rid) - 1
            tup0 = None
            if field.startswith("our"):
                if idx < len(our_points):
                    tup0 = rob_update(frame, our_points[idx], DT)
            elif field.startswith("opp"):
                if idx < len(opp_points):
                    tup0 = rob_update(frame, opp_points[idx], DT)
            if tup0 and len(tup0) >= 3:
                frame_veloc_dict[field] = tup0[2] 
            else:
                frame_veloc_dict[field] = None
        n_list = [our_n_list, opp_n_list]
    for field, hit in rules_hit_dict.items():
        if field != "frame":
            if hit:
                if field.startswith("our"):
                    rid = field.split('_')[-1]
                    idx = int(rid) - 1
                    points_list.append(our_points[idx])
                elif field.startswith("opp"):
                    rid = field.split('_')[-1]
                    idx = int(rid) - 1
                    points_list.append(opp_points[idx])
    print("时序数据更新完毕.")
    print(f"规则触发状态打印: {rules_hit_dict}")
    return frame_locat_dict, frame_veloc_dict, points_list, n_list
# 时序轨迹表更新
# ps:只管理论路线，后期改成画实际路线
def traje_update(half_num: int = 2,
                 n_list: list = None,
                 strategy_dict: dict = None,
                 frame_traje_dict: dict = None):
    if frame_traje_dict is None:
        frame_traje_dict = {
    "our_1": [],
    "our_2": [],
    "our_3": [],
    "our_4": [],
    "our_5": [],
    "opp_1": [],
    "opp_2": [],
    "opp_3": [],
    "opp_4": [],
    "opp_5": []}
    if not strategy_dict or not n_list:
        return frame_traje_dict
    our_points = strategy_dict["our_points"]
    opp_points = strategy_dict["opp_points"]
    if n_list and len(n_list) == 2:
        our_n = n_list[0]
        opp_n = n_list[1]
        m = half_num 
        if our_n and opp_n:
            for field in frame_traje_dict.keys():
                idx = int(field.split('_')[-1]) - 1
                trajectory = frame_traje_dict[field]
                if field.startswith("our"):
                    if idx >= len(our_n) or idx >= len(our_points):
                        continue
                    n = int(our_n[idx])
                    # 遍历points中索引为n-1到n+m的所有节点
                    a = max(0, n-1)
                    b = min(len(our_points[idx]), n+m+1)
                    if a < b:
                        points_set = set(tuple(p) for p in trajectory)
                        new_points = []
                        for i in range(a, b):
                            point = our_points[idx][i]
                            if len(point) >= 2:
                                if tuple(point) not in points_set:
                                    new_points.append(list(point))
                        if new_points:
                            trajectory.extend(new_points)
                        if len(trajectory) > m + 2:
                            frame_traje_dict[field] = trajectory[-(m+2):]
                elif field.startswith("opp"):
                    if idx >= len(opp_n) or idx >= len(opp_points):
                        continue
                    n = int(opp_n[idx])
                    # 遍历points中索引为n-1到n+m的所有节点
                    a = max(0, n-1)
                    b = min(len(opp_points[idx]), n+m+1)
                    if a < b:
                        points_set = set(tuple(p) for p in trajectory)
                        new_points = []
                        for i in range(a, b):
                            point = opp_points[idx][i]
                            if len(point) >= 2:
                                if tuple(point) not in points_set:
                                    new_points.append(list(point))
                        if new_points:
                            trajectory.extend(new_points)
                        if len(trajectory) > m + 2:
                            frame_traje_dict[field] = trajectory[-(m+2):]
    return frame_traje_dict
# 参数运算
def calcu_args(args_list: list[dict], Environ: list, 
               mesh_dict: dict, act_list: list[list],
               benefit_points: list, ball_pos: list) -> list:
    def pass_block(P, A, B, epsilon = 1e-9):
        """
        P = A + t * (B - A)
        0 <= t <= 1
        """
        x , y  = P
        x1, y1 = A
        x2, y2 = B
        if abs(x2 - x1) > epsilon:
            t = (x - x1) / (x2 - x1)
        elif abs(y2 - y1) > epsilon:
            t = (y - y1) / (y2 - y1)
        else:
            return False  # A和B是同一个点
        if not (0 <= t <= 1):
            return False
        # 验证点是否在直线上
        px = x1 + t * (x2 - x1)
        py = y1 + t * (y2 - y1)
        if abs(px - x) < epsilon and abs(py - y) < epsilon:
            return True
        return False
    # 字典存储值的语义一定要清楚是针对哪一方来说的
    # 所有算法计算结果一定要指明针对的对象
    if not args_list:
        return args_list
    Env_args = args_list[ENV]
    holder_args = args_list[HOLDER]
    our_args = args_list[OUR]
    opp_args = args_list[OPP]
    # 统一初始化重置
    Env_args["env.robots"]     = None
    Env_args["env.mesh"]       = None
    Env_args["env.ball.pos"]   = None
    Env_args["env.ball.to_our_goal"] = None
    Env_args["env.ball.to_opp_goal"] = None

    holder_args["holder.team"] = None
    holder_args["holder.id"]   = None
    holder_args["holder.pos"]  = None

    holder_args["holder.min_mate_ds"]  = float("inf")
    holder_args["holder.min_mate_id"]  = None
    holder_args["holder.min_mate_pos"] = None
    holder_args["holder.min_opp_ds"]  = float("inf")
    holder_args["holder.min_opp_id"]  = None
    holder_args["holder.min_opp_pos"] = None
    
    holder_args["holder.better_to_pass"] = False
    holder_args["holder.pass_block"]     = False
    holder_args["holder.shoot_block"]    = False
    holder_args["holder.target_pos"]     = None

    our_args["our.benefit.exists"] = False
    our_args["our.benefit.points"] = []
    opp_args["opp.benefit.exists"] = False
    opp_args["opp.benefit.points"] = []

    our_args["our.act.contain_hit"] = False
    our_args["our.act.pass_hit"]    = False
    opp_args["opp.act.contain_hit"] = False
    opp_args["opp.act.pass_hit"]    = False
    opp_args["opp.act.chase_hit"]   = False

    team0 = None
    holder_found = False
    min_mate_ds = float('inf')
    min_opp_ds = float('inf')
    # 按字典逐个更新:全局环境
    if Environ:
        Env_args["env.robots"] = Environ
    if mesh_dict:
        Env_args["env.mesh"] = mesh_dict
    if ball_pos:
        Env_args["env.ball.pos"] = ball_pos
        if len(ball_pos) == 2: 
            ds1, *_ = ds_theta_calcu(ball_pos, OPPGOAL)
            ds2, *_ = ds_theta_calcu(ball_pos, OURGOAL)
            Env_args["env.ball.to_our_goal"] = round(ds2, 2)
            Env_args["env.ball.to_opp_goal"] = round(ds1, 2)
    # 持球者
    if Environ:
        for rob in Environ:
            # 遍历机器人序列
            x, y = rob[ENV_X], rob[ENV_Y]
            if x is None or y is None:
                continue
            x = round(x, 1)
            y = round(y, 1)
            if rob[ENV_HAVEBALL] == 1:
                # 找到持球者
                holder_found = True
                holder_args["holder.team"] = rob[ENV_TEAM]
                holder_args["holder.id"] = rob[ENV_ID]
                holder_args["holder.pos"] = (x, y)
                team0 = holder_args["holder.team"]
        if holder_found:
            matched = []
            # 获取准备好的持球者信息
            x0, y0 = holder_args["holder.pos"]
            team0 = holder_args["holder.team"]
            rid0 = holder_args["holder.id"]
            for rob in Environ:
                x1, y1 = rob[ENV_X], rob[ENV_Y]
                if x1 is None or y1 is None:
                    continue
                x1 = round(x1, 1)
                y1 = round(y1, 1)
                team1 = rob[ENV_TEAM]
                rid1 = rob[ENV_ID]
                if team1 == "our":
                    opp_color = OPP_COLOR
                    goal = OPPGOAL
                else: 
                    opp_color = OUR_COLOR
                    goal = OURGOAL
                if team1 == team0:
                    if rid1 == rid0:
                        continue
                    ds3, *_ = ds_theta_calcu((x0, y0), (x1, y1))
                    if ds3 < min_mate_ds:
                        min_mate_ds = round(ds3, 2)
                        holder_args["holder.min_mate_ds"] = min_mate_ds
                        holder_args["holder.min_mate_id"] = rid1
                        holder_args["holder.min_mate_pos"] = (x1, y1)
                        benefit0, *_ = benefit_generate((x0, y0), opp_color)
                        benefit = benefit_generate((x1, y1), opp_color)[0]
                        if benefit >= benefit0:
                            matched.append([rid1, (x1, y1)])
                else:
                    ds4, *_ = ds_theta_calcu((x0, y0), (x1, y1))
                    if ds4 < min_opp_ds:
                        min_opp_ds = round(ds4, 2)
                        holder_args["holder.min_opp_ds"] = min_opp_ds
                        holder_args["holder.min_opp_id"] = rid1
                        holder_args["holder.min_opp_pos"] = (x1, y1)
            if matched:
                holder_args["holder.better_to_pass"] = True
                for mate in matched:
                    rid1 = mate[0]
                    x1, y1 = mate[1]
                    for rob in Environ:
                        x2, y2 = rob[ENV_X], rob[ENV_Y]
                        team2 = rob[ENV_TEAM]
                        rid2 = rob[ENV_ID]
                        if x2 is None or y2 is None:
                            continue
                        # 跳过 队友 和 持球者
                        if team2 == team0 and rid2 == rid1:
                            continue
                        elif team2 == team0 and rid2 == rid0:
                            continue
                        if pass_block((x0, y0), (x2, y2), (x1, y1)):
                            holder_args["holder.pass_block"] = True
                        else: 
                            # target具体定哪个点根据规则判断
                            # 逻辑上最好是在有利位置的队友附近
                            holder_args["holder.target_pos"] = (x2-40, y2)
                        if pass_block((x0, y0), (x2, y2), goal):
                            holder_args["holder.pass_block"] = True
                            break
    # 有利区
    if benefit_points and team0 is not None:
        if team0 == "our":
            our_args["our.benefit.exists"] = True
            our_args["our.benefit.points"] = benefit_points
            opp_args["opp.benefit.exists"] = False
            opp_args["opp.benefit.points"] = []
        elif team0 == "opp":
            opp_args["opp.benefit.exists"] = True
            opp_args["opp.benefit.points"] = benefit_points
            our_args["our.benefit.exists"] = False
            our_args["our.benefit.points"] = []
        # 动作触发
        if act_list:
            print("正在更新动作执行情况...")
            for act in act_list:
                name = act[ACTION_NAME]
                team = act[ACTION_OBJECTS][-1].split("_")[0]
                # team 是"our"或"opp"，与队伍颜色是不同的
                if team == "our":
                    match name:
                        case "牵制":
                            our_args["our.act.contain_hit"] = True
                        case "传球":
                            our_args["our.act.pass_hit"] = True
                        case "围追堵截":
                            pass
                        case "带球":
                            our_args["our.act.carry_hit"] = True
                        case _:
                            print(f"字典中未检索到动作名: {name}")
                elif team == "opp":
                    match name:
                        case "牵制":
                            opp_args["opp.act.contain_hit"] = True
                        case "传球":
                            opp_args["opp.act.pass_hit"] = True
                        case "围追堵截":
                            opp_args["opp.act.chase_hit"] = True
                        case "带球":
                            our_args["opp.act.carry_hit"] = True
                        case _:
                            print(f"字典中未检索到动作名: {name}")
    if holder_args["holder.min_mate_ds"] == float("inf"):
        holder_args["holder.min_mate_ds"] = None
    if holder_args["holder.min_opp_ds"] == float("inf"):
        holder_args["holder.min_opp_ds"] = None
    return args_list
# 记录机器人位置函数
# 将时序表中的信息传入Environ
def Env_update(Env: list = None, 
               frame_locat_dict: dict = None,
               frame_veloc_dict: dict = None) -> list:
    if not Env:
        return Env
    elif not frame_locat_dict or not frame_veloc_dict:
        return Env
    id_to_index = {}
    for i, robot in enumerate(Env):
        rob_id = robot[ENV_ID]
        if rob_id is not None:
            # ps: key的两个均为字符串
            key = (robot[ENV_TEAM], rob_id)
            id_to_index[key] = i
    update_count = 0
    # 位置
    for field, value in frame_locat_dict.items():
        if value is None or field == "ball" or field == "frame":
            continue
        if "_" in field:
            team, rid = field.split("_", 1)
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            print(f'警告！{field}位置信息异常！')
            continue
        key = (team, rid)
        if key in id_to_index:
            idx = id_to_index[key]
            Env[idx][ENV_X] = value[0]
            Env[idx][ENV_Y] = value[1]
            update_count += 1
    print(f'成功更新{update_count}个机器人位置到列表.')
    # 速度
    for field, value in frame_veloc_dict.items():
        if value is None or field == "ball":
            continue
        if "_" in field:
            team, rid = field.split("_", 1)
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            print(f'警告！{field}速度信息异常！')
            continue
        key = (team, rid)
        if key in id_to_index:
            idx = id_to_index[key]
            Env[idx][ENV_VX] = value[0]
            Env[idx][ENV_VY] = value[1]
    return Env
            
def auto_set_haveball(ball_pos: list = None, env: list = None) -> list:
    """自动设置机器人持球状态"""
    has_ball = False
    if env:
        for robot in env:
            if robot[ENV_X] == None or robot[ENV_Y] == None:
                # 跳过未更新的机器人
                continue
            x = robot[ENV_X]
            y = robot[ENV_Y]
            if not ball_pos:
                print("警告！足球位置未传入！")
                return env
            ds, *_ = ds_theta_calcu(ball_pos, (x, y))
            if 0 <= ds < BALL_DS + 10:
                robot[ENV_HAVEBALL] = 1
                has_ball = True
                break
            else:
                robot[ENV_HAVEBALL] = 0
    if not has_ball:
        print("无人持球！")
    return env

