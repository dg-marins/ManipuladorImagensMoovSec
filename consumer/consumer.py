import requests
import logging

class Consumer:
    def __init__(self, host_ip, host_moovsec_port, host_iot_handler_port, user, password) -> None:
        self.HostIp = host_ip
        self.user = user
        self.password = password

        self.Moovsec_Url = f'http://{self.HostIp}:{host_moovsec_port}'
        self.Iot_Handler_Url = f'http://{self.HostIp}:{host_iot_handler_port}'
        self.logger = logging.getLogger(__name__)

    def get_api_token(self):
        url = f'{self.Moovsec_Url}/auth/login'
        payload = {
            "login": self.user,
            "password": self.password
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()

            data = response.json()
            return data.get("data")

        except requests.exceptions.RequestException as e:
            print(f'Erro na requisição {e}')

    def get_car_records_url(self, car, date, source_records, stream_type):
        url = f'{self.Iot_Handler_Url}/dvr/{car}/mediarecords?YearMonthDay={date}&source={source_records}&streamType={stream_type}'
        return url
    
    def get_media_records(self, car, date, source_records, stream_type):

        try:
            api_token = self.get_api_token()
            headers = {'Authorization': f'Bearer {api_token}'}

            response = requests.get(self.get_car_records_url(car, date, source_records, stream_type), headers=headers)
            response.raise_for_status()
        
        except requests.exceptions.RequestException as e:
            print(f'Erro na requisição {e}')

        data = response.json()
        return data.get("data")
    
    def get_all_vehicles_information(self):
        url = f'{self.Moovsec_Url}/vehicle/all/true'
        
        try:
            api_token = self.get_api_token()
            headers = {'Authorization': f'Bearer {api_token}'}

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get("data")

        except requests.exceptions.RequestException as e:
            print(f'Erro na requisição {e}')

    def get_download_task(self, vehicleID, inicialDate, finalDate):
        
        url = f'{self.Moovsec_Url}/downloadTask/verify'
        payload = {
            "pagination": {
                "limit": 15,
                "page": 1
                },
                "filter": {
                    "vehicleIdList": [vehicleID],
                    "initialDate": inicialDate,
                    "finalDate": finalDate,
                    "order": "descendingTime",
                    "search": ""
                }
            }
        
        api_token = self.get_api_token()
        headers = {'Authorization': f'Bearer {api_token}'}
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()
            return data.get("data")

        except requests.exceptions.RequestException as e:
            print(f'Erro na requisição {e}')