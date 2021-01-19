from typing import Tuple

import cv2
from os import path as os_path, listdir as os_listdir, stat as os_stat, remove as os_remove, makedirs as os_makedirs
from tkinter.filedialog import askdirectory
from tkinter import Tk
import json
import configparser
import contovia
import numpy as np
import re

# 六種顏色的上下限值
lows: np.array = np.array([[128, 0, 0],
                           [0, 128, 0],
                           [0, 0, 128],
                           [128, 128, 0],
                           [128, 0, 128],
                           [0, 128, 128]])

highs: np.array = np.array([[255, 20, 20],
                            [20, 255, 20],
                            [20, 20, 255],
                            [255, 255, 20],
                            [255, 20, 255],
                            [20, 255, 255]])


def get_contours(filepath: str, threshold: int, color_max: int, mode: int, preview: bool):
    """
    依據設定使用 OpenCV 偵測輪廓
    :param filepath: 來源圖檔名稱
    :param threshold: 門檻值 (參閱 OpenCV 文件)
    :param color_max: 顏色上限 (參閱 OpenCV 文件)
    :param mode: 模式 (參閱 OpenCV 文件)
    :param preview: 即時預覽結果
    :return: 回傳 contours 及圖片高、寬
    """
    print(filepath)
    # 讀取圖檔
    print('File found' if os_path.exists(filepath) else 'File Not found')
    im = cv2.imread(filepath)
    im_h, im_w, c = im.shape
    cons = []

    # 針對六個不同的顏色各執行一次輪廓偵測
    for i in range(6):
        output = cv2.inRange(im, lows[i], highs[i])
        ret, thresh = cv2.threshold(output, threshold, color_max, mode)

        # 尋找輪廓
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) != 0:
            for area in contours:
                cons.append((area, i))

    if preview and (len(cons) != 0):
        # 畫出輪廓線
        img = cv2.drawContours(im, cons, -1, (0, 255, 0), 3)
        # 縮小四分之一比較容易看
        height, width = img.shape[0], img.shape[1]
        img_resize = cv2.resize(im, (int(width / 4), int(height / 4)))
        # 視窗顯示
        cv2.imshow('Image', img_resize)
        cv2.waitKey(0)

    return cons, im_w, im_h


def get_save_filename(directory: str, f_name: str) -> str:

    save_path = f'{directory}/{f_name}.json'
    # 儲存 JSON 檔案前檢查檔案是否存在
    if os_path.exists(save_path):
        json_files = [f for f in os_listdir(directory) if re.match(f'{f_name}\([0-9]+\).json', f)]

        idx = 1
        if len(json_files) > 0:
            for jsn in json_files:
                st, ed = re.search('[0-9]+', jsn).span()
                print(jsn[st:ed])
                idx = max(idx, int(jsn[st:ed]))
            idx += 1

        save_path = f'{directory}/{f_name}({idx}).json'

    return save_path


if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate VIA JSON file with png images.')
    # 是否開啟 Contours 預覽 (預設關閉)
    parser.add_argument('-v', '--preview', required=False,
                        action='store_true',
                        help="Preview contours")
    # 在相機清單中的項目加上前綴。(ex. "Photogroup 1")
    parser.add_argument('-p', '--prefix', required=False,
                        help="Add prefix")
    args = parser.parse_args()

    prev = args.preview
    print("preview contours: ", prev)

    # 開啟設定檔
    try:
        settings = open("settings.ini", "r")
        settings.close()
        config = configparser.ConfigParser()
        config.read("settings.ini")
        obj_class = config.get('GeneralSettings', 'ClassName')
        g_threshold = int(config.get('ContoursSettings', 'Threshold'))
        g_color_max = int(config.get('ContoursSettings', 'ColorMax'))
        g_mode = int(config.get('ContoursSettings', 'Mode'))
    except FileNotFoundError:

        config = configparser.ConfigParser()
        config["GeneralSettings"] = {'ClassName': 'vehicle'}
        config["ContoursSettings"] = {'Threshold': '20',
                                      'ColorMax': '255',
                                      'Mode': '0'
                                      }
        obj_class = config.get('GeneralSettings', 'ClassName')
        g_threshold = int(config.get('ContoursSettings', 'Threshold'))
        g_color_max = int(config.get('ContoursSettings', 'ColorMax'))
        g_mode = int(config.get('ContoursSettings', 'Mode'))
        with open('settings.ini', 'w') as file:
            config.write(file)

    # 建立並隱藏主視窗
    root = Tk()
    root.withdraw()
    # 選擇圖片目錄
    folder = askdirectory()

    labelfile = {}
    # 有找到 contours 的相機清單
    available_cams: dict = {"cam_list": []}

    for filename in os_listdir(folder):
        if filename.endswith(".png"):
            path = folder + '/' + filename
            # 取得圖片 Contours
            CONTOURS, w, h = get_contours(path, g_threshold, g_color_max, g_mode, prev)
            # 沒找到就跳過，並且刪除遮罩圖片
            if len(CONTOURS) == 0:
                print(f'No area found. Deleting {path}...')
                os_remove(path)
                print('Done')
                continue

            # 更改附檔名 (空拍照片皆為 jpg 格式)
            b_name = os_path.splitext(filename)[0]
            fnamejpg = b_name + '.JPG'
            # 加入至相機清單
            available_cams["cam_list"].append((args.prefix if args.prefix is not None else "") + '/' + b_name)

            if os_path.exists(fnamejpg):
                filesize = os_stat(folder + '/' + fnamejpg).st_size
            else:
                filesize = os_stat(path).st_size
            # 將 Contours 點寫入 JSON
            contovia.process_image(fnamejpg, filesize, CONTOURS, w, h, obj_class, labelfile)
    # 輸出兩個檔案
    with open(get_save_filename(folder, "via_region_data"), "w") as outfile:
        outfile.write(str(json.dumps(labelfile)))
    with open(get_save_filename(folder, "cam_list"), "w") as cam_list_file:
        cam_list_file.write(str(json.dumps(available_cams)))
