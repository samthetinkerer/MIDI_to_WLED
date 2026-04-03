# MIDI_to_WLED

Youtube video guide: 

I have uploaded 3 python files
Minimum code needed.py - This is a good starting point for using python to send LED information to a ESP32 flashed with WLED - https://kno.wled.ge/
MIDI to WLED Pulse Trail - This reads MIDI data and when it recives a note on message send a pulse down the led strip 
MIDI TO WLED Random Glow - This reads MIDI data and set random LEDs to glow. 

I have set 3 pots to set the RGB values by defult these will be 0 and no LED with show. 

either modify the Current RGB values
current_r = 0
current_g = 0
current_b = 0

or change the channel number to match the MIDI control knobs you want. 
PotA = 48 #red Channel
PotB = 49 #Green Channel
PotC = 50 #Blue Channel
