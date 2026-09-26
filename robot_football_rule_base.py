"""
5v5机器人足球仿真的规则库,存储规则并按需调用
面向过程式
规则定义,环境参数,推理机
用二维列表存储规则与环境情况
用环境参数去匹配规则
参数更新分门别类,各行其道
"""
from typing import Callable
from robot_football_geomo_calcu import random_choose, ds_theta_calcu
from robot_football_base import (LINE, HEIGHT, RULE_ID, RULE_NAME, BALL_DS, 
                                 RULE_CONDITIONS, RULE_ACTIONS, DT,
                                 RULE_ACTIONS_PARAMS, RULE_PRIORITY, 
                                 RULE_PHASE, RULE_DESCRIPTIONS,
                                 RULE_ENABLED, RULE_HIT_COUNT, RULE_PROGRESS,
                                 BALL_VM, ROBOT_V, ENV_TEAM, ENV_ID,
                                 OURGOAL, OPPGOAL, ENV, HOLDER, 
                                 OUR, OPP, ENV_X, ENV_Y, ACTION_NAME,
                                 descriptions_list, actions_params_list, 
shoot_params, pass_params, carry_params, control_params,
rove_params, chase_params, contain_params, sprint_params,
our_shoot_conds, opp_shoot_conds,
our_pass_conds, opp_pass_conds,
our_pripass_conds, opp_pripass_conds,
our_carry_conds, opp_carry_conds,
our_control_conds, opp_control_conds,
opp_chase_conds, priority_list,
our_cut_conds, opp_cut_conds,
our_contain_conds, our_sprint_conds)
import math
# 执行记录
_execution_history = []
# 动作处理器
_action_handlers = {}
# 帧内机器人占用
_frame_occupied = set()
# =============== 区域规则处理 ==================
# ps:单独对本方来说，对方使用单独的坐标系
def region_rules(pos: list, state: str, 
                line: int = LINE, height: int = HEIGHT) -> str:
    """区域位置判定"""
    x, y = pos
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
    name = None
    if corner:
        name = "corner"
    elif goal:
        name = "goal"
    elif half_mid:
        name = "half_mid"
    elif all_mid:
        name = "all_mid"
    return name

def region(name: str):
    """基于具体位置判定区域规则是否启用"""
    
    return

# ============ 规则管理 ============
def add_rule(rule_base: list,
             base_name: str,
             rule_name: str,
             conditions_list: list[list],
             actions: list[str],
             actions_params: list[dict] = None,
             priority: int = 5,
             phase: str = "all",
             descriptions_list: list[str] = None,
             enabled: bool = False) -> str:
    """添加规则到规则库"""
    n = len(rule_base) + 1
    rule_id = f"{base_name}_{n:03d}"
    rule = [
        rule_id,                       # ID
        rule_name,                     # 名称
        conditions_list or [[]],       # 条件组
        actions,                       # 动作链
        0,                             # 动作进程
        actions_params or [{}],        # 动作参数
        priority,                      # 优先级
        phase,                         # 阶段
        descriptions_list,             # 描述
        enabled,                       # 启用
        0                              # 触发次数
    ]
    rule_base.append(rule)  
    if base_name in ["our_rules", "opp_rules"]:
        print(f"[{rule_id}] {rule_name} (优先级: {priority}, 阶段: {phase})")
    return rule_id
  
def get_rule(rule_base: list, rule_id: str):
    """根据规则ID获取规则"""
    for rule in rule_base:
        if rule[RULE_ID] == rule_id:  
            return rule
    return None    

def get_rule_from_name(rule_base: list, rule_name: str):
    for rule in rule_base:
        if rule[RULE_NAME] == rule_name:
            return rule
    return None
    
def get_enabled_rules(rule_base: list) -> list[list]:
    """获取所有启用的规则"""
    return [rule for rule in rule_base if rule[RULE_ENABLED]]

def update_rule(rule_base: list, rule_id: str, **kwargs) -> bool:
    """更新规则"""
    rule = get_rule(rule_base, rule_id)
    if not rule:
        return False
    update_map = {
        'name': RULE_NAME,
        'conditions': RULE_CONDITIONS,
        'actions': RULE_ACTIONS,
        'actions_progress': RULE_PROGRESS,
        'action_params': RULE_ACTIONS_PARAMS,
        'priority': RULE_PRIORITY,
        'phase': RULE_PHASE,
        'description': RULE_DESCRIPTIONS,
        'enabled': RULE_ENABLED,
    }
    for key, value in kwargs.items():
        if key in update_map:
            rule[update_map[key]] = value
    return True

