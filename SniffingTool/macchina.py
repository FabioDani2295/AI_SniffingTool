import json

class Macchina:
    def __init__(self, nome_macchina, protocollo, endpoint, variabili=None):
        self.nome_macchina = nome_macchina
        self.protocollo = protocollo
        self.endpoint = endpoint
        self.variabili = variabili if variabili else []

    def aggiungi_variabile(self, nome, indirizzo, tipo_dato, accesso, descrizione):
        var = {
            'nome': nome,
            'indirizzo': indirizzo,
            'tipo_dato': tipo_dato,
            'accesso': accesso,
            'descrizione': descrizione
        }
        self.variabili.append(var)

    def to_dict(self):
        return {
            'nome_macchina': self.nome_macchina,
            'protocollo': self.protocollo,
            'endpoint': self.endpoint,
            'variabili': self.variabili
        }

    @staticmethod
    def from_extracted_data(nome_macchina, extracted_data):
        """
        Crea un'istanza della classe a partire da un dizionario strutturato secondo lo standard estratto dall'LLM.
        """
        protocollo = extracted_data.get('protocollo', '')
        endpoint = extracted_data.get('endpoint', '')
        variabili = extracted_data.get('variabili', [])
        return Macchina(nome_macchina, protocollo, endpoint, variabili)
