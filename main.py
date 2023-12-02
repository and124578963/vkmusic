# -*- coding: utf-8 -*-
import os
import sys

from resourses.vk_audio import *
from vk_api import *
from vkaudiotoken import get_kate_token, get_vk_official_token
import requests
import pickle

import configparser
from sys import argv


def get_login_password():
    config = configparser.ConfigParser()
    config.read(get_abs_path('AUTH.properties'))

    return [config['AUTH']['login'], config['AUTH']['password']]

#Получаем токен KateMobile, который позволяет скачивать музыку по id
def auth_kate_mobile():
    login, password = get_login_password()
    assert login!=None and password!=None

    try:
        info = get_kate_token(login, password)

    except Exception as exc:
        if "need_validation":
            code = input("SMS CODE: >>> ")

        info = get_kate_token(login, password, code)
    with open(get_abs_path('auth_info_kmobile.pkl'), 'wb') as auth_file:
        pickle.dump(info, auth_file, 4)


#Получаем список 10 первых найденных песен: [('название', 'id'),...]
def get_list_id(name_music, token_only=True):
    try:
        with open(get_abs_path('auth_info_kmobile.pkl'), 'rb') as auth_file:
            info = pickle.load(auth_file)
    except FileNotFoundError:
        auth_kate_mobile()
        with open(get_abs_path('auth_info_kmobile.pkl'), 'rb') as auth_file:
            info = pickle.load(auth_file)

    login, password = get_login_password()
    vk_session = vk_api.VkApi(login=login, password=password, token=info['token'], app_id=2685278)
    vk_session.auth(token_only=token_only)
    vk = vk_audio.VkAudio(vk=vk_session)
    return vk.search(name_music)


#Передаем id песни, получаем ['название', 'url cылку на mp3']
def get_url_music_by_id(music_id, check_first=True):
    try:
        with open(get_abs_path('auth_info_kmobile.pkl'), 'rb') as auth_file:
            info = pickle.load(auth_file)

        sess = requests.session()

        sess.headers.update({'User-Agent': info["user_agent"], 'Accept-Encoding': 'gzip, deflate'})

        track_list = sess.get(
            # "https://api.vk.com/method/audio.get",
            "https://api.vk.com/method/audio.getById",
            params=[('access_token', info['token']),
                    # ('user_id', user_id),
                    # ("count", 2),
                    # ("offset", 0),
                    ("audios", music_id),
                    # ('v', '5.89')]
                    ("v", "5.95")]
        ).json()
        track = track_list['response'][0]
        return [track["artist"] + " - " + track["title"], track["url"]]
    except Exception as e:
        print(e)
        if check_first:
            auth_kate_mobile()
            return get_url_music_by_id(music_id, check_first=False)



def test():

    with open(get_abs_path('auth_info_kmobile.pkl'), 'rb') as auth_file:
        info = pickle.load(auth_file)

    sess = requests.session()




    sess.headers.update({'User-Agent': info["user_agent"], 'X-Requested-With':'XMLHttpRequest'})


    track_list = sess.post(
        # "https://api.vk.com/method/audio.get",
        "https://vk.com/al_audio.php?act=section",
        params=[
                ('act', 'section'),
                ('al', 1),
                ('claim', 0),
                ('is_layer', 0),
                ('owner_id', '693703972'),
                ('q', 'test'),
                ('section', 'search'),
                # ('user_id', user_id),
                # ("count", 2),
                # ("offset", 0),
                # ('v', '5.89')]
                ("v", "5.92"), ]
    ).json()
    print(track_list)


def get_abs_path(file_name):
    script = os.path.basename(__file__)
    path = os.path.abspath(__file__).replace(script,'')
    return path + file_name

try:
    script, command, value = argv

except:
    print("Используйте ключи find '<Название песни>' или get '<id из результата find>'")
    exit(1)

if command == 'find':
    #принемает строку названия поиска
    list_name_and_id = get_list_id(value)
    if len(list_name_and_id) == 0: get_list_id(value, token_only=False)
    for row in list_name_and_id:
        result = row[0] + ';;' + row[1] + '\n'
        sys.stdout.buffer.write(result.encode('utf8'))


    exit(0)
elif command == "get":
    #принемает id из результата find
    name, url = get_url_music_by_id(value)
    result = name + ';;' + url
    sys.stdout.buffer.write(result.encode('utf8'))
    exit(0)
elif command == "test":
    test()
else:
    print("Используйте ключи find '<Название песни>' или get '<id из результата find>'")
    exit(1)

