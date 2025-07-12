import sounddevice as sd

devices = sd.query_devices()

with open("device_id.txt", "w", encoding="utf-8") as f:
    f.write(str(devices))