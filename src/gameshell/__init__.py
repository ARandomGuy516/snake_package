import random
import sys
import time
import tty
import termios
import select
import tkinter as tk
import math

class breakout:
    obj = []
    class Ball:
        def __init__(self, r=10, rotaion=45, speed=5, x=None, y=None, alive=True, color="white"):
            if x is None:
                x = breakout.Screen.w/2
            if y is None:
                y = breakout.Screen.h/2
            self.rotation = [math.cos(math.radians(rotaion)), math.sin(math.radians(rotaion))]
            self.x = x
            self.y = y
            self.type = "ball"
            self.r = r
            self.speed = speed
            self.color = color
            self.alive = alive
            breakout.obj.append(self)

        def forward(self):
            self.y -= self.rotation[1]*self.speed
            self.x += self.rotation[0]*self.speed
        
        def collition(self):
            for i in breakout.obj:
                if i != self:
                    if i.type=="platform":
                        if abs(self.x-i.x)<=i.w/2+self.r and abs(self.y-i.y)<=i.h/2+self.r:
                            self.rotation[1] = abs(self.rotation[1])
                            if abs(self.y-(self.rotation[1]*self.speed)-i.y)<=i.h/2+self.r:
                                if self.x > i.x:
                                    self.rotation[0] = abs(self.rotation[0])
                                    self.x = i.x+self.r+1+i.w/2
                                else:
                                    self.rotation[0] = -abs(self.rotation[0])
                                    self.x = i.x-self.r-1-i.w/2
                            
                    if i.type=="block":
                        hit = []
                        for g in i.block_cords[:]:
                            if abs(self.x-g[0])<=i.w/2+self.r and abs(self.y-g[1])<=i.h/2+self.r:
                                hit.append(g)

                        if hit:
                            g = hit[0]
                            if abs(self.y+(self.rotation[1]*self.speed)-g[1])<=i.h/2+self.r:
                                if self.x > g[0]:
                                    self.rotation[0] = abs(self.rotation[0])
                                else:
                                    self.rotation[0] = -abs(self.rotation[0])
                            else:
                                self.rotation[1] *= -1

                            for g in hit:
                                i.block_cords.remove(g)

            
            if self.x+self.r >= breakout.Screen.w:
                self.x = breakout.Screen.w-self.r-1
                self.rotation[0] = -abs(self.rotation[0])
            if self.x-self.r < 0:
                self.x = self.r+1
                self.rotation[0] = abs(self.rotation[0])
            if self.y-self.r < 0:
                self.y = self.r+1
                self.rotation[1] = -abs(self.rotation[1])
            if self.y+self.r >= breakout.Screen.h:
                self.alive = False
            

        
    class Platform:
        def __init__(self, x=None, y=None, w=75, h=25, color="white"):
            if x is None:
                x = breakout.Screen.w/2
            if y is None:
                y = breakout.Screen.h-25-h/2
            self.x = x
            self.y = y
            self.w = w
            self.h = h
            self.type = "platform"
            self.color = color
            breakout.obj.append(self)
        
        def update_pos(self, key):
            if "d" in key and self.x+self.w/2 < breakout.Screen.w:
                self.x += min(10, breakout.Screen.w-(self.x+self.w/2))
            if "a" in key and self.x-self.w/2 > 0:
                self.x += max(-10, 0-(self.x-self.w/2))

    class Block:
        def __init__(self, n=None, w=None, h=None, gap_x=None, gap_y=None, rows=None, color="white"):
            screen_w = breakout.Screen.w
            screen_h = breakout.Screen.h
            if n is None:
                n = screen_w//40

            if w is None:
                w = screen_w/(n+(n+1)/10)
    
            if gap_x is None:
                gap_x = (screen_w-w*n)/(n+1)

            if rows is None:
                rows = screen_h//300

            if h is None:
                h = screen_h/(rows+(rows+1)/0.5)*0.2
                
            if gap_y is None:
                gap_y = (screen_h*0.2-h*rows)/(rows+1)
            
            self.block_cords = []

            y=gap_y
            x=gap_x

            for i in range(rows):
                for g in range(n):
                    self.block_cords.append([round(x+w/2), round(y+h/2)])
                    x+=gap_x
                    x+=w
                y+=h
                y+=gap_y
                x = gap_x
            
            self.w = w
            self.h = h
            self.gap_y = gap_y
            self.gap_x = gap_x
            self.type="block"
            self.rows = rows
            self.n = n
            self.color = color
            breakout.obj.append(self)
        
        def cleared(self):
            if len(self.block_cords)==0:
                return True
            return False

    class Screen:
        w = 400
        h = 600
        def __init__(self, w=400, h=600, title="breakout", bg="black", x=None, y=None, fps=60):
            self.w = w
            self.h = h
            self.root = tk.Tk()
            self.root.title(title)
            self.canvas = tk.Canvas(self.root, width=w, height=h, bg=bg, highlightthickness=0)
            self.canvas.pack()
            self.keys = set()
            self.root.bind("<KeyPress>", lambda e: self.keys.add(e.keysym))
            self.root.bind("<KeyRelease>", lambda e: self.keys.discard(e.keysym))

            x_m = self.root.winfo_screenwidth()/2
            y_m = self.root.winfo_screenheight()/2

            if y is None:
                y = y_m
            if x is None:
                x = x_m
            
            self.root.geometry(f"{w}x{h}+{int(x-w/2)}+{int(y-h/2)}")
            self.x = x
            self.y = y
            breakout.Screen.w = w
            breakout.Screen.h = h

            self._fps = fps
            self._next_frame = time.perf_counter()

        def check_for_inputs(self):
            return self.keys

        def update(self):
            try:
                self.canvas.delete("all")
                for i in breakout.obj:
                    if i.type=="platform":
                        self.canvas.create_rectangle(i.x-(i.w/2), i.y-(i.h/2), i.x+(i.w/2), i.y+(i.h/2), fill=i.color, outline="")
                    if i.type=="ball":
                        self.canvas.create_oval(i.x-(i.r), i.y-(i.r), i.x+(i.r), i.y+(i.r), fill=i.color, outline="")
                    if i.type=="block":
                        for g in i.block_cords:
                            self.canvas.create_rectangle(g[0]-i.w/2, g[1]-i.h/2, g[0]+i.w/2, g[1]+i.h/2, fill=i.color, outline="")

                self._next_frame += 1 / self._fps
                sleep_for = self._next_frame - time.perf_counter()
                if sleep_for > 0:
                    time.sleep(sleep_for)
                else:
                    self._next_frame = time.perf_counter()

                self.root.update()
            except tk.TclError:
                sys.exit()

        def winner_menu(self):
            self.canvas.delete("all")
            self.canvas.create_text(self.w/2, self.h/2, text="You win!!   :)", fill="white", font=("Arial", 40, "bold"))
            while True:
                keys = self.check_for_inputs()
                if "r" in keys:
                    self.reset()
                    return
                try:
                    self.root.update()
                    time.sleep(0.05)
                except tk.TclError:
                    sys.exit()

        def looser_menu(self):
            self.canvas.delete("all")
            self.canvas.create_text(self.w/2, self.h/2, text="You lose!!   :(", fill="white", font=("Arial", 40, "bold"))
            while True:
                keys = self.check_for_inputs()
                if "r" in keys:
                    self.reset()
                    return
                try:
                    self.root.update()
                    time.sleep(0.05)
                except tk.TclError:
                    sys.exit()
        
        def reset(self):
            for i in breakout.obj:
                if i.type=="block":
                    i.block_cords = []

                    y=i.gap_y
                    x=i.gap_x

                    for e in range(i.rows):
                        for g in range(i.n):
                            i.block_cords.append([round(x+i.w/2), round(y+i.h/2)])
                            x+=i.gap_x
                            x+=i.w
                        y+=i.h
                        y+=i.gap_y
                        x = i.gap_x

                if i.type=="platform":
                    i.x = breakout.Screen.w/2
                    i.y = breakout.Screen.h-25-i.h/2
                
                if i.type=="ball":
                    i.x = breakout.Screen.w/2
                    i.y = breakout.Screen.h/2
                    i.rotation[1] = abs(i.rotation[1])
                    i.rotation[0] = abs(i.rotation[0])
                    i.alive = True




