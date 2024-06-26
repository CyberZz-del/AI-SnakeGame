<<<<<<< HEAD
# AI-SnakeGame
基于A*寻路算法的AI贪吃蛇的贪心与哈密尔顿实现
=======
# 需求

Python3.9+(64-bit)with pygame and heaqp installed.

# 可执行操作

- 在setting.py文件中可修改蛇的初始速度，蛇的速度单位，地图的长宽等
- 在run.py文件中可选择hamilton或者greedy两种解决方法之一来运行贪吃蛇ai
- 在游戏开始后按 $\uparrow$ 和 $\downarrow$ 来调整蛇的速度大小

## 选题描述

用python实现贪吃蛇ai。游戏的目的是尽可能多的吃到食物且尽可能快的占满地图中的所有格子，在游戏进行的过程中蛇的头不能撞到地图边缘或者蛇的身体。

## 设计方案

在如何保证自身安全并尽可能快的吃满地图的问题上，这次的课程设计采用了两种解决方法，分别为greedy solver和hamilton solver。

### greedy solver

step1：计算蛇头到食物的最短路径，如果存在则到step2，如果不存在则到step4

step2：如果吃到食物后蛇身占满地图，则返回蛇头到食物的最短路径，如果吃到食物后蛇身没有占满地图，则到step3

step3：创造一个模拟蛇，将让模拟蛇沿最短路径吃到食物后，搜索蛇头到蛇尾的最短路径，如果蛇头到蛇尾的最短路径存在，则返回蛇头到食物的最短路径，如果不存在，则到step4

step4：搜索蛇头到蛇尾的最长路径，如果存在，则返回蛇头到蛇尾的最长路径，如果不存在，则到step5

step5：让蛇头尽量远离食物移动

### hamilton solver

在地图上构建一个哈密尔顿回路，使蛇沿着哈密尔顿回路遍历地图上的每一个点即可，且在安全时允许蛇走近路（蛇长度小于等于地图容量的一半时)

## 实现效果

用以下参数来评判不同策略的表现：

1. 完成率：在所有测试中成功吃满整张地图的次数所占的比例。
2. 平均长度（平均分）：在所有测试中蛇的平均长度，即平均分。
3. 平均步数：在所有成功吃满整张地图的蛇走过的平均步数

测试结果如下（均为1000次）

**10*10map**：

| Solvers  | Completion rate | Average score | Average steps |
| :------: | :-------------: | :-----------: | :-----------: |
|  Greedy  |      67.1%      |    99.242     |    1821.3     |
| Hamilton |      97.8%      |    98.996     |    1229.8     |

不难看出，Greedy的完成度明显低于Hamilton，但平均长度却和Hamilton相差无几甚至多出一点，但平均步数明显大于Hamiton。

这是很有意思的现象。具体原因可能是Hamilton无法完成游戏时（陷入死循环）蛇身长度一般还很小，而Greedy只在蛇身长度达到98或96左右时才陷入死循环。

**9*9map**：

|  solver  | Completion rate | Average score | Average steps |
| :------: | :-------------: | :-----------: | :-----------: |
|  Greedy  |      91.0%      |    80.675     |    1275.9     |
| Hamilton |      0.0%       |      --       |      --       |

需要指出，当地图格数为奇数时，地图上不存在hamilton图，故解决方案hamilton彻底失效。

有意思的是在格数为奇数时，Greedy Solver的表现比格数为偶数时要好得多。

## 功能划分与描述

setting.py文件中存放游戏的参数，包括地图长宽，蛇的初始速度，蛇的速度单位等

greedy_solver.py文件中存放解决方法的类GreedySolver

hamilton_solver.py文件中存放解决方法的类HamiltonSolver

run.py文件用于选择性运行两种ai

以GreedySolver为例：

- 定义GreedySolver类

```py
class GreedySolver:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((setting.WIDTH, setting.HEIGHT))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.speed=setting.SNAKE_SPEED
        self.reset()
    def reset(self):
        self.snake_pos = [(setting.GRID_WIDTH // 2, setting.GRID_HEIGHT // 2)]
        self.snake_dir = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.apple_pos = self.generate_apple()
        self.score = 1
        self.game_over = False
```

- 生成食物函数

```py
 def generate_apple(self):
        while True:
            x = random.randint(0, setting.GRID_WIDTH - 1)
            y = random.randint(0, setting.GRID_HEIGHT - 1)
            if (x, y) not in self.snake_pos:
                return (x, y)
```

- 获取蛇的下一步可能的位置

 ```py
def get_neighbors(self, node):
        neighbors = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            x = node[-1][0] + dx
            y = node[-1][1] + dy
            new_node=list(node)
            new_node.append((x,y))
            del(new_node[0])
            if 0 <= x < setting.GRID_WIDTH and 0 <= y < setting.GRID_HEIGHT and (x,y) not in node[1:]:
                neighbors.append(new_node)
        return neighbors
 ```

- “启发式函数”（曼哈顿距离）

```py
def heuristic(self, a, node):
        return abs(a[0] - node[-1][0]) + abs(a[1] - node[-1][1])
```

- A Star算法搜索最短路径

