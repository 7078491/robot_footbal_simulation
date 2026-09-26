# import os
# import tkinter as tk
# from PIL import Image, ImageDraw, ImageTk
# from robot_football_base import LINE, HEIGHT
# img_path = os.path.join("simulation_frames", "frame_0000.png")
# # ============ Tkinter 显示和交互 ============
# root = tk.Tk()
# root.title("机器人足球仿真 - 战术路线获取")
# # 转换 PIL 图像为 tkinter 格式
# img = Image.open(img_path)
# tk_image = ImageTk.PhotoImage(img)
# # 在 Canvas 上显示图像
# canvas = tk.Canvas(root, width = LINE, height = HEIGHT)
# canvas.pack()
# # 在画布上放置图像
# canvas.create_image(0, 0, anchor="nw", image=tk_image)
# canvas.image = tk_image  
# forward_points_1 = []
# forward_points_2 = []
# pass_points = []
# def on_canvas_click_1(event):
#     """鼠标点击事件处理函数"""
#     x = event.x
#     y = event.y
#     # 记录坐标
#     forward_points_1.append((x, y))
#     print(f"点击位置: {(x, y)}")
#     print(f"已记录 {len(forward_points_1)} 个点")
#     # 在点击位置画一个点作为标记
#     canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="red")
#     # 显示坐标文字
#     canvas.create_text(x+10, y-10, text=f"{(x, y)}", fill="white", anchor="w")
# def on_canvas_click_2(event):
#     """鼠标点击事件处理函数"""
#     x = event.x
#     y = event.y
#     # 记录坐标
#     forward_points_2.append((x, y))
#     print(f"点击位置: {(x, y)}")
#     print(f"已记录 {len(forward_points_2)} 个点")
#     # 在点击位置画一个点作为标记
#     canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", outline="blue")
#     # 显示坐标文字
#     canvas.create_text(x+10, y-10, text=f"{(x, y)}", fill="white", anchor="w")
# def on_canvas_click_3(event):
#     """鼠标点击事件处理函数"""
#     x = event.x
#     y = event.y
#     # 记录坐标
#     pass_points.append((x, y))
#     print(f"点击位置: {(x, y)}")
#     print(f"已记录 {len(pass_points)} 个点")
#     # 在点击位置画一个点作为标记
#     canvas.create_oval(x-3, y-3, x+3, y+3, fill="cyan", outline="cyan")
#     # 显示坐标文字
#     canvas.create_text(x+10, y-10, text=f"{(x, y)}", fill="white", anchor="w")

# def clear_points():
#     """清除所有标记点"""
#     forward_points_1.clear()
#     forward_points_2.clear()
#     pass_points.clear()
#     # 重新显示图像（清除所有绘制）
#     canvas.delete("all")
#     canvas.create_image(0, 0, anchor="nw", image=tk_image)
#     print("已清除所有标记点")

# def save_coordinates_1():
#     """保存坐标到文件"""
#     if forward_points_1:
#         with open("forward_points_1.txt", "w") as f:
#             for x, y in forward_points_1:
#                 # ps:方便后续作为路径列表传给其他函数
#                 f.write(f"({x/LINE:.2f}*line, {y/HEIGHT:.2f}*height), \n")
#         print(f"已保存 {len(forward_points_1)} 个坐标到 forward_points_1.txt")
#     else:
#         print("没有坐标可保存")
# def save_coordinates_2():
#     """保存坐标到文件"""
#     if forward_points_2:
#         with open("forward_points_2.txt", "w") as f:
#             for x, y in forward_points_2:
#                 # ps:方便后续作为路径列表传给其他函数
#                 f.write(f"({x/LINE:.2f}*line, {y/HEIGHT:.2f}*height), \n")
#         print(f"已保存 {len(forward_points_2)} 个坐标到 forward_points_2.txt")
#     else:
#         print("没有坐标可保存")
# def save_coordinates_3():
#     """保存坐标到文件"""
#     if pass_points:
#         with open("pass_points.txt", "w") as f:
#             for x, y in pass_points:
#                 # ps:方便后续作为路径列表传给其他函数
#                 f.write(f"({x/LINE:.2f}*line, {y/HEIGHT:.2f}*height), \n")
#         print(f"已保存 {len(pass_points)} 个坐标到 pass_points.txt")
#     else:
#         print("没有坐标可保存")

