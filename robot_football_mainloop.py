"""
这是一个关于机器人足球仿真的项目代码示例。
目的旨在展现一场5v5的机器人足球比赛中的单方策略与逻辑结构。
Mesh网格划分 若干小矩形
单方策略（举例）：
    2攻2守的梯形结构
逻辑结构：
    机器人
        1.能运动
        2.简单控球（触球）
        3.能与别机通讯实现协作（广播）    
    基本动作定义
        1.传球
        2.射门
        3.抢断
        4.防守
----------------------------------------
规则库
    规则定义，环境参数，推理机
    用环境参数去匹配规则
    1.生成时序数据集
    2.用时序数据集初始化环境参数并进行绘图
    3.环境参数更新后匹配规则库找出规则集
    4.执行规则集对应的动作集
    5.动作集返回参数更新时序数据集
----------------------------------------

规则基于参数判断：
    for id in all_id:
        I.计算本机的传球有利位置
        II.计算本机的射门有利位置
        if 持球:
            1. 自己带,前往II
            2. 传队友,传到I
        elif 无球:
            1. 队友持球,钻空当
            2. 对手持球,防守或尝试抢断
        
主循环结构更新:
    1.调用库和头文件
        from ... import ...
        import ...

    2.初始化数据,提取预设路径
        frame = 0 帧
        running = True
        strategy_dict = ...

    3.主循环主体结构
        if __name__ == "__main__":
            while running:
                更新时序数据(位置，速度) = locat_veloc_update(...)
                构造球路 = ...
                更新时序轨迹 = traje_update(...)
                划分区域并绘制 frame_draw(...)
        
                参数更新 = Env_update(...)
                计算参数，生成规则参数表 = args_calcu(...)
                规则匹配执行 = ...
        
                帧数自增，日志更新
                延迟 time.sleep(dt)
                生成动画
        
                设定条件达成，循环结束

"""
# 只调用基本库或者可靠的第三方库，以及自己的文件
from robot_football_data_update import (loc_vel_update, Env_update,
                                        traje_update, calcu_args,
                                        auto_set_haveball)
from robot_football_section_calcu import mesh_division
from robot_football_field_draw import frame_draw
from robot_football_convertion import opp_convert, convert_opp
from robot_football_strategy import strategy_generate
from robot_football_rule_base import auto_match_execute
from robot_football_base import (DT, OUTPUT_FOLDER, MAX_FRAMES, FRAME_DELAY,
                                 Environ, args_global, clone,
                                 ball_pos, ball_v, 
                                 frame_locat_dict, frame_veloc_dict, 
                                 frame_traje_dict)
from robot_football_access import (document_log, folder_generate, 
                                   get_savepath, video_generate,
                                   export_frames_to_folder,
                                   )# play_from_folder) ---> 从指定文件播放动画的函数
import time
print("\n 机器人足球仿真模拟程序启动! \n")
FRAME_DIR = folder_generate(OUTPUT_FOLDER, exist_clear = True)
# 主循环
frame = 0
running = True
strategy_dict = strategy_generate()
if strategy_dict:
    our_points = strategy_dict["our_points"]
    opp_points = strategy_dict["opp_points"]
    our_rules = strategy_dict["our_rules"]
    opp_rules = strategy_dict["opp_rules"]
    ball_points = []
if __name__ == "__main__":
    while running:
        if frame == 0:
            ball_pos[0] = our_points[1][0][0] - 13
            ball_pos[1] = our_points[1][0][1] - 13
            ball_points.append(ball_pos)
            our_act_list = []      
            opp_act_list = []
            act_list = []
        # 时序表更新
        frame_locat_dict, frame_veloc_dict, points_list, n_list = loc_vel_update(frame, DT, 
                                              frame_locat_dict, frame_veloc_dict,
                                              strategy_dict, ball_pos, ball_v,
                                              act_list)
        # print(f"{frame_locat_dict}, \n {frame_veloc_dict}, \n{frame_traje_dict}")
        ball_pos = frame_locat_dict["ball"]
        frame_traje_dict = traje_update(3, n_list, strategy_dict, frame_traje_dict)
        # 区域更新
        best_points, mesh_dict, *_ = mesh_division(args_global, frame_locat_dict)
        # 全局环境更新
        Environ = Env_update(Environ, frame_locat_dict, frame_veloc_dict)
        Environ = auto_set_haveball(ball_pos, Environ)
        # 规则参数字典列表匹配规则
        args_global = calcu_args(args_global, Environ, mesh_dict, 
                                 act_list, best_points, ball_pos)
        args_opp = clone(args_global)
        args_opp = convert_opp(args_opp)
        if frame >= 1:
            our_act_list = []
            opp_act_list = []
            act_list = []
            ball_points.append(ball_pos)
        print(f"每帧参数自动更新并匹配规则,规则参数生成: \n{args_global[-3:]}")
        our_act_list = auto_match_execute(our_rules, args_global, our_act_list)
        opp_act_list = auto_match_execute(opp_rules, args_opp, opp_act_list)
        if opp_act_list:
            print(opp_act_list)
            opp_act_list = opp_convert(opp_act_list)
        else:
            opp_act_list = []
        act_list = our_act_list + opp_act_list
        print(f"动作列表测试打印: \n {act_list}") 
        # 绘图显示
        frame_path = get_savepath(FRAME_DIR, frame, "frame", "png")
        img, name0, all_robot = frame_draw(frame, mesh_dict, frame_path, 
                                           frame_locat_dict, frame_traje_dict)
        frame += 1
        if frame >= MAX_FRAMES:
            delta_t = document_log(frame, DT, ball_points, our_points, opp_points)
            running = False
        time.sleep(DT)
    # ps:这里只要修改备份文件夹名称就能创建新文件夹
    export_frames_to_folder("simulation_frames", "simulation_backup1")
    print(f"\n 仿真动画播放中: \n")
    video_generate(FRAME_DIR, FRAME_DELAY)