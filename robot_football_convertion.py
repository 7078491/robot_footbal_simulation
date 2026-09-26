"""
转换层
从仿真环境获取全局坐标
我方直接使用全局坐标
对方坐标系是我方旋转180度的结果
x = LINE - x
y = HEIGHT - y
...
按这些公式进行转换
动作返回值经过转换再传入双方参数表

目的:实现动作处理器标准统一
    避免出现按队伍不同的情况
"""
from robot_football_base import (LINE, HEIGHT, ENV_VX, ENV_VY,
                                 ENV, HOLDER, OPP, OUR, ENV_X, ENV_Y, 
                                 ACTION_POSITIONS, ACTION_VELOCITIES)

def convert_opp(args_list: list, line: int = LINE, height: int = HEIGHT):
    if args_list:
        # 取出4个对应字典,把全局参数转成对方坐标形式
        env = args_list[ENV]
        hol = args_list[HOLDER]
        opp = args_list[OPP]
        our = args_list[OUR]
        for field, pos in hol.items():
            if field.endswith("pos"):
                if pos is None:
                    continue
                x0, y0 = pos
                x = line - x0
                y = height - y0
                hol[field] = (x, y)
        if env:
            x1, y1 = env["env.ball.pos"]
            x2 = line - x1
            y2 = height - y1
            env["env.ball.pos"] = (x2, y2)
            env["env.ball.to_our_goal"], env["env.ball.to_opp_goal"] = env["env.ball.to_opp_goal"], env["env.ball.to_our_goal"]
            if env["env.mesh"]:
                m_points = []
                mesh_points = env["env.mesh"]["flat_pos"]
                for x0 ,y0 in mesh_points:
                    x = line - x0
                    y = height - y0
                    m_points.append((x, y))
            if env["env.robots"]:
                for rob in env["env.robots"]:
                    x0, y0 = rob[ENV_X], rob[ENV_Y]
                    vx0, vy0 = rob[ENV_VX], rob[ENV_VY]
                    if x0 is None or y0 is None:
                        continue
                    x = line - x0
                    y = height - y0
                    vx = - vx0
                    vy = - vy0
                    rob[ENV_X] = x
                    rob[ENV_Y] = y
                    rob[ENV_VX] = vx
                    rob[ENV_VY] = vy
        if opp and our:
            b_points = []
            opp_benefit_points = opp["opp.benefit.points"]
            if opp_benefit_points:
                for x0, y0 in opp_benefit_points:
                    x = line - x0
                    y = height - y0
                    b_points.append((x, y))
            opp["opp.benefit.points"] = b_points
            b_points = []
            our_benefit_points = our["our.benefit.points"]
            if our_benefit_points:
                for x0, y0 in our_benefit_points:
                    x = line - x0
                    y = height - y0
                    b_points.append((x, y))
            our["our.benefit.points"] = b_points
    return args_list

def opp_convert(act_list: list, line: int = LINE, height: int = HEIGHT):
    # 单独处理对方的动作返回值列表的位置和速度
    if not act_list or not isinstance(act_list, list):
        return act_list
    new_act_list = []
    for act in act_list:
        if not act or not isinstance(act, list) or len(act) != 4:
            new_act_list.append(act)
            continue
        a_points = act[ACTION_POSITIONS] # 2
        a_vels = act[ACTION_VELOCITIES]  # 3
        points = []
        vels = []
        if a_points:
            for x0, y0 in a_points:
                x = line - x0
                y = height - y0
                points.append((x, y))
        act[ACTION_POSITIONS] = points
        if a_vels:
            for vx0, vy0 in a_vels:
                vx = - vx0
                vy = - vy0
                vels.append((vx, vy))
        act[ACTION_VELOCITIES] = vels
        new_act_list.append(act)
    return new_act_list
        
    