def change_rule_state(rule_base: list, rule_id: str, state: str) -> bool:
    """规则状态修改"""
    enable = False
    if state == "enable":
        enable = True
    elif state == "disable":
        enable = False
    else:
        return False
    return update_rule(rule_base, rule_id, enabled = enable)

def delete_rule(rule_base: list, rule_id: str) -> bool:
    """删除规则"""
    for i, rule in enumerate(rule_base):
        if rule[RULE_ID] == rule_id:
            del rule_base[i]
            return True
    return False

def clear_rules(rule_base: list):
    """清空运行库"""
    rule_base.clear()
    print(f"运行库{rule_base}已清空.")

# ============ 条件评估 =============
def evaluate_condition(condition: list, args_list: list = None) -> bool:
    """评估单个条件"""
    # 条件字段名
    field = condition[0]
    # 条件操作符
    operator = condition[1]
    # 条件要求的值
    value = condition[2]
    if args_list is None:
        return operator in ["exists", "not_exists"]
    # 遍历所有字典，查找包含该字段的字典
    actual = None
    found = False
    for data_dict in args_list:
        if isinstance(data_dict, dict) and field in data_dict:
            actual = data_dict[field]
            found = True
            break
    # 如果没找到，检查是否存在并返回评估结果
    if not found:
        if operator == "exists":
            return False
        elif operator == "not_exists":
            return True
        else:
            print(f"警告: 字段 '{field}' 在所有字典中未找到")
            return False
    if actual != None:
        if operator == "==":
            return actual == value
        elif operator == "!=":
            return actual != value
        elif operator == ">":
            return actual > value
        elif operator == "<":
            return actual < value
        elif operator == ">=":
            return actual >= value
        elif operator == "<=":
            return actual <= value
        elif operator == "in":
            return actual in value
        elif operator == "not_in":
            return actual not in value
        elif operator == "contains":
            return value in actual
        elif operator == "exists":
            return actual is not None
        elif operator == "not_exists":
            return actual is None
    return False

def evaluate_condition_group(conditions: list, 
                             args_list: list) -> bool:
    if not conditions:
        return True
    result = True
    for i, cond in enumerate(conditions):
        cond_result = evaluate_condition(cond, args_list)
        logic = cond[3] if len(cond) > 3 else "and"
        if i == 0:
            result = cond_result
        else:
            if logic == "and":
                result = result and cond_result
            elif logic == "or":
                result = result or cond_result
            elif logic == "nor":
                result = result and not cond_result
    return result

def evaluate_rule(rule: list, args_list: list) -> bool:
    """评估规则"""
    if not rule[RULE_ENABLED]:
        return False
    progress = rule[RULE_PROGRESS]
    conditions_list = rule[RULE_CONDITIONS]
    # conditions:每个动作的条件组
    if progress >= len(conditions_list):
        return False
    return evaluate_condition_group(conditions_list[progress], args_list)

def conflicts_resolve(rule_A: list, rule_B: list):
    """规则冲突裁定"""
    # 考虑到场上的机器人可能需要同时执行多个规则，只按优先级取规则不够合理，
    # 所以应该在匹配到的规则中判断是否存在矛盾，如果是那么选择较高优先级的规则执行
    """
    定义当规则发生冲突等多种情况如何选用规则(预留未实现)
    """
    if rule_A and rule_B:
        return
    return None
    
# ============== 规则匹配与推进 ==============
def match_rules(rule_base: list, args_list: list) -> list[tuple]:
    """匹配所有符合条件的规则"""
    matched = []
    for rule in rule_base:
        # 检测规则启用及其进程状态,只要初始化的规则
        if not rule[RULE_ENABLED]:
            continue
        if rule[RULE_PROGRESS] != 0:
            continue
        # 取得条件组的第一组并检测
        conditions_list = rule[RULE_CONDITIONS]
        if not conditions_list:
            continue
        first_conds = conditions_list[0]
        if evaluate_condition_group(first_conds, args_list):
            matched.append(rule)
    matched.sort(key = lambda r: r[RULE_PRIORITY], reverse = True)
    return matched

