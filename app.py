from consumer.consumer import Consumer
from dto.banco import Database
import os
import json

class Main():

    def __init__(self) -> None:
        self._source_path = os.path.dirname(os.path.realpath(__file__))


    def ReadJson(self):
        
        self._config_folder = os.path.join(self._source_path, 'config')

        config_file = 'config.json'
        arquivo = os.path.join(self._config_folder, config_file)

        with open(arquivo, 'r') as json_file:
            dados = json.load(json_file)

            return dados

    def main(self):

        #Carrega arquivo de configuração
        config_data = self.ReadJson()

        #Configura Api Coonsumer
        api_consumer = Consumer(config_data.get("host_ip"), config_data.get("host_port"), 
                        config_data.get("user"), config_data.get("password"))

        #Inicia Database
        db = Database()
        db.adicionar_carro('15204')
        db.adicionar_info_carro(1, '2023-08-08T00:30:01Z', '2023-08-08T00:45:01Z', '1', '-03:00', '/BackupMedia/15204/hist-44D1AB4A721A5FD8-1.mp4', 'NO', '/BackupMedia/15204', '/home/publico/imagens/15204/camera1/2023-08-08')
        
        
        tc = db.carros_processados()
        for carro_info in tc:
            print(carro_info)

        cars = os.listdir(config_data.get("default_directory"))

        for car in cars:
            date = '2023-08-07'
            media_records = api_consumer.get_media_records(car, date, 
                        config_data.get("source_records"), config_data.get("stream_type"))

            # print(media_records)

        db.close_connection()


if __name__ == '__main__':
    mr = Main()
    mr.main()