# # 绑定鼠标左键点击事件
# canvas.bind("<Button-1>", on_canvas_click_1)
# canvas.bind("<Button-3>", on_canvas_click_2)
# canvas.bind("<Button-2>", on_canvas_click_3)

# # 添加控制按钮
# button_frame = tk.Frame(root)
# button_frame.pack(pady=5)

# clear_btn = tk.Button(button_frame, text="清除标记", command=clear_points)
# clear_btn.pack(side=tk.LEFT, padx=5)

# save_btn_1 = tk.Button(button_frame, text="保存坐标(1)", command=save_coordinates_1)
# save_btn_1.pack(side=tk.LEFT, padx=5)
# save_btn_2 = tk.Button(button_frame, text="保存坐标(2)", command=save_coordinates_2)
# save_btn_2.pack(side=tk.LEFT, padx=5)
# save_btn_3 = tk.Button(button_frame, text="保存坐标(3)", command=save_coordinates_3)
# save_btn_3.pack(side=tk.LEFT, padx=5)

# # 显示提示
# info_label = tk.Label(root, text="左键点击球场记录坐标 | 清除标记 | 保存坐标到文件")
# info_label.pack(pady=5)
# root.mainloop()

import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from robot_football_base import LINE, HEIGHT

# ============ 1. 先创建主窗口 ============
root = tk.Tk()
root.title("机器人足球仿真 - 战术路线获取")

# ============ 2. 加载图片 ============
image_path = os.path.join("simulation_frames", "frame_0000.png")
if not os.path.exists(image_path):
    image_path = os.path.join("generated_images", "机器人足球仿真:frame0.png")
    if not os.path.exists(image_path):
        # 创建空白球场
        img = Image.new("RGBA", (LINE + 1, HEIGHT + 1), color=(19, 19, 19, 255))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0, 0, LINE, HEIGHT], outline=(255, 255, 255, 255), width=2)
        draw.line([LINE/2, 0, LINE/2, HEIGHT], fill=(255, 255, 255, 255), width=2)
        draw.ellipse([LINE/2 - 80, HEIGHT/2 - 80, LINE/2 + 80, HEIGHT/2 + 80], 
                     outline=(255, 255, 255, 255), width=2)
        draw.rectangle([0, HEIGHT/2 - 100, 150, HEIGHT/2 + 100], 
                       outline=(255, 255, 255, 255), width=2)
        draw.rectangle([LINE - 150, HEIGHT/2 - 100, LINE, HEIGHT/2 + 100], 
                       outline=(255, 255, 255, 255), width=2)
        img.save("empty_field.png")
        image_path = "empty_field.png"

img = Image.open(image_path)

# ============ 3. 创建 PhotoImage（在 root 之后） ============
tk_image = ImageTk.PhotoImage(img)

# ============ 4. 创建画布并显示 ============
canvas = tk.Canvas(root, width=LINE, height=HEIGHT)
canvas.pack()
canvas.create_image(0, 0, anchor="nw", image=tk_image)
canvas.image = tk_image  # 保持引用

forward_points_1 = []
forward_points_2 = []
pass_points = []


def on_canvas_click_1(event):
    """左键点击 - 记录路线1"""
    x, y = event.x, event.y
    if x < 0 or x > LINE or y < 0 or y > HEIGHT:
        return
    forward_points_1.append((x, y))
    print(f"路线1 点击位置: ({x}, {y})，共 {len(forward_points_1)} 个点")
    canvas.create_oval(x-3, y-3, x+3, y+3, fill="red", outline="red", tags="marker")
    canvas.create_text(x+10, y-10, text=f"{len(forward_points_1)}", fill="white", anchor="w", tags="marker")


