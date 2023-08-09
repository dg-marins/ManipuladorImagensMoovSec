import requests

class Consumer:
    def __init__(self, host_ip, host_port, user, password) -> None:
        self.HostIp = host_ip
        self.HostPort = host_port
        self.user = user
        self.password = password

        self.urlBase = f'http://{self.HostIp}:{self.HostPort}'

    def get_api_token(self):
        url = f'http://{self.HostIp}:5000/auth/login'
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
        url = f'{self.urlBase}/dvr/{car}/mediarecords?YearMonthDay={date}&source={source_records}&streamType={stream_type}'
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
           