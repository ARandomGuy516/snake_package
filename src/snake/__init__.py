import random
import sys
import tty
import termios
import select

class Snake():
    obj = []
    started = False
    score = 0
    dif = "normal"
    class snake:
        def __init__(snake, name="Ishay", size=0, dir=0, shape="0", pos=[], tail_shape="1"):
            dir = dir//90*90
            if size < 0:
                size = 0
            snake.shape=shape+"   "
            snake.name = name
            snake.size = size
            snake.dir = dir
            snake.x = Snake.Screen.w//2
            snake.y = Snake.Screen.h//2
            snake.pos = pos
            snake.type = "snake"
            snake.tail_shape = tail_shape+"   "
            Snake.obj.append(snake)

        def forward(snake):
            if snake.dir == 0:
                snake.x+=1
            if snake.dir == 90:
                snake.y-=1
            if snake.dir == 180:
                snake.x -= 1
            if snake.dir == 270:
                snake.y += 1

        def collition(coll):
            lis = []
            for i in Snake.obj:
                if i != coll:
                    if i.type=="boulder":
                        for f in i.boulders:
                            if f[0] == coll.x and f[1]-10 == coll.y:
                                lis.append("boulder")
                        continue
                    if i.x == coll.x and i.y == coll.y:
                        lis.append(i)
            if coll.x >= Snake.Screen.w:
                if Snake.dif == "normal":
                    coll.x = Snake.Screen.w-1
                    lis.append("wall")
                else:
                    coll.x = 0
            if coll.x < 0:
                if Snake.dif == "normal":
                    coll.x = 0
                    lis.append("wall")
                else:
                    coll.x = Snake.Screen.w-1
    
            if coll.y>=Snake.Screen.h:
                if Snake.dif == "normal":
                    coll.y = Snake.Screen.h-1
                    lis.append("wall")
                else:
                    coll.y = 0
            if coll.y < 0:
                if Snake.dif == "normal":
                    coll.y = 0
                    lis.append("wall")
                else:
                    coll.y = Snake.Screen.h-1

            if coll.type == "snake":
                for i in range(len(coll.pos)):
                    if coll.pos[i][0] == int(coll.x) and coll.pos[i][1] == int(coll.y) and i != 0:
                        lis.append("tail")
            return lis

        def grow(snake):
            snake.size += 1
            Snake.score += 1

        def save_pos(snake):
            snake.pos.append([int(snake.x//1), int(snake.y//1)])
        def update_der(snake, k=None):
            if k == "w" and snake.size==0 or k=="w" and snake.dir!=270:
                snake.dir = 90
            if k == "d" and snake.size==0 or k=="d" and snake.dir!=180:
                snake.dir = 0
            if k == "a" and snake.size==0 or k=="a" and snake.dir!=0:
                snake.dir = 180
            if k == "s" and snake.size==0 or k=="s" and snake.dir!=90:
                snake.dir = 270

    class Screen():
        w = 15
        h = 15
        def  __init__(screen, w=15, h=15, blank="."):
            screen.w = w
            screen.h = h
            screen.screen = []
            screen.blank = blank+"   "

            for i in range(10):
                screen.screen.append([])
                for f in range(screen.w):
                    screen.screen[i].append("   ")
            
            for i in range(h):
                screen.screen.append([])
                for f in range(w):
                    screen.screen[i+10].append(screen.blank)
            Snake.Screen.w = w
            Snake.Screen.h = h

        def update(screen):
            for i in range(50):
                print("")

            screen.screen = []
            for i in range(10):
                screen.screen.append([])
                for f in range(screen.w):
                    screen.screen[i].append("    ")
            for i in range(screen.h):
                screen.screen.append([])
                for f in range(screen.w):
                    screen.screen[i+10].append(screen.blank)
            for i in Snake.obj:
                if i.type=="boulder":
                    for i in i.boulders:
                        screen.screen[i[1]][i[0]] = i[2]
                    continue
                if i.type=="snake":
                    while len(i.pos) > i.size:
                        i.pos.pop(0)
                    for f in range(len(i.pos)):
                        screen.screen[i.pos[f][1]+10][i.pos[f][0]] = i.tail_shape
                screen.screen[int(i.y//1)+10][int(i.x//1)] = i.shape
            for i in screen.screen:
                print("".join(i))
                print("")

        def get_key(screen, timeout):
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

        def check_for_inputs(screen):
            return screen.get_key(0.125)

        def inputed(screen, key):
            if key != 1:
                Snake.started = True
            return Snake.started

        def start_menu(screen):
            print("press e to play on easy mode, press n to play on normal mode. press q to quit.")
            k = screen.get_key(1)
            while k != "e" and k !="n" and k != "q":
                k = screen.get_key(1)
                if k == "e":
                    Snake.dif = "easy"
                    return
                if k == "n":
                    Snake.dif = "normal"
                    return
                if k == "q":
                    exit()
                if k != "n" and k != "e" and k != "q" and k != 1:
                    print("I didnt get that")

        def looser_menu(screen):
            print("your score was", Snake.score, "press r to restart. press q to quit.")
            k = screen.get_key(1)
            while k != "r" and k != "q":
                k = screen.get_key(1)
                if k == "r":
                    return
                if k == "q":
                    exit()
                if k != "r" and k != "q" and k != 1:
                    print("I didnt get that")

        def reset(screen):
            for i in Snake.obj:
                if i.type == "snake":
                    i.x = screen.w//2
                    i.y = screen.h//2
                    i.size = 0
                if i.type == "apple":
                    i.rtp()
            Snake.started = False
            Snake.score = 0

    class Apple():
        def __init__(apple, x=None, y=None, shape="2", rtp_size_x=None, rtp_size_y=None):
            if rtp_size_x is None:
                rtp_size_x = Snake.Screen.w

            if rtp_size_y is None:
                rtp_size_y = Snake.Screen.h

            if x is None:
                x = random.randint(0, rtp_size_x-1)
            if y is None:
                y = random.randint(0, rtp_size_y-1)
            apple.x = x
            apple.y = y
            apple.shape = shape+"   "
            apple.type = "apple"
            apple.rtp_size_x = rtp_size_x
            apple.rtp_size_y = rtp_size_y
            Snake.obj.append(apple)
        def rtp(apple):
            apple.x = random.randint(0, apple.rtp_size_x - 1)
            apple.y = random.randint(0, apple.rtp_size_y - 1)
    
    class Boulder():
        def __init__(boulder, shape="3", fall_speed=1, max=None, min=0, max_x=None, min_x=1, boulders=[], type="boulder", min_y=0, max_y = 2):
            if max_x is None:
                max_x = Snake.Screen.w-1
            if max is None:
                max = (max_x - min_x)//2
            boulder.shape = shape+"   "
            boulder.fall_speed = fall_speed
            boulder.max = max
            boulder.min = min
            boulder.max_x = max_x
            boulder.min_x = min_x
            boulder.y = 0
            boulder.type = type
            boulder.max_y = max_y
            boulder.min_y = min_y
            if len(boulders) == 0:
                i = 0
                while i < max:
                    boulders.append([random.randint(min_x, max_x), random.randint(min_y, max_y), boulder.shape, boulder.fall_speed, boulder.max, boulder.min_x, boulder.max_x, boulder.type])
                    i+=1
            boulder.boulders = boulders
            Snake.obj.append(boulder)

        def go_down(boulder):
            for i in boulder.boulders:
                i[1] += 1
                if i[1] >= Snake.Screen.h+10:
                    i[1] = random.randint(boulder.min_y, boulder.max_y)
                    i[0] = random.randint(boulder.min_x, boulder.max_x)


def main():
    import argparse
    argparse.ArgumentParser(
        prog="snake",
        description=(
            "A terminal snake game.\n\n"
            "Eat apples to grow, avoid your own tail, and dodge falling boulders.\n"
            "On normal mode you also lose if you hit a wall; on easy mode you wrap around.\n"
            "Controls:\n"
            "  w / a / s / d  move up / left / down / right\n"
            "  e              start playing on easy mode (walls wrap)\n"
            "  n              start playing on normal mode (walls kill)\n"
            "  r              restart (after losing)\n"
            "  q              quit"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    ).parse_args()
    boulder = Snake.Boulder()
    screen = Snake.Screen()
    apple = Snake.Apple()
    snake = Snake.snake()
    screen.start_menu()
    while True:
        screen.update()
        k = screen.check_for_inputs()
        snake.save_pos()
        snake.update_der(k)
        if screen.inputed(k):
            snake.forward()
        coll = snake.collition()
        if len(coll) > 0 and apple not in coll:
            screen.update()
            print(snake.name, "died")
            screen.looser_menu()
            screen.reset()
        boulder.go_down()
        coll = snake.collition()
        if len(coll) > 0 and apple not in coll:
            screen.update()
            print(snake.name, "died")
            screen.looser_menu()
            screen.reset()
        if apple in coll:
            snake.grow()
            apple.rtp()

__all__ = ["Snake", "main"]
