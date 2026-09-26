"""
绘图函数汇总:划线,生成球场,机器人,足球
基于帧数自增的动画函数实现
青色(Cyan):(0, 255, 255)
"""
from robot_football_base import (LINE, HEIGHT, WIGHT, 
                                 BALL_COLOR, BLACK,
                                 OUR_POINTS_COLOR,
                                 OPP_POINTS_COLOR,
                                 OUR_COLOR, OPP_COLOR)
from PIL import Image, ImageDraw
import math
import os
def image_output_path(name: str = None):
    """返回统一的图片输出路径"""
    if name is not None and os.path.isabs(name):
        return name
    return None
def draw_line(img: any = None, sp: list = None, ep: list = None,
              lines: list = None, linestyle: int = 1, color: str = None):
    # ps:color要传入元组(red, green, blue, alpha)
    # lines范围仅限于1,2,3,4,5
    # linestyle范围为1,2,3
    x0, y0 = sp
    x1, y1 = ep
    dx = x1 - x0
    dy = y1 - y0
    # abs()绝对值
    steps = max(abs(dx), abs(dy))
    # 法向偏移实现加粗
    length = math.sqrt(dx ** 2 + dy ** 2) if steps > 0 else 1
    nx = - dy / length
    ny = dx / length
    half = lines // 2
    if lines % 2 == 1:
        offsets = list(range(-half, half + 1))
    else:
        offsets = list(range(-half + 1, half + 1))
    for i in range(1, round(steps) + 1, linestyle):
        t = i / steps if steps > 0 else 0
        # round()四舍五入
        bas_x = x0 + dx * t
        bas_y = y0 + dy * t
        for offset in offsets:
            x = round(bas_x + nx * offset)
            y = round(bas_y + ny * offset) 
            # 避免访问越界
            if 0 <= x < LINE and 0 <= y < HEIGHT:
                img.putpixel((x, y), color)
    return True
# 折线
def draw_lines(img: any = None, points: list = None, 
               lines: int = 3, linestyle: int = 1, 
               color: str = None):
    for i in range(len(points) - 1):
        draw_line(img, points[i], points[i+1], lines, linestyle, color)
    return True
# 球
def draw_ball(img: any = None, center: list = None, radius: int = 8):
    draw = ImageDraw.Draw(img)
    x, y = center
    draw.ellipse([x - radius, y - radius,
                  x + radius, y + radius], 
                 fill = BALL_COLOR)
# 仿真机器人初始化
def draw_robot(img: any = None, center: list = None, 
               fillcolor: str = None, radius: int = 10):
    draw = ImageDraw.Draw(img)
    x, y = center
    draw.ellipse([x - radius, y - radius,
                  x + radius, y + radius], 
                 fill = fillcolor, outline = "yellow")
    heading = math.pi if fillcolor == OUR_COLOR else 0
    x = center[0]
    y = center[1]
    d_r = radius * 1.2
    end = [x + d_r * math.cos(heading), y + d_r * math.sin(heading)]
    draw_line(img, center, end, 2, 1, WIGHT)
# 阵型推进
def format_move(img: any = None, ori_format: list = None, 
                color: str = None, leader_id: int = 1, 
                new_leader_pos: list = None):
    new_format = []
    x = new_leader_pos[0] - ori_format[leader_id - 1][0]
    y = new_leader_pos[1] - ori_format[leader_id - 1][1]
    delta_pos = [x, y]                          
    for i in range(len(ori_format)):
        new_pos = [ori_format[i][0] + delta_pos[0], 
                   ori_format[i][1] + delta_pos[1]]
        new_format.append(new_pos)
        draw_robot(img, new_format[i], color)
    return new_format
# 每帧路线
def frame_traje(img: any = None, frame_traje_dict: dict = None):
    for field, points in frame_traje_dict.items():
        # value 是包含至少3个点的二维列表
        if points != None:
            if len(points) >= 3:
                if field.startswith("our"):
                    draw_lines(img, points, 2, 1, OUR_POINTS_COLOR)
                elif field.startswith("opp"):
                    draw_lines(img, points, 2, 1, OPP_POINTS_COLOR)
    return img
# 整合绘图函数，逐帧更新
# 完整版
def frame_draw(frame: int = 0, 
               mesh_dict: dict = None, 
               output_path: str = None,
               frame_locat_dict: dict = None, 
               frame_traje_dict: dict = None,
               line: int = LINE, height: int = HEIGHT):
    if output_path is not None:
        name = os.path.basename(output_path)
        save_path = output_path
    else:
        # 默认路径
        name = f"机器人足球仿真: 第 {frame} 时刻 .png"
        save_path = image_output_path(name)
    img = Image.new("RGBA", (LINE + 1, HEIGHT + 1), color = BLACK)
    from robot_football_section_calcu import mesh_visual
    # 区域更新，内部已有检查
    img = mesh_visual(img, mesh_dict)
    # 球场线
    points_3 = [[round(line/2), 0], [round(line/2), round(height)]]
    points_4 = [[0, round(height*5/12)], [round(line/256), round(height*5/12)], 
                [round(line/256), round(height*7/12)], [0, round(height*7/12)]]
    points_5 = [[round(line), round(height*5/12)], [round(line*255/256), round(height*5/12)], 
                [round(line*255/256), round(height*7/12)], [round(line), round(height*7/12)]]
    draw_lines(img, points_3, 5, 1, WIGHT)
    draw_lines(img, points_4, 5, 1, WIGHT)
    draw_lines(img, points_5, 5, 1, WIGHT)
    # 预设位置
    ball_pos = None
    our_list = []
    opp_list = []
    if frame_locat_dict:
        for field, value in frame_locat_dict.items():
            if value is None:
                continue
            elif field.startswith("our"):
                our_list.append(value)
            elif field.startswith("opp"): 
                opp_list.append(value)
            elif field == "ball":
                ball_pos = value
    if frame_traje_dict:
        frame_traje(img, frame_traje_dict)
    # 拼接成当前帧所有机器人位置列表
    all_rob = our_list + opp_list
    for pos in our_list:
        draw_robot(img, pos, OUR_COLOR)
    for pos in opp_list:
        draw_robot(img, pos, OPP_COLOR)
    if ball_pos is not None:
        draw_ball(img, ball_pos)
    if save_path is not None:
        img.save(save_path)
        print(f"当前帧已保存: {save_path}")
    return img, name, all_rob