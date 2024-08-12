import pygame
import threading

# 初始化 Pygame
pygame.init()

# 设置屏幕尺寸
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Keyboard Input Demo")

# 定义游戏状态变量
running = True

# 定义按键状态变量
pressed_time = 0
current_time = 0
mix_combo = ""
# 锁对象
lock = threading.Lock()

END_EVENT = threading.Event()
DETECT_EVENT = threading.Event()
CLOCK = pygame.time.Clock()
fps = 24


def for_pressed_thread():
    global mix_combo
    while running:
        combo = ""
        for event in pygame.event.get(pygame.KEYDOWN):
            print(event.unicode)
            combo += event.unicode
        print("--------------------------")
        combo = "".join(sorted(combo, key=lambda x: "jfvn".index(x)))
        mix_combo = combo
        pygame.time.wait(60)


# 处理键盘输入的函数


# 创建并启动键盘输入线程
pressed_thread = threading.Thread(target=for_pressed_thread)
pressed_thread.daemon = True
pressed_thread.start()
print(pressed_thread.is_alive())
# 游戏主循环
while running:
    # 处理游戏逻辑
    # 这里只是一个示例，你可以根据需要添加游戏逻辑
    # s = pygame.time.get_ticks()
    # 绘制屏幕
    screen.fill((0, 0, 0))

    for event in pygame.event.get([pygame.QUIT, pygame.KEYUP]):
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            END_EVENT.set()
        elif event.type == pygame.KEYDOWN:
            pressed_time = pygame.time.get_ticks()
            print(f"pygame event: {event.unicode}")
            # print(f"pressed: {pressed_time}")
    # 绘制其他游戏元素
    # print(1)
    # 在屏幕上绘制按键状态
    # with lock:
    # print(2)
    work_surface = pygame.font.SysFont(None, 36).render(
        "working", True, (255, 255, 255)
    )
    combo_surface = pygame.font.SysFont(None, 36).render(
        mix_combo, True, (255, 255, 255)
    )
    screen.blit(work_surface, (50, 200))
    screen.blit(combo_surface, (50, 250))

    # 更新屏幕
    pygame.display.flip()
    # 控制帧率
    CLOCK.tick(fps)


# 等待键盘输入线程结束
# 退出 Pygame
pygame.quit()
print("end")
