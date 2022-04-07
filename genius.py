from email.headerregistry import Group
from math import ceil 
from app import *
import requests
import json
import xlwt

from db.dispatcher import objects_filter
from db.models import Groups, User

def chunk(arr, size):
    return list(map(lambda x: arr[x * size:x*size+size], list(range(0, ceil(len(arr)/ size)))))

def touched():
    with open('titles/buttons.json', 'r', encoding='UTF-8') as file:
        data = json.load(file)
    return data


def request(link, params: dict = None, json: dict = None) -> dict:
    if params: 
        request = requests.post(SERVER_HOST + link, params=params).json()
    elif json: 
        request = requests.post(SERVER_HOST + link, json=json).json()
    return request


def excel_download(session,groups):
    
    style0 = xlwt.easyxf('font: name Raleway',
                        num_format_str='####')

    group_name = xlwt.easyxf('font: name Raleway, bold on, height 280; align: wrap on, vert center, horiz center',
                        num_format_str='# ###')
    
    table_name = xlwt.easyxf('font: name Raleway, bold on; align: wrap on, vert center, horiz center',
                        num_format_str='# ###')
    
    wb = xlwt.Workbook()
    ws = wb.add_sheet('object')

    ws.col(0).width = 256*30
    ws.col(1).width = 256*30
    ws.col(2).width = 256*30
    ws.col(3).width = 256*30
    ws.col(4).width = 256*30
    # ws.write(0, 0, "Пользователь", table_name)
    count, index = 0, 0
    for group in groups:
        
        ws.write(count, index, group.title, group_name)
        count +=1
        ws.write(count, index, "№", table_name)
        index +=1
        ws.write(count, index, "ID", table_name)
        index +=1
        ws.write(count, index, "Имя", table_name)
        index +=1
        ws.write(count, index, "Юзернейм", table_name)
        index +=1 
        ws.write(count, index, "Мобильный", table_name)
        users = objects_filter(session=session, model=User, group_id=group.id)
        count += 1
        index = 0
        no = 1
        for user in users:
            ws.write(count, index, no, style0)
            index +=1 
            ws.write(count, index, user.telegram_id, style0)
            index +=1 
            ws.write(count, index, user.fullname, style0)
            index +=1 
            ws.write(count, index, user.username, style0)
            index +=1
            ws.write(count, index, user.phone, style0)
            count +=1
            index = 0 
            no +=1
        
        count+=1
        index = 0
                
    
    path = './users.xls'
    wb.save(path)

    return path