def infer_executor(action: str, args_list: list) -> list:
    # 调取参数字典
    hol = args_list[HOLDER]
    env = args_list[ENV]["env.robots"]
    # 获取当前持球者状态
    holder_id = hol.get("holder.id")
    holder_team = hol.get("holder.team")
    holder_robot = f"{holder_team}_{holder_id}" if holder_id else None
    if action in ["射门", "传球", "带球", "牵制"]:
        # 涉及直接对球处理动作的执行者为持球者
        return [holder_robot] if holder_robot else []
    if action in ["破袭"]:
        # 理论上是除了持球者外的队友
        other = [r for r in env
                 if r[ENV_TEAM] == holder_team and
                 r[ENV_ID] != holder_id]
        if other:
            return [f"{holder_team}_{other[0][ENV_ID]}"]
        return []
    if action == "围追堵截":
        # 所有对手
        return [f"opp_{r[ENV_ID]}" for r in env if r[ENV_TEAM] == "opp"]
    if action == "漫游":
        # 未设置
        return []
    if action == "控场防守":
        # 找持球者的最近对手
        rid0 = hol.get("holder.min_opp_id")
        team0 = "opp" if holder_team == "our" else "our"
        if rid0:
            return [f"{team0}_{rid0}"]
        return []
    return []

def clear_fram_occupied():
    _frame_occupied.clear()
    
def frame_occupied(executors: list[str]) -> bool:
    for r in executors:
        if r in _frame_occupied:
            return True
    return False

def mark_occupied(executors: list[str]):
    for r in executors:
        _frame_occupied.add(r)

def trigger_rules(rule_base: list, args_list: list,
                  act_list: list):
    # 针对进程为0的规则,初始化进程
    matched = match_rules(rule_base, args_list)
    if not matched:
        print("无可触发规则匹配.")
        return
    rule = matched[0]
    team = rule[RULE_ID]
    name = rule[RULE_NAME]
    print(f"已匹配到可触发规则:{team}_{name}")
    actions = rule[RULE_ACTIONS]
    action = actions[0]
    action_params = rule[RULE_ACTIONS_PARAMS][0]
    executors = infer_executor(action, args_list)
    if not executors:
        print(f"[{action}]未找到执行者,跳过.")
        return
    if frame_occupied(executors):
        print(f"[{action}]的执行者本帧已被占用,跳过.")
        return
    act = execute_action(rule, action, action_params, args_list)
    if act is not None and isinstance(act, list):
        act_list.append(act)
        mark_occupied(executors)
        print(f"规则[{rule[RULE_NAME]}]触发, 执行动作:[{action}]")
    rule[RULE_PROGRESS] += 1
    # 动作序列只包含1个动作,执行完成后重置
    if rule[RULE_PROGRESS] >= len(actions):
        rule[RULE_PROGRESS] = 0

def advance_rules(rule_base: list, args_list: list, act_list: list):
    # 针对已启动,进程不为0的规则
    for rule in rule_base:
        if not rule[RULE_ENABLED]:
            # 未启用,跳过
            continue
        progress = rule[RULE_PROGRESS]
        if progress <= 0:
            # 未初始化,跳过
            continue
        actions = rule[RULE_ACTIONS]
        if progress >= len(actions):
            # 执行完毕,重置
            rule[RULE_PROGRESS] = 0
            continue
        action = actions[progress]
        action_params = rule[RULE_ACTIONS_PARAMS][progress]
        conds = rule[RULE_CONDITIONS][progress]
        if not evaluate_condition_group(conds, args_list):
            print(f"[{rule[RULE_ID]}]规则进度:{progress}的条件不符,重置.")
            rule[RULE_PROGRESS] = 0
            continue
        executors = infer_executor(action, args_list)
        if not executors:
            print("执行者缺失,动作执行暂停.")
            continue
        if frame_occupied(executors):
            print("执行者已被占用,动作执行暂停.")
            continue
        act = execute_action(rule, action, action_params, args_list)
        if act is not None and isinstance(act, list):
            act_list.append(act)
            mark_occupied(executors)
            print(f"动作{act[ACTION_NAME]}执行,进度增加:{progress}->{progress+1}")
            rule[RULE_PROGRESS] += 1 
            if rule[RULE_PROGRESS] >= len(actions):
                rule[RULE_PROGRESS] = 0
                print("规则序列执行完毕,重置.")
    
def auto_match_execute(rule_base: list, args_list: list, 
                       act_list: list) -> list:
    """规则自动匹配执行"""
    act_list.clear()
    # 帧内占用清除
    clear_fram_occupied()
    # 执行规则推进
    advance_rules(rule_base, args_list, act_list)
    # 触发可触发规则
    trigger_rules(rule_base, args_list, act_list)
    return act_list
    