def play_breakout():
    screen = breakout.Screen()
    platform = breakout.Platform()
    ball = breakout.Ball()
    block = breakout.Block()
    while True:
        ball.forward()
        keys = screen.check_for_inputs()
        platform.update_pos(keys)
        if "w" in keys:
            block.block_cords = []
        ball.collition()
        screen.update()
        if block.cleared():
            screen.winner_menu()
        if not ball.alive:
            screen.looser_menu()
                


class snake():
    obj = []
    started = False
    score = 0
    dif = "normal"
    class Snake:
        def __init__(self, name="Ishay", size=0, dir=0, shape="0", pos=[], tail_shape="1"):
            dir = dir//90*90
            if size < 0:
                size = 0
            self.shape=shape+"   "
            self.name = name
            self.size = size
            self.dir = dir
            self.x = snake.Screen.w//2
            self.y = snake.Screen.h//2
            self.pos = pos
            self.type = "snake"
            self.tail_shape = tail_shape+"   "
            snake.obj.append(self)

        def forward(self):
            if self.dir == 0:
                self.x+=1
            if self.dir == 90:
                self.y-=1
            if self.dir == 180:
                self.x -= 1
            if self.dir == 270:
                self.y += 1

        def collition(self):
            lis = []
            for i in snake.obj:
                if i != self:
                    if i.type=="boulder":
                        for f in i.boulders:
                            if f[0] == self.x and f[1]-10 == self.y:
                                lis.append("boulder")
                        continue
                    if i.x == self.x and i.y == self.y:
                        lis.append(i)
            if self.x >= snake.Screen.w:
                if snake.dif == "normal":
                    self.x = snake.Screen.w-1
                    lis.append("wall")
                else:
                    self.x = 0
            if self.x < 0:
                if snake.dif == "normal":
                    self.x = 0
                    lis.append("wall")
                else:
                    self.x = snake.Screen.w-1

            if self.y>=snake.Screen.h:
                if snake.dif == "normal":
                    self.y = snake.Screen.h-1
                    lis.append("wall")
                else:
                    self.y = 0
            if self.y < 0:
                if snake.dif == "normal":
                    self.y = 0
                    lis.append("wall")
                else:
                    self.y = snake.Screen.h-1

            if self.type == "snake":
                for i in range(len(self.pos)):
                    if self.pos[i][0] == int(self.x) and self.pos[i][1] == int(self.y) and i != 0:
                        lis.append("tail")
            return lis

        def grow(self):
            self.size += 1
            snake.score += 1

        def save_pos(self):
            self.pos.append([int(self.x//1), int(self.y//1)])
        def update_der(self, k=None):
            if k == "w" and self.size==0 or k=="w" and self.dir!=270:
                self.dir = 90
            elif k == "d" and self.size==0 or k=="d" and self.dir!=180:
                self.dir = 0
            elif k == "a" and self.size==0 or k=="a" and self.dir!=0:
                self.dir = 180
            elif k == "s" and self.size==0 or k=="s" and self.dir!=90:
                self.dir = 270

    class Screen():
        w = 15
        h = 15
        def  __init__(self, w=15, h=15, blank="."):
            self.w = w
            self.h = h
            self.screen = []
            self.blank = blank+"   "

            for i in range(10):
                self.screen.append([])
                for f in range(self.w):
                    self.screen[i].append("   ")

            for i in range(h):
                self.screen.append([])
                for f in range(w):
                    self.screen[i+10].append(self.blank)
            snake.Screen.w = w
            snake.Screen.h = h

        def update(self):
            for i in range(50):
                print("")

            self.screen = []
            for i in range(10):
                self.screen.append([])
                for f in range(self.w):
                    self.screen[i].append("    ")
            for i in snake.obj:
                if i.type=="boulder":
                    for i in i.boulders:
                        self.screen[i[1]][i[0]] = i[2]
                    continue
                if i.type=="snake":
                    while len(i.pos) > i.size:
                        i.pos.pop(0)
                    for f in range(len(i.pos)):
                        self.screen[i.pos[f][1]+10][i.pos[f][0]] = i.tail_shape
                self.screen[int(i.y//1)+10][int(i.x//1)] = i.shape
            for i in self.screen:
                print("".join(i))
                print("")

        def get_key(self, timeout):
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setcbreak(fd)
                rlist, _, _ = select.select([sys.stdin], [], [], timeout)
                if rlist:
                    return sys.stdin.read(1)
                return 1
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

        def check_for_inputs(self):
            return self.get_key(0.125)

        def inputed(self, key):
            if key != 1:
                snake.started = True
            return snake.started

        def start_menu(self):
            print("press e to play on easy mode, press n to play on normal mode. press q to quit.")
            k = self.get_key(1)
            while k != "e" and k !="n" and k != "q":
                k = self.get_key(1)
                if k == "e":
                    snake.dif = "easy"
                    return
                if k == "n":
                    snake.dif = "normal"
                    return
                if k == "q":
                    exit()
                if k != "n" and k != "e" and k != "q" and k != 1:
                    print("I didnt get that")

        def looser_menu(self):
            print("your score was", snake.score, "press r to restart. press q to quit.")
            k = self.get_key(1)
            while k != "r" and k != "q":
                k = self.get_key(1)
                if k == "r":
                    return
                if k == "q":
                    exit()
                if k != "r" and k != "q" and k != 1:
                    print("I didnt get that")

        def reset(self):
            for i in snake.obj:
                if i.type == "snake":
                    i.x = self.w//2
                    i.y = self.h//2
                    i.size = 0
                if i.type == "apple":
                    i.rtp()
                if i.type == "boulder":
                    j = 0
                    i.boulders = []
                    while j < i.max:
                        g = [random.randint(i.min_x, i.max_x), random.randint(i.min_y, i.max_y), i.shape, i.fall_speed, i.max, i.min_x, i.max_x, i.type]
                        if g in i.boulders:
                            continue
                        i.boulders.append(g)
                        j+=1
            snake.started = False
            snake.score = 0

    class Apple():
        def __init__(self, x=None, y=None, shape="2", rtp_size_x=None, rtp_size_y=None):
            if rtp_size_x is None:
                rtp_size_x = snake.Screen.w

            if rtp_size_y is None:
                rtp_size_y = snake.Screen.h

            if x is None:
                x = random.randint(0, rtp_size_x-1)
            if y is None:
                y = random.randint(0, rtp_size_y-1)
            self.x = x
            self.y = y
            self.shape = shape+"   "
            self.type = "apple"
            self.rtp_size_x = rtp_size_x
            self.rtp_size_y = rtp_size_y
            snake.obj.append(self)
        def rtp(self):
            self.x = random.randint(0, self.rtp_size_x - 1)
            self.y = random.randint(0, self.rtp_size_y - 1)

    class Boulder():
        def __init__(self, shape="3", fall_speed=1, max=None, min=0, max_x=None, min_x=1, boulders=[], type="boulder", min_y=0, max_y = 2):
            if max_x is None:
                max_x = snake.Screen.w-1
            if max is None:
                max = (max_x - min_x)//2
            self.shape = shape+"   "
            self.fall_speed = fall_speed
            self.max = max
            self.min = min
            self.max_x = max_x
            self.min_x = min_x
            self.y = 0
            self.type = type
            self.max_y = max_y
            self.min_y = min_y
            i = 0
            while i < max:
                g = [random.randint(min_x, max_x), random.randint(min_y, max_y), self.shape, self.fall_speed, self.max, self.min_x, self.max_x, self.type]
                if g in boulders:
                    continue
                boulders.append(g)
                i+=1
            self.boulders = boulders
            snake.obj.append(self)

        def go_down(self):
            for i in self.boulders:
                i[1] += 1
                if i[1] >= snake.Screen.h+10:
                    i[1] = random.randint(self.min_y, self.max_y)
                    i[0] = random.randint(self.min_x, self.max_x)


def main():
    import argparse
    argparse.ArgumentParser(
        prog="snake",
        description=(
            "Snake toolkit (terminal).\n\n"
            "Quick setup:\n"
            "  screen = snake.Screen()\n"
            "  s = snake.snake()\n"
            "  apple = snake.Apple()\n"
            "  if you're_feeling_fancy == True:\n"
            "    boulder = snake.Boulder()\n\n"
            "Controls:\n"
            "  w / a / s / d  move\n"
            "  e              easy mode (wrap walls)\n"
            "  n              normal mode (wall = death)\n"
            "  r              restart after death\n"
            "  q              quit\n\n"
            "Menus:\n"
            "  Start menu (shown at launch):\n"
            "    press e for easy, n for normal, q to quit\n"
            "  Lose menu (shown after death):\n"
            "    press r to restart, q to quit\n\n"
            "Screen:\n"
            "  screen.update()              redraw frame\n"
            "  k = screen.check_for_inputs() read one key\n"
            "  screen.inputed(k)            has game started\n"
            "  screen.start_menu()          run start menu (e/n/q)\n"
            "  screen.looser_menu()         run lose menu (r/q)\n"
            "  screen.reset()               reset game state\n\n"
            "Snake:\n"
            "  s.forward()                  move one step in the direction it is facing\n"
            "  collisions = s.collition()   check collisions\n"
            "  s.grow()                     grow by one step\n"
            "  s.save_pos()                 save tail position\n"
            "  s.update_der(k)              update direction based on the key pressed\n\n"
            "Boulder:\n"
            "  boulder.go_down()            move boulders down\n\n"
            "Apple:\n"
            "  apple.rtp()                  respawn apple\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    ).parse_args()
    boulder = snake.Boulder()
    screen = snake.Screen()
    apple = snake.Apple()
    s = snake.snake()
    screen.start_menu()
    while True:
        screen.update()
        k = screen.check_for_inputs()
        s.save_pos()
        s.update_der(k)
        if screen.inputed(k):
            s.forward()
        coll = s.collition()
        if len(coll) > 0 and apple not in coll:
            screen.update()
            print(s.name, "died")
            screen.looser_menu()
            screen.reset()
        if screen.inputed(k):
            boulder.go_down()
        coll = s.collition()
        if len(coll) > 0 and apple not in coll:
            screen.update()
            print(s.name, "died")
            screen.looser_menu()
            screen.reset()
        if apple in coll:
            s.grow()
            apple.rtp()

__all__ = ["snake", "main", "breakout"]
