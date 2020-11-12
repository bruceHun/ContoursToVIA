import cv2
from os import path as os_path
from os import listdir as os_listdir
from os import stat as os_stat
import json
import configparser
import contovia
import numpy as np


def get_contours(filepath: str, threshold: int, color_max: int, mode: int, preview: bool) -> list:
    print(filepath)
    # 讀取圖檔
    im = cv2.imread(filepath)
    # 轉灰階
    # im = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
    lows = []
    highs = []
    lows.append(np.array([128, 0, 0]))
    lows.append(np.array([0, 128, 0]))
    lows.append(np.array([0, 0, 128]))
    highs.append(np.array([255, 0, 0]))
    highs.append(np.array([0, 255, 0]))
    highs.append(np.array([0, 0, 255]))
    cons = []
    for i in range(3):
        output = cv2.inRange(im, lows[i], highs[i])
        ret, thresh = cv2.threshold(output, threshold, color_max, mode)

        # 4.Erodes the Thresholded Image
        element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
        thresh = cv2.erode(thresh, element)

        # 尋找輪廓
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_TC89_L1)
        if len(contours) != 0:
            for area in contours:
                cons.append(area)

    if preview and (len(cons) != 0):
        # 畫出輪廓線
        img = cv2.drawContours(im, cons, -1, (0, 255, 0), 3)
        # 縮小四分之一比較容易看
        height, width = img.shape[0], img.shape[1]
        img_resize = cv2.resize(im, (int(width / 4), int(height / 4)))
        # 視窗顯示
        cv2.imshow('Image', img_resize)
        cv2.waitKey(0)

    return cons


if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Generate VIA JSON file with png images.')
    # 是否開啟 Contours 預覽 (預設關閉)
    parser.add_argument('-p', '--preview', required=False,
                        action='store_true',
                        help="Preview contours")
    args = parser.parse_args()

    prev = args.preview
    print("preview contours: ", prev)

    # 開啟設定檔
    try:
        settings = open("settings.ini", "r")
        settings.close()
        config = configparser.ConfigParser()
        config.read("settings.ini")
        folder = config.get('GeneralSettings', 'ImageDir')
        g_threshold = int(config.get('ContoursSettings', 'Threshold'))
        g_color_max = int(config.get('ContoursSettings', 'ColorMax'))
        g_mode = int(config.get('ContoursSettings', 'Mode'))
    except FileNotFoundError:

        config = configparser.ConfigParser()

        config["GeneralSettings"] = {'ImageDir': './images'  # 圖片資料夾
                                     }
        config["ContoursSettings"] = {'Threshold': '20',
                                      'ColorMax': '255',
                                      'Mode': '0'
                                      }
        folder = config.get('GeneralSettings', 'ImageDir')
        g_threshold = int(config.get('ContoursSettings', 'Threshold'))
        g_color_max = int(config.get('ContoursSettings', 'ColorMax'))
        g_mode = int(config.get('ContoursSettings', 'Mode'))
        with open('settings.ini', 'w') as file:
            config.write(file)

    labelfile = {}
    # 資料夾中所有檔案
    images = os_listdir(folder)
    count = 0

    for filename in images:
        if filename.endswith(".png"):
            path = folder + '/' + filename
            # 取得圖片 Contours
            CONTOURS = get_contours(path, g_threshold, g_color_max, g_mode, prev)
            # 沒找到就跳過
            if len(CONTOURS) == 0:
                print('No area found')
                continue

            # 更改附檔名 (空拍照片皆為 jpg 格式)
            fnamejpg = os_path.splitext(filename)[0] + '.JPG'
            filesize = os_stat(folder + '/' + fnamejpg).st_size
            # 將 Contours 點寫入 JSON
            contovia.process_image(fnamejpg, filesize, CONTOURS, "vehicle", labelfile)

    with open("../labels.json", "w") as outfile:
        print(labelfile)
        outfile.write(str(json.dumps(labelfile)))
