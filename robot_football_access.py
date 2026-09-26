"""
机器人动作执行完成后，调用评价函数评分
写入日志记录
"""
# 以下所调用的模块均为可靠模块
# ps:文件处理相关的部分是AI做的
from robot_football_base import FRAME_DELAY
from robot_football_section_calcu import still_region_weights
import os
import shutil
import tkinter as tk
from PIL import Image, ImageTk
# 升级版日志函数
# 记录每次演示时机器人和球的位置数据并写入文件
def document_log(frame: int = 0, dt: float = None,
                 ball_points: list = None, 
                 our_points: list = None, 
                 opp_points: list = None):
    with open("./document_log.txt", "w", encoding="utf-8") as f:
        delta_t = frame * dt
        f.write(f"演示数据如下: \n")
        if ball_points != None:
            f.write(f"本次演示的球路为: {ball_points} \n")
            # ball_pos = ball_points[frame]
            # f.write(f"足球在{delta_t:3f}s的位置: [{ball_pos[0]:.1f}, {ball_pos[1]:.1f}] \n")
        f.write("注意，下述路线各点为运动路线节点 \n")
        if our_points != None:
            for i in range(len(our_points)):
                f.write(f"我方{i+1}号机的行动折线:{our_points[i]} \n")
        if opp_points != None:
            for i in range(len(opp_points)):
                f.write(f"对方{i+1}号机的行动折线:{opp_points[i]} \n")
    print("\n 机器人与足球的位置信息已写入日志。 \n")
    return round(delta_t, 3)
