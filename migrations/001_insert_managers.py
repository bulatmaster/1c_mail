import sqlite3 
import os 
from datetime import datetime as dt

os.system(f'cp data/database.db backups/{dt.now()}.db.bak')

conn = sqlite3.connect('data/database.db')


with conn:
    conn.execute(
        'INSERT INTO tg_users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
        (1275619497, 'VRV', None, None)
    )
    conn.execute(
        'INSERT INTO tg_users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
        (1962795144, 'Наташа', None, None)
    )
    conn.execute(
        'INSERT INTO tg_users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
        (2091459400, 'Альбина', None, 'Albinos78')
    )
    conn.execute(
        'INSERT INTO tg_users (user_id, first_name, last_name, username) VALUES (?, ?, ?, ?)',
        (5636186161, 'Ирина', None, 'mivv761')
    )
