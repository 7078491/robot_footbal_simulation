""" 
常量数据库
"""
# ============ 索引常量 ============
# 规则索引
RULE_ID = 0             # id号
RULE_NAME = 1           # 规则名
RULE_CONDITIONS = 2     # 条件组
RULE_ACTIONS = 3        # 动作(链)
RULE_PROGRESS = 4       # 动作进程
RULE_ACTIONS_PARAMS = 5 # 动参
RULE_PRIORITY = 6       # 优先级
RULE_PHASE = 7          # 阶段
RULE_DESCRIPTIONS = 8   # 描述
RULE_ENABLED = 9        # 启用状态
RULE_HIT_COUNT = 10     # 触发次数
# 动作索引(返回值)
ACTION_NAME = 0         # 动作名
ACTION_OBJECTS = 1      # 执行实体序列
ACTION_POSITIONS = 2    # 位置序列
ACTION_VELOCITIES = 3   # 速度序列
# 机器人环境参数索引
ENV_TEAM = 0            # 队伍
ENV_ID = 1              # id号
ENV_X = 2               # 位置x
ENV_Y = 3               # 位置y
ENV_VX = 4              # 速度x
ENV_VY = 5              # 速度y
ENV_HAVEBALL = 6        # 持球状态
# 字典索引(保持4字典结构)
ENV = 0
HOLDER = 1
OUR = 2
OPP = 3
# 环境常数
LINE = 1000
HEIGHT = 800
FPS = 60
DT = 2.0 # 2.0s
OURGOAL = [LINE*63/64, HEIGHT/2]
OPPGOAL = [LINE/64, HEIGHT/2]
ROBOT_V = LINE * 0.035 # 35
BALL_VM = LINE * 0.075 # 75
BALL_DS = 30 # 可触球的最大距离
# 动画参数
OUTPUT_FOLDER = "simulation_frames"
MAX_FRAMES = 20
FRAME_DELAY = int(3 * DT * FPS)  # 3*120ms
# 颜色相关参数
WIGHT = (255, 255, 255, 255)
BLACK = (19, 19, 19, 255)
OUR_COLOR = "blue"
OPP_COLOR = "red"
BENEFIT_COLOR = (60, 179, 113, 200)
THREAT_COLOR = (75, 0, 130, 200)
DANGER_COLOR = (255, 69, 71, 200)
SAFE_COLOR = (0, 255, 255, 200)
SECT_LINE_COLOR = (255, 255, 0, 250)
BALL_COLOR = (222, 184, 135, 255)
OUR_POINTS_COLOR = (60, 179, 113, 200)
OPP_POINTS_COLOR = (128, 0, 128, 200)
# 球相关的全局变量
global ball_pos, ball_v
ball_v = [0, 0]
ball_pos = [LINE/2, HEIGHT/2]
# 机器人环境参数
Environ = [
    # 机器人实体
    #   0  ,   1   ,  2  ,  3  ,  4  ,  5  ,   6   
    # team ,id name,  x  ,  y  ,  vx ,  vy ,haveball
    ["our" ,  "1"  , None, None,  0  ,  0  ,   0   ],
    ["our" ,  "2"  , None, None,  0  ,  0  ,   0   ],
    ["our" ,  "3"  , None, None,  0  ,  0  ,   0   ],
    ["our" ,  "4"  , None, None,  0  ,  0  ,   0   ],
    ["our" ,  "5"  , None, None,  0  ,  0  ,   0   ],
    ["opp" ,  "1"  , None, None,  0  ,  0  ,   0   ],
    ["opp" ,  "2"  , None, None,  0  ,  0  ,   0   ],
    ["opp" ,  "3"  , None, None,  0  ,  0  ,   0   ],
    ["opp" ,  "4"  , None, None,  0  ,  0  ,   0   ],
    ["opp" ,  "5"  , None, None,  0  ,  0  ,   0   ]]

""" 
基础条件定义
"""
def cond(field: str, operator: str, 
         value: any, logic: str = "and") -> list:
    """
    创建条件
    Args:
        field (str): 事实字段名
        operator (str): 比较算符
        value (Any): 比较值
        logic (str, optional): 与前后条件逻辑关系
    Returns:
        List: [field, operator, value, logic]
    """
    return [field, operator, value, logic]
# 一定要注意条件的语义指代
# 按前缀为条件分3类,每个条件的语义都是准确的
# holder相关
our_hold = cond("holder.team", "==", "our")
opp_hold = cond("holder.team", "==", "opp")
shoot_clear = cond("holder.shoot_block", "==", False)
pass_clear = cond("holder.pass_block", "==", False)
mate_better = cond("holder.better_to_pass", "==", True)
has_space = cond("holder.min_opp_ds", ">", ROBOT_V * DT * 1.5)
under_press = cond("holder.min_opp_ds", "<=", ROBOT_V * DT * 2)
# Env相关
near_our_goal = cond("env.ball.to_our_goal", "<=", LINE / 4)
near_opp_goal = cond("env.ball.to_opp_goal", "<=", LINE / 4)
# 双方队伍相关
# ps:动作_触发(hit)
our_pass_hit = cond("our.act.pass_hit", "==", True)
our_contain_hit = cond("our.act.pass_hit", "==", True)
opp_pass_hit = cond("opp.act.pass_hit", "==", True)
opp_contain_hit = cond("opp.act.pass_hit", "==", True)
opp_chase_hit = cond("opp.act.chase_hit", "==", True)

