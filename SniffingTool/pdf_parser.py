import os
import logging
import pdfplumber
import google.generativeai as genai

GOOGLE_AI_API_KEY = os.getenv('GOOGLE_AI_API_KEY')

def estrai_testo_da_pdf(pdf_file):
    """
    Estrae il testo da un file PDF.
    """
    try:
        testo = ""
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                testo += page.extract_text() or ""
        if not testo.strip():
            raise ValueError("Testo non rilevato: il PDF potrebbe essere scansionato o non testuale.")
        return testo
    except Exception as e:
        logging.error(f"Errore nell'estrazione del testo dal PDF: {e}")
        raise e

def chiama_gemini(prompt):
    """
    Invoca il modello Google Gemini-1.5-Flash con il prompt fornito.
    """
    if not GOOGLE_AI_API_KEY:
        raise EnvironmentError("Chiave API Google AI non trovata. Configurare la variabile d'ambiente GOOGLE_AI_API_KEY.")
    try:
        genai.configure(api_key=GOOGLE_AI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logging.error(f"Errore nella chiamata al modello Gemini: {e}")
        raise e

import math

def estrai_informazioni_macchina(testo, nome_macchina=None, chunk_size=12000):
    """
    Suddivide il testo in chunk e invia più richieste all'LLM, aggregando i risultati.
    Restituisce un dizionario strutturato unico, con dati aggregati.
    """
    # Suddividere il testo in blocchi di chunk_size caratteri
    chunks = [testo[i:i+chunk_size] for i in range(0, len(testo), chunk_size)]
    logging.info(f"Manuale suddiviso in {len(chunks)} blocchi da {chunk_size} caratteri.")
    risultati = []

    for idx, chunk in enumerate(chunks):
        prompt = genera_prompt_gemini(chunk, nome_macchina)
        try:
            risposta = chiama_gemini(prompt)
            # Cerca il primo blocco JSON valido nella risposta
            import re, json
            match = re.search(r'\{[\s\S]*?\}', risposta)
            if match:
                dati = json.loads(match.group(0))
                risultati.append(dati)
        except Exception as e:
            logging.error(f"Errore nella chiamata all'LLM per il chunk {idx+1}: {e}")

    # Unire i risultati: il protocollo e l'endpoint più frequenti (se diversi), tutte le variabili aggregate e senza duplicati
    protocollo = None
    endpoint = None
    variabili = []
    protocolli = []
    endpoints = []

    for res in risultati:
        if res.get('protocollo'):
            protocolli.append(res.get('protocollo'))
        if res.get('endpoint'):
            endpoints.append(res.get('endpoint'))
        if res.get('variabili'):
            for v in res.get('variabili', []):
                # Per evitare duplicati, si usa una chiave su nome+indirizzo
                if v not in variabili:
                    variabili.append(v)

    # Scelta del protocollo/endpoint più frequente oppure il primo trovato
    from collections import Counter
    if protocolli:
        protocollo = Counter([p for p in protocolli if p]).most_common(1)[0][0]
    if endpoints:
        endpoint = Counter([e for e in endpoints if e]).most_common(1)[0][0]

    return {
        "protocollo": protocollo if protocollo else "",
        "endpoint": endpoint if endpoint else "",
        "variabili": variabili
    }


def genera_prompt_gemini(testo, nome_macchina=None):
    """
    Genera il prompt ottimizzato per l'estrazione delle informazioni dai manuali tecnici.
    """
    nome = nome_macchina if nome_macchina else "<NOME_MACCHINA>"
    prompt = f"""
Il seguente testo è parte di un manuale tecnico di una macchina industriale denominata "{nome}". 
Estrarre in modo strutturato le seguenti informazioni, anche se presenti in sezioni diverse o con formati variabili:
- Protocollo di comunicazione (es. Modbus, OPC UA, Euromap, etc.)
- Endpoint di connessione (es. IP e porta, parametri seriali, indirizzo del server, etc.)
- Tabella delle variabili di comunicazione: per ogni variabile estrarre:
    - nome (es. "Pressione di iniezione")
    - indirizzo o identificativo (es. "Registro 40010", "NodeID 102", ecc.)
    - tipo di dato (es. Integer, Float, Boolean, etc.)
    - accesso (lettura/scrittura, sola lettura, etc.)
    - descrizione (unità di misura, intervallo valori, dettagli aggiuntivi)

Restituire ESCLUSIVAMENTE un oggetto JSON nel formato seguente:

{{
    "protocollo": "...",
    "endpoint": "...",
    "variabili": [
        {{
            "nome": "...",
            "indirizzo": "...",
            "tipo_dato": "...",
            "accesso": "...",
            "descrizione": "..."
        }},
        ...
    ]
}}

Testo da analizzare:
<<<
{testo[:12000]}
>>>
Se i dati richiesti non sono presenti, restituire una stringa vuota ("") per il campo mancante o una lista vuota per le variabili.
"""
    return prompt
