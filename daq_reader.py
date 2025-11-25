import threading
import numpy as np
import pandas as pd
from PySide6 import QtCore

class DAQReader(QtCore.QThread):
    data_ready = QtCore.Signal(dict)

    def __init__(self, usb_port="COM3", fs=2000, block_size=200):
        super().__init__()
        self.usb_port = usb_port
        self.fs = fs
        self.block_size = block_size
        self.running = False
        self.saved_data = []

        # Diccionario de canales
        self.channels = ['Va','Vb','Vc','Ia','Ib','Ic','speed','torque']

    def open_usb(self):
        """
        Método genérico para abrir el puerto USB o API del DAQ.
        Aquí hay que agregar la inicialización específica según tu modelo.
        """
        print(f"Abriendo DAQ USB en {self.usb_port}...")
        # self.daq = DAQLibrary(self.usb_port)
        # self.daq.configure_channels(self.channels)
        # self.daq.start_acquisition()
        self.connected = True

    def close_usb(self):
        """
        Cierra la conexión con el DAQ
        """
        print("Cerrando DAQ USB...")
        # self.daq.stop()
        self.connected = False

    def read_block(self):
        """
        Lee un bloque de datos del DAQ.
        Devuelve un diccionario con arrays de tamaño block_size.
        """
        # EJEMPLO CON DATOS SIMULADOS (para probar sin DAQ)
        t = np.linspace(0, self.block_size/self.fs, self.block_size)
        w = 2*np.pi*50
        Va = 220*np.sqrt(2)*np.sin(w*t)
        Vb = 220*np.sqrt(2)*np.sin(w*t - 2*np.pi/3)
        Vc = 220*np.sqrt(2)*np.sin(w*t + 2*np.pi/3)
        Ia = 5*np.sqrt(2)*np.sin(w*t - np.pi/6)
        Ib = 5*np.sqrt(2)*np.sin(w*t - 2*np.pi/3 - np.pi/6)
        Ic = 5*np.sqrt(2)*np.sin(w*t + 2*np.pi/3 - np.pi/6)
        speed = 1500 + 50*np.sin(w*t)
        torque = 10 + 2*np.sin(w*t - np.pi/4)

        return {
            "t": t,
            "Va": Va, "Vb": Vb, "Vc": Vc,
            "Ia": Ia, "Ib": Ib, "Ic": Ic,
            "speed": speed, "torque": torque
        }

    def run(self):
        self.open_usb()
        self.running = True
        while self.running:
            data = self.read_block()
            self.saved_data.append(data)
            self.data_ready.emit(data)
            self.msleep(int(1000*self.block_size/self.fs))
        self.close_usb()

    def stop(self):
        self.running = False
        self.wait()

    def save_to_csv(self, filename="mediciones_labvolt_usb.csv"):
        if not self.saved_data:
            return
        df_list = []
        for entry in self.saved_data:
            temp_df = pd.DataFrame(entry)
            df_list.append(temp_df)
        df = pd.concat(df_list, ignore_index=True)
        df.to_csv(filename, index=False)
        print(f"Datos guardados en {filename}")
