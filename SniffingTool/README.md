# Analizzatore Manuali Tecnici - Industria 4.0

Questa applicazione consente di caricare manuali tecnici in PDF relativi a macchine industriali, estrarre automaticamente dati chiave (protocollo, endpoint, variabili) tramite Google Gemini AI, e archiviarli in un database locale.

## Funzionalità principali

- **Caricamento multiplo PDF**: Carica più manuali contemporaneamente.
- **Estrazione automatica**: Utilizza l'intelligenza artificiale Google Gemini-1.5-Flash per estrarre protocollo, endpoint e variabili.
- **Archiviazione e ricerca**: Dati strutturati e salvati in SQLite, facilmente consultabili.
- **Esportazione**: Tabella variabili esportabile in CSV.
- **Gestione errori e logging**: Interfaccia robusta e tracciamento degli errori in file di log.

## Requisiti

- Python 3.8 o superiore
- Una chiave API Google AI (`GOOGLE_AI_API_KEY`)
- Le seguenti librerie Python (installabili da requirements.txt):
    - streamlit
    - PyPDF2
    - pdfplumber
    - google-generativeai
    - pandas

## Installazione

1. **Clonare il repository o copiare i file in una cartella di progetto.**

2. **Installare le dipendenze:**
   ```bash
   pip install -r requirements.txt
