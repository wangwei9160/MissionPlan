import json
import math
import os
import subprocess
import shapely
import matplotlib.pyplot as plt
from datetime import timedelta

import gpkg_test

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
    plt.plot(x1, y1, color='blue', label='Polygon 1')

    # 如果提供了第二个 Polygon，绘制它
    if polygon2 is not None:
        for i in polygon2:
            x2, y2 = i.exterior.xy
            plt.plot(x2, y2, color='black', label='Polygon 2')

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


def cmd_satellite_tools(satellite, area):
    # print(type(area[3]))
    show_polygon_shape(area[3], area[0])

    xx, yy = area[3].exterior.coords.xy
    x, y = xx.tolist(), yy.tolist()
    x_left, x_right = min(x), max(x)
    y_button, y_top = min(y), max(y)
    print(x_left, x_right, y_top, y_button)
    dx, dy = 0.1, 0.1
    # [Point(longitude , latitudes) ]
    point_list = [shapely.Point(min(x_left + dx * i, x_right), min(y_button + dy * j, y_top))
                  for i in range(math.ceil((x_right - x_left) / dx))
                  for j in range(math.ceil((y_top - y_button) / dy))]

    # print(point_list)
    # print(len(point_list))
    show_polygon_with_point(area[3], point_list, area[0] + ' with point')
    m2json = dict()
    m2json['point_longitudes'] = []
    m2json['point_latitudes'] = []

    # m3json = dict()
    # m3json['satellite_id'] = "1"
    # m3json['start_time'] = ""
    # m3json['end_time'] = ""
    # m3json['roll_angle'] = 0

    for i in point_list:
        if i.within(area[3]):
            # 当前点位于多边形内部
            m2json['point_longitudes'].append(i.x)
            m2json['point_latitudes'].append(i.y)
            pass

    GeoDataFrames = []
    cur_path = os.getcwd()
    os.chdir("../../")
    for i in satellite:
        m2json['satellite_id'] = i
        # m3json['satellite_id'] = i
        with open("./input/m2001.json", 'w') as f:
            json.dump(m2json, f, indent=1)
        command = "sattools.exe run -i m2001.json -m 2"
        # 执行command命令
        result = subprocess.run(command, shell=True, check=True)
        getGeoDataFrame = gpkg_test.get_output_gpkg("m2001", "./output")
        # print(getGeoDataFrame.iloc[0].time)
        # print(type(getGeoDataFrame.iloc[0].time))
        for idx in range(len(getGeoDataFrame)):
            GeoDataFrames.append(getGeoDataFrame.iloc[idx].geometry)

            # show_polygon_shape(getGeoDataFrame.iloc[idx].geometry, i + " in " + area[0] + " No" + str(idx + 1))
            # # m3 test
            # m3json['start_time'] = seconds_to_time_str(getGeoDataFrame.iloc[idx].time)
            # m3json['end_time'] = seconds_to_time_str(int(getGeoDataFrame.iloc[idx].time) + 10)
            # m3json['roll_angle'] = getGeoDataFrame.iloc[idx].roll_angle
            # print(m3json)
            # with open("./input/m3001.json", 'w') as f:
            #     json.dump(m3json, f, indent=1)
            # command = "sattools.exe run -i m3001.json -m 3"
            # result = subprocess.run(command, shell=True, check=True)
            # getGeoDataFrame1 = gpkg_test.get_output_gpkg("m3001", "./output")
            # show_polygon_shape(getGeoDataFrame1.iloc[0].geometry, "m3")
            #
            # show_polygon_shape_2(area[3], [getGeoDataFrame.iloc[idx].geometry, getGeoDataFrame1.iloc[idx].geometry], point_list, "all")

        # for idx in range(len(getGeoDataFrame)):
        #     show_polygon_shape(getGeoDataFrame.iloc[idx].geometry, i + " in " + area[0] + " No" + str(idx+1))

        # print(getGeoDataFrame.head(5))

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

        if area_res.area < min_area:
            break

        pass

    show_polygon_shape_2(area[3], select_geos, point_list, "select")

    return
