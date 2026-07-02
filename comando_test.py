import serial

ser = serial.Serial(
    "COM4",
    baudrate=115200,
    timeout=1
)

print("Conectado")

while True:

    comando = input("Enviar: ")

    ser.write(comando.encode())

    respuesta = ser.read(512)

    print("RX HEX :", respuesta.hex(" "))

    try:
        print("RX TXT :", respuesta.decode())
    except:
        pass