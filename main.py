from resourses.vk_audio import *
from vk_api import *
from vkaudiotoken import get_kate_token, get_vk_official_token
import requests
import pickle

import configparser
from sys import argv


def get_login_password():
    config = configparser.ConfigParser()
    config.read('AUTH.properties')
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
    with open('auth_info_kmobile.pkl', 'wb') as auth_file:
        pickle.dump(info, auth_file, 4)


#Получаем токен от VKApi, который позволяет делать поиск песен
def auth_vk_api():
    login, password = get_login_password()

    vk_session = vk_api.VkApi(login=login, password=password)
    vk_session.auth(token_only=True)
    print(vk_session)
    with open('auth_info_VKApi.pkl', 'wb') as auth_file:
        pickle.dump(vk_session, auth_file, 4)

#Получаем список 10 первых найденных песен: [('название', 'id'),...]
def get_list_id(name_music):
    login, password = get_login_password()
    vk_session = vk_api.VkApi(login=login, password=password)
    vk_session.auth()
    vk = vk_audio.VkAudio(vk=vk_session)
    return vk.search(name_music)


#Передаем id песни, получаем ['название', 'url cылку на mp3']
def get_url_music_by_id(music_id, check_first=True):
    try:
        with open('auth_info_kmobile.pkl', 'rb') as auth_file:
            info = pickle.load(auth_file)

        sess = requests.session()

        sess.headers.update({'User-Agent': info["user_agent"]})

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

try:
    script, command, value = argv
except:
    print("Используйте ключи find '<Название песни>' или get '<id из результата find>'")

if command == 'find':
    #принемает строку названия поиска
    list_name_and_id = get_list_id(value)
    for row in list_name_and_id:
        print(row[0], ';;', row[1])
    exit(0)
elif command == "get":
    #принемает id из результата find
    name, url = get_url_music_by_id(value)
    print(name, ';;', url)
    exit(0)
else:
    print("Используйте ключи find '<Название песни>' или get '<id из результата find>'")
    exit(1)