# ============ 动作执行 ============
def register_action(action: str, handler: Callable):
    """注册动作处理器"""
    _action_handlers[action] = handler
    print(f"{action}动作处理器已注册.")
    
def execute_action(rule: list, action: str, 
                   action_params: dict, args_list: list):
    """执行动作接口函数"""
    # 在注册表中查找函数
    handler = _action_handlers.get(action)
    if handler:
        # 执行动作链,返回result是列表
        result = handler(action_params, args_list)
    else:
        print("查找执行器失败,返回默认值.")
        result = f"{rule}的执行器未注册."
    # 更新统计
    rule[RULE_HIT_COUNT] += 1
    _execution_history.append({
        "rule_id": rule[RULE_ID],
        "rule_name": rule[RULE_NAME],
        "action": action,
        "action_params": action_params,
        "result": result
    })
    if result:
        print(f"动作执行结果已生成: \n{result}")
    return result

# ============ 统计和调试 ============
def get_stats(rule_base: list) -> dict:
    """获取规则统计信息"""
    enabled = get_enabled_rules(rule_base)
    disabled = len(rule_base) - len(enabled)
    phase_stats = {}
    for rule in rule_base:
        phase = rule[RULE_PHASE]
        phase_stats[phase] = phase_stats.get(phase, 0) + 1
    active = [r for r in rule_base if r[RULE_PROGRESS] > 0]
    sorted_by_hit = sorted(rule_base, key=lambda r: r[RULE_HIT_COUNT], reverse=True)
    top_rules = sorted_by_hit[:5]
    return {
        "total_rules": len(rule_base),
        "enabled_rules": len(enabled),
        "disabled_rules": disabled,
        "phase_distribution": phase_stats,
        "active_rules": len(active),
        "total_executions": len(_execution_history),
        "most_active_rules": [
            {"id": r[RULE_ID], "name": r[RULE_NAME], "hits": r[RULE_HIT_COUNT]}
            for r in top_rules if r[RULE_HIT_COUNT] > 0
        ]
    }

def reset_statistics(rule_base: list):
    """重置统计信息"""
    for rule in rule_base:
        rule[RULE_HIT_COUNT] = 0
        rule[RULE_PROGRESS] = 0
    _execution_history.clear()

# ============ 动作执行器 ============
# 返回值标准格式:动作名，执行实体，位置序列，速度序列
# act = [act_name, object_list, pos_list, vel_list]
# ps: 原则上每个实体的数据索引应该对应一致，先球后机，先我后敌
def shoot(action_params: dict, args_list: list) -> list:
    """射门处理器"""
    # 先取动参
    params = action_params
    power = params.get("power", 1.0)
    v = params.get("v", BALL_VM)
    # 取得规参字典
    env = args_list[ENV]
    hol = args_list[HOLDER]
    # 取规参数据
    team = hol["holder.team"]
    rid = hol["holder.id"]
    pos = hol["holder.pos"]
    x0, y0 = env["env.ball.pos"]
    if not team or not rid or not pos or not x0 or not y0:
        return None
    # 动作逻辑处理
    if team == "our":
        goal = OPPGOAL
    else:
        goal = OURGOAL
    ds, theta, *_ = ds_theta_calcu((x0, y0), goal)
    vx = v * power * math.cos(theta)
    vy = v * power * math.sin(theta)
    x0 = round(x0, 1)
    y0 = round(y0, 1)
    vx = round(vx, 2)
    vy = round(vy, 2)
    # 返回标准结果
    return ["射门", ["ball", f"{team}_{rid}"], 
            [(x0, y0), tuple(pos)], [(vx, vy), (0, 0)]]

def prepass(action_params: dict, args_list: list) -> list:
    """传球处理器"""
    # 基于距离比例确定传球的速度
    params = action_params
    power = params.get("power", 0.8)
    v = params.get("v", BALL_VM)
    env = args_list[ENV]
    hol = args_list[HOLDER]
    pos0 = hol["holder.pos"]
    pos1 = hol["holder.min_mate_pos"]
    ball_pos = env["env.ball.pos"]
    team = hol["holder.team"]
    rid = hol["holder.id"]
    target = hol["holder.target_pos"]
    if not team or not rid or not pos0:
        return None
    # 优先找传球目标位置,没有就传给最近队友
    if target:
        ds, theta, *_ = ds_theta_calcu(ball_pos, target)
        vx0 = v * power * math.cos(theta)
        vy0 = v * power * math.sin(theta)
    else:
        ds, theta, *_ = ds_theta_calcu(ball_pos, pos1)
        vx0 = v * power * math.cos(theta)
        vy0 = v * power * math.sin(theta)
    vx0 = round(vx0, 2)
    vy0 = round(vy0, 2)
    vx = 0.3 * vx0
    vy = 0.3 * vy0
    return ["传球", ["ball", f"{team}_{rid}"], 
                    [ball_pos, pos0], [(vx0, vy0), (vx, vy)]]

