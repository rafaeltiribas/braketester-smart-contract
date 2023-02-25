from eventHandler import ManipuladorDeEventos
from converterData import ConverterData
from senderAPI import Sender

def main():
    converter = ConverterData()
    send_data = Sender()

    eventos = ManipuladorDeEventos(converter, send_data, "ExemplosTeste")
    # insert = InsertBlockchain()


if __name__ == "__main__":
    main()

