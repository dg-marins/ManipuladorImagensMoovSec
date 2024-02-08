from itertools import chain
import time
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

        if 0 <= parsed_datetime.hour < 3:
            # Subtrair um dia
            parsed_datetime -= datetime.timedelta(days=1)

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

    def get_videos_found_in_api(self, api_consumer, config_data, car, dates):
        apt_media_records_data = []

        for date in dates:
            apt_media_records_data.append(api_consumer.get_media_records(car, date,
                                                                         config_data.get("source_records"),
                                                                         config_data.get("stream_type")))

        if all(item is None for item in apt_media_records_data):
            return None

        unified_api_media_records_data = list(chain(*apt_media_records_data))

        dict_unified_api_informations = {}
        for record in unified_api_media_records_data:
            if 'fileName' in record:
                file_name = os.path.basename(record['fileName'])
                dict_unified_api_informations[file_name] = record

        return dict_unified_api_informations

    def set_unprocessed_file(self, destination_directory, car_id, source_car_path, start_time, end_time, channel, time_zone, file_name):
        self.db.adicionar_info_carro(car_id, start_time, end_time, channel, time_zone, os.path.basename(file_name),
                                      'NO', 'NO', source_car_path, destination_directory)

    def process_unprocessed_file(self, unprocessed_file_information):
        event_id, car_id, utc_start_time, utc_final_time, channel = unprocessed_file_information[:5]
        date = self.get_date(utc_start_time)
        start_time = self.convert_utc_to_local_and_get_time(utc_start_time, unprocessed_file_information[5])
        final_time = self.convert_utc_to_local_and_get_time(utc_final_time, unprocessed_file_information[5])
        destination_path = unprocessed_file_information[9]
        
        if not os.path.isdir(destination_path):
            os.makedirs(destination_path)

        print(f"Iniciando processo de particionamento file {unprocessed_file_information[6]}")
        new_videos_created = self.fp.cortar_video_por_minuto(os.path.join(unprocessed_file_information[8], unprocessed_file_information[6]),
                                   destination_path, date, start_time, final_time)
        
        for new_video_file_name in new_videos_created:
            self.db.registrar_video(event_id, new_video_file_name)

        self.db.set_processed_to_yes(event_id)

    def process_car_videos(self, api_consumer, config_data, car, vehicle_id, dates):
    
        #Lista os arquivos encontrados no diretorio do carro
        for folder in config_data.get("folders_to_process"):

            if not os.path.isdir(os.path.join(config_data.get("default_directory"), folder, car)):
                continue
            
            source_car_path_files = os.listdir(os.path.join(config_data.get("default_directory"), folder, car))
            if len(source_car_path_files) <= 0:
                (f"[{car}] Não há videos descarregados")
                return

            if folder == "backup":

                #Pega videos encontrador na API com as datas informadas
                dict_unified_api_informations = self.get_videos_found_in_api(api_consumer, config_data, car, dates)
                if dict_unified_api_informations == None:
                    return
                
                #Compara se o arquivo do diretorio encontra-se no registo da API
                for file in source_car_path_files:
                    x = dict_unified_api_informations.get(file)
                    if x:
                        destination_path = os.path.join(config_data.get("destination_directory"), car, "camera" + str(x.get("channel")), self.get_date(x.get("starttime")))

                        print(f"Arquivo {file} do carro {car} registrado no banco")

                        self.set_unprocessed_file(destination_path, self.db.get_car_id_by_name(car), os.path.join(config_data.get("default_directory"), folder, car), x.get("starttime"),
                                                  x.get("endtime"), x.get("channel"), x.get("timezone"), x.get("fileName"))
            
            elif folder == "download":
                download_task_data = api_consumer.get_download_task(vehicle_id, dates[0], dates[-1])

                
                if isinstance(download_task_data, dict):
                    task_list = download_task_data.get("list")
                else:
                    task_list = download_task_data
                
                for file in source_car_path_files:
                    for data in task_list:
                        taskInfo = data.get("taskInfo")

                        if taskInfo.get("status") == "SUCCESS" and data.get("vehiclePlate") == car:
                            
                            media_info = taskInfo.get("media")

                            for x in media_info:
                                if x.get("fileName") and x.get("fileName"):
                                    destination_path = os.path.join(config_data.get("destination_directory"), car, "camera" + str(data.get("channels")[0]), self.get_date(x.get("startTime")))
                                    self.set_unprocessed_file(destination_path, self.db.get_car_id_by_name(car), os.path.join(config_data.get("default_directory"), folder, car), 
                                                        x.get("startTime"), x.get("endTime"), data.get("channels")[0], data.get("timezone"), x.get("fileName"))

    def delete_file(self, file_information):
        event_id = file_information[0]
        file_path = os.path.join(file_information[9], file_information[6])
        
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f'Removido: {file_path}')
            self.db.set_erased_status(event_id)
    
    
    def main(self):
        config_data = self.read_json()
        api_consumer = Consumer(config_data.get("host_ip"), config_data.get("host_moovsec_port"),
                                config_data.get("host_iot_handler_port"), config_data.get("user"), config_data.get("password"))
        self.db = Database()
        self.db.create_database()
        
        self.fp = FileProcesser()

        #Registra os carros dos diretorio no banco
        print(f'Registrando carros no banco ...')
        all_cars = []
        for directory in config_data.get("folders_to_process"):
            itens_in_directory = os.listdir(os.path.join(config_data.get("default_directory"), directory))
            for item in itens_in_directory:
                if not os.path.isdir(os.path.join(config_data.get("default_directory"), directory, item)):
                    itens_in_directory.remove(item)

            all_cars.append(itens_in_directory)
            
        cars_unified = []
        for sublist in all_cars:
            cars_unified.extend(sublist)
        
        cars = list(set(cars_unified))

        api_vehicles_data = api_consumer.get_all_vehicles_information()

        for car in cars:
            for car_information in api_vehicles_data:
                deviceSerial = car_information.get("deviceList")[0].get("deviceSerial")
                if car_information.get("plate") == car or deviceSerial == car:
                    print(f'Carro {car} registrado no banco')
                    self.db.register_car(car, car_information.get("_id"))

        #Registra todos os videos pertencentes aos carros no banco
        dates = [(datetime.datetime.now() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(config_data.get("days_to_process")-1, -1, -1)]
        registered_cars = self.db.get_all_cars()
        for information in registered_cars:
            print(f"Registrando os videos no banco do carro : {information[0]}")
            self.process_car_videos(api_consumer, config_data, information[0], information[1], dates)

        #Inicia processo de particionamento e organização dos vídeos
        unprocessed_files = self.db.get_unprocessed_info()
        for unprocessed_file_information in unprocessed_files:
            self.process_unprocessed_file(unprocessed_file_information)

        # #Inicia processo de limpeza dos vídeos processados
        files_to_delete = self.db.get_files_to_delete(config_data.get("dias_para_manter"))
        for file in files_to_delete:
            self.delete_file(file)

if __name__ == '__main__':

    mr = Main()
    
    while True:
        # try:
        mr.main()
        
        # except Exception as e:
        #     print(f'Erro: {e}')
        #     time.sleep(3)

        #Aguarda 30 minutos ate o proximo loop
        print(f"Aguardando próximo loop")
        time.sleep(1800)