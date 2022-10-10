#!/usr/bin/env python
# coding:utf-8
"""
Name   : process.py
Author : CampusAmour
Contect: campusamour@gmail.com
Time   : 2022/3/2 12:55
Desc   : 读取输入数据
"""
import json
import pandas as pd
from utils.model import InputItem


def readRoadInfo(path):
    df = pd.DataFrame(pd.read_excel(path))
    input_items = []
    for index, row in df.iterrows():
        if index == 0:
            continue
        input_items.append(InputItem(row))
    return input_items


def readCarInfo(path):
    df = pd.DataFrame(pd.read_excel(path))
    columns = df.columns.values.tolist()
    # print(columns)
    create_car_info = []
    for _, row in df.iterrows():
        for i in range(1, len(columns)):
            create_car_info.append((int(row[columns[0]]), int(columns[i]), int(row[columns[i]])))
    return create_car_info


def parseJsonFile(json_path):
    with open(json_path, 'r', encoding="utf-8") as read_content:
        data = json.load(read_content)
    return data


if __name__ == "__main__":
    pass
