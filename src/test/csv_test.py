import pandas as pd

csv_path = '../../'


def get_satellite_csv(path="../../data/satellite/"):
    satellite_csv_name = "satellite.csv"
    data = pd.read_csv(path + satellite_csv_name)
    mp = dict()
    for idx, row in data.iterrows():
        mp[row['satellite_id']] = idx
    return data, mp
