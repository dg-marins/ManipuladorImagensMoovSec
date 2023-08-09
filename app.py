from consumer.consumer import Consumer
import os
import json

class Main():

    def __init__(self) -> None:
        pass


    def ReadJson(self):

        self._source_path = os.path.dirname(os.path.realpath(__file__))
        
        self._config_folder = os.path.join(self._source_path, 'config')

        config_file = 'config.json'
        arquivo = os.path.join(self._config_folder, config_file)

        with open(arquivo, 'r') as json_file:
            dados = json.load(json_file)

            return dados

    def main(self):

        cd = self.ReadJson()

        car = '15204'
        date = '2023-08-07'

        cc = Consumer(cd.get("host_ip"), cd.get("host_port"), cd.get("user"), cd.get("password"))

        media_records = cc.get_media_records(car, date, cd.get("source_records"), cd.get("stream_type"))

        print(media_records)

if __name__ == '__main__':
    mr = Main()
    mr.main()