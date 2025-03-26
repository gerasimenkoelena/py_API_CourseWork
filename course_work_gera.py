import requests
from tqdm import tqdm
import logging
import configparser
from pprint import pprint
import json


config = configparser.ConfigParser()
config.read('settings.ini')
vk_token = config['Tokens']['vk_token']
yd_token = config['Tokens']['yd_token']



logging.basicConfig(
     level=logging.INFO,
     filename='log.log',
     filemode='w',
     format='[%(asctime)s] %(levelname)s - %(message)s'
)

class VK:
    def __init__(self, access_token, version='5.199'):
        self.params = {
            'access_token': access_token,
            'v': version
        }
        self.base_url = 'https://api.vk.com/method/'

    def get_photos(self, user_id, count = 5):
        url = f'{self.base_url}photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': 'profile',
            'extended': 1
        }
        params.update(self.params)
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200: #код успеха 
                logging.info('The photos were  received successfully')
                return response.json()
            else:
                logging.error(f'An error has occurred while trying to recieve photos: {response.text}')
                return None
        except Exception as e:
            logging.error(f'An exception has occurred while trying to recieve photos: {e}')
            return None
    
class YD:
    def __init__(self):
        self.base_url = 'https://cloud-api.yandex.net'

    def create_folder(self, folder_name):
        yd_url_create_folder = f'{self.base_url}/v1/disk/resources'
        params = {
           'path':  folder_name
        }
        headers = {'Authorization': f'OAuth {yd_token}'}
        try:
            response = requests.put(yd_url_create_folder, params=params, headers=headers)
            if response.status_code == 201: #код успеха для создания ресурса
                logging.info('The folder was created successfully')
                return response.json
            else:
                logging.error(f'An error has occurred while creating folder: {response.text}')
                return None
        except Exception as e:
            logging.error(f'An exception has occurred while creating folder: {e}')
            return None
        
    def yd_upload_photo(self,folder_name,photo_name, photo_url):
        yd_url_uplink = f'{self.base_url}/v1/disk/resources/upload'
        params ={
            'url': photo_url,
            'path': f'disk:/{folder_name}/{photo_name}'
        }

        headers = {'Authorization': f'OAuth {yd_token}'}
        try:
            response = requests.post(yd_url_uplink, params= params, headers=headers)
            if response.status_code == 202: #Код 202 Accepted: Запрос принят в обработку
                logging.info('The download process has started')
             #  print(response.json())  # Выводим информацию об операции (operation_id)
                return response.json()
            else:
                logging.error(f'An error has occurred while starting download: {response.text}')
                return None
        except Exception as e:
            logging.error(f'An exception has occurred while starting download:: {e}')
            return None
    

user_id = input("Enter VK user ID, whose photos you want to save: ") # идентификатор пользователя vk
vk = VK(vk_token)
result= vk.get_photos(user_id, count=5)
#pprint(result)


result_list = []
for photo in result['response']['items']:
    max_size = max(photo['sizes'], key=lambda x: x['height'])
    res = {
        'likes': photo['likes']['count'],
        'date': photo['date'],
        'max_height': max_size['height'],
        'max_width': max_size['width'],
        'url': max_size['url']
    }
    res['name'] = res['likes']
    if result_list:
        for photo in result_list:
            if res['name'] == photo['name']:
                res['name'] =f"{res['likes']}{res['date']}"
    res['name'] = str(res['name']) + '.jpg'
    result_list.append(res)
#pprint(result_list)

json_data = []
for photo in result_list:
    data = {
        'file_name': str(photo['name']),
        'size': str(photo['max_height'])                       
    }
    json_data.append(data)

with open("json_result.json","w") as f:
    json.dump(json_data, f, ensure_ascii=False, indent=2)

yd = YD()
folder_name = 'api_course_work'
yd.create_folder(folder_name)
for photo in tqdm(result_list):
    yd.yd_upload_photo(folder_name,photo['name'],photo['url'] )

    