```py
def shortest_path(self,start_node,goal):
        frontier=[(0,start_node)]
        came_from={}
        cost_so_far={start_node[-1]:0}
        final=None
        while frontier:
            _,current=heapq.heappop(frontier)
            if current[-1]==goal:
                final=current
                break
            lis=self.adjacent(current)
            if len(came_from)!=0:
                for i in range(len(lis)):
                    if lis[i][-1][0]-current[-1][0]==current[-1][0]-came_from[current[-1]][-1][0]\
                    and lis[i][-1][1]-current[-1][1]==current[-1][1]-came_from[current[-1]][-1][1]:
                        lis[0],lis[1]=lis[1],lis[0]
            for next_pos in lis:
                if next_pos[-1] not in start_node[1:]:
                    new_cost=cost_so_far[current[-1]]+1
                    if next_pos[-1] not in cost_so_far or new_cost<cost_so_far[next_pos[-1]]:
                        cost_so_far[next_pos[-1]]=new_cost
                        priority=new_cost+self.heuristic(goal,next_pos)
                        heapq.heappush(frontier,(priority,next_pos))
                        came_from[next_pos[-1]]=current
        path=[]
        current=final
        if current==None: 
            return path
        while current!=start_node:
            path.append(current)
            current=came_from[current[-1]]
        path.append(start_node)
        path.reverse()
        return path
```

- 最长路径

 ```py
def longest_path_to_tail(self,start_node):
        tail=start_node[0]
        path=[]
        current=list(start_node)
        path.append(current)
        lis=self.get_neighbors(current)
        lis.sort(key=lambda node:self.heuristic(tail,node),reverse=True)
        for i in range(len(lis)):
            if lis[i][-1]==self.apple_pos:
                del(lis[i])
                break
        for next_node in lis:
            if len(self.shortest_path(next_node,next_node[0]))>1:
                path.append(next_node)
                break
        return path
 ```

- greedy的具体实现

```py
def greedy(self,start_node,goal):
        path=self.shortest_path(start_node,goal)

        if len(path)>1:
            new_snake=list(path[-1])
            new_snake.insert(0,path[-2][0])
            if len(new_snake)==setting.GRID_HEIGHT*setting.GRID_WIDTH:
                return path
            
            path_to_tail=self.shortest_path(new_snake,path[-2][0])
            if len(path_to_tail)>1:
                return path
        
        path_to_tail=self.longest_path_to_tail(self.snake_pos)
        if len(path_to_tail)>1:
            return path_to_tail
        
        max_dist=-1
        max_node=None
        for new_node in self.adjacent(start_node):
            if new_node[-1] not in self.snake_pos and 0<=new_node[-1][0]<setting.GRID_WIDTH and 0<=new_node[-1][1]<setting.GRID_HEIGHT:
                dist=self.heuristic(goal,new_node)
                if dist>max_dist:
                    max_dist=dist
                    max_node=new_node
        path=[max_node]
        return path
```

- 更新状态（用装饰器函数可以打印出蛇当前的步数）

```py
@call_counter
    def update_snake(self):
        head_pos = self.snake_pos[-1]
        new_head_pos = (head_pos[0] + self.snake_dir[0], head_pos[1] + self.snake_dir[1])
        if new_head_pos == self.apple_pos:
            self.snake_pos.append(new_head_pos)
            
            self.score += 1
            if len(self.snake_pos)==setting.GRID_WIDTH*setting.GRID_HEIGHT:
                self.game_over=True
                return
            self.apple_pos = self.generate_apple()
       
        else:
            
            self.snake_pos.pop(0)
            self.snake_pos.append(new_head_pos)

    def update(self):
        if not self.game_over:
            path = self.greedy(self.snake_pos, self.apple_pos)
            if path==None:
                return
            if len(path) > 1:
                next_pos = path[1][-1]
                dx = next_pos[0] - self.snake_pos[-1][0]
                dy = next_pos[1] - self.snake_pos[-1][1]
                self.snake_dir = (dx, dy)
            self.update_snake()
            if self.snake_pos[-1] in self.snake_pos[:-1]:
                self.game_over=True
            if not self.in_screen(self.snake_pos[-1]):
                self.game_over=True
            if len(self.snake_pos) == setting.GRID_WIDTH * setting.GRID_HEIGHT:
                self.game_over = True
        self.draw()
```

- 绘图函数

```py
def draw(self):
        self.screen.fill(setting.BLACK)
        rect = pygame.Rect(self.apple_pos[0] * setting.GRID_SIZE, self.apple_pos[1] * setting.GRID_SIZE, setting.GRID_SIZE, setting.GRID_SIZE)
        pygame.draw.rect(self.screen, setting.RED, rect)
        rect=pygame.Rect(self.snake_pos[0][0]*setting.GRID_SIZE,self.snake_pos[0][1]*setting.GRID_SIZE,setting.GRID_SIZE,setting.GRID_SIZE)
        pygame.draw.rect(self.screen,setting.BLUE,rect)
        for pos in self.snake_pos[1:-1]:
            rect = pygame.Rect(pos[0] * setting.GRID_SIZE, pos[1] * setting.GRID_SIZE, setting.GRID_SIZE-1, setting.GRID_SIZE-1)
            pygame.draw.rect(self.screen, setting.WHITE, rect)
        rect=pygame.Rect(self.snake_pos[-1][0]*setting.GRID_SIZE,self.snake_pos[-1][1]*setting.GRID_SIZE,setting.GRID_SIZE,setting.GRID_SIZE)
        pygame.draw.rect(self.screen,setting.GREEN,rect)
        
        text = self.font.render(f'Score: {self.score}', True, setting.PURPLE)
        self.screen.blit(text, (10, 10))
        if self.game_over:
            text = self.font.render(f'Game Over!', True, setting.BLACK)
            self.screen.blit(text, (setting.WIDTH // 2 - text.get_width() // 2, setting.HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
```

- 运行函数

```py
def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                if event.type == pygame.KEYDOWN:
                    if event.key==pygame.K_UP:
                        self.speed+=setting.SPEED_UNIT
                    elif event.key ==pygame.K_DOWN:
                        self.speed-=setting.SPEED_UNIT
            self.update()
            self.clock.tick(self.speed)
```

>>>>>>> 8b41152 (commit)
