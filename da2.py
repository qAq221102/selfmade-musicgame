# import keyboard
import time
import pygame
import sys
import math
import random
import os
import cv2
from pygame.locals import *
import librosa
import threading
import csv

# 初始化
pygame.init()
# 遊戲名稱
pygame.display.set_caption("DA")
MusicPlayer = pygame.mixer.music
# 獲取螢幕的寬和高
screen_info = pygame.display.Info()
Width, Height = screen_info.current_w, screen_info.current_h
print((Width, Height), "\n")
# 預設fps
fps = 30
# 正中矩形的位置(左上右下)
mid_rect_pos = [[], []]
mid_rect_size = []
mid_rect_midpoint = []
game_region = []
# 背景角落顏色
ori_corner_color = [200, 200, 200, -10]
# 打擊後的文字顏色
clicked_txt_color = [200, 200, 200, -10]
clicked_txt = ""
last_clicked_txt = ""
# 打擊後的正中矩形角落顏色
clicked_corner_color = [225, 233, 39]
# 使用FULLSCREEN標誌設定全螢幕模式
screen = pygame.display.set_mode((Width, Height), pygame.FULLSCREEN)
# 選單的旗幟
Select_Flag = True
# 遊戲中的選單的旗幟
Gaming_Exit_Flag = False
# 製作圖譜的旗幟
Draw_Map_Flag = False
# 設定字體檔案名稱
system_font_filename = "system.ttf"
gaming_font_filename = "gaming.ttf"
# 音樂路徑列表
Music_Path_List = []
MPL_index = 0
# 影片路徑列表
Video_Path_List = []
Video_1st_image = None
# 開啟影片檔案
Video_Path = ""
Selected_Cap = ""
video_total_frame = 0
prev_frame = 0
video_target_ms = -1
# 背景圖片
bg_image_filename = "bg_image.jfif"
# 擊打物件圖片路徑
beat_img_filename = "python.png"
object_size = 0
beat_score = 0
# 音效
buffer_ae_name = "buffer.mp3"
select_ae_name = "select.mp3"
check_ae_name = "check.mp3"
exit_ae_name = "exit.mp3"
end_ae_name = "end.mp3"
click_ae_name = "clap.wav"
clickL_ae_name = "ClapL.wav"
clickR_ae_name = "ClapR.wav"
buffer_ae = 0
select_ae = 0
check_ae = 0
exit_ae = 0
end_ae = 0
click_ae = 0
clickL_ae = 0
clickR_ae = 0
# 路徑dict
file_path_dict = {
    system_font_filename: "",
    gaming_font_filename: "",
    bg_image_filename: "",
    beat_img_filename: "",
    buffer_ae_name: "",
    select_ae_name: "",
    check_ae_name: "",
    exit_ae_name: "",
    end_ae_name: "",
    click_ae_name: "",
    clickL_ae_name: "",
    clickR_ae_name: "",
}
# 初始化計時器
Clock = pygame.time.Clock()
KEYDOWN_INTERVAL = 15
current_time = 0
last_keydown_time = 0
# 音樂訊息
music_bpm = 0
music_len = 0
beat_times_ms = []
ms_per_beat = 0
beats = 0
beat_count = 0
refer_time = 0
start_music_time = 0  # ms
delta = 0  # ms
time_move = 3  # second
beat_stamp = []
last_stamp = 0
music_S2E_interval = 0
Music_Play = True
# 按下的按鍵
downkeys = pygame.key.get_pressed()
pressed_combo = ""
pressed_for_drawmap = ""
pressed_combo_time = 0
# 生成的打擊區塊 [j,f,v,n]
blocks_dict = {"j": False, "f": False, "v": False, "n": False}
block_combo = ""
gnrt_block_time = 0
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)
LOCK = threading.Lock()


