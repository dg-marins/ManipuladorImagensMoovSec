from itertools import chain
from consumer.consumer import Consumer
from dto.banco import Database
import os
import json
import datetime

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
        # db.adicionar_info_carro(1, '2023-08-08T00:30:01Z', '2023-08-08T00:45:01Z', '1', '-03:00', 'hist-33D8AF9D8702BF88-1.mp4', 'NO', '/BackupMedia/15204', '/home/publico/imagens/15204/camera1/2023-08-08')
        
        cars = os.listdir(config_data.get("default_directory"))

        #Gera uma lista com as datas dos ultimos 4 dias
        dates = []
        for i in range(10, -1, -1):
            date = (datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)


        for car in cars:

            db.adicionar_carro(car)
            car_id = db.get_car_id_by_name(car)

            source_car_path = os.path.join(config_data.get("default_directory"), car)
            car_files = os.listdir(source_car_path)
            
            api_media_records = []
            
            for date in dates:
                api_media_records.append(api_consumer.get_media_records(car, date, 
                            config_data.get("source_records"), config_data.get("stream_type")))
            
            unified_api_media_records = list(chain(*api_media_records))

            for file in car_files:
                for info in unified_api_media_records:
                    file_name = os.path.basename(info['fileName'])
                    if file == file_name:
                        db.adicionar_info_carro(car_id, info['starttime'], info['endtime'], info['channel'], 
                                                info['timezone'], file_name, 'NO', os.path.dirname(info['fileName']), config_data.get('destination_directory'))
        db.close_connection()


if __name__ == '__main__':
    mr = Main()
    mr.main()