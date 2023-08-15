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
        
    def main(self):

        #Carrega arquivo de configuração
        config_data = self.read_json()

        #Configura Api Coonsumer
        api_consumer = Consumer(config_data.get("host_ip"), config_data.get("host_port"), 
                        config_data.get("user"), config_data.get("password"))

        #Inicia Database
        db = Database()

        #Inicial Processador arquivos
        fp = FileProcesser()
        
        cars = os.listdir(config_data.get("default_directory"))

        #Gera uma lista com as datas dos ultimos 7 dias
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(6, -1, -1)]

        #Cadastra todos os carros e arquivos de vídeos no banco da aplicação
        for car in cars:

            db.adicionar_carro(car)
            car_id = db.get_car_id_by_name(car)

            source_car_path = os.path.join(config_data.get("default_directory"), car)
            source_car_path_files = os.listdir(source_car_path)
            
            apt_media_records_data = []
            
            for date in dates:
                apt_media_records_data.append(api_consumer.get_media_records(car, date, 
                            config_data.get("source_records"), config_data.get("stream_type")))
            
            self.unified_api_media_records_data = list(chain(*apt_media_records_data))

            if len(self.unified_api_media_records_data) <= 0:
                continue

            for file in source_car_path_files:
                for info in self.unified_api_media_records_data:
                    file_name = os.path.basename(info['fileName'])
                    if file == file_name:
                        db.adicionar_info_carro(car_id, info['starttime'], info['endtime'], info['channel'], 
                                                info['timezone'], file_name, 'NO', source_car_path, config_data.get('destination_directory'))
        
        #Inicia processamento dos vídeos
        #Processar todos arquivos que não foram processados ainda
        unprocessed_files = db.get_unprocessed_info()

        for unprocessed_file_information in unprocessed_files:

            inicial_file_name = unprocessed_file_information[6]
            event_id = unprocessed_file_information[0]
            car = db.get_car_name_by_id(unprocessed_file_information[1])
            date = self.get_date(unprocessed_file_information[2])
            start_time = self.convert_utc_to_local_and_get_time(unprocessed_file_information[2], unprocessed_file_information[5])
            final_time = self.convert_utc_to_local_and_get_time(unprocessed_file_information[3], unprocessed_file_information[5])
            camera = 'camera' + unprocessed_file_information[4]
            
            #Criar diretório final
            destination_path = fp.cria_diretorio(unprocessed_file_information[9], car, camera, date)

            fp.cortar_video_por_minuto(unprocessed_file_information[8], destination_path, date, start_time, final_time)
            
            #Passar para processado
            db.set_processed_to_yes(event_id)


if __name__ == '__main__':
    mr = Main()
    mr.main()