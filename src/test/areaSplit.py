import json
import math
import os
import subprocess
import shapely
import matplotlib.pyplot as plt
from datetime import timedelta

import gpkg_test
import csv_test

data_path = "../../data/"


def show_polygon_shape(polygon, name="Shapely Polygon"):
    x, y = polygon.exterior.xy

    # 创建绘图
    plt.figure()
    plt.plot(x, y, color='blue')

    # 设置图形的比例和轴
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(name)
    plt.show()


def show_polygon_shape_2(polygon1, polygon2=None, point=None, name="Shapely Polygon"):
    x1, y1 = polygon1.exterior.xy
    plt.figure()
    plt.plot(x1, y1, color='blue')

    # 如果提供了第二个 Polygon，绘制它
    if polygon2 is not None:
        for i in polygon2:
            x2, y2 = i.exterior.xy
            plt.plot(x2, y2, color='black')

    if point is not None:
        for i in point:
            plt.plot(i.x, i.y, 'o', color='red')

    # 设置图形的比例和轴
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(name)

    # 显示图例
    plt.legend()

    # 显示图像
    plt.show()


def show_polygon_with_point(polygon, point, name="Shapely Polygon"):
    x, y = polygon.exterior.xy

    # 创建绘图
    plt.figure()
    plt.plot(x, y, color='blue')

    for i in point:
        plt.plot(i.x, i.y, 'o', color='red')

    # 设置图形的比例和轴
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title(name)
    plt.show()


def seconds_to_time_str(seconds):
    seconds = int(seconds)
    time_delta = timedelta(seconds=seconds)
    hrs, remainder = divmod(time_delta.seconds, 3600)
    mins, secs = divmod(remainder, 60)
    return f"{hrs:02d}:{mins:02d}:{secs:02d}"


# 返回前一个是否小于后一个
def comp_sunlight(a, b):
    aa = float(a)
    bb = float(b)
    return a < b


# 在范围内返回true
def comp_in_left_right_roll(a, left, right) -> bool:
    aa = float(a)
    ll = float(left)
    rr = float(right)
    return ll <= aa <= rr


def cmd_satellite_tools_m3(m3json):
    # print(m3json)
    with open("./input/m3001.json", 'w') as f:
        json.dump(m3json, f, indent=1)
    command = "sattools.exe run -i m3001.json -m 3"
    # 执行command命令
    result = subprocess.run(command, shell=True, check=True)


def cmd_satellite_tools(satellite, area):
    area_shape = area[3]
    area_name = area[0]

    # show_polygon_shape(area_shape, area_name)

    xx, yy = area_shape.exterior.coords.xy
    x, y = xx.tolist(), yy.tolist()
    x_left, x_right = min(x), max(x)
    y_button, y_top = min(y), max(y)
    # print(x_left, x_right, y_top, y_button)
    dx, dy = 0.05, 0.05
    # [Point(longitude , latitudes) ]
    point_list = [shapely.Point(min(x_left + dx * i, x_right), min(y_button + dy * j, y_top))
                  for i in range(math.ceil((x_right - x_left) / dx))
                  for j in range(math.ceil((y_top - y_button) / dy))]

    # show_polygon_with_point(area_shape, point_list, area[0] + ' with point')
    # 调用计算工具模式2
    m2json = dict()
    m2json['point_longitudes'] = []
    m2json['point_latitudes'] = []

    # 调用计算工具模式3
    m3json = dict()
    m3json['satellite_id'] = "1"
    m3json['start_time'] = ""
    m3json['end_time'] = ""
    m3json['roll_angle'] = 0

    for i in point_list:
        if i.within(area_shape):
            # 当前点位于多边形内部
            m2json['point_longitudes'].append(i.x)
            m2json['point_latitudes'].append(i.y)
            pass
    satellite_data, mp_name2id = csv_test.get_satellite_csv()
    GeoDataFrames = []
    cur_path = os.getcwd()
    os.chdir("../../")
    flag = False
    for i in satellite:
        getSatellite = gpkg_test.get_satellite_gpkg(i, './data/satellite')

        m2json['satellite_id'] = i
        m3json['satellite_id'] = i
        set_name = "set001"
        if os.path.exists("./output/" + set_name + "_" + area_name + "_" + i + ".gpkg"):
            flag = True
            tmp_time_list = []
            getGeoDataFrame = gpkg_test.get_output_gpkg(set_name + "_" + area_name + "_" + i, "./output")
            getGeoDataFrame = getGeoDataFrame.sort_values(by='time')
            left = right = -1
            roll_angle_ = 0
            roll_angle_cnt = 0
            for idx in range(len(getGeoDataFrame)):
                # 判断太阳高度角是否满足角度
                # print(i, getSatellite.iloc[getGeoDataFrame.iloc[idx].time].sun_elevation_angle,
                #       satellite_data.iloc[mp_name2id[i]].sunlight)
                if comp_sunlight(getSatellite.iloc[getGeoDataFrame.iloc[idx].time].sun_elevation_angle,
                                 satellite_data.iloc[mp_name2id[i]].sunlight):
                    continue
                # print(i, getGeoDataFrame.iloc[idx].roll_angle,
                #       satellite_data.iloc[mp_name2id[i]].left_roll, satellite_data.iloc[mp_name2id[i]].right_roll)
                # 判断侧摆角是否在范围内
                if not comp_in_left_right_roll(getGeoDataFrame.iloc[idx].roll_angle,
                                               satellite_data.iloc[mp_name2id[i]].left_roll,
                                               satellite_data.iloc[mp_name2id[i]].right_roll):
                    continue

                # 查找连续的时间序列区间 设置时间序列
                cur = int(getGeoDataFrame.iloc[idx].time)
                if left == -1 and right == -1:
                    left = right = cur

                if cur >= right + 100:
                    tmp_time_list.append([left, right, 1.0 * roll_angle_ / roll_angle_cnt])
                    tmp_time_list.append([left, right, 1.0 * roll_angle_ / roll_angle_cnt - 1])
                    tmp_time_list.append([left, right, 1.0 * roll_angle_ / roll_angle_cnt + 1])
                    left = right = cur
                    roll_angle_ = roll_angle_cnt = 1

                roll_angle_ += getGeoDataFrame.iloc[idx].roll_angle
                roll_angle_cnt += 1
                right = cur

            # 结束查找后可能仍存在方案
            if left != right and left != -1:
                tmp_time_list.append([left - 1, right + 1, 1.0 * roll_angle_ / roll_angle_cnt])
                tmp_time_list.append([left, right, 1.0 * roll_angle_ / roll_angle_cnt - 1])
                tmp_time_list.append([left, right, 1.0 * roll_angle_ / roll_angle_cnt + 1])

            # 生成新的候选数据集
            idx_use = 0
            for time in tmp_time_list:
                m3json['start_time'] = seconds_to_time_str(time[0])
                m3json['end_time'] = seconds_to_time_str(time[1])
                m3json['roll_angle'] = time[2]
                cmd_satellite_tools_m3(m3json)
                if os.path.exists("./output/m3001.gpkg"):
                    getGeoDataFrame = gpkg_test.get_output_gpkg("m3001", "./output")
                    if os.path.exists("./output/m3001.gpkg"):
                        if not os.path.exists(
                                "./output/m3" + set_name + "_" + area_name + "_" + i + "_" + str(idx_use) + ".gpkg"):
                            os.rename("./output/m3001.gpkg",
                                      "./output/m3" + set_name + "_" + area_name + "_" + i + "_" + str(
                                          idx_use) + ".gpkg")
                        idx_use += 1
                    for idx in range(len(getGeoDataFrame)):
                        GeoDataFrames.append(getGeoDataFrame.iloc[idx].geometry)
                # 丢给m3生成新的图像
                # GeoDataFrames.append(getGeoDataFrame.iloc[idx].geometry)

            continue
        if flag:
            continue
        with open("./input/m2001.json", 'w') as f:
            json.dump(m2json, f, indent=1)
        command = "sattools.exe run -i m2001.json -m 2"
        # 执行command命令
        result = subprocess.run(command, shell=True, check=True)
        if os.path.exists("./output/m2001.gpkg"):
            getGeoDataFrame = gpkg_test.get_output_gpkg("m2001", "./output")
            os.rename("./output/m2001.gpkg", "./output/" + set_name + "_" + area_name + "_" + i + ".gpkg")
            for idx in range(len(getGeoDataFrame)):
                GeoDataFrames.append(getGeoDataFrame.iloc[idx].geometry)

    os.chdir(cur_path)
    show_polygon_shape_2(area[3], GeoDataFrames, point_list, "all")
    print("size " + str(len(GeoDataFrames)) + ", point " + str(len(point_list)))

    select_geos = []
    select_geos_idx = [0 for i in range(len(GeoDataFrames))]
    area_res = area[3]
    while True:
        select_idx = -1
        select_area = 0
        select_geo = None
        min_area = area_res.area

        for idx, geo in enumerate(GeoDataFrames):
            if select_geos_idx[idx] == 1:
                continue
            intersection = area_res.intersection(geo)
            intersection_area = intersection.area
            min_area = min(min_area, intersection_area)
            if intersection_area > select_area:
                select_idx = idx
                select_area = intersection_area
                select_geo = geo

        if select_geo is None:
            break

        area_res = area_res.difference(select_geo)
        select_geos_idx[select_idx] = 1
        select_geos.append(select_geo)

        if area_res.area < 0.01:
            break

        pass

    show_polygon_shape_2(area[3], select_geos, point_list, "select")

    return