def enter_buffer():
    # 中間的圓
    radius = Height // 4
    position = (Width // 2, Height // 2)
    # 圓上的點
    ver_pin = 90.0
    hor_pin = 0.0
    rate = 0

    def progress(angle):
        for theta in range(0, angle):
            rc = random.randint(100, 200)
            dot_color = (rc, rc, rc)
            draw_dot(position, dot_color, radius, hor_pin + theta)  # 水平上右
            draw_dot(position, dot_color, radius, 180 - (hor_pin + theta))  # 水平上左
            draw_dot(position, dot_color, radius, -(hor_pin + theta))  # 水平下右
            draw_dot(
                position, dot_color, radius, -(180 - (hor_pin + theta))
            )  # 水平下左
            draw_dot(position, dot_color, radius, ver_pin + theta)  # 垂直上左
            draw_dot(position, dot_color, radius, ver_pin - theta)  # 垂直上右
            draw_dot(position, dot_color, radius, -(ver_pin + theta))  # 垂直下左
            draw_dot(position, dot_color, radius, -(ver_pin - theta))  # 垂直下右

    buffer_ae.play()
    for i in range(0, 46):
        screen.fill((0, 0, 0))
        bg_img(file_path_dict[bg_image_filename])
        perc = round(rate / 45 * 100, 1)
        textprint(
            file_path_dict[system_font_filename],
            Height // 8,
            str(perc) + " %",
            position,
        )
        rate += 1
        progress(i)
        pygame.time.wait(11)
        pygame.display.flip()
    fade_out()


def fade_out(txt=" "):
    fade_speed = 50
    for alpha in range(0, 256, fade_speed):
        # 創建带有透明度信息的 Surface,覆蓋進度條
        surface = pygame.Surface((Width, Height), pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, alpha), (0, 0, Width, Height))
        # 将带有透明度信息的 Surface 绘制到屏幕上
        screen.blit(surface, (0, 0))
        if txt != " ":
            textprint(
                file_path_dict[system_font_filename],
                (mid_rect_pos[1][1] - mid_rect_pos[0][1]) // 2,
                txt,
                (Width // 2, Height // 2),
                (225, 10, 10),
            )
        Clock.tick(fps)
        pygame.display.flip()


def get_file_path(folder_name, file_name=("None")):
    # 取得程式執行的目錄
    current_dir = os.path.dirname(__file__)
    # 設定目標資料夾的相對路徑
    target_folder_path = os.path.join(current_dir, folder_name)
    # 傳目標資料夾中的各檔案路徑
    if os.path.isdir(target_folder_path) and file_name == "None":
        contents_name_list = os.listdir(target_folder_path)
        path_list = []
        for file in contents_name_list:
            file_path = os.path.join(target_folder_path, file)
            path_list.append(file_path)
        return path_list
    # 傳目標檔案的路徑
    elif os.path.isdir(target_folder_path):
        file_path = os.path.join(target_folder_path, file_name)
        if os.path.isfile(file_path):
            return file_path
        return "No file"
    return "No dir"


def select_music(SWITCH=False, REPLAY=False):
    if SWITCH:
        if not pygame.mixer.music.get_busy() or SWITCH:  # 播歌或切歌
            pygame.mixer.music.load(Music_Path_List[MPL_index])
            if REPLAY:
                pygame.mixer.music.play(loops=-1)
            else:
                # 取得音樂的訊息
                # get_music_info()
                global start_music_time, music_len
                music = pygame.mixer.Sound(Music_Path_List[MPL_index])
                music_len = int(music.get_length())
                pygame.mixer.music.play()
                start_music_time = pygame.time.get_ticks()


def load_video():
    global fps, Video_1st_image, video_total_frame, prev_frame
    if Music_Play:
        # 取得影片的寬度和高度
        video_width = int(Selected_Cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(Selected_Cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        video_total_frame = int(Selected_Cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if video_target_ms != -1:  # 製作圖譜時控制播放位置
            Selected_Cap.set(cv2.CAP_PROP_POS_MSEC, video_target_ms)
        ret, frame = Selected_Cap.read()
        if ret and (not Gaming_Exit_Flag):
            # 根據影片設定fps
            fps = Selected_Cap.get(cv2.CAP_PROP_FPS)
            # 轉換 OpenCV 影格到 Pygame surface
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = pygame.image.frombuffer(
                img.tobytes(), (video_width, video_height), "RGB"
            )
            new_image = pygame.transform.scale(img, (int(Width), int(Height)))
            Video_1st_image = new_image
            Video_1st_image.set_alpha(200)
            # 顯示影片畫面
            new_image.set_alpha(80)
            prev_frame = new_image
            screen.fill((0, 0, 0))
            screen.blit(new_image, (0, 0))
        else:
            Selected_Cap.release()
    else:
        screen.fill((0, 0, 0))
        screen.blit(prev_frame, (0, 0))


def get_1st_img():
    global Selected_Cap
    Selected_Cap = cv2.VideoCapture(Video_Path_List[MPL_index])
    Selected_Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 從頭開始讀取
    start = pygame.time.get_ticks()
    while True:
        load_video()
        end = pygame.time.get_ticks()
        if end - start >= (1 / 30) * 1000 * 3:
            Selected_Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 從頭開始讀取
            break


def select():
    global Select_Flag, Draw_Map_Flag
    switch = True
    line_color = [255, 255, 255]
    while Select_Flag:
        screen.fill((0, 0, 0))

        # 撥歌
        if switch:  # 只執行一次
            select_music(SWITCH=switch, REPLAY=True)
            get_1st_img()
        switch = False
        # 宣傳照
        screen.blit(Video_1st_image, (0, 0))

        # 顯示滑鼠造型
        mid_rectangle()
        midpoint_width = mid_rect_pos[0][0] + mid_rect_size[0] // 2
        midpoint_height = mid_rect_pos[0][1] + mid_rect_size[1] // 2
        interval = mid_rect_size[1] // 10
        # 垂直線
        start_pos = (midpoint_width, mid_rect_pos[0][1])
        end_pos = (
            midpoint_width,
            mid_rect_pos[0][1] + mid_rect_size[1] // 2,
        )
        pygame.draw.line(screen, line_color, start_pos, end_pos, width=1)

        def draw_roller():
            # 垂直線(滾輪)
            start_pos = (midpoint_width, mid_rect_pos[0][1] + interval)
            end_pos = (
                midpoint_width,
                mid_rect_pos[0][1] + mid_rect_size[1] // 2 - interval,
            )
            pygame.draw.line(screen, line_color, start_pos, end_pos, width=15)

        draw_roller()
        # 水平線
        start_pos = (mid_rect_pos[0][0], midpoint_height)
        end_pos = (mid_rect_pos[1][0], midpoint_height)
        pygame.draw.line(screen, line_color, start_pos, end_pos, width=1)

        # 確認鍵的區域
        button_rect = pygame.Rect(
            (mid_rect_pos[0][0], midpoint_height),
            (mid_rect_size[0], mid_rect_size[1] // 2),
        )

        # 鍵盤輸入
        for event in pygame.event.get():

            def check():
                global MPL_index, Select_Flag, delta
                check_ae.play()
                Select_Flag = False
                fade_out()
                global Video_Path, Selected_Cap
                Video_Path = Video_Path_List[MPL_index]
                Selected_Cap = cv2.VideoCapture(Video_Path)
                delta = 0
                # 遊戲倒數
                pygame.mixer.music.stop()
                countdown()

            def leftmove():
                global MPL_index

                list_len = len(Music_Path_List)
                select_ae.play()
                select_rect = (mid_rect_size[0] // 2, mid_rect_size[1] // 2)
                pygame.mixer.music.fadeout(1000)
                pygame.draw.rect(screen, GRAY, (mid_rect_pos[0], select_rect))
                draw_roller()
                fade_out()
                if list_len > 0:
                    MPL_index = (MPL_index - 1) % list_len
                    select_music(True, True)
                    get_1st_img()
                else:
                    print("No Music Can Play\n")

            def rightmove():
                global MPL_index

                list_len = len(Music_Path_List)
                select_ae.play()
                select_rect = (mid_rect_size[0] // 2, mid_rect_size[1] // 2)
                pygame.mixer.music.fadeout(1000)
                pygame.draw.rect(
                    screen,
                    GRAY,
                    ((midpoint_width, mid_rect_pos[0][1]), select_rect),
                )
                draw_roller()
                fade_out()
                if list_len > 0:
                    MPL_index = (MPL_index + 1) % list_len
                    select_music(True, True)
                    get_1st_img()
                else:
                    print("No Music Can Play\n")

            if event.type == pygame.QUIT:  # 離開遊戲
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_ESCAPE]:  # 離開遊戲
                    textprint(
                        file_path_dict[system_font_filename],
                        (mid_rect_pos[1][1] - mid_rect_pos[0][1]) // 2,
                        "See You",
                        (Width // 2, Height // 2),
                        (225, 10, 10),
                    )
                    pygame.display.flip()
                    end_ae.play()
                    pygame.mixer.music.fadeout(2000)
                    while pygame.mixer.music.get_busy():
                        pass
                    pygame.quit()
                    sys.exit()
                elif keys[pygame.K_RETURN]:
                    check()
                    return True
                elif keys[pygame.K_m]:
                    check()
                    Draw_Map_Flag = True
                    return True
                elif keys[pygame.K_LEFT]:
                    leftmove()
                    break
                elif keys[pygame.K_RIGHT]:
                    rightmove()
                    break
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mousebuttons = pygame.mouse.get_pressed()
                # 確認歌曲
                if button_rect.collidepoint(pygame.mouse.get_pos()) and mousebuttons[0]:
                    check()
                    return True

                if mousebuttons[0]:  # 左鍵
                    leftmove()
                    break

                elif mousebuttons[2]:  # 右鍵
                    rightmove()
                    break

        # 檢測滑鼠懸停
        if button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(screen, GRAY, button_rect)
            txt_pos = (midpoint_width, midpoint_height + mid_rect_size[1] // 4)
            pygame.draw.rect(screen, (225, 225, 225), button_rect, width=2)
            textprint(
                file_path_dict[system_font_filename],
                mid_rect_size[1] // 4,
                "Check!",
                txt_pos,
                BLACK,
            )

        Clock.tick(fps)
        pygame.display.flip()
    return False


def countdown():
    txt_list = ["Ready", "Go"]
    i = 0
    while i < 2:
        screen.fill((0, 0, 0))
        screen.blit(Video_1st_image, (0, 0))
        textprint(
            file_path_dict[gaming_font_filename],
            (mid_rect_pos[1][1] - mid_rect_pos[0][1]) // 2,
            txt_list[i],
            (Width // 2, Height // 2),
            (200, 10, 10),
        )
        pygame.display.flip()
        time.sleep(1)
        i += 1
    time.sleep(0.5)


def gaming_exit():
    global Gaming_Exit_Flag, Select_Flag, Draw_Map_Flag
    while Gaming_Exit_Flag:
        mid_rectangle()
        midpoint_width = mid_rect_pos[0][0] + mid_rect_size[0] // 2
        midpoint_height = mid_rect_pos[0][1] + mid_rect_size[1] // 2
        hover_size = (mid_rect_size[0], mid_rect_size[1] // 2)
        pygame.draw.line(
            screen,
            (225, 225, 225),
            (mid_rect_pos[0][0], midpoint_height),
            (mid_rect_pos[1][0], midpoint_height),
            width=2,
        )
        con_rect = pygame.Rect(mid_rect_pos[0], hover_size)
        menu_rect = pygame.Rect((mid_rect_pos[0][0], midpoint_height), hover_size)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 離開遊戲
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 繼續遊戲
                if con_rect.collidepoint(pygame.mouse.get_pos()) and event.button == 1:

                    select_ae.play()
                    Gaming_Exit_Flag = False
                    countdown()
                    pygame.mixer.music.unpause()
                    return

                # 返回主選單
                elif (
                    menu_rect.collidepoint(pygame.mouse.get_pos()) and event.button == 1
                ):
                    select_ae.play()
                    fade_out()
                    Gaming_Exit_Flag = False
                    Draw_Map_Flag = False
                    Select_Flag = True  # 重啟選單的程式
                    return
        text_size = mid_rect_size[1] // 3
        textprint(
            file_path_dict[system_font_filename],
            text_size,
            "Continue",
            (
                midpoint_width,
                mid_rect_pos[0][1] + mid_rect_size[1] // 4,
            ),
            (225, 10, 10),
        )

        textprint(
            file_path_dict[system_font_filename],
            text_size,
            "Menu",
            (
                midpoint_width,
                midpoint_height + mid_rect_size[1] // 4,
            ),
            (225, 10, 10),
        )
        Clock.tick(fps)
        pygame.display.flip()


def draw_dot(position, color, radius, angle):
    dot_pos = [0, 0]
    dot_pos[0] = int(position[0] + radius * math.cos(math.radians(angle)))
    dot_pos[1] = int(position[1] - radius * math.sin(math.radians(angle)))
    pygame.draw.circle(screen, color, dot_pos, 2)


def bg_img(imgpath):
    image = pygame.image.load(imgpath)
    new_image = pygame.transform.scale(image, (Width, Height))
    new_image.set_alpha(80)
    screen.blit(new_image, (0, 0))


def bg_corner(color):
    radius = mid_rect_pos[0][1] // 6
    corner_pos = [(0, Height), (Width, Height), (Width, 0), (0, 0)]
    if color[0] >= 200:  # 改變透明度
        color[3] = -5
    elif color[0] <= 50:
        color[3] = 5
    if 50 <= color[0] <= 200:
        for i in range(3):
            color[i] += color[3]
    for corner in corner_pos:
        pygame.draw.circle(screen, color[0:3], corner, radius)


def init_mid_rect():
    global mid_rect_pos, mid_rect_size, mid_rect_midpoint, game_region
    mid_rect_size = [Width // 2.5, Height // 2.5]
    rect_position = ((Width - mid_rect_size[0]) // 2, (Height - mid_rect_size[1]) // 2)
    mid_rect_pos = [
        rect_position,
        (
            rect_position[0] + mid_rect_size[0],
            rect_position[1] + mid_rect_size[1],
        ),
    ]
    mid_rect_midpoint = [
        mid_rect_pos[0][0] + mid_rect_size[0] // 2,
        mid_rect_pos[0][1] + mid_rect_size[1] // 2,
    ]
    game_region = [[Width // 16, Height // 16], [Width // 8 * 7, Height // 8 * 7]]


def mid_rectangle(color=(225, 225, 225), width=2):
    pygame.draw.rect(screen, color, (mid_rect_pos[0], mid_rect_size), width)  # 寬度2


def draw_game_region(color=(225, 225, 225), width=2):
    pygame.draw.rect(screen, color, game_region, width)  # 寬度2


def textprint(font, size, text, position=(0, 0), color=(225, 225, 225)):
    # 使用自定義字型文件創建字體
    def_font = pygame.font.Font(font, int(size))
    text_surface = def_font.render(text, True, color)
    txt_wid = text_surface.get_width()
    txt_hei = text_surface.get_height()
    position = center_to_topleft(position, (txt_wid, txt_hei))
    # 將文字Surface繪製到視窗上
    screen.blit(text_surface, position)


def imgprint(imgpath, position=(0, 0), scl_factor=(1.0, 1.0), alpha=(225)):
    image = pygame.image.load(imgpath)
    img_wid = image.get_width()
    img_hei = image.get_height()
    img_wid = int(img_wid * scl_factor[0])
    img_hei = int(img_hei * scl_factor[1])
    new_image = pygame.transform.scale(image, (img_wid, img_hei))
    new_image.set_alpha(alpha)
    position = center_to_topleft(position, (img_wid, img_hei))
    screen.blit(new_image, position)


def center_to_topleft(position, img_size):
    pos_x = max(0, min(position[0] - img_size[0] // 2, Width - img_size[0]))
    pos_y = max(0, min(position[1] - img_size[1] // 2, Height - img_size[1]))
    return int(pos_x), int(pos_y)


def draw_corner(corner_pos1, pos2, pos3, color=clicked_corner_color):
    pygame.draw.line(
        screen,
        color,
        corner_pos1,
        [(corner_pos1[0] + pos2[0]) // 2, (corner_pos1[1] + pos2[1]) // 2],
        width=5,
    )
    pygame.draw.line(
        screen,
        color,
        corner_pos1,
        [(corner_pos1[0] + pos3[0]) // 2, (corner_pos1[1] + pos3[1]) // 2],
        width=5,
    )
    pygame.display.flip()


def corner_j(audio, color=clicked_corner_color):
    draw_corner(
        [mid_rect_pos[1][0], mid_rect_pos[0][1]],
        mid_rect_pos[0],
        mid_rect_pos[1],
        color,
    )
    if audio:
        clickR_ae.play()


def corner_f(audio, color=clicked_corner_color):
    draw_corner(
        mid_rect_pos[0],
        [mid_rect_pos[1][0], mid_rect_pos[0][1]],
        [mid_rect_pos[0][0], mid_rect_pos[1][1]],
        color,
    )
    if audio:
        clickL_ae.play()


def corner_v(audio, color=clicked_corner_color):
    draw_corner(
        [mid_rect_pos[0][0], mid_rect_pos[1][1]],
        mid_rect_pos[0],
        mid_rect_pos[1],
        color,
    )
    if audio:
        clickL_ae.play()


def corner_n(audio, color=clicked_corner_color):
    draw_corner(
        mid_rect_pos[1],
        [mid_rect_pos[1][0], mid_rect_pos[0][1]],
        [mid_rect_pos[0][0], mid_rect_pos[1][1]],
        color,
    )
    if audio:
        clickR_ae.play()


def rect_mid(color=(255, 255, 255), linewidth=2):
    mid_width_pos = mid_rect_pos[0][0] + mid_rect_size[0] // 2
    mid_height_pos = mid_rect_pos[0][1] + mid_rect_size[1] // 2
    pygame.draw.line(
        screen,
        color,
        [mid_width_pos, mid_rect_pos[0][1]],
        [mid_width_pos, mid_rect_pos[1][1]],
        linewidth,
    )
    pygame.draw.line(
        screen,
        color,
        [mid_rect_pos[0][0], mid_height_pos],
        [mid_rect_pos[1][0], mid_height_pos],
        linewidth,
    )
    radius = mid_rect_pos[0][1] // 32
    pygame.draw.circle(screen, ori_corner_color[0:3], (Width // 2, Height // 2), radius)


def blocks_last(color=GRAY):
    block_size = (mid_rect_size[0] // 2, mid_rect_size[1] // 2)
    combo = ""
    if blocks_dict["j"]:
        pygame.draw.rect(
            screen,
            color,
            ((mid_rect_midpoint[0], mid_rect_pos[0][1]), block_size),
        )
        combo += "j"
    if blocks_dict["f"]:
        pygame.draw.rect(
            screen,
            color,
            (mid_rect_pos[0], block_size),
        )
        combo += "f"
    if blocks_dict["v"]:
        pygame.draw.rect(
            screen,
            color,
            ((mid_rect_pos[0][0], mid_rect_midpoint[1]), block_size),
        )
        combo += "v"
    if blocks_dict["n"]:
        pygame.draw.rect(
            screen,
            color,
            ((mid_rect_midpoint[0], mid_rect_midpoint[1]), block_size),
        )
        combo += "n"
    global block_combo
    order = "jfvn"
    block_combo = "".join(sorted(combo, key=lambda x: order.index(x)))


def get_music_info():
    global music_bpm, beat_times_ms, ms_per_beat, beats
    # 加載音訊文件
    audio_path = Music_Path_List[MPL_index]
    y, sr = librosa.load(audio_path)
    # 計算音樂的節拍信息
    music_bpm, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
    # 將節拍幀轉換為時間（秒）
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)
    beat_times_ms = [int(time * 1000) for time in beat_times]
    ms_per_beat = int(60 / music_bpm * 1000)
    beats = len(beat_times_ms)


def show_combo():
    combo_len = len(pressed_combo)
    color = [0, 0, 0]
    if combo_len > 1:
        color[4 - combo_len] = 255
    else:
        color = clicked_corner_color
    if "j" in pressed_combo:
        corner_j(False, color)
    if "f" in pressed_combo:
        corner_f(False, color)
    if "v" in pressed_combo:
        corner_v(False, color)
    if "n" in pressed_combo:
        corner_n(False, color)


def for_pressed_thread():
    global pressed_combo, pressed_for_drawmap, beat_stamp, Gaming_Exit_Flag, last_stamp
    while not Select_Flag:
        if not Gaming_Exit_Flag:
            combo = ""
            pressed_for_drawmap = ""
            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_ESCAPE:
                    Gaming_Exit_Flag = True
                    pygame.mixer.music.pause()
                    continue
                elif event.unicode in "jfvn":
                    combo += event.unicode
                if Draw_Map_Flag:
                    if event.key == pygame.K_RIGHT:
                        pressed_for_drawmap = "RIGHT"
                    elif event.key == pygame.K_LEFT:
                        pressed_for_drawmap = "LEFT"
                    elif event.key == pygame.K_s:
                        pressed_for_drawmap = "STOP"
                    elif event.key == pygame.K_p and len(beat_stamp) > 0:
                        pressed_for_drawmap = "PREVIOUS"
                        last_stamp = beat_stamp.pop()
                    elif event.key == pygame.K_SPACE:
                        pass

            combo = "".join(sorted(combo, key=lambda x: "jfvn".index(x)))
            pressed_combo = combo
            if pressed_combo:
                if Draw_Map_Flag and Music_Play:
                    print(refer_time - start_music_time)
                    beat_stamp.append([pressed_combo, refer_time - start_music_time])
                if pressed_combo in "fv":
                    clickL_ae.play()
                elif pressed_combo in "jn":
                    clickR_ae.play()
                else:
                    click_ae.play()
        # pygame.time.wait(60)
        Clock.tick(fps)


def open_thread(switch):
    if switch:
        pressed_thread = threading.Thread(target=for_pressed_thread)
        pressed_thread.daemon = True
        pressed_thread.start()


def draw_map():
    global refer_time, start_music_time, music_S2E_interval, delta, beat_stamp, video_target_ms, Music_Play
    if Draw_Map_Flag:
        video_target_ms = -1
        refer_time = pygame.time.get_ticks() + delta  # ms
        if refer_time - start_music_time > music_len * 1000:
            print("end music")
            MusicPlayer.stop()
            path = Music_Path_List[MPL_index].split("Musics_Folder")
            csv_path = path[0] + "Maps_Folder" + path[1].split(".mp3")[0] + ".csv"
            # 打开 CSV 文件并写入数据
            with open(csv_path, mode="w", newline="") as file:
                writer = csv.writer(file)
                for row in beat_stamp:
                    writer.writerow(row)
        if Music_Play and MusicPlayer.get_busy():
            if pressed_for_drawmap == "RIGHT":
                move2s = int((refer_time - start_music_time) / 1000 + time_move)
                MusicPlayer.rewind()
                MusicPlayer.set_pos(max(0, min(move2s, music_len)))
                video_target_ms = max(0, min(move2s, music_len)) * 1000
                delta += time_move * 1000
            elif pressed_for_drawmap == "LEFT":
                move2s = int((refer_time - start_music_time) / 1000 - time_move)
                MusicPlayer.rewind()
                MusicPlayer.set_pos(min(max(move2s, 0), music_len))
                video_target_ms = min(max(move2s, 0), music_len) * 1000
                if move2s < 0:
                    delta = 0
                    start_music_time = refer_time = pygame.time.get_ticks()
                else:
                    delta -= time_move * 1000
            elif pressed_for_drawmap == "PREVIOUS":
                MusicPlayer.rewind()
                MusicPlayer.set_pos(last_stamp[1] / 1000)
                video_target_ms = last_stamp[1]
            if pressed_for_drawmap == "STOP":
                if Music_Play:
                    MusicPlayer.pause()
                    music_S2E_interval = refer_time - start_music_time
                    Music_Play = False
                else:
                    Music_Play = True
                    MusicPlayer.unpause()
                    start_music_time = refer_time - music_S2E_interval


def init_path():
    global file_path_dict, Music_Path_List, Video_Path_List, buffer_ae, select_ae, check_ae, exit_ae, end_ae, click_ae, clickL_ae, clickR_ae
    # 設定字體、音樂、影片、音效路徑
    file_path_dict[system_font_filename] = get_file_path(
        "Fonts_Folder", system_font_filename
    )
    file_path_dict[gaming_font_filename] = get_file_path(
        "Fonts_Folder", gaming_font_filename
    )
    Music_Path_List = get_file_path("Musics_Folder")
    Video_Path_List = get_file_path("Videos_Folder")
    file_path_dict[bg_image_filename] = get_file_path("Images", bg_image_filename)
    file_path_dict[beat_img_filename] = get_file_path("Images", beat_img_filename)
    file_path_dict[buffer_ae_name] = get_file_path(
        "Audio_Effect_Folder", buffer_ae_name
    )
    buffer_ae = pygame.mixer.Sound(file_path_dict[buffer_ae_name])
    file_path_dict[select_ae_name] = get_file_path(
        "Audio_Effect_Folder", select_ae_name
    )
    select_ae = pygame.mixer.Sound(file_path_dict[select_ae_name])
    file_path_dict[check_ae_name] = get_file_path("Audio_Effect_Folder", check_ae_name)
    check_ae = pygame.mixer.Sound(file_path_dict[check_ae_name])
    file_path_dict[exit_ae_name] = get_file_path("Audio_Effect_Folder", exit_ae_name)
    exit_ae = pygame.mixer.Sound(file_path_dict[exit_ae_name])
    file_path_dict[end_ae_name] = get_file_path("Audio_Effect_Folder", end_ae_name)
    end_ae = pygame.mixer.Sound(file_path_dict[end_ae_name])
    file_path_dict[click_ae_name] = get_file_path("Audio_Effect_Folder", click_ae_name)
    click_ae = pygame.mixer.Sound(file_path_dict[click_ae_name])
    file_path_dict[clickL_ae_name] = get_file_path(
        "Audio_Effect_Folder", clickL_ae_name
    )
    clickL_ae = pygame.mixer.Sound(file_path_dict[clickL_ae_name])
    file_path_dict[clickR_ae_name] = get_file_path(
        "Audio_Effect_Folder", clickR_ae_name
    )
    clickR_ae = pygame.mixer.Sound(file_path_dict[clickR_ae_name])


init_path()
# 首開隨機歌曲
if len(Music_Path_List) > 0:
    MPL_index = random.randint(0, len(Music_Path_List) - 1)

# 正中矩形位置初始化
init_mid_rect()
# 緩衝(等待)動畫
enter_buffer()


while True:
    # 清屏
    screen.fill((0, 0, 0))
    # 選擇畫面
    switch = select()  # 得到選擇的歌曲索引值、影片
    # 開啟多線程
    open_thread(switch)
    # 背景影片
    load_video()
    # 滑鼠區域
    draw_game_region()
    # 顯示角落圓形
    bg_corner(ori_corner_color)
    # 啟動撥歌,直接撥歌
    select_music(switch, False)
    # 製作圖譜
    draw_map()
    # 生成打擊區塊
    # 顯示打擊區塊
    # # 顯示矩形正中央
    # rect_mid()
    # 遊戲中處理鍵盤輸入
    for event in pygame.event.get([pygame.QUIT]):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    # 評分
    # 持續顯示按鍵組合
    show_combo()
    # 遊戲中選單
    gaming_exit()

    # 更新視窗
    pygame.display.flip()
    # 控制偵數
    Clock.tick(fps)