def carry(action_params: dict, args_list: list) -> list:
    """带球处理器"""
    params = action_params
    dx = params.get("robot_ball_dx", 13)
    dy = params.get("robot_ball_dy", 13)
    v = params.get("v", ROBOT_V)
    hol = args_list[HOLDER]
    team = hol["holder.team"]
    rid = hol["holder.id"]
    pos = hol["holder.pos"]
    if not team or not rid or not pos:
        return None
    x, y = pos
    x0 = x - dx
    y0 = y - dy
    benefit_points = []
    if team == "our":
        default_pos = OPPGOAL
        our_args = args_list[OUR]
        benefit_points = our_args["our.benefit.points"]
    else:
        default_pos = OURGOAL
        opp_args = args_list[OPP]
        benefit_points = opp_args["opp.benefit.points"]
    # 有有利区去有利区，否则去找门
    target = random_choose(benefit_points) if benefit_points else default_pos
    if not target:
        target = default_pos
    ds, theta, *_ = ds_theta_calcu((x, y), target)
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)
    x0 = round(x0, 1)
    y0 = round(y0, 1)
    vx = round(vx, 2)
    vy = round(vy, 2)
    return ["带球", ["ball", f"{team}_{rid}"], 
            [(x0, y0), (x, y)], [(vx, vy), (vx, vy)]]

def control_offence(action_params: dict, args_list: list) -> list:
    """防控处理器"""
    params = action_params
    s = params.get("s", BALL_DS)
    v = params.get("v", ROBOT_V)
    hol = args_list[HOLDER]
    env = args_list[ENV]
    opp_team = hol["holder.team"]
    if opp_team == "our":
        team = "opp"
    else:
        team = "our" 
    ball_pos = env["env.ball.pos"]
    x1, y1 = hol["holder.pos"]
    x2, y2 = hol["holder.min_mate_pos"]
    x0, y0 = hol["holder.min_opp_pos"]
    rid0 = hol["holder.min_opp_id"]
    mid_1 = [(x1 + x2) / 2, (y1 + y2)/2]
    mid_2 = [(mid_1[0]+ball_pos[0])/2, (mid_1[1]+ball_pos[1])/2]
    ds, theta, *_ = ds_theta_calcu((x0, y0), mid_2)
    if ds <= s:
        return ["控场防守", [f"{team}_{rid0}"], 
               [(x0, y0)], [(0, 0)]]
    elif ds > s:
        vx = v * math.cos(theta)
        vy = v * math.sin(theta)   
        x0 = round(x0, 1)
        y0 = round(y0, 1)
        vx = round(vx, 2)
        vy = round(vy, 2)
    return ["控场防守", [f"{team}_{rid0}"], 
            [(x0, y0)], [(vx, vy)]]

def rove(action_params: dict, args_list: list) -> list:
    """无球漫游处理器"""
    params = action_params
    v = params.get("v", ROBOT_V)
    step = v * DT
    env = args_list[ENV]
    hol = args_list[HOLDER]
    pos_list = []
    updated_velocities = []
    rid_list = []
    benefit_points = None
    Env = env["env.robots"]
    if hol["holder.pos"] is not None:
        team = hol["holder.team"]
        if team == "our":
            our_args = args_list[OUR]
            benefit_points = our_args["our.benefit.points"]
        elif team == "opp":
            opp_args = args_list[OPP]
            benefit_points = opp_args["opp.benefit.points"]
        for rob in Env:
            if rob[ENV_TEAM] == team:
                x, y = rob[ENV_X], rob[ENV_Y]
                if x is None or y is None:
                    continue
                rid = rob[ENV_ID]
                rid_list.append(f"{team}_{rid}")
                pos = random_choose(benefit_points)
                ds, theta, *_ = ds_theta_calcu((x, y), pos)
                if step <= ds:
                    vx = v * math.cos(theta)
                    vy = v * math.sin(theta)
                else:
                    vx = 0
                    vy = 0
                x = round(x, 1)
                y = round(y, 1)
                vx = round(vx, 2)
                vy = round(vy, 2)
                pos_list.append((x, y))
                updated_velocities.append((vx, vy))
    return ["漫游", rid_list, pos_list, updated_velocities]

