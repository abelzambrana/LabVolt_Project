import serial
import serial.tools.list_ports
import threading
import time


def listar_puertos():
    puertos = serial.tools.list_ports.comports()

    if not puertos:
        print("No se encontraron puertos COM.")
        return []

    print("Puertos encontrados:\n")

    for i, p in enumerate(puertos):
        print(f"{i} -> {p.device}    {p.description}")

    return puertos


puertos = listar_puertos()

indice = int(input("\nSeleccione puerto: "))

puerto = puertos[indice].device


baud = int(input("Baudrate (ej. 115200): "))


ser = serial.Serial(
    puerto,
    baudrate=baud,
    bytesize=8,
    parity='N',
    stopbits=1,
    timeout=0.1
)

print("\nEscuchando...\n")


while True:

    datos = ser.read(256)

    if len(datos):

        hex_data = " ".join(f"{b:02X}" for b in datos)

        ascii_data = "".join(chr(b) if 32 <= b <= 126 else "." for b in datos)

        print("---------------------------------------")
        print("HEX  : ", hex_data)
        print("ASCII: ", ascii_data)