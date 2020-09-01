import cv2
import os
import contovia


def get_contours(filepath: str, preview: bool) -> list:
    # 讀取圖檔
    im = cv2.imread(filepath)
    # 轉灰階
    imgray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # 定門檻值
    ret, thresh = cv2.threshold(imgray, 100, 255, 0)
    # 尋找輪廓
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if preview:
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
    # 指定點最小距離
    parser.add_argument('-d', '--distance', required=False,
                        help="The minimum distance required between points")
    # 是否開啟 Contours 預覽 (預設關閉)
    parser.add_argument('-p', '--preview', required=False,
                        action='store_true',
                        help="Preview contours")
    args = parser.parse_args()

    # 最小點與點距離
    dist = args.distance
    if dist is None:
        dist = 0
    print("distance: ", dist)
    prev = args.preview
    print("preview contours: ", prev)

    # 開啟檔案供寫入
    f = open("labels.json", "w")

    # Begin JSON
    f.write("{\n")
    folder = 'blenderimages/'
    # 資料夾中所有檔案
    images = os.listdir(folder)
    # 圖檔數量
    ttimgs = len(images)
    count = 0

    for filename in images:
        count += 1
        if filename.endswith(".png"):
            path = folder + filename
            filesize = os.stat(path).st_size
            # 取得圖片 Contours
            CONTOURS = get_contours(path, prev)
            # 更改附檔名 (空拍照片皆為 jpg 格式)
            fnamejpg = os.path.splitext(filename)[0] + '.JPG'
            # 將 Contours 點寫入 JSON
            contovia.process_image(fnamejpg, filesize, CONTOURS, f, dist)
            if count != ttimgs:
                f.write(",")
            f.write("\n")

    # End of JSON
    f.write("}\n")
    f.close()