def goofy_move(action_params: dict, args_list: list) -> list:
    """围追堵截处理器"""
    params = action_params
    chase_speed = params.get("chase_speed", ROBOT_V)
    step = chase_speed * DT 
    env = args_list[ENV]
    rid_list = []
    pos_list = []
    updated_velocities = []
    if not env:
        print("传入规则参数残缺!")
        return None
    ball_pos = env["env.ball.pos"]
    # 遍历所有对方机器人，计算新数据
    Env = env["env.robots"]
    for rob in Env:
        if rob[ENV_TEAM] == "our":
            continue
        x, y = rob[ENV_X], rob[ENV_Y]
        if x is None or y is None:
            continue
        x = round(x, 1)
        y = round(y, 1)
        pos_list.append((x, y))
        rid = rob[ENV_ID]
        rid_list.append(f"opp_{rid}")
        # 计算机器人到球的距离和方向
        ds, theta, *_ = ds_theta_calcu((x, y), ball_pos)
        if ds < step:
            vx = 0
            vy = 0
        elif ds >= step:
            vx = chase_speed * math.cos(theta)
            vy = chase_speed * math.sin(theta)
        vx = round(vx, 2)
        vy = round(vy, 2)
        updated_velocities.append((vx, vy))
    return ["围追堵截", rid_list, pos_list, updated_velocities]
   
def contain(action_params: dict, args_list: list) -> list:
    """牵制处理器"""
    def vari_calcu(ds_list: list[float]) -> float:
        """方差计算"""
        n = len(ds_list)
        if n == 0:
            return 0.0
        sum_ds = 0
        total = 0
        for ds in ds_list:   
            sum_ds += ds
        mean_ds = sum_ds / n
        for ds in ds_list:
            delta = (ds - mean_ds) ** 2
            total += delta
        variance = total / n
        return variance
    def mesh_points(pos_list: list, R: float, 
                    pos0: list, mesh_dict: dict) -> list:
        """
        遍历对方机器人和网格点，
        基于方差找出一块到对方距离都接近的区域
        """
        flat_pos = mesh_dict["flat_pos"]
        if not pos_list:
            return []
        # 存储(方差，网格)
        candidates = []
        for point in flat_pos:
            ds0, *_ = ds_theta_calcu(pos0, point)
            if ds0 >= R:
                continue
            ds_list = []
            for pos in pos_list:
                ds, *_ = ds_theta_calcu(point, pos)
                ds_list.append(ds)  
            variance = vari_calcu(ds_list)    
            candidates.append((variance, point))  
        # 按方差升序排序
        candidates.sort(key = lambda c: c[0])
        # 取出方差最小的25个点
        K = 25
        near_points = [c[1] for c in candidates[:K]]
        return near_points
    params = action_params
    v = params.get("v", ROBOT_V)
    hol = args_list[HOLDER]
    env = args_list[ENV]
    step = v * DT
    vx, vy = 0, 0
    R = 5 * step
    if env:
        ball_pos = env["env.ball.pos"]
        Env = env["env.robots"]
        mesh = env["env.mesh"]
        if hol:
            # 假定牵制者就是持球机
            x0, y0 = hol["holder.pos"]
            team0 = hol["holder.team"]
            rid0 = hol["holder.id"]
            if not x0 or not y0 or not team0 or not rid0:
                return None
            if team0 in ["our", "opp"]:
                pos_list = []
                for rob in Env:
                    if rob[ENV_TEAM] != team0:
                        x, y = rob[ENV_X], rob[ENV_Y]
                        if x is not None and y is not None:
                            ds, *_ = ds_theta_calcu((x0, y0), (x, y))
                            # 如果对手在5帧距离开外,直接无视
                            if ds >= R:
                                continue
                            pos_list.append((x, y))
                # 利用mesh推算牵制者的目标点范围
                if pos_list:
                    near_points = mesh_points(pos_list, R, (x0, y0), mesh)
                    if near_points:
                        point = random_choose(near_points)
                        if point:
                            ds1, theta, *_ = ds_theta_calcu((x0, y0), point)
                            vx = v * math.cos(theta)
                            vy = v * math.sin(theta)
                else:
                    vx = 0
                    vy = 0
            vx = round(vx, 2)
            vy = round(vy, 2)
            return ["牵制", ["ball", f"{team0}_{rid0}"], 
                    [ball_pos, (x0, y0)], [(vx, vy), (vx, vy)]]
    return None

