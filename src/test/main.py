import json

import gpkg_test
import json_test
import areaSplit

if __name__ == '__main__':
    # get set001.json
    json_dict = json_test.get_json()
    # 找到当前场景下所有的卫星集合
    satellite_list = gpkg_test.get_satellite_list(json_dict['satellite_id'])

    # 获取当前场景下所有的任务集合
    mission_list = gpkg_test.get_mission_id(json_dict['mission_id'])

    area_select = []
    for i in mission_list:
        if i[1] == 'area':
            area_select = i
            break

    # print(area_select)

    areaSplit.cmd_satellite_tools(json_dict['satellite_id'], area_select)

    # 生成m1001.json 通过计算工具计算条带状
    output_m1001 = gpkg_test.get_output_gpkg("m1001")
    # print(output_m1001)
    # for i in output_m1001:
    #     print(i)

    # for i in mission_list:
    #     print(i)
    # if len(json_dict['mission_id']) == len(mission_list):
    #     print('ok')
    # else:
    #     print('no')

    # 动态追加部分
    # dyn1 = [i for i in range(1, 2 + 1)]
    # dyn2 = [i for i in range(1, 11 + 1)]
    #
    #
    # def number2dyn(x) -> str:
    #     if x < 10:
    #         return '0' + str(x)
    #     return str(x)
    #
    #
    # dyn1_name_list = ['dyn1' + number2dyn(i) for i in dyn1]
    # dyn2_name_list = ['dyn2' + number2dyn(i) for i in dyn2]
    # dyn1_mission_list = []
    # dyn2_mission_list = []
    # for i in dyn1_name_list:
    #     dyn1_mission_list.append(gpkg_test.get_mission_id(json_dict[i]))
    #
    # for i in dyn2_name_list:
    #     dyn2_mission_list.append(gpkg_test.get_mission_id(json_dict[i]))

    # for i, element in enumerate(dyn1_mission_list):
    #     if len(element) == len(json_dict[dyn1_name_list[i]]):
    #         ok = 1
    #     else:
    #         ok = 0
    #         print("error")
    #         break
    #
    # for i, element in enumerate(dyn2_mission_list):
    #     if len(element) == len(json_dict[dyn2_name_list[i]]):
    #         ok = 1
    #     else:
    #         ok = 0
    #         print("error")
    #         break
