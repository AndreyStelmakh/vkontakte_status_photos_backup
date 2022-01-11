import json
from pprint import pprint
import requests
from progress.bar import IncrementalBar
import time


VKONTAKTE_TOKEN = ''
YANDEX_DISK_TOKEN = ''


class VkontakteAPI:
    def __init__(self, access_token, version_api='5.131'):
        self.access_token = access_token
        self.version_api = version_api

    def get_photos(self, count=5):
        request = requests.get(f'https://api.vk.com/method/photos.get?count={count}&album_id=profile&extended=1&access_token={self.access_token}&v={self.version_api}')

        json = request.json()

        images = []

        for item in json['response']['items']:
            # pprint(item)
            # for size in item['sizes']:
            #     print(size)
            max_size_image = max(item['sizes'], key=lambda s: s['height']*s['width'])
            max_size_image['date'] = item['date']
            max_size_image['likes'] = item['likes']['count']

            images.append(max_size_image)

        # pprint(images)

        return images


class YaUploader:
    def __init__(self, token: str):
        self.token = token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {self.token}'
        }

    def _get_upload_link(self, disk_file_path):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        params = {"path": disk_file_path, "overwrite": "true"}
        response = requests.get(upload_url, headers=headers, params=params)

        return response.json()

    def upload(self, file_path: str, disk_file_path: str):
        href = self._get_upload_link(disk_file_path=disk_file_path).get("href", "")

        with open(file_path, 'rb') as file:
            response = requests.put(href, data=file)
        response.raise_for_status()
        if response.status_code == 201:
            # print("Success")
            pass


if __name__ == "__main__":

    bar = IncrementalBar('Progress:\t', max=16)
    vk_api = VkontakteAPI(VKONTAKTE_TOKEN)
    yadisk_api = YaUploader(YANDEX_DISK_TOKEN)

    photos = vk_api.get_photos(5)
    bar.next()

    photos_info = []

    for photo in photos:
        file_name = f'{photo["likes"]} ({photo["date"]}).jpg'
        file_size = f'{photo["type"]}'

        photos_info.append({"file_name": file_name, "size": file_size})

        with open(file_name, 'wb') as file:
            response = requests.get(photo['url'])
            bar.next()
            file.write(response.content)
            bar.next()

        yadisk_api.upload(file_name, 'vkontakte_backup/' + file_name)
        bar.next()

    bar.finish()

    with open('photos_info.json', 'w') as info_file:
        json.dump(photos_info, info_file)


