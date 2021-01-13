from typing import Tuple

import cv2
from os import path as os_path, listdir as os_listdir, stat as os_stat, remove as os_remove
from tkinter.filedialog import askdirectory
import json
import configparser
import contovia
import numpy as np


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
    print(filepath)
    # 讀取圖檔
    print('File found' if os_path.exists(filepath) else 'File Not found')
    im = cv2.imread(filepath)
    im_h, im_w, c = im.shape
    # 轉灰階
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    cons = []

    for i in range(6):
        output = cv2.inRange(im, lows[i], highs[i])
        ret, thresh = cv2.threshold(output, threshold, color_max, mode)

        # # 4.Erodes the Thresholded Image
        # element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        # thresh = cv2.erode(thresh, element)

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


if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate VIA JSON file with png images.')
    # 是否開啟 Contours 預覽 (預設關閉)
    parser.add_argument('-v', '--preview', required=False,
                        action='store_true',
                        help="Preview contours")
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

    folder = askdirectory()

    labelfile = {}
    # 資料夾中所有檔案
    images = os_listdir(folder)
    count = 0
    available_cams: dict = {"cam_list": []}

    for filename in images:
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
            available_cams["cam_list"].append((args.prefix if args.prefix is not None else "") + '/' + b_name)

            if os_path.exists(fnamejpg):
                filesize = os_stat(folder + '/' + fnamejpg).st_size
            else:
                filesize = os_stat(path).st_size
            # 將 Contours 點寫入 JSON
            contovia.process_image(fnamejpg, filesize, CONTOURS, w, h, obj_class, labelfile)

    with open(f"{folder}/via_region_data.json", "w") as outfile:
        outfile.write(str(json.dumps(labelfile)))
    with open(f"{folder}/cam_list.json", "w") as cam_list_file:
        cam_list_file.write(str(json.dumps(available_cams)))