def sprint(action_params: dict, args_list: list) -> list:
    """破袭处理器"""
    params = action_params
    v = params.get("v", ROBOT_V)
    step = v * DT
    hol = args_list[HOLDER]
    target = hol["holder.target"]
    team0 = hol["holder.team"]
    rid0 = hol["holder.min_mate_id"]
    x, y = hol["holder.min_mate_pos"]
    ds, theta = ds_theta_calcu((x, y), target)
    vx = v * math.cos(theta)
    vy = v * math.sin(theta)
    # 破袭者初始无球，先跑好位置等队友传球
    return ["破袭", [f"{team0}_{rid0}"], [(x, y)], [(vx, vy)]]

# ============ 注册动作 ============
""" 
动作处理器：外部定义后注册
"""

actions = ["射门", "传球", 
           "带球", "控场防守", "漫游", 
           "围追堵截", "牵制", "破袭"]
handlers = [shoot, prepass,
            carry, control_offence, rove,
            goofy_move, contain, sprint]

def actions_register(actions: list[str], handlers: list):
    if not actions:
        actions = ["射门", "传球", 
           "带球", "控场防守", "漫游", 
           "围追堵截", "牵制", "破袭"]
    if not handlers:
        handlers = [shoot, prepass,
            carry, control_offence, rove,
            goofy_move, contain, sprint]
    for i, action in enumerate(actions):
        register_action(action, handlers[i])
    # register_action("射门", shoot)
    # register_action("传球", prepass)
    # register_action("带球", carry)
    # register_action("控场防守", control_offence)
    # register_action("漫游", rove)
    # register_action("围追堵截", goofy_move)
    # register_action("牵制", contain)
    # register_action("破袭", sprint)
    
actions_register(actions, handlers)

def Rules_initalize(Rules: list = [],
                    params: list = actions_params_list,
                    priority_list: list = priority_list,
                    descriptions: list = descriptions_list):
    # 初始化大规则库，动作名,条件,动参,优先级无实际价值
    add_rule(Rules, "Rules", "通用:射门", [[]],
             ["射门"], [params[0]], priority_list[0], "attack",
             [descriptions[0]])
    add_rule(Rules, "Rules", "通用:传球", [[]],
             ["传球"], [params[1]], priority_list[1], "all",
             [descriptions[1]])
    add_rule(Rules, "Rules", "通用:优先传球", [[]],
             ["传球"], [params[1]], priority_list[2], "all",
             [descriptions[2]])
    add_rule(Rules, "Rules", "通用:带球", [[]],
             ["带球"], [params[2]], priority_list[3], "all",
             [descriptions[3]])
    add_rule(Rules, "Rules", "通用:控场防守", [[]],
             ["控场防守"], [params[3]], priority_list[4], "offence",
             [descriptions[4]])
    add_rule(Rules, "Rules", "通用:无球漫游", [[]],
             ["漫游"], [params[4]], priority_list[5], "all",
             [descriptions[5]])
    add_rule(Rules, "Rules", "策略:围追堵截", [[]],
             ["围追堵截"], [chase_params], 10.0, "offence",
             ["围追堵截:针对对方持球机器人围追堵截，但不考虑其他对手"])
    add_rule(Rules, "Rules", "策略:逼抢截断", [[]],
             ["逼抢截断"], [{}], 10.0, "offence",
             ["逼抢截断:多台机器人协同，一台上前逼抢，其他封锁传球路线"])
    add_rule(Rules, "Rules", "策略:破袭者", [[]],
             ["破袭"], [{}], 8.0, "attack",
             ["破袭:由其他牵制队友带球吸引对手注意，自己到达对手空当，伺机接收传球突破"])
    add_rule(Rules, "Rules", "策略:牵制者", [[]],
             ["牵制"], [{}], 8.0, "attack",
             ["牵制:持球在特定位置附近徘徊，当对手接近到一定距离后传球给破袭队友"])
    return Rules

