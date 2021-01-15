from math import pow as m_pow
from math import sqrt as m_sqrt

color_names = ['Red', 'Green', 'Blue', 'Yellow', 'Magenta', 'Cyan']


def process_image(filename: str, filesize: int, contours: list, width: int, height: int, typename: str, file: dict):
    """
    將結果整理成 VIA 2.0 標示檔格式。
    :param filename: 圖檔名稱
    :param filesize: 圖檔大小
    :param contours: 圖片中偵測到的輪廓資訊
    :param width: 圖片寬度
    :param height: 圖片高度
    :param typename: 類別名稱
    :param file: 用來輸出為 JSON 檔的 dictionary
    :return:
    """
    file[f"{filename}{filesize}"] = {}
    root = file[f"{filename}{filesize}"]
    root["filename"] = filename
    root["size"] = filesize
    # 加入寬高資訊，訓練資料準備時就不需要透過載入圖片來取得。
    root["width"] = width
    root["height"] = height
    root["regions"] = []

    # Area 內容
    for area, color in contours:
        sattr = {"name": "polygon", "all_points_x": [], "all_points_y": []}

        for i in range(len(area)):
            sattr["all_points_x"].append(int(area[i][0][0]))
            sattr["all_points_y"].append(int(area[i][0][1]))

        root["regions"].append(
            {
                "shape_attributes": sattr,
                "region_attributes":
                {
                    "Class": typename,
                    "Color": color_names[color]
                }
            }
        )


