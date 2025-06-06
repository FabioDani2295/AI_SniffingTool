import sqlite3
import logging
import json

DB_FILE = "macchine.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS macchine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_macchina TEXT NOT NULL,
            protocollo TEXT,
            endpoint TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS variabili (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            macchina_id INTEGER,
            nome TEXT,
            indirizzo TEXT,
            tipo_dato TEXT,
            accesso TEXT,
            descrizione TEXT,
            FOREIGN KEY(macchina_id) REFERENCES macchine(id) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

def salva_macchina(macchina):
    """
    Salva un'istanza di Macchina e le sue variabili nel database.
    Restituisce l'id della macchina inserita.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO macchine (nome_macchina, protocollo, endpoint)
        VALUES (?, ?, ?)
    ''', (macchina.nome_macchina, macchina.protocollo, macchina.endpoint))
    macchina_id = c.lastrowid

    for var in macchina.variabili:
        c.execute('''
            INSERT INTO variabili (macchina_id, nome, indirizzo, tipo_dato, accesso, descrizione)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (macchina_id, var['nome'], var['indirizzo'], var['tipo_dato'], var['accesso'], var['descrizione']))
    conn.commit()
    conn.close()
    return macchina_id

def recupera_macchine():
    """
    Recupera tutte le macchine e le relative variabili dal database.
    Restituisce una lista di dizionari.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT * FROM macchine')
    macchine_rows = c.fetchall()
    macchine = []
    for row in macchine_rows:
        macchina_id = row[0]
        c.execute('SELECT nome, indirizzo, tipo_dato, accesso, descrizione FROM variabili WHERE macchina_id=?', (macchina_id,))
        variabili = [
            {
                'nome': v[0],
                'indirizzo': v[1],
                'tipo_dato': v[2],
                'accesso': v[3],
                'descrizione': v[4]
            }
            for v in c.fetchall()
        ]
        macchine.append({
            'id': macchina_id,
            'nome_macchina': row[1],
            'protocollo': row[2],
            'endpoint': row[3],
            'variabili': variabili
        })
    conn.close()
    return macchine

def recupera_macchina(macchina_id):
    """
    Recupera una singola macchina per id.
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT nome_macchina, protocollo, endpoint FROM macchine WHERE id=?', (macchina_id,))
    macchina_row = c.fetchone()
    if macchina_row:
        c.execute('SELECT nome, indirizzo, tipo_dato, accesso, descrizione FROM variabili WHERE macchina_id=?', (macchina_id,))
        variabili = [
            {
                'nome': v[0],
                'indirizzo': v[1],
                'tipo_dato': v[2],
                'accesso': v[3],
                'descrizione': v[4]
            }
            for v in c.fetchall()
        ]
        macchina = {
            'nome_macchina': macchina_row[0],
            'protocollo': macchina_row[1],
            'endpoint': macchina_row[2],
            'variabili': variabili
        }
        conn.close()
        return macchina
    conn.close()
    return None
