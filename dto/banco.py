import sqlite3
import os

class Database():
    # Conectar-se ao banco de dados (ou criar um novo se não existir)

    def __init__(self) -> None:

        self.databse_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carros.db")
        self.conn = sqlite3.connect(self.databse_path)

    
    def create_database(self):

        # Criar a tabela de carros
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cars (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    car TEXT UNIQUE
                )
            ''')

            # Criar a tabela de informações dos carros
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS info_carros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    carro_id INTEGER,
                    starttime TEXT,
                    finaltime TEXT,
                    channel TEXT,
                    timezone TEXT,
                    filename TEXT UNIQUE,
                    processed TEXT,
                    erased TEXT,
                    inicialpath TEXT,
                    finalpath TEXT,
                    FOREIGN KEY (carro_id) REFERENCES carros (id)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS videos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    info_carro_id INTEGER,
                    filename TEXT UNIQUE,
                    FOREIGN KEY (info_carro_id) REFERENCES info_carros (id)
                )
            ''')

    # Função para adicionar um carro à tabela 'carros'
    def register_car(self, car):
        
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO cars (car)
                    VALUES (?)
                ''', (car,))
                self.conn.commit()
            except sqlite3.IntegrityError:
                return

    # Função para adicionar informações de um carro à tabela 'info_carros'
    def adicionar_info_carro(self, car_id, starttime, finaltime, channel, timezone, filename, processed, erased, inicialpath, finalpath):
        with self.conn:
            cursor = self.conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO info_carros (carro_id, starttime, finaltime, channel, timezone, filename, processed, erased, inicialpath, finalpath)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (car_id, starttime, finaltime, channel, timezone, filename, processed, erased, inicialpath, finalpath))
                self.conn.commit()
            except sqlite3.IntegrityError:
                pass
    
    def registrar_video(self, info_carro_id, filename):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO videos (info_carro_id, filename) VALUES (?, ?)
            ''', (info_carro_id, filename))

    def carros_processados(self, processed = 'NO'):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f'''
            SELECT ic.carro_id, c.car, ic.starttime, ic.finaltime, ic.channel, ic.timezone, ic.filename, ic.processed, ic.inicialpath, ic.finalpath
            FROM cars c
            JOIN info_carros ic ON c.id = ic.carro_id
            WHERE ic.processed = '{processed}'
        ''')
            return cursor.fetchall()

    def get_car_id_by_name(self, car):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM cars WHERE car = ?', (car,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
    
    def get_car_name_by_id(self, car_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT car FROM cars WHERE id = ?', (car_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None
        
    def get_all_cars(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT car FROM cars')
            result = cursor.fetchall()
            return [row[0] for row in result]

    def get_unprocessed_info(self):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT id, carro_id, starttime, finaltime, channel, timezone, filename, processed, inicialpath, finalpath
                FROM info_carros
                WHERE processed = 'NO'
            ''')
            result = cursor.fetchall()
            return result
    
    def set_processed_to_yes(self, info_id):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE info_carros
                SET processed = 'YES'
                WHERE id = ?
            ''', (info_id,))
            self.conn.commit()

    def set_erased_status(self, info_id):
        with self.conn:
            cursor = self.conn.cursor()
            # Atualizar o status 'erased' para 'YES' com base no info_id
            cursor.execute('''
                UPDATE info_carros
                SET erased = 'YES'
                WHERE id = ?
            ''', (info_id,))
            self.conn.commit()

    def get_files_to_delete(self, days_to_keep):
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                SELECT id, carro_id, starttime, finaltime, channel, timezone, filename, processed, erased, inicialpath, finalpath
                FROM info_carros
                WHERE processed = 'YES' AND erased = 'NO' AND datetime(starttime) < datetime('now', '-{days_to_keep} days')
            ''')
            result = cursor.fetchall()
            return result
        
    def close_connection(self):
        self.conn.close()