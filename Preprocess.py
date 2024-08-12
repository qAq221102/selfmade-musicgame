from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import shutil
import pyautogui

scr_wid, scr_hei = pyautogui.size()
current_folder = os.getcwd()
pendingdir = "Pending_Folder"
pendingdir_path = os.path.join(current_folder, pendingdir)
musicdir = "Musics_Folder"
musicdir_path = os.path.join(current_folder, musicdir)
videodir = "Videos_Folder"
videodir_path = os.path.join(current_folder, videodir)
mapdir = "Maps_Folder"
mapdir_path = os.path.join(current_folder, mapdir)

download_url = "https://y2meta.app/zh-tw/youtube"
wanted_yt_url = ""
target_url = ""
# 設置下載選項
options = Options()
options.add_experimental_option(
    "prefs",
    {
        "download.default_directory": pendingdir_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    },
)
# 設置選項
options.add_argument("--log-level=1")
options.add_argument(f"--window-size={scr_wid//2},{scr_hei//2}")

print("--THIS IS PREPROCESS FUNC--")
print(f"Current Directory: {current_folder}")


def cls_terminal(s):
    time.sleep(s)
    os.system("cls")


def download_mv():
    Driver = webdriver.Chrome(options=options)
    os.system("cls")
    wait = WebDriverWait(Driver, timeout=120)

    def open_Driver(url):
        Driver.get(url)
        time.sleep(0.5)

    print("--Start downloading--")
    open_Driver(target_url)
    mv_text = Driver.find_element(By.XPATH, "//*[@id='result']/div/div[1]/div[1]/div/b")
    wanted_mv_filename = mv_text.text
    pending_filenames = os.listdir(pendingdir_path)
    if all(wanted_mv_filename not in filename for filename in pending_filenames):
        Video_download_button = Driver.find_element(
            By.XPATH, "//*[@id='moretab']/tr[1]/td[3]/button"
        )
        Video_download_button.click()
        mp4_download = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//a[contains(@href,"download?file=")]')
            )
        )
        mp4_url = mp4_download.get_attribute("href")
        print("> Mp4 url fetched SUCCESS")
        print("--------------------------------")
        open_Driver(target_url)
        Mp3_above_button = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="result"]/div/div[2]/ul/li[2]/a')
            )
        )
        Mp3_above_button.click()
        time.sleep(0.2)
        mp3_download_button = Driver.find_element(
            By.XPATH, "//*[@id='mp3-body']/tr[1]/td[3]/button"
        )
        mp3_download_button.click()
        mp3_download = wait.until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='process-result']/div/a[1]")
            )
        )
        mp3_url = mp3_download.get_attribute("href")
        print("> Mp3 url fetched SUCCESS")
        print("--------------------------------")
        cls_terminal(2)

        def wait(extension, url):
            open_Driver(url)
            dots = 1
            while True:
                pos = dots % 11
                s = "downloading"
                s_list = list(s)
                s_list[pos] = s_list[pos].upper()
                s = "".join(s_list)
                os.system("cls")
                pending_filenames = os.listdir(pendingdir_path)
                if all(
                    ".tmp" not in filename and ".crdownload" not in filename
                    for filename in pending_filenames
                ):
                    print(f'"{extension}" download SUCCESS')
                    print("-------------------------------")
                    cls_terminal(3)
                    break
                print(f'"{extension}" ' + s + "." * (dots % 5 + 1))
                dots += 1
                time.sleep(0.3)

        wait("MP3", mp3_url)
        wait("MP4", mp4_url)
        rename_pending()
    else:
        print("repeat download")
    Driver.close()
    print(Driver)
    print(f'--Download "{wanted_mv_filename}" SUCCESS--')
    cls_terminal(5)


def rename_pending():
    pending_filenames = os.listdir(pendingdir_path)
    if len(pending_filenames) > 0:
        print("--Start renaming--")
        for filename in pending_filenames:
            ori_filepath = os.path.join(pendingdir_path, filename)
            new_filename = ""
            if "Y2meta.app - " in filename:
                new_filename = filename.split("Y2meta.app - ")[1]
            elif "Y2meta.app-" in filename:
                new_filename = filename.split("Y2meta.app-")[1]
            basename, extension = os.path.splitext(filename)
            if any(trash in basename for trash in ["-(1080p)", " (320 kbps)"]):
                if extension == ".mp4":
                    new_filename = new_filename.split("-(1080p)")[0] + extension
                    new_filepath = os.path.join(pendingdir_path, new_filename)
                    os.rename(ori_filepath, new_filepath)
                    print("Mp4 rename SUCCESS")
                elif extension == ".mp3":
                    new_filename = new_filename.split(" (320 kbps)")[0] + extension
                    new_filepath = os.path.join(pendingdir_path, new_filename)
                    os.rename(ori_filepath, new_filepath)
                    print("Mp3 rename SUCCESS")
        print("--Rename Pending_Folder SUCCESS--")


def mc_file():  # move file and create file.csv
    pending_filenames = os.listdir(pendingdir_path)
    if len(pending_filenames) > 0:
        print("--Start moving and creating--")
        music_filenames = os.listdir(musicdir_path)
        video_filenames = os.listdir(videodir_path)
        map_filenames = os.listdir(mapdir_path)
        csv_by_mp3 = False
        for filename in pending_filenames:
            filepath = os.path.join(pendingdir_path, filename)
            basename, extension = os.path.splitext(filename)
            if extension == ".mp3" or extension == ".wav":
                if filename not in music_filenames:
                    csv_by_mp3 = False
                    shutil.move(filepath, musicdir_path)
                    music_filenames = os.listdir(musicdir_path)
                    print(f"{filename} moved to Musics_Folder")
                    print("---------------------------------------")
                else:
                    os.remove(filepath)
                    print(f"Delete repeated file: {filepath}")

            elif extension == ".mp4" or extension == ".mov":
                if filename not in video_filenames:
                    shutil.move(filepath, videodir_path)
                    video_filenames = os.listdir(videodir_path)
                    print(f"{filename} moved to Videos_Folder")
                    print("---------------------------------------")
                else:
                    os.remove(filepath)
                    print(f"Delete repeated file: {filepath}")
            else:
                os.remove(filepath)
                print(f"Delete error file: {filepath}")
            if all((basename + ".csv") not in map for map in map_filenames) and (
                not csv_by_mp3
            ):
                csv_by_mp3 = True
                csv_filepath = os.path.join(mapdir_path, basename + ".csv")
                open(csv_filepath, "w").close()
                map_filenames = os.listdir(mapdir_path)
                print(f"{basename}.csv created")
                print("---------------------------------------")
        print("--Move and Create file success--")
        cls_terminal(5)


while True:
    wanted_yt_url = input(
        "| INPUT v \n| 'CLS' to clean terminal\n| Anything without 'https://www.youtube.com/watch?v=' to exit\n| Wanted music url from youtube: "
    )

    if wanted_yt_url.upper() == "CLS":
        os.system("cls")
    elif wanted_yt_url.upper() == "TEST":
        rename_pending()
        mc_file()
        print("--Test success--")
    elif "https://www.youtube.com/watch?v=" in wanted_yt_url:
        try:
            cls_terminal(2)
            keyword = wanted_yt_url.split("watch?v=")[1]
            target_url = download_url + "/" + keyword
            download_mv()
            mc_file()
        except:
            print("ERROR INPUT")
            cls_terminal(2)
    else:
        print("--END PREPROCESS--")
        break
