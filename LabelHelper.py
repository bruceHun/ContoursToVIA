import cv2
from os import path as os_path
from os import listdir as os_listdir
from os import stat as os_stat
import json
import configparser
import contovia


def get_contours(filepath: str, threshold: int, color_max: int, mode: int, preview: bool) -> list:
    # 讀取圖檔
    im = cv2.imread(filepath)
    # 轉灰階
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # 定門檻值 (灰階圖，門檻，最大值，)
    ret, thresh = cv2.threshold(imgray, threshold, color_max, mode)

    # 4.Erodes the Thresholded Image
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3, 3))
    thresh = cv2.erode(thresh, element)

    # 尋找輪廓
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if preview and (len(contours) != 0):
        # 畫出輪廓線
        img = cv2.drawContours(im, contours, -1, (0, 255, 0), 3)
        # 縮小四分之一比較容易看
        height, width = img.shape[0], img.shape[1]
        img_resize = cv2.resize(im, (int(width / 4), int(height / 4)))
        # 視窗顯示
        cv2.imshow('Image', img_resize)
        cv2.waitKey(0)

    return contours


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

        config["GeneralSettings"] = {'ImageDir': '../images'  # 圖片資料夾
                                     }
        config["ContoursSettings"] = {'Threshold': '20',
                                      'ColorMax': '255',
                                      'Mode': '1'
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
        if filename.endswith(".png") or filename.endswith("_mask.tif"):
            path = folder + '/' + filename
            # 取得圖片 Contours
            CONTOURS = get_contours(path, g_threshold, g_color_max, g_mode, prev)
            # 沒找到就跳過
            if len(CONTOURS) == 0:
                print('No area found')
                continue

            # 更改附檔名 (空拍照片皆為 jpg 格式)
            if filename.endswith("_mask.tif"):
                fnamejpg = filename[:len(filename) - 9] + '.JPG'
            else:
                fnamejpg = os_path.splitext(filename)[0] + '.JPG'
            filesize = os_stat(folder + '/' + fnamejpg).st_size
            # 將 Contours 點寫入 JSON
            contovia.process_image(fnamejpg, filesize, CONTOURS, "vehicle", labelfile)

    with open("../labels.json", "w") as outfile:
        print(labelfile)
        outfile.write(str(json.dumps(labelfile)))
