import heapq
import pygame
import random
import setting

step=0

def call_counter(func):
    count = 0
    def wrapper(*args,**kwargs):
        nonlocal count
        count+=1
        value=func(*args,**kwargs)
        print(f'{func.__name__} called {count} times')
        global step
        step=count
        return value
    return wrapper

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

    def generate_apple(self):
        while True:
            x = random.randint(0, setting.GRID_WIDTH - 1)
            y = random.randint(0, setting.GRID_HEIGHT - 1)
            if (x, y) not in self.snake_pos:
                return (x, y)
            
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
    
    def adjacent(self,node):
        adj=[]
        for dx,dy in [(0,1),(0,-1),(1,0),(-1,0)]:
            x=node[-1][0]+dx
            y=node[-1][1]+dy
            if 0<=x<setting.GRID_WIDTH and 0<=y<setting.GRID_HEIGHT:
                new_node=list(node)
                new_node.append((x,y))
                del(new_node[0])
                adj.append(new_node)
        return adj

    def heuristic(self, a, node):
        return abs(a[0] - node[-1][0]) + abs(a[1] - node[-1][1])
    
    def in_screen(self,head):
        return 0<=head[0]<setting.GRID_WIDTH and 0<=head[1]<setting.GRID_HEIGHT

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
