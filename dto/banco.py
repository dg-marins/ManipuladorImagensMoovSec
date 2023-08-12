import sqlite3
import os

class Database():
    # Conectar-se ao banco de dados (ou criar um novo se não existir)

    def __init__(self) -> None:

        source_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "carros.db")
        self.conn = sqlite3.connect(source_path)
        self.cursor = self.conn.cursor()

        # Criar a tabela de carros
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                car TEXT UNIQUE
            )
        ''')

        # Criar a tabela de informações dos carros
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS info_carros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                carro_id INTEGER,
                starttime TEXT,
                finaltime TEXT,
                channel TEXT,
                timezone TEXT,
                filename TEXT UNIQUE,
                processed TEXT,
                inicialpath TEXT,
                finalpath TEXT,
                FOREIGN KEY (carro_id) REFERENCES carros (id)
            )
        ''')

    # Função para adicionar um carro à tabela 'carros'
    def adicionar_carro(self, car):
        try:
            self.cursor.execute('''
                INSERT INTO cars (car)
                VALUES (?)
            ''', (car,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            print(f"Carro {car} informado ja cadastrador.")

    # Função para adicionar informações de um carro à tabela 'info_carros'
    def adicionar_info_carro(self, carro_id, starttime, finaltime, channel, timezone, filename, processed, inicialpath, finalpath):
        try:
            self.cursor.execute('''
                INSERT INTO info_carros (carro_id, starttime, finaltime, channel, timezone, filename, processed, inicialpath, finalpath)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (carro_id, starttime, finaltime, channel, timezone, filename, processed, inicialpath, finalpath))
            self.conn.commit()
        except sqlite3.IntegrityError:
            x = self.get_car_name_by_id(1)
            print(f"Dados informados do carro {x} ja existem no banco.")

    # Consulta para buscar carros processados com suas informações
    def carros_processados(self, processed = 'NO'):
        self.cursor.execute(f'''
            SELECT ic.carro_id, c.car, ic.starttime, ic.finaltime, ic.channel, ic.timezone, ic.filename, ic.processed, ic.inicialpath, ic.finalpath
            FROM cars c
            JOIN info_carros ic ON c.id = ic.carro_id
            WHERE ic.processed = '{processed}'
        ''')
        return self.cursor.fetchall()

    def get_car_id_by_name(self, car):
        self.cursor.execute('SELECT id FROM cars WHERE car = ?', (car,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
    
    def get_car_name_by_id(self, car_id):
        self.cursor.execute('SELECT car FROM cars WHERE id = ?', (car_id,))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def get_all_cars(self):
        self.cursor.execute('SELECT car FROM cars')
        result = self.cursor.fetchall()
        return [row[0] for row in result]

    def get_unprocessed_info(self):
        self.cursor.execute('''
            SELECT id, carro_id, starttime, finaltime, channel, timezone, filename, processed, inicialpath, finalpath
            FROM info_carros
            WHERE processed = 'NO'
        ''')
        result = self.cursor.fetchall()
        return result
    
    def set_processed_to_yes(self, info_id):
        self.cursor.execute('''
            UPDATE info_carros
            SET processed = 'YES'
            WHERE id = ?
        ''', (info_id,))
        self.conn.commit()
        
    def close_connection(self):
        self.conn.close()