# 存帧文件夹
def folder_generate(name: str, exist_clear: bool = False):
    # 清空文件夹
    def folder_clear(name: str):
        """清空文件夹中的所有内容"""
        if not os.path.exists(name):
            print("目标文件夹不存在!")
            return
        for item in os.listdir(name):
            item_path = os.path.join(name, item)
            if os.path.isfile(item_path):
                os.remove(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
    if not os.path.exists(name):
        os.makedirs(name)
        print(f"存帧文件夹{name}已创建: ")
    else:
        if exist_clear:
            folder_clear(name)
            print(f"存帧文件夹{name}已清空: ")
    return os.path.abspath(name)
# 每帧图片的保存路径获取
def get_savepath(name: str, n_frame: int, 
                 prefix: str = "frame", ext: str = "png"):
    def get_filename(n_frame: int,  # 文件名生成
                     prefix: str = "frame", ext: str = "png"):
        return f"{prefix}_{str(n_frame).zfill(4)}.{ext}"
    filename = get_filename(n_frame, prefix, ext)
    return os.path.join(name, filename)
# 获取所有文件
def list_files(name: str, ext: str = "png"):
    """列出文件夹中所有指定扩展名的文件（已排序）"""
    if not os.path.exists(name):
        return []
    files = [f for f in os.listdir(name) 
             if f.endswith(f".{ext}")]
    files.sort()
    return files
# 动画生成
_playback_state = {
    "paused": False,
    "current_index": 0,
    "images": [],
    "window": None,
    "label": None,
    "after_id": None,
    "delay": FRAME_DELAY,  # 毫秒
}
# 帧更新函数
def _update_frame():
    global _playback_state
    state = _playback_state
    if state["window"] is None:
        return
    if state["paused"]:
        state["after_id"] = state["window"].after(100, _update_frame)
        return
    images = state["images"]
    if not images:
        return
    idx = state["current_index"]
    label = state["label"]
    label.config(image = images[idx])
    label.image = images[idx]
    total = len(images)
    state["window"].title(f"仿真动画: (点击可暂停) - 帧 {idx + 1}/{total}")
    next_idx = idx + 1
    if next_idx >= total:
        if state["loop"]:
            next_idx = 0
        else:
            return
    state["current_index"] = next_idx
    state["after_id"] = state["window"].after(state["delay"], _update_frame)
# 切换暂停函数
def _toggle_pause(event):
    global _playback_state
    state = _playback_state
    state["paused"] = not state["paused"]
    if state["paused"]:
        print("动画已暂停")
        state["window"].title("仿真动画: (点击可继续播放)")
    else:
        print("动画继续播放")
        state["window"].title("仿真动画: (点击可暂停)")
        if state["after_id"]:
            state["window"].after_cancel(state["after_id"])
        _update_frame()
# 动画综合
def video_generate(name: str, delay: int = FRAME_DELAY, loop: bool = True):
    global _playback_state
    files = list_files(name)
    if not files:
        print("查找目标图片失败!")
        return
    root = tk.Tk()
    root.title("仿真动画: (点击可暂停)")
    root.resizable(False, False)
    # ========== 主布局：左侧图片，右侧图例 ==========
    main_frame = tk.Frame(root)
    main_frame.pack(side=tk.LEFT, padx=10, pady=10)
    label = tk.Label(main_frame)
    label.pack()
    # ========== 图例（两列网格） ==========
    legend_frame = tk.Frame(root, relief=tk.RAISED, bd=2, padx=15, pady=15)
    legend_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)
    legend_title = tk.Label(legend_frame, text="🎨 图例", font=("Arial", 14, "bold"))
    legend_title.pack(pady=(0, 10))
    # 图例数据
    legend_items = [
        ("我方机器人", "#2039C2", "●"),
        ("对方机器人", "#FF0000", "●"),
        ("足球", "#DEB887", "●"),
        ("我方轨迹", "#3CB371", "─"),
        ("对方轨迹", "#792999", "─"),
        ("有利区域", "#3CB371", "■"),
        ("危险区域", "#DF27A1", "■"),
        ("安全区域", "#00FFFF", "■"),
        ("网格线", "#FFFF00", "─"),
        ("球场边界", "#FFFFFF", "─"),
    ]
    # 创建网格容器
    grid_frame = tk.Frame(legend_frame)
    grid_frame.pack()
    # 每行2列
    for i, (text, color, shape) in enumerate(legend_items):
        row = i // 2
        col = i % 2
        item_frame = tk.Frame(grid_frame)
        item_frame.grid(row=row, column=col, padx=8, pady=4, sticky="w")
        # 颜色标记
        color_box = tk.Canvas(item_frame, width=16, height=16, 
                              highlightthickness=0, bg="#2e2e2e")
        color_box.pack(side=tk.LEFT, padx=(0, 6))
        if shape == "●":
            color_box.create_oval(2, 2, 14, 14, fill=color, outline="white")
        elif shape == "■":
            color_box.create_rectangle(2, 2, 14, 14, fill=color, outline="gray")
        elif shape == "─":
            color_box.create_line(2, 8, 14, 8, fill=color, width=2)
        # 文字
        tk.Label(item_frame, text=text, font=("Arial", 9), 
                 fg="white", bg="#2e2e2e").pack(side=tk.LEFT)
    # ========== 操作提示 ==========
    tip_frame = tk.Frame(legend_frame)
    tip_frame.pack(pady=(10, 0))
    tk.Label(tip_frame, text="💡 点击画面暂停/继续 | ESC关闭",
             font=("Arial", 9), fg="#FFD700").pack()
    label.bind("<Button-1>", _toggle_pause)
    root.bind("<Escape>", lambda e: root.destroy())
    # ========== 加载图片 ==========
    images = []
    for filename in files:
        file_path = os.path.join(name, filename)
        img = Image.open(file_path)
        img.thumbnail((1000, 800), Image.Resampling.LANCZOS)
        images.append(ImageTk.PhotoImage(img))
    _playback_state["images"] = images
    _playback_state["current_index"] = 0
    _playback_state["paused"] = False
    _playback_state["delay"] = int(delay)
    _playback_state["loop"] = loop
    _playback_state["window"] = root
    _playback_state["label"] = label
    _playback_state["after_id"] = None
    _update_frame()
    root.mainloop()
        
def export_frames_to_folder(source_folder: str = "simulation_frames", 
                            target_folder: str = None,
                            prefix: str = "frame",
                            ext: str = "png"):
    """将源文件夹中的所有图片导出到目标文件夹"""
    # 检查源文件夹是否存在
    if not os.path.exists(source_folder):
        print(f"源文件夹不存在: {source_folder}")
        return 0
    # 获取源文件夹中的所有图片
    files = list_files(source_folder, ext)
    if not files:
        print(f"源文件夹中没有找到图片: {source_folder}")
        return 0
    # 如果未指定目标文件夹，弹出对话框选择
    if target_folder is None:
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.attributes('-topmost', True)
        target_folder = tk.filedialog.askdirectory(
            title="选择导出目标文件夹",
            initialdir=os.getcwd()
        )
        temp_root.destroy()
        if not target_folder:
            print("未选择目标文件夹，取消导出")
            return 0
    # 确保目标文件夹存在
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)
        print(f"创建目标文件夹: {target_folder}")
    # 复制文件
    exported_count = 0
    for filename in files:
        source_path = os.path.join(source_folder, filename)
        target_path = os.path.join(target_folder, filename)
        try:
            shutil.copy2(source_path, target_path)
            exported_count += 1
        except Exception as e:
            print(f"复制失败: {filename}, 错误: {e}")
    print(f"成功导出 {exported_count} 张图片到: {target_folder}")
    return exported_count

def play_from_folder(folder_path: str = None, delay: int = FRAME_DELAY):
    """从指定文件夹加载图片并播放动画"""
    # 如果未指定文件夹，弹出对话框选择
    if folder_path is None:
        temp_root = tk.Tk()
        temp_root.withdraw()
        temp_root.attributes('-topmost', True)
        folder_path = tk.filedialog.askdirectory(
            title="选择包含图片的文件夹",
            initialdir=os.getcwd()
        )
        temp_root.destroy()
        if not folder_path:
            print("❌ 未选择文件夹")
            return
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        print(f"❌ 文件夹不存在: {folder_path}")
        return
    # 检查文件夹中是否有图片
    files = list_files(folder_path)
    if not files:
        print(f"❌ 文件夹中没有找到图片: {folder_path}")
        return
    print(f"📁 从 {folder_path} 加载 {len(files)} 张图片")
    # 直接调用 video_generate 播放
    video_generate(folder_path, delay=delay, loop=True)
       
# 威胁系数:评估球员在不同位置的威胁能力
# ps:有需要再说
# 惩罚函数,评估危险系数
def danger_access(state: str, ball_pos: list, 
                  our_pos: list, opp_pos: list):
    # 危险系数:分防守,进攻两种权重,联合计算得到危险系数
    # 防守时危险系数尽量低,进攻时危险系数尽量高
    attack_weight = 0
    offend_weight = 0
    ball_weight = 10 * still_region_weights(ball_pos, state)
    match state:
        case "进攻":
            for pos in our_pos:
                attack_weight += 8 * still_region_weights(pos, state)
            for pos in opp_pos:
                attack_weight += -8 * still_region_weights(pos, state)
        case "防守":
            for pos in our_pos:
                offend_weight += 8 * still_region_weights(pos, state)
            for pos in opp_pos:
                offend_weight += -8 * still_region_weights(pos, state)
        case _:
            print("请重新输入状态!")
    danger = attack_weight + offend_weight + ball_weight
    if danger >= 30:
        danger_level = "强"
    elif 10 < danger < 30:
        danger_level = "中等"
    else:
        danger_level = "弱"
    match state:
        case "进攻":
            print(f"我方在{state}时，造成对方的危险系数为{danger}，评定等级:{danger_level}")
        case "防守":
            print(f"我方{state}危险系数为{danger}，评定等级:{danger_level}")
    return danger_level, danger
