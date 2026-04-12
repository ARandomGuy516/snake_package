import random
import sys
import tty
import termios
import select


class Snake():
    obj = []
    started = False
    score = 0
    has_run = False
    class snake:
        def __init__(snake, name="Ishay", size=0, dir=0, shape="0", pos=[], tail_shape="1", alive=True):
            dir = dir//90*90
            if size < 0:
                size = 0
            snake.shape=shape+"  "
            snake.name = name
            snake.size = size
            snake.dir = dir
            snake.x = Snake.Screen.w//2
            snake.y = Snake.Screen.h//2
            snake.pos = pos
            snake.type = "snake"
            snake.tail_shape = tail_shape+"  "
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
                    if i.x == coll.x and i.y == coll.y:
                        lis.append(i)
            if coll.x >= Snake.Screen.w or coll.x < 0 or coll.y>=Snake.Screen.h or coll.y < 0:
                lis.append("wall")
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
            if k == "w":
                snake.dir = 90
            if k == "d":
                snake.dir = 0
            if k == "a":
                snake.dir = 180
            if k == "s":
                snake.dir = 270

    class Screen():
        w = 15
        h = 15
        def  __init__(screen, w=15, h=15, blank="."):
            screen.w = w
            screen.h = h
            screen.screen = []
            screen.blank = blank+"   "
            print(screen.blank)
            for i in range(h):
                screen.screen.append([])
                for f in range(w):
                    screen.screen[i].append(screen.blank)
            Snake.Screen.w = w
            Snake.Screen.h = h

        def update(screen):
            for i in range(50):
                print("")

            screen.screen = []
            for i in range(screen.h):
                screen.screen.append([])
                for f in range(screen.w):
                    screen.screen[i].append(screen.blank)
            for i in Snake.obj:
                if i.type=="snake":
                    while len(i.pos) > i.size:
                        i.pos.pop(0)
                    for f in range(len(i.pos)):
                        screen.screen[i.pos[f][1]][i.pos[f][0]] = i.tail_shape
                screen.screen[int(i.y//1)][int(i.x//1)] = i.shape

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
            print("press p to play. press q to quit.")
            k = screen.get_key(1)
            while k != "p" and k != "q":
                k = screen.get_key(1)
                if k == "p":
                    return
                if k == "q":
                    exit()
                if k != "p" and k != "q" and k != 1:
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
            Snake.score = False

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
            apple.shape = shape+"  "
            apple.type = "apple"
            Snake.obj.append(apple)
        def rtp(apple):
            apple.x = random.randint(0, Snake.Screen.w - 1)
            apple.y = random.randint(0, Snake.Screen.h - 1)


def main():
    screen = Snake.Screen(15, 15)
    apple = Snake.Apple()
    snake = Snake.snake()
    screen.start_menu()
    while True:
        k = screen.check_for_inputs()
        snake.save_pos()
        snake.update_der(k)
        if screen.inputed(k):
            snake.forward()
        coll = snake.collition()
        if len(coll) > 0 and apple not in coll:
            print(snake.name, "died")
            screen.looser_menu()
            screen.reset()
        if apple in coll:
            snake.grow()
            apple.rtp()
        screen.update()


__all__ = ["Snake", "main"]
