import os
import json
import requests
from tqdm import tqdm
import time
from urllib.parse import quote
from requests.exceptions import HTTPError, RequestException

BASE_PATH = os.path.abspath(".")

def print_json(obj):
    """Print JSON object in a human-readable format."""
    print(json.dumps(obj, indent=4))

def api_error(json_obj):
    """Check if the JSON object represents an API error."""
    json_data = json_obj
    # Check if the 'result' key exists and if its value is equal to the desired string
    if 'result' in json_data and json_data['result'] == "Błędna metoda lub parametry wywołania":
        return True
    else:
        return False


def api_request(url, maxcout=100):
    """Send an HTTP GET request to the specified URL and handle retries.

    Args:
        url (str): The URL to send the request to.
        maxcount (int): Maximum number of retries (default is 100).

    Returns:
        dict: JSON response object.
    """
    for _ in range(maxcout):
        try:
            response = requests.get(url, timeout=10)
            response_json = response.json()

            if api_error(response_json):
                # print("api error")
                time.sleep(1)
                continue

            break
        except requests.exceptions.Timeout:
            # print("api timeout error")
            time.sleep(1)
            continue

    return response_json

def request_save(url, save_path, append=False):
    """Make an API request, save the JSON response to a file.

    Args:
        url (str): The URL to send the request to.
        save_path (str): The file path to save the JSON response.
        append (bool): Whether to append to the file if it exists (default is False).
    """
    response_json = api_request(url)

    if (append):
        with open(save_path, 'a', encoding='utf-8') as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)
    else:
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(response_json, f, ensure_ascii=False, indent=4)

class DataLoader:
    """Class for downloading data from the Warsaw public transport API."""

    __base_url = 'https://api.um.warszawa.pl/api/action/'
    __dictionary_file = 'dictionary.json'
    __stops_info_file = 'stop_info.json'
    __routes_file = 'routes.json'

    def __init__(self, api_key, data_path):
        self.api_key = api_key
        self.data_path = os.path.join(BASE_PATH, data_path)
        self.dictinary_path = os.path.join(self.data_path, self.__dictionary_file)
        self.stops_info_path = os.path.join(self.data_path, self.__stops_info_file)
        self.routes_path = os.path.join(self.data_path, self.__routes_file)

        print("api key: ", self.api_key)
        print("data path:", self.data_path)
        print("created data loader")
        self.basic_data_downloaded = False
        # self.download_offline_data()

    def download_basic_data(self):
        """Initialize the DataLoader instance.

        Args:
            api_key (str): The API key for accessing the Warsaw public transport API.
            data_path (str): The path to save downloaded data files.
        """
        print("downloading offline data")
        # self.download_dictionary()

        urls_save_paths = [(f'{self.__base_url}public_transport_dictionary/?apikey={self.api_key}', f'{self.dictinary_path}'),
                           (f'{self.__base_url}dbstore_get/?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey={self.api_key}', f'{self.stops_info_path}'),
                           (f'{self.__base_url}public_transport_routes/?apikey={self.api_key}', f'{self.routes_path}')]
       
        for (url, save_path) in urls_save_paths:
            request_save(url, save_path)

        self.basic_data_downloaded = True

    def download_online_data(self, time_interval, dump_name):
        """Download basic data including public transport dictionary, stop information, and routes."""
        # tiem_intrval in minutes

        online_url = f'{self.__base_url}busestrams_get/?resource_id=%20f2e5503e-927d-4ad3-9500-4ab9e55deb59&apikey={self.api_key}&type=1'
        print(online_url)
        save_path = os.path.join(self.data_path, dump_name)

        final_json = []

        # Use tqdm to create a progress bar
        for _ in tqdm(range(time_interval), desc="Processing", unit="iteration"):
            # Simulate some task that takes time to complete
            res_json = api_request(online_url)
            final_json += res_json["result"]
            time.sleep(60)

        with open(save_path, 'a', encoding='utf-8') as f:
                json.dump(final_json, f, ensure_ascii=False, indent=4)

    def download_stop_info(self, name):
        """Download information about a specific bus stop by its name.

        Args:
            name (str): The name of the bus stop.

        Returns:
            dict: JSON response object containing information about the bus stop.
        """
        url_name = quote(name)
        stop_info_url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get/?id=b27f4c17-5c50-4a5b-89dd-236b282bc499&name={url_name}&apikey={self.api_key}'
        res_json = api_request(stop_info_url)
        return res_json

    def download_lines_info(self, busstop_id, busstop_nr):
        """Download information about bus lines passing through a specific bus stop.

        Args:
            busstop_id (str): The ID of the bus stop.
            busstop_nr (str): The number of the bus stop.

        Returns:
            dict: JSON response object containing information about bus lines.
        """
        lines_info_url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get?id=88cd555f-6f31-43ca-9de4-66c479ad5942&busstopId={busstop_id}&busstopNr={busstop_nr}&apikey={self.api_key}'
        res_json = api_request(lines_info_url)
        return res_json
    
    def download_schedule_info(self, busstop_id, busstop_nr, line):
        """Download schedule information for a specific bus line at a specific bus stop.

        Args:
            busstop_id (str): The ID of the bus stop.
            busstop_nr (str): The number of the bus stop.
            line (str): The number or name of the bus line.

        Returns:
            dict: JSON response object containing schedule information.
        """
        schedule_url = f'https://api.um.warszawa.pl/api/action/dbtimetable_get?id=e923fa0e-d96c-43f9-ae6e-60518c9f3238&busstopId={busstop_id}&busstopNr={busstop_nr}&line={line}&apikey={self.api_key}'
        res_json = api_request(schedule_url)
        return res_json
