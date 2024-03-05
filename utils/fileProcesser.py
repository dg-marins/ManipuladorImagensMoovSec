import os
import shutil
import datetime
import subprocess
from os.path import join
# from moviepy.editor import VideoFileClip
# from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

class FileProcesser():

    def __init__(self):
        pass

    def calculate_time_difference(self, start_time_str, end_time_str):
        start_time = datetime.datetime.strptime(start_time_str, '%H:%M:%S')
        end_time = datetime.datetime.strptime(end_time_str, '%H:%M:%S')
        
        time_difference = end_time - start_time
        
        total_seconds = time_difference.total_seconds()
        total_minutes = int(total_seconds // 60)
        remaining_seconds = int(total_seconds % 60)
        
        return total_minutes, remaining_seconds


    def cortar_video_por_minuto(self, full_file_path, destination_path, date, start_time, final_time):
        
        video_duration_minutes, video_duration_seconds = self.calculate_time_difference(start_time, final_time)

        FMT = "%Y-%m-%d %H:%M:%S"
    
        # Hora Inicial do Arquivo
        time = datetime.datetime.strptime(date + ' ' + start_time, FMT)
        formatted_time = time.strftime("%Y%m%d%H%M%S")  # Formata para "%Y%m%d%H%M%S"
    

        lista_novos_arquivos = []

        for x in range(video_duration_minutes):
        
            t1 = x * 60
            t2 = t1 + 60

            target_file_formatted_time = formatted_time  # Salva o nome formatado atual

            target_file = os.path.join(destination_path, target_file_formatted_time + '.mp4')

            if os.path.isfile(target_file):
                print(f'Arquivo existe: {target_file}')
                 # Adiciona 1 minuto ao nome do arquivo
                time = time + datetime.timedelta(minutes=1)
                formatted_time = time.strftime("%Y%m%d%H%M%S")
                continue

            tempo_inicio_convertido = datetime.timedelta(seconds = t1)
            tempo_inicio_formatado = datetime.datetime.strptime(str(tempo_inicio_convertido), "%H:%M:%S").time()

            tempo_fim_convertido = datetime.timedelta(seconds = t2)
            tempo_fim_formatado = datetime.datetime.strptime(str(tempo_fim_convertido), "%H:%M:%S").time()

            cmnd = ['ffmpeg', '-i', full_file_path, '-b:v', '64k', '-bufsize', '64k', '-ss', str(tempo_inicio_formatado), '-to', str(tempo_fim_formatado), '-c', 'copy', target_file]
            p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err =  p.communicate()

            print(f"Fragmento criado: {target_file}")
            lista_novos_arquivos.append(target_file)
            
            # Adiciona 1 minuto ao nome do arquivo
            time = time + datetime.timedelta(minutes=1)
            formatted_time = time.strftime("%Y%m%d%H%M%S")
        
        if video_duration_seconds > 0:

            t1 = t1 + 60
            t2 = t1 + video_duration_seconds
            target_file_formatted_time = formatted_time  # Salva o nome formatado atual

            target_file = os.path.join(destination_path, target_file_formatted_time + '.mp4')

            if os.path.isfile(target_file):
                print(f'Existe: {target_file}')
                return lista_novos_arquivos

            tempo_inicio_convertido = datetime.timedelta(seconds = t1)
            tempo_inicio_formatado = datetime.datetime.strptime(str(tempo_inicio_convertido), "%H:%M:%S").time()

            tempo_fim_convertido = datetime.timedelta(seconds = t2)
            tempo_fim_formatado = datetime.datetime.strptime(str(tempo_fim_convertido), "%H:%M:%S").time()

            cmnd = ['ffmpeg', '-i', full_file_path, '-b:v', '64k', '-bufsize', '64k', '-ss', str(tempo_inicio_formatado), '-to', str(tempo_fim_formatado), '-c', 'copy', target_file]
            p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err =  p.communicate()

            lista_novos_arquivos.append(target_file)
            
            # Adiciona 1 minuto ao nome do arquivo
            time = time + datetime.timedelta(minutes=1)
            formatted_time = time.strftime("%Y%m%d%H%M%S")

        print(f'{os.path.basename(full_file_path)} particionado')
        return lista_novos_arquivos