import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ManipuladorDeEventos(FileSystemEventHandler):
    # TODO adicionar lista

    def __init__(self, conversor, send_data,  diretorio='.'):
        self._conversor = conversor
        self._send_data = send_data

        observador = Observer()
        observador.schedule(self, diretorio, recursive=False)
        observador.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observador.unschedule(self)
            observador.stop()
        observador.join()


    def catch_all_handler(self, event):
            pass

    def on_created(self, event):
        print("CREATED " + str(event))
        # print(event.src_path)

        data = self._conversor.conversor(event.src_path)

        self._send_data.send_to_api(data=data)

        self.catch_all_handler(event)

