from math import pow as m_pow
from math import sqrt as m_sqrt


def process_image(filename: str, filesize: int, contours: list, typename: str, file):

    num_of_areas = len(contours)

    # Image Header
    file.write(
        f"\t\"{filename}{filesize}\":" + " {\n" +
        f"\t\t\"filename\": \"{filename}\",\n" +
        f"\t\t\"size\": {filesize},\n" +
        "\t\t\"regions\": [\n")

    idx = 0

    # Area 內容
    for area in contours:
        idx += 1
        tp = len(area)
        all_x = []
        all_y = []
        for i in range(tp):
            all_x.append(area[i][0][0])
            all_y.append(area[i][0][1])
            # p1 = area[i][0]
            # p2 = area[(i + 1) % tp][0]
            # dist = m_sqrt(m_pow(p1[0] - p2[0], 2) + m_pow(p1[1] - p1[1], 2))
            #
            # if dist > distance or i == 0:
            #     all_x.append(p1[0])
            #     all_y.append(p1[1])

        file.write(
            "\t\t\t{\n" +
            "\t\t\t\t\"shape_attributes\": {\n" +
            "\t\t\t\t\t\"name\": \"polygon\",\n" +
            "\t\t\t\t\t\"all_points_x\": [\n"
        )
        # 區域輪廓取的點數
        sample = len(all_x)
        count = 1
        for x in all_x:
            file.write(f"\t\t\t\t\t\t{x}")
            if count != sample:
                file.write(",")
            file.write("\n")
            count += 1
        file.write(
            "\t\t\t\t\t],\n" +
            "\t\t\t\t\t\"all_points_y\": [\n"
        )
        count = 1
        for y in all_y:
            file.write(f"\t\t\t\t\t\t{y}")
            if count != sample:
                file.write(",")
            file.write("\n")
            count += 1
        file.write(
            "\t\t\t\t\t]\n" +
            "\t\t\t\t},\n" +
            "\t\t\t\t\"region_attributes\": {\n" +
            f"\t\t\t\t\t\"Name\": \"{typename}\"\n" +
            "\t\t\t\t}\n" +
            "\t\t\t}"
        )
        if idx != num_of_areas:
            file.write(",")
        file.write("\n")

    # Image footer
    file.write(
        "\t\t],\n" +
        "\t\t\"file_attributes\": {}\n" +
        "\t}"
    )

