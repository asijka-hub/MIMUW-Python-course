import os
import json
import requests
from tqdm import tqdm
import time

BASE_PATH = os.path.abspath(".")

def request_save(url, save_path, append=False):
    response = requests.get(url, timeout=5)

    if response.status_code == 200:
        response_json = response.json()

        if (append):
            with open(save_path, 'a', encoding='utf-8') as f:
                json.dump(response_json, f, ensure_ascii=False, indent=4)
        else:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(response_json, f, ensure_ascii=False, indent=4)
    else:
        print(f'Failed to retrieve data from the URL. Status code: {response.status_code}')

class DataLoader:
    """Class for dowloading data"""

    __base_url = 'https://api.um.warszawa.pl/api/action/'

    def __init__(self, api_key, data_path):
        self.api_key = api_key
        self.data_path = os.path.join(BASE_PATH, data_path)
        print("api key: ", self.api_key)
        print("data path:", self.data_path)
        print("created data loader")
        self.download_offline_data()

    def download_offline_data(self):
        print("downloading offline data")
        # self.download_dictionary()

        urls_save_paths = [(f'{self.__base_url}public_transport_dictionary/?apikey={self.api_key}', f'{self.data_path}/dictionary.json'),
                           (f'{self.__base_url}dbstore_get/?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey={self.api_key}', f'{self.data_path}/stops_info.json'),
                           (f'{self.__base_url}public_transport_routes/?apikey={self.api_key}', f'{self.data_path}/routes.json')]
       
        for (url, save_path) in urls_save_paths:
            request_save(url, save_path)

    def download_online_data(self, time_interval, dump_name):
        # tiem_intrval in minutes

        online_url = f'{self.__base_url}busestrams_get/?resource_id=%20f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={self.api_key}&type=1'
        print(online_url)
        save_path = os.path.join(self.data_path, dump_name)

        # Use tqdm to create a progress bar
        for i in tqdm(range(time_interval), desc="Processing", unit="iteration"):
            # Simulate some task that takes time to complete
            request_save(online_url, save_path, True)
            time.sleep(60)
