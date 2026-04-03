import socket
from time import sleep

UDP_IP = "4.3.2.1"  # your WLED IP 4.3.2.1 for AP mode. Change if added to Wifi network
UDP_PORT = 65506 #Defult port
LED_COUNT = 60 #number of LEDs
led_data = [0] * (LED_COUNT * 3) #Led data array

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# ---------- TPM2 SEND ----------
def send_tpm2(data, packet_num=1, total_packets=1):
    length = len(data)
    packet = bytearray()

    packet += b'\x9C\xDA'
    packet += length.to_bytes(2, 'big')
    packet += bytes([packet_num])
    packet += bytes([total_packets])
    packet += data
    packet += b'\x36'

    sock.sendto(packet, (UDP_IP, UDP_PORT))

# ---------- LED CONTROL ----------
def set_led(index, r, g, b):
    i = index * 3
    if i + 2 >= len(led_data):
        return

    led_data[i] = r
    led_data[i+1] = g
    led_data[i+2] = b

# Example: All LEDs turn on Red, Green, Blue then off (RGB)
for i in range(LED_COUNT):
    set_led(i, 255, 0, 0) #Index, Red, Green, Blue
send_tpm2(bytearray(led_data))
sleep(2)

for i in range(LED_COUNT):
    set_led(i, 0, 255, 0)
send_tpm2(bytearray(led_data))
sleep(2)

for i in range(LED_COUNT):
    set_led(i, 0, 0, 255)
send_tpm2(bytearray(led_data))
sleep(2)

for i in range(LED_COUNT):
     set_led(i, 0, 0, 0)  # off
send_tpm2(bytearray(led_data))
sleep(2)