# 射门条件组:持球,近门,无阻挡
our_shoot_conds = [our_hold, near_opp_goal, shoot_clear]
opp_shoot_conds = [opp_hold, near_our_goal, shoot_clear]
# 传球条件组:持球,有目标队友,无阻挡
our_pass_conds = [our_hold, mate_better, pass_clear]
opp_pass_conds = [opp_hold, mate_better, pass_clear]
# 优先传球条件组:持球,对手逼抢
our_pripass_conds = [our_hold, under_press]
opp_pripass_conds = [opp_hold, under_press]
# 带球条件组:持球,有空间
our_carry_conds = [our_hold, has_space]
opp_carry_conds = [opp_hold, has_space]
# 控场条件组:对手持球,多人压上
our_control_conds = [opp_hold]
opp_control_conds = [our_hold]
# 漫游条件组:未持球
our_rove_conds = []
opp_rove_conds = []
# 围追堵截条件 ps:这条只限对手有,对手持球,无脑追球
opp_chase_conds = [our_hold]
# 逼抢截断条件:对手持球
our_cut_conds = [opp_hold]
opp_cut_conds = [our_hold]
# 牵制条件:(对手围追堵截),持球,有空间
our_contain_conds = [our_hold, has_space]
opp_contain_conds = [opp_hold, has_space]
# 破袭条件:牵制触发(球已传)
our_sprint_conds = [our_contain_hit, has_space]
opp_sprint_conds = [opp_contain_hit, has_space]

""" 
动参定义
"""
# 射门
shoot_params = {
    "power": 1.0,
    "v": BALL_VM
}
# 传球
pass_params = {
    "power": 0.8,
    "v": BALL_VM,
}
# 带球
carry_params = {
    "robot_ball_dx": 13,
    "robot_ball_dy": 13,
    "v": ROBOT_V
}
# 控场
control_params = {
    "s": BALL_DS,
    "v": ROBOT_V
}
# 漫游
rove_params = {
    "v": ROBOT_V
}
# 追风赶月
chase_params = {
    "chase_speed": ROBOT_V
}
# 牵制
contain_params = {
    "v": ROBOT_V
}
# 破袭
sprint_params = {
    "v": ROBOT_V
}

# 规则只分区域规则和全局规则
our_conditions = [[our_shoot_conds], [our_pass_conds], [our_pripass_conds],
                  [our_carry_conds], [our_control_conds], [our_rove_conds]]
opp_conditions = [[opp_shoot_conds], [opp_pass_conds], [opp_pripass_conds],
                  [opp_carry_conds], [opp_control_conds], [opp_rove_conds]]
actions_list = [["射门"], ["传球"], ["传球"],
                ["带球"], ["控场防守"], ["漫游"]]
actions_params_list = [[shoot_params], [pass_params], [pass_params],
                       [carry_params], [{}], [rove_params]]
descriptions_list = [["射门:本机持球，且在对方半场内，与对方球门连线无遮挡"],
                    ["传球:本机持球，且存在队友处于有利位置，存在合适传球路径"],
                    ["优先传球:本机持球，且存在对手逼抢"],
                    ["带球:本机持球，无队友位置更好且前方有空间时"],
                    ["控场防守:阻止对手任意前进，占据有利位置"],
                    ["漫游:当我方持球时，以略低速度向有利区靠近"]]
# 这些是跟规则绑定的参数
rulename_list = ["通用:射门", "通用:传球", "通用:优先传球",
                 "通用:带球", "通用:控场防守", "通用:无球漫游"]
phase_list = ["attack", "all", "all", "all", "offence", "all"]
priority_list = [10.0, 6.5, 7.0, 7.9, 6.4, 4.9]

""" 
添加规则
部分策略类规则需要匹配动作链
"""
rules_dict = {
    "rulename_list": rulename_list,
    "actions_list": actions_list,
    "actions_params_list": actions_params_list,
    "phase_list": phase_list,
    "priority_list": priority_list,
    "descriptions_list": descriptions_list
}
# 时序位置与速度集
# 位置x, y
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
# 速度vx, vy
# 所有机器人速度大小均定为ROBOT_V
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
# 包含当前帧的轨迹
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
# ============ 字典列表 ===============
# 计算所得结果
Env_args = {
    "env.robots": Environ,
    "env.ball.pos": None,
    "env.ball.to_our_goal": None,
    "env.ball.to_opp_goal": None,
    "env.mesh": {},
    
}

holder_args = { 
    "holder.pos": None,
    "holder.team": None,
    "holder.id": None,
    "holder.min_mate_ds": None,
    "holder.min_mate_pos": None,
    "holder.min_mate_id": None,
    "holder.min_opp_ds": None,
    "holder.min_opp_pos": None,
    "holder.min_opp_id": None,
    "holder.shoot_block": None,
    "holder.pass_block": None,
    "holder.better_to_pass": None,
    "holder.target_pos": None
}

our_args = {
    "our.benefit.exists": None, 
    "our.benefit.points": None,
    "our.act.contain_hit": False,
    "our.act.pass_hit": False,
    "our.act.carry_hit": True
}

opp_args = {
    "opp.benefit.exists": None, 
    "opp.benefit.points": None,
    "opp.act.contain_hit": False,
    "opp.act.pass_hit": False,
    "opp.act.chase_hit": False,
    "opp.act.carry_hit": True
}

# 大规则库(显示规则格式),加入所有通用规则
Rules = [
    #   ID , 名称 , 条件组列表,  动作序列 , 动作进程 , 动参列表 , 优先级 , 阶段, 描述列表,  启用 , 触发次数]
    #   0  ,  1  ,     2    ,   3      ,    4   ,   5     ,  6   ,   7   ,  8  ,    9  ,   10
]
# 双方选用的运行库配置和参数库
our_rules, opp_rules = [], []

# 创建对象函数
def clone(obj: any) -> any:
    # 递归克隆元素
    if isinstance(obj, dict):
        return {k: clone(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [clone(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(clone(v) for v in obj)
    return obj

args_global = [Env_args, holder_args, our_args, opp_args]