def on_canvas_click_2(event):
    """右键点击 - 记录路线2"""
    x, y = event.x, event.y
    if x < 0 or x > LINE or y < 0 or y > HEIGHT:
        return
    forward_points_2.append((x, y))
    print(f"路线2 点击位置: ({x}, {y})，共 {len(forward_points_2)} 个点")
    canvas.create_oval(x-3, y-3, x+3, y+3, fill="blue", outline="blue", tags="marker")
    canvas.create_text(x+10, y-10, text=f"{len(forward_points_2)}", fill="white", anchor="w", tags="marker")


def on_canvas_click_3(event):
    """中键点击 - 记录传球点"""
    x, y = event.x, event.y
    if x < 0 or x > LINE or y < 0 or y > HEIGHT:
        return
    pass_points.append((x, y))
    print(f"传球点 点击位置: ({x}, {y})，共 {len(pass_points)} 个点")
    canvas.create_oval(x-3, y-3, x+3, y+3, fill="cyan", outline="cyan", tags="marker")
    canvas.create_text(x+10, y-10, text=f"P{len(pass_points)}", fill="white", anchor="w", tags="marker")


def clear_points():
    """清除所有标记点"""
    forward_points_1.clear()
    forward_points_2.clear()
    pass_points.clear()
    canvas.delete("marker")
    print("已清除所有标记点")


def save_coordinates_1():
    """保存路线1坐标"""
    if forward_points_1:
        with open("forward_points_1.txt", "w") as f:
            for x, y in forward_points_1:
                f.write(f"[{x:.1f}, {y:.1f}],\n")
        print(f"已保存 {len(forward_points_1)} 个坐标到 forward_points_1.txt")
    else:
        print("没有坐标可保存")


def save_coordinates_2():
    """保存路线2坐标"""
    if forward_points_2:
        with open("forward_points_2.txt", "w") as f:
            for x, y in forward_points_2:
                f.write(f"[{x:.1f}, {y:.1f}],\n")
        print(f"已保存 {len(forward_points_2)} 个坐标到 forward_points_2.txt")
    else:
        print("没有坐标可保存")


def save_coordinates_3():
    """保存传球点坐标"""
    if pass_points:
        with open("pass_points.txt", "w") as f:
            for x, y in pass_points:
                f.write(f"[{x:.1f}, {y:.1f}],\n")
        print(f"已保存 {len(pass_points)} 个坐标到 pass_points.txt")
    else:
        print("没有坐标可保存")


# 绑定鼠标事件
canvas.bind("<Button-1>", on_canvas_click_1)   # 左键
canvas.bind("<Button-3>", on_canvas_click_2)   # 右键
canvas.bind("<Button-2>", on_canvas_click_3)   # 中键

# 控制按钮
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

clear_btn = tk.Button(button_frame, text="清除标记", command=clear_points)
clear_btn.pack(side=tk.LEFT, padx=5)

save_btn_1 = tk.Button(button_frame, text="保存路线1", command=save_coordinates_1)
save_btn_1.pack(side=tk.LEFT, padx=5)

save_btn_2 = tk.Button(button_frame, text="保存路线2", command=save_coordinates_2)
save_btn_2.pack(side=tk.LEFT, padx=5)

save_btn_3 = tk.Button(button_frame, text="保存传球点", command=save_coordinates_3)
save_btn_3.pack(side=tk.LEFT, padx=5)

# 提示标签
info_label = tk.Label(
    root, 
    text="左键:路线1 | 右键:路线2 | 中键:传球点 | 清除标记 | 保存坐标到文件",
    fg="gray"
)
info_label.pack(pady=5)

root.mainloop()