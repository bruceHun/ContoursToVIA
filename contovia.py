from math import pow as m_pow
from math import sqrt as m_sqrt


def process_image(filename: str, filesize: int, contours: list, typename: str, file: dict):

    file[f"{filename}{filesize}"] = {}
    root = file[f"{filename}{filesize}"]
    root["filename"] = filename
    root["size"] = filesize
    root["regions"] = []

    # Area 內容
    for area in contours:
        sattr = {"name": "polygon", "all_points_x": [], "all_points_y": []}

        for i in range(len(area)):
            sattr["all_points_x"].append(int(area[i][0][0]))
            sattr["all_points_y"].append(int(area[i][0][1]))

        root["regions"].append({"shape_attributes": sattr, "region_attributes": {"Name": typename}})


