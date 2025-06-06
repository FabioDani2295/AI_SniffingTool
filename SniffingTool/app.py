import streamlit as st
import pandas as pd
import os
import logging
from macchina import Macchina
import database
import pdf_parser
import tempfile

# Configurazione logging
logging.basicConfig(
    filename='macchine_app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

database.init_db()

st.set_page_config(
    page_title="Analizzatore Manuali Tecnici - Industria 4.0",
    layout="wide"
)

st.title("Analisi Manuali Tecnici per Macchine Industriali")
st.markdown(
    """
    Questa applicazione consente di caricare manuali tecnici di macchine industriali in formato PDF, 
    estrarre informazioni chiave (protocolli, endpoint, tabella variabili) e archiviarle in un database.
    """
)

# --- Sidebar
st.sidebar.header("Menu")
pagina = st.sidebar.radio(
    "Seleziona pagina:",
    ("Carica e Analizza PDF", "Risultati Estratti", "Archivio Macchine")
)

if pagina == "Carica e Analizza PDF":
    st.header("Caricamento manuali PDF")
    pdf_files = st.file_uploader(
        "Caricare uno o più file PDF relativi a una macchina industriale.",
        type=["pdf"],
        accept_multiple_files=True
    )

    nome_macchina = st.text_input(
        "Nome/Identificativo della macchina",
        help="Inserire un nome identificativo univoco per la macchina di riferimento."
    )

    if st.button("Analizza", disabled=not pdf_files or not nome_macchina):
        risultati = []
        for pdf_file in pdf_files:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                    tmp.write(pdf_file.read())
                    tmp_path = tmp.name

                testo_pdf = pdf_parser.estrai_testo_da_pdf(tmp_path)
                extracted = pdf_parser.estrai_informazioni_macchina(testo_pdf, nome_macchina)
                macchina = Macchina.from_extracted_data(nome_macchina, extracted)
                database.salva_macchina(macchina)
                risultati.append(macchina.to_dict())

                os.remove(tmp_path)
                st.success(f"Manuale '{pdf_file.name}' analizzato con successo.")

            except Exception as e:
                logging.error(f"Errore durante l'analisi di {pdf_file.name}: {e}")
                st.error(f"Errore durante l'analisi del file '{pdf_file.name}': {str(e)}")

        if risultati:
            st.session_state['ultimi_risultati'] = risultati

if pagina == "Risultati Estratti":
    st.header("Risultati più recenti")
    risultati = st.session_state.get('ultimi_risultati', [])
    if not risultati:
        st.info("Nessun risultato disponibile. Caricare e analizzare almeno un PDF.")
    else:
        for idx, macchina in enumerate(risultati):
            st.subheader(f"Macchina: {macchina['nome_macchina']}")
            st.markdown(f"**Protocollo di comunicazione:** {macchina['protocollo']}")
            st.markdown(f"**Endpoint:** {macchina['endpoint']}")
            if macchina['variabili']:
                df = pd.DataFrame(macchina['variabili'])
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "Esporta variabili in CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"variabili_{macchina['nome_macchina']}.csv",
                    mime='text/csv'
                )
            else:
                st.warning("Nessuna variabile trovata nel manuale analizzato.")

if pagina == "Archivio Macchine":
    st.header("Archivio macchine analizzate")
    macchine = database.recupera_macchine()
    if not macchine:
        st.info("Nessuna macchina registrata.")
    else:
        for macchina in macchine:
            st.subheader(f"Macchina: {macchina['nome_macchina']}")
            st.markdown(f"**Protocollo:** {macchina['protocollo']}")
            st.markdown(f"**Endpoint:** {macchina['endpoint']}")
            if macchina['variabili']:
                df = pd.DataFrame(macchina['variabili'])
                st.dataframe(df, use_container_width=True)
                st.download_button(
                    "Esporta variabili in CSV",
                    data=df.to_csv(index=False).encode('utf-8'),
                    file_name=f"variabili_{macchina['nome_macchina']}.csv",
                    mime='text/csv'
                )
            else:
                st.warning("Nessuna variabile disponibile per questa macchina.")