def rules_choose(Rules: list, team: str,
                 conds_list: list,
                 rules_dict: dict,
                 strategy_style: str) -> tuple[list, list]:
    """
    先初始化大规则库，设计好除条件外的其他规则参数
    函数中单独传入条件组，直接从大规则库中提取规则参数
    然后基于用户选用的战术规则去匹配条件字典
    用条件字典初始化运行库
    规则按类型分为通用规则和策略规则
    通用规则总是启用，策略规则根据战术策略启用
    """
    def get_args_from_name(team: str, rule_name: str):
        name = rule_name
        # 动作链默认顺序执行
        if team == "our":
            match name:
                case "策略:逼抢截断":
                    actions = ["逼抢截断"]
                    conds_list = [our_cut_conds]
                    params_list = [chase_params]
                    priority = 9.0
                case "策略:破袭者":
                    actions = ["破袭", "带球", "射门"]
                    conds_list = [our_sprint_conds, our_carry_conds, our_shoot_conds]
                    params_list = [sprint_params, carry_params, shoot_params]
                    priority = 8.1
                case "策略:牵制者":
                    # 牵制者先牵制2帧，然后带球1帧，最后传球队友
                    actions = ["带球", "牵制", "牵制", "传球"]
                    conds_list = [our_carry_conds, our_contain_conds, 
                                  our_contain_conds, our_pass_conds]
                    params_list = [carry_params, contain_params, 
                                   contain_params, pass_params]
                    priority = 8.7
                case _:
                    return None, None, None, None
        elif team == "opp":
            match name:
                case "策略:围追堵截":
                    actions = ["围追堵截"] 
                    conds_list = [opp_chase_conds] 
                    params_list = [chase_params] 
                    priority = 10.0
                case "策略:逼抢截断":
                    actions = ["逼抢截断"]
                    conds_list = [opp_cut_conds]
                    params_list = [chase_params]
                    priority = 10.0
                case _:
                    return None, None, None, None
        if len(actions) != len(conds_list) or len(actions) != len(params_list):
            print(f"规则 {rule_name} 动作/条件/动参长度不一致!")
            return None, None, None, None
        return (actions, conds_list, 
                params_list, priority)
    if not Rules:
        Rules = Rules_initalize()
    running_rules = []
    print("正在基于给定的战术匹配规则...")
    choice = strategy_style
    strategy_rules = None
    if team == "our":
        base_name = "our_rules"
        match choice:
            case "双人成行":
                strategy_rules = ["策略:牵制者", "策略:破袭者", ]
            case "锋矢阵":
                strategy_rules = ["策略:牵制者", "策略:破袭者", "策略:逼抢截断"]
            case "铁锅阵":
                strategy_rules = ["策略:牵制者", "策略:破袭者", ]
            case _:
                print("未匹配到对应的战术策略!")
    elif team == "opp":
        base_name = "opp_rules"
        match choice:
            case "双人成行":
                strategy_rules = ["策略:围追堵截"]
            case "锋矢阵":
                strategy_rules = ["策略:围追堵截"]
            case "铁锅阵":    
                strategy_rules = ["策略:逼抢截断"]
            case _:
                print("未匹配到对应的战术策略!")
    if rules_dict:
        # 获取通用规则的参数
        # ps:取用副本，避免原字典被修改
        conditions_list = conds_list.copy() if conds_list else []
        rulename_list = rules_dict["rulename_list"].copy()
        actions_list = rules_dict["actions_list"].copy()
        actions_params_list = rules_dict["actions_params_list"].copy()
        priority_list = rules_dict["priority_list"].copy()
        descriptions_list = rules_dict["descriptions_list"].copy()
        phase_list = rules_dict["phase_list"].copy()
        if strategy_rules:
            for name in strategy_rules:
                # 从大规则库抽取规则
                rule = get_rule_from_name(Rules, name)
                actions = rule[RULE_ACTIONS]
                actions_params = rule[RULE_ACTIONS_PARAMS]
                phase = rule[RULE_PHASE]
                descriptions = rule[RULE_DESCRIPTIONS]
                # 对应参数一一添加
                actions, conds, actions_params, priority, *_ = get_args_from_name(team, name)
                conditions_list.append(conds)
                rulename_list.append(name)
                actions_list.append(actions)
                actions_params_list.append(actions_params)
                priority_list.append(priority)
                phase_list.append(phase)
                descriptions_list.append(descriptions)
        for i, conds in enumerate(conditions_list):
            add_rule(running_rules, base_name,
                     rulename_list[i], 
                     conds, actions_list[i],
                     actions_params_list[i],
                     priority_list[i], 
                     phase_list[i],
                     descriptions_list[i],
                     enabled = True)
    else:
        return
    return running_rules

# 推断对手采取策略并应对的策略生成器

