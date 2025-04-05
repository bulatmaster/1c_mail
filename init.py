import sqlite3 
import os 
import config 


if os.path.exists(config.db_path):
    os.makedirs('backups', exist_ok=True)
    os.system(f'cp {config.db_path} backups/')
    print('Бэкап сделан')
    os.remove(config.db_path)

os.makedirs('data', exist_ok=True)

with sqlite3.connect(config.db_path) as conn:
    with open('schema.sql') as f:
        conn.executescript(f.read())
    
print('ok')