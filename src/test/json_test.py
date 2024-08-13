import os
import json

json_path = '../../data/setting'


def get_json() -> dict:
    for i in os.listdir(json_path):
        json_i = json_path + '/' + i
        with open(json_i, 'r') as f:
            s1 = json.load(f)
            return s1

# if __name__ == '__main__':
#     for i in os.listdir(json_path):
#         json_i = json_path + '/' + i
#         with open(json_i, 'r') as f:
#             s1 = json.load(f)
#             for key, value in s1.items():
#                 print(key, value)

