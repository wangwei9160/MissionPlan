import geopandas as gpd
import pandas as pd
import os

data_path = "../../data"
output_path = "../../output"


def get_output_gpkg(mission) -> list:
    # ret = []

    out_gpkg_data = gpd.read_file(output_path + '/' + mission + '.gpkg')
    # for i in range(len(out_gpkg_data.iloc[0].geometry.bounds)):
    #     print(out_gpkg_data.iloc[0].geometry.bounds[i])
    # ret.append(out_gpkg_data)

    return out_gpkg_data


def get_mission_id(mission_list) -> list:
    area_data = gpd.read_file(data_path + '/mission/area.gpkg')
    point_data = gpd.read_file(data_path + '/mission/point.gpkg')

    ret = []
    for i in range(len(area_data)):
        if area_data.at[i, 'mission_id'] in mission_list:
            ret.append(
                [area_data.at[i, 'mission_id'], 'area', area_data.at[i, 'area'], area_data.at[i, 'geometry']])

    for i in range(len(point_data)):
        if point_data.at[i, 'mission_id'] in mission_list:
            ret.append([point_data.at[i, 'mission_id'], 'point', point_data.at[i, 'geometry']])

    return ret


def get_satellite_list(satellite_list) -> dict:
    # print(satellite_list)
    area_data_path = data_path + '/satellite/'
    ret = dict()
    for i in os.listdir(area_data_path):
        file_fe = i.split('.')[1]
        satellite_name = i.split('.')[0]
        if satellite_name in satellite_list:
            if satellite_name not in ret.keys():
                ret[satellite_name] = []
            # print(satellite_name)
            if file_fe == 'ftr':
                data = pd.read_feather(area_data_path + i)
                ret[satellite_name].append(data)
                # print(data)
            else:
                data = gpd.read_file(area_data_path + i)
                ret[satellite_name].append(data)
                # print(data)

    return ret

# if __name__ == '__main__':
#     # 资源普查和防灾减灾点任务数据
#     point_data = gpd.read_file(data_path + '/mission/area.gpkg')
#     print(point_data)
#     point_data_mission_id_list = point_data['mission_id']
#     point_data_geometry_list = point_data['geometry']

# print(point_data_mission_id_list)
# print(point_data_geometry_list)

# area_data_path = data_path + '/satellite/'
# for i in os.listdir(area_data_path):
#     if i.split('.')[1] != 'ftr':
#         i_data = gpd.read_file(area_data_path + i)
#         i_name = i.split('.')[0] + '.txt'
#         if not os.path.exists(i_name):
#             with open(i_name, 'a') as f:
#                 f.write(i_data.to_string())
#         else:
#             with open(i_name, 'w') as f:
#                 f.write(i_data.to_string())
#         break
