import socket
import threading
from time import sleep
import mido
import random

# ---------------- CONFIG ----------------
UDP_IP = "4.3.2.1"  # your WLED IP
UDP_PORT = 65506
LED_COUNT = 60
led_data = [0] * (LED_COUNT * 3)

current_r = 0
current_g = 0
current_b = 0

PotA = 48 #red Channel
PotB = 49 #Green Channel
PotC = 50 #Blue Channel

random_index = 0

active_notes = {}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

trails = []

class Trail:
    def __init__(self, start=0, speed=1, color=(255, 0, 0)):
        self.pos = start
        self.speed = speed
        self.color = color

    def update(self):
        self.pos += self.speed

    def is_alive(self):
        return self.pos < LED_COUNT



def fade_leds(amount=0.8):
    for i in range(len(led_data)):
        led_data[i] = int(led_data[i] * amount)

def draw_trail(trail):
    index = int(trail.pos)

    if 0 <= index < LED_COUNT:
        set_led(index, *trail.color)

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
# ---------- MIDI HANDLER ----------
def handle_midi(msg):
    global active_notes, current_r, current_g, current_b
    if msg.type == 'control_change':
        if msg.control == PotA:
            current_r = int((msg.value / 127) * 255)

        elif msg.control == PotB:
            current_g = int((msg.value / 127) * 255)

        elif msg.control == PotC:
            current_b = int((msg.value / 127) * 255)


        print(f"RGB: {current_r}, {current_g}, {current_b}")

    if msg.type == 'note_on' and msg.velocity > 0:
        used_leds = {d["center"] for d in active_notes.values()}
        available = list(set(range(LED_COUNT)) - used_leds)

        if available:
            led_index = random.choice(available)
        else:
            led_index = random.randint(0, LED_COUNT - 1)

        active_notes[msg.note] = {
            "center": led_index,
            "radius": 6,
            "brightness": msg.velocity * 2,
            "held": True,
            "color": (current_r, current_g, current_b)
        }

    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
        if msg.note in active_notes:
            active_notes[msg.note]["held"] = False



def update_leds():
    global active_notes

    while True:
        # fade everything slightly (nice smooth effect)
        fade_leds(0.9)

        to_delete = []

        for note, data in list(active_notes.items()):
            center = data["center"]
            radius = int(data["radius"])
            r, g, b = data["color"]

            for offset in range(-radius, radius + 1):
                led = center + offset

                if 0 <= led < LED_COUNT:
                    distance = abs(offset)

                    # smooth falloff
                    falloff = max(0, 1 - (distance / (radius + 1)))
                    falloff = falloff ** 2  # softer edges

                    brightness = (data["brightness"] / 255) * falloff

                    i = led * 3
                    led_data[i] = min(255, led_data[i] + int(r * brightness))
                    led_data[i + 1] = min(255, led_data[i + 1] + int(g * brightness))
                    led_data[i + 2] = min(255, led_data[i + 2] + int(b * brightness))



        # remove finished notes
        for note in to_delete:
            del active_notes[note]

        send_tpm2(bytearray(led_data))
        sleep(0.02)


# ---------- MAIN ----------
def main():
    print("\nAvailable MIDI inputs:")
    inputs = mido.get_input_names()

    for i, name in enumerate(inputs):
        print(f"{i}: {name}")

    port = mido.open_input(inputs[2])

    # Start LED update thread
    threading.Thread(target=update_leds, daemon=True).start()

    print("\nListening for MIDI... Ctrl+C to exit")

    for msg in port:
        handle_midi(msg)


# Example: 33 LEDs (RGB)
for i in range(LED_COUNT):
    set_led(i, 255, 0, 0)
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


print(i)
for i in range(LED_COUNT):
     set_led(i, 0, 0, 0)  # off
send_tpm2(bytearray(led_data))
sleep(2)


if __name__ == "__main__":
    main()