"搜索专题: BFS与DFS"

import sys
from collections import deque
# 一维青蛙跳杯问题BFS
s1 = input().strip()
s2 = input().strip()
# 算出从s1变成s2需要步数
# *空 W白 B黑
# 青蛙可选：到相邻3个内的空杯子 
def frog_bfs(start, target):
    # start:初始状态, target:目标状态
    if start == target:
        # 如果初始状态就是目标状态,直接返回0步
        return 0
    q = deque([(start, 0)])
    # 队列中存储状态和步数(双端队列)
    visited = {start}
    # 已访问集合，入队标记
    while q:
        # 队列不空，扩展
        s, d = q.popleft()
        # 出队
        e = s.index('*')                
        # 唯一的空杯位置
        for p in range(len(s)):
            # 遍历所有位置，尝试交换
            if s[p] == '*':
                # 跳过空的
                continue
            if 1 <= abs(p - e) <= 3:    
                # 距离 1/2/3 合法,交换 p 和 e
                lst = list(s)
                # 字符换成列表方便交换
                lst[p], lst[e] = lst[e], lst[p]
                # 状态转移
                ns = ''.join(lst)
                # 新局面字符串生成
                if ns == target:
                    # 目标找到，返回结果步数
                    return d + 1
                if ns not in visited:
                    # 更新已访问
                    visited.add(ns)
                    q.append((ns, d + 1))
    return -1   # 不可达（本题一般有解）
print(frog_bfs(s1, s2))

# BFS:AB对换,卡片换位
# 对于二维的 拼成一维处理
# 用e标记空位，只要实现AB位置互换即可
s1 = input().rstrip('\n')
s2 = input().rstrip('\n')
s0 = s1 + s2
def ab_bfs(start):
    q = deque([(start, 0)])
    visited = {start}
    rows = 2
    cols = 3
    a = start.index('A')
    b = start.index('B')
    dirs = ((-1,0), (1,0), (0,-1), (0,1))
    while q:
        s, d = q.popleft()
        e = s.index(' ')
        er, ec = divmod(e, cols) 
        # 输入a,b,返回a对b的商和余数元组.这里用来取空位的行列号
        # 一维变高维,获得空位序列号
        for dr, dc in dirs:
            nr, nc = er+dr, ec+dc
            if not (0 <= nr < rows and 0 <= nc < cols):
                continue # 越界
            p = nr * cols + nc # 邻居的一维下标折算
            if s[p] == ' ': # 空位只有1个
                continue
            lst = list(s)
            lst[e], lst[p] = lst[p], lst[e]
            ns = ''.join(lst)
            if ns[a] == 'B' and ns[b] == 'A':
                # AB完成对换
                return d + 1
            if ns not in visited:
                visited.add(ns)
                q.append((ns, d+1))
    return -1
print(ab_bfs(s0))

# 胖子走迷宫
from collections import deque

n,k = map(int,input().split())
s = [list(input()) for i in range(n)]
q = deque([(2,2,2,0)])
# 用数字012标记胖瘦状态，最右侧数值标记当前时刻
vir = [[0 for _ in range(n)] for _ in range(n)]
vir[2][2] = 1
dir = [[-1,0],[1,0],[0,-1],[0,1]]
def f(t):  # 检验时间返回状态
    if t < k:
        return 2
    if t <2*k:
        return 1
    else:
        return 0
def check(x,y,z): # 检查标记
    for i in range(x-z,x+z+1):
        for j in range(y-z,y+z+1):
            if s[i][j] == '*':
                return False
    return True
def weigh_bfs():
    while q:
        x,y,z,cnt = q.popleft()
        if x == n-3 and y == n-3:
            return cnt
        if z != 0:
            q.append((x,y,f(cnt + 1),cnt+1))
        for d in range(4):
            nx = x + dir[d][0]
            ny = y + dir[d][1]
            if 0 <= nx-z and nx+z < n and 0<= ny-z and ny+z < n and vir[nx][ny] == 0:
                if check(nx,ny,z) == True:
                    q.append((nx,ny,f(cnt+1),cnt+1))
                    vir[nx][ny] = 1
print(weigh_bfs())

# BFS: 九宫重排
start = input().rstrip('\n')
target = input().rstrip('\n')
from collections import deque
def magsqu_bfs(start, target):
    # 一维转二维
    if start == target:
        return 0
    r = c = 3
    # start = list(start) 转二维表: [list(s[i*c:(i+1)*c]) for i in range(r)]
    visited = {start}
    q = deque([(start, 0)])
    dirs = ((-1,0), (1,0), (0,-1), (0,1))
    while q:
        s, d = q.popleft()
        e = s.index('.')
        er, ec = divmod(e, c)
        # 调用divmod取行列号
        for dr, dc in dirs:
            nr, nc = er+dr, ec+dc
            if 0 <= nr < r and 0 <= nc < c:
                p = nr * c + nc
                lst = list(s)
                lst[e], lst[p] = lst[p], lst[e]
                ns = ''.join(lst)
                if ns == target:
                    return d+1
                if ns not in visited:
                    visited.add(ns)
                    q.append((ns, d+1))
    return -1
print(magsqu_bfs(start, target))

# BFS:长草
n, m = map(int, input().split())
land = ''.join(input().strip() for _ in range(n))
# 一行读入，len(land) = m * n
k = int(input())
def grass_bfs(land, k, m, n):
    grid = list(land)         
    q = deque()
    for i in range(n * m):
        if grid[i] == 'g':
            q.append(i)        
            # 一维下标遍历g
    dirs = ((-1, 0), (1, 0), (0, -1), (0, 1))
    for _ in range(k):
        size = len(q)
        if size == 0:
            # 无草需要扩散
            break
        for _ in range(size):
            i = q.popleft()
            r, c = divmod(i, m)
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                if 0 <= nr < n and 0 <= nc < m:
                    p = nr * m + nc
                    if grid[p] == '.':
                        grid[p] = 'g'
                        q.append(p)   # 新草留到下一层
    return ''.join(grid)
land = grass_bfs(land, k, m, n)
for i in range(n):
    print(land[i*m:(i+1)*m])

# BFS: 迷宫陷阱
n, K = map(int, input().split())
maze = [list(input().strip()) for _ in range(n)]
# 四种: . # X % 路 墙 坑 宝
# 返回从左上角到右下需要最少步数
def maze_bfs():
    # dist[r][c][t] 表示当前步数，t表示无敌剩余步数<=K
    # -1 表示未访问,访问区域列表初始化
    dist = [[[-1]*(K+1) for _ in range(n)] for _ in range(n)]
    # 起点 (0,0) 如果是 '%'，第一次到达获得无敌
    start_t = 0
    if maze[0][0] == '%':
        start_t = K
        maze[0][0] = '.'  # 道具拿掉
    # 若起点是 X 且无无敌，则无法出发
    if maze[0][0] == 'X' and start_t == 0:
        return -1
    dist[0][0][start_t] = 0
    q = deque()
    q.append((0, 0, start_t))
    # 队列存当前行列号和无敌剩余步数
    dirs = ((-1,0),(1,0),(0,-1),(0,1))
    while q:
        # 局面更新！
        r, c, t = q.popleft()
        d = dist[r][c][t]
        if r == n-1 and c == n-1:
            # 到达出口，返回步数
            return d
        for dr, dc in dirs:
            nr, nc = r+dr, c+dc
            if not (0 <= nr < n and 0 <= nc < n):
                continue # 越界跳过
            cell = maze[nr][nc]
            if cell == '#':
                # 墙，不管它
                continue
            nt = t
            if cell == 'X':
                if t == 0:
                    # 没无敌不能通过陷阱
                    continue
                nt = t - 1
                # 能过，无敌时长-1
            elif cell == '%':
                # 第一次到达还是 '%'，说明之前没被拿过
                # 拿到后无敌时长设为 K，并标记道具消失
                nt = K
                maze[nr][nc] = '.'  
            else:  # '.'
                if t > 0:
                    nt = t - 1
                else:
                    nt = 0
            if dist[nr][nc][nt] == -1:
                # (nr, nc)尚未访问，更新步数
                dist[nr][nc][nt] = d + 1
                q.append((nr, nc, nt))
    return -1
print(maze_bfs())
    
# BFS:简单迷宫
n, m = map(int, input().split())
maze = [list(map(int, input().split())) for _ in range(n)]
# 迷宫数阵
def simbaze_bfs(maze):
    sx, sy, ex, ey = map(int, input().split())
    dist = [[-1 for _ in range(m)] for _ in range(n)]
    # dist[x][y]初始化-1表示未访问
    dirs = ((-1, 0), (1, 0), (0, -1), (0, 1))
    q = deque()
    ex -= 1
    ey -= 1
    sx -= 1
    sy -= 1
    q.append((sx, sy, 0))
    # sx, sy表示当前位置, 后面的0是当前步数
    while q:
        # ps: 这里不需要专门检查起终点.
        x, y, d = q.popleft()
        if x == ex and y == ey:
            # 已抵达终点.
            return d
        for dx, dy in dirs:
            xt, yt = x+dx, y+dy
            # 遍历上下左右
            if 0 <= xt < n and 0 <= yt < m:
                cell = maze[xt][yt]
                if cell == 1 and dist[xt][yt] == -1:
                    # 未访问且可通行，试试！
                    dist[xt][yt] = 1
                    q.append((xt, yt, d+1))
    return -1
print(simbaze_bfs(maze))
# 通过

# 无限画布扩散
ans = 0
for i in range(-2020, 4041):
    for j in range(-2020, 4021):
        if any(abs(i - x) + abs(j - y) <= 2020 for x, y in [(0, 0), (2020, 11), (11, 14), (2000, 2000)]):
            ans += 1
print(ans)
        
# 最少操作数BFS
n, k = map(int, input().split())
def cooperate_bfs(n, k):
    q = deque()
    q.append((n, 0))
    visited = {n}
    while q:
        num, cnt = q.popleft()
        if num == k:
            return cnt
        nums = [num + 1, num - 1, num * 2]
        for i in range(3):
            if 1e5 >= nums[i] >= 1 and nums[i] not in visited:
                q.append((nums[i], cnt+1))
                visited.add(nums[i])
    return -1
print(cooperate_bfs(n, k))
        
# 类bfs:扫雷
n, m = map(int, input().split())
old = [list(map(int, input().split())) for _ in range(n)]
dist = [[0 for _ in range(m)] for _ in range(n)]
surround = [(-1, -1), (-1, 0), (-1, 1), 
            (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
for i in range(n):
    for j in range(m):
        locat = old[i][j]
        if locat == 1:
            dist[i][j] = 9
            for dr, dc in surround:
                r, c = i+dr, j+dc
                if 0 <= r < n and 0 <= c < m:
                    if old[r][c] == 0:
                        dist[r][c] += 1
for row in dist:
    print(' '.join(map(str, row)))

# 染色Dijkstra问题
# 带边权时BFS失效,本题值得研究
import heapq
n, m = map(int, input().split())
ts = [list(map(int, input().split())) for _ in range(n)]
INF = float('inf')
finish = [[INF] * m for _ in range(n)]
finish[0][0] = ts[0][0]
pq = [(ts[0][0], 0, 0)]
dirs = ((-1,0),(1,0),(0,-1),(0,1))
while pq:
    t, r, c = heapq.heappop(pq)
    if t > finish[r][c]:
        continue
    for dr, dc in dirs:
        nr, nc = r + dr, c + dc
        if 0 <= nr < n and 0 <= nc < m:
            nt = t + ts[nr][nc]
            if nt < finish[nr][nc]:
                finish[nr][nc] = nt
                heapq.heappush(pq, (nt, nr, nc))
print(max(finish[r][c] for r in range(n) for c in range(m)))

# 01BFS: 两栖作战
from collections import deque
n = int(input())
land = [input().strip() for _ in range(n)] 
# 0地1水
def amphibious_bfs():
    INF = float('inf')
    # 预设为无穷大，未确定最少切换次数
    dist = [[INF] * n for _ in range(n)]
    dist[0][0] = 0
    # dist[r][c] 表示从(0, 0)到(r, c)最少切换次数
    # 起点初始化,代价0
    dq = deque([(0, 0)])
    # 双端队列初始化,只放坐标(r, c)
    dirs = ((-1,0),(1,0),(0,-1),(0,1))
    while dq:
        r, c = dq.popleft()
        d = dist[r][c]
        # 当前格最少切换次数
        for dr, dc in dirs:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n:
                # 不越界, 计算边权(同0异1)
                w = 0 if land[r][c] == land[nr][nc] else 1
                nd = d + w
                # 边权+当前代价
                if nd < dist[nr][nc]:
                    # 当前切换更少,更新(可执行多次)
                    dist[nr][nc] = nd
                    if w == 0:
                        dq.appendleft((nr, nc))   
                        # 代价 0，去队头
                    else:
                        dq.append((nr, nc))       
                        # 代价 1，去队尾
                    # 上面相当于优先做代价0的.
    return dist[n-1][n-1]
print(amphibious_bfs())
# 内存限制，只过7成(Python3),PyPy3可以全过

# 串门: BFS两次求树直径
def main():
    data = sys.stdin.read().split()
    if not data:
        return
    n = int(data[0])
    adj = [[] for _ in range(n + 1)]
    total = 0
    idx = 1
    for _ in range(n - 1):
        v = int(data[idx]); u = int(data[idx+1]); w = int(data[idx+2])
        idx += 3
        adj[v].append((u, w))
        adj[u].append((v, w))
        total += w

    def bfs(start):
        dist = [-1] * (n + 1)
        dist[start] = 0
        q = deque([start])
        far_node, far_dist = start, 0
        while q:
            x = q.popleft()
            for y, w in adj[x]:
                if dist[y] == -1:
                    dist[y] = dist[x] + w
                    q.append(y)
                    if dist[y] > far_dist:
                        far_dist = dist[y]
                        far_node = y
        return far_node, far_dist

    u, _ = bfs(1)          # 第一次 BFS：找最远点 u
    _, diameter = bfs(u)   # 第二次 BFS：从 u 找最远距离 = 直径

    print(2 * total - diameter)
