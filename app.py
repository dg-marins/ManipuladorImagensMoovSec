from itertools import chain
from consumer.consumer import Consumer
from dto.banco import Database
from utils.fileProcesser import FileProcesser
import os
import json
import datetime

class Main():

    def __init__(self) -> None:
        self._source_path = os.path.dirname(os.path.realpath(__file__))


    def read_json(self):
        
        self._config_folder = os.path.join(self._source_path, 'config')

        config_file = 'config.json'
        arquivo = os.path.join(self._config_folder, config_file)

        with open(arquivo, 'r') as json_file:
            dados = json.load(json_file)

            return dados

    def get_date(self, source_date):

        # Converter a string para um objeto datetime
        parsed_datetime = datetime.datetime.strptime(source_date, '%Y-%m-%dT%H:%M:%SZ')

        # Retorna a data formatada como 'yyyy-mm-dd'
        return parsed_datetime.strftime('%Y-%m-%d')

    def convert_utc_to_local_and_get_time(self, utc_time, time_zone):
        utc_datetime = datetime.datetime.strptime(utc_time, '%Y-%m-%dT%H:%M:%SZ')
        
        # Extrair o sinal (+ ou -) e o valor do fuso horário
        tz_sign = time_zone[0]
        tz_hours = int(time_zone[1:3])
        tz_minutes = int(time_zone[4:6])
        
        if tz_sign == '+':
            local_datetime = utc_datetime + datetime.timedelta(hours=tz_hours, minutes=tz_minutes)
        elif tz_sign == '-':
            local_datetime = utc_datetime - datetime.timedelta(hours=tz_hours, minutes=tz_minutes)
        else:
            raise ValueError("Fuso horário inválido")

        time_string = local_datetime.strftime('%H:%M:%S')
        return time_string

    def register_car_and_get_files_info(self, api_consumer, config_data, car, dates):
        self.db.adicionar_carro(car)
        
        apt_media_records_data = []

        for date in dates:
            apt_media_records_data.append(api_consumer.get_media_records(car, date,
                                                                         config_data.get("source_records"),
                                                                         config_data.get("stream_type")))
        unified_api_media_records_data = list(chain(*apt_media_records_data))

        return {os.path.basename(record['fileName']): record for record in unified_api_media_records_data}
                
    def process_file(self, destination_directory, car_id, source_car_path, file_info):
        self.db.adicionar_info_carro(car_id, file_info['starttime'], file_info['endtime'], file_info['channel'],
                                file_info['timezone'], os.path.basename(file_info['fileName']), 'NO', source_car_path,
                                destination_directory)

    def process_unprocessed_file(self, unprocessed_file_information):
        event_id, car_id, utc_start_time, utc_final_time, channel = unprocessed_file_information[:5]
        car = self.db.get_car_name_by_id(car_id)
        date = self.get_date(utc_start_time)
        start_time = self.convert_utc_to_local_and_get_time(utc_start_time, unprocessed_file_information[5])
        final_time = self.convert_utc_to_local_and_get_time(utc_final_time, unprocessed_file_information[5])
        camera = 'camera' + channel
        destination_path = self.fp.cria_diretorio(unprocessed_file_information[9], car, camera, date)
        self.fp.cortar_video_por_minuto(os.path.join(unprocessed_file_information[8], unprocessed_file_information[6]),
                                   destination_path, date, start_time, final_time)
        self.db.set_processed_to_yes(event_id)

    def main(self):
        config_data = self.read_json()
        api_consumer = Consumer(config_data.get("host_ip"), config_data.get("host_port"),
                                config_data.get("user"), config_data.get("password"))
        self.db = Database()
        self.fp = FileProcesser()
        cars = os.listdir(config_data.get("default_directory"))
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

        for car in cars:
            dict_unified_api_informations = self.register_car_and_get_files_info(api_consumer, config_data, car, dates)
            source_car_path_files = os.listdir(os.path.join(config_data.get("default_directory"), car))

            for file in source_car_path_files:
                x = dict_unified_api_informations.get(file)
                if x:
                    self.process_file(config_data.get("destination_directory"), self.db.get_car_id_by_name(car), os.path.join(config_data.get("default_directory"), car), x)
                else:
                    print("Arquivo nao localizado na API")

        unprocessed_files = self.db.get_unprocessed_info()
        for unprocessed_file_information in unprocessed_files:
            self.process_unprocessed_file(unprocessed_file_information)

if __name__ == '__main__':
    mr = Main()
    mr.main()