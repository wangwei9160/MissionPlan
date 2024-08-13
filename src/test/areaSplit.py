import json
import math

import geopandas as gpd
import os
import subprocess
import shapely
import matplotlib.pyplot as plt

data_path = "../../data/"


def show_polygon_shape(polygon):
    x, y = polygon.exterior.xy

    # 创建绘图
    plt.figure()
    plt.plot(x, y, color='blue')

    # 设置图形的比例和轴
    plt.gca().set_aspect('equal', adjustable='box')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Shapely Polygon')
    plt.show()


def show_polygon_with_point(polygon, point):
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
    plt.title('Shapely Polygon')
    plt.show()


def cmd_satellite_tools(satellite, area):
    # print(type(area[3]))
    show_polygon_shape(area[3])

    xx, yy = area[3].exterior.coords.xy
    x, y = xx.tolist(), yy.tolist()
    x_left, x_right = min(x), max(x)
    y_button, y_top = min(y), max(y)
    print(x_left, x_right, y_top, y_button)
    dx, dy = 0.1, 0.1
    point_list = [shapely.Point(min(x_left + dx * i, x_right), min(y_button + dy * j, y_top))
                  for i in range(math.ceil((x_right - x_left) / dx))
                  for j in range(math.ceil((y_top - y_button) / dy))]
    # print(point_list)
    # print(len(point_list))
    for i in point_list:
        if i.within(area[3]):
            print(i)
    show_polygon_with_point(area[3], point_list)
    cur_path = os.getcwd()
    os.chdir("../../")
    command = "sattools run -i m1001.json -m 1"

    os.chdir(cur_path)

    return
