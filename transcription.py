import tkinter as tk
import threading
import queue
import sounddevice as sd
import json
from vosk import Model, KaldiRecognizer
import configparser
import sys
import os
import time

if getattr(sys, 'frozen', False):
    # PyInstallerでビルドされた実行ファイルの場合
    exe_dir = os.path.dirname(sys.executable) + '\\'
else:
    # 通常のPythonスクリプトとして実行されている場合
    exe_dir = os.path.dirname(os.path.abspath(__file__)) + '\\'

# === 設定をコンフィグファイルから読み込む ===
config = configparser.ConfigParser()
config.read(exe_dir + 'config.ini')

# === 設定 ===
window_width = int(config['general']['window_width'])
window_height = int(config['general']['window_height'])
background_color = config['general']['background_color']
font_color = config['general']['font_color']
font_family = config['general']['font_family']
font_size = int(config['general']['font_size'])

MODEL_PATH = config['audio']['model_path']
SAMPLE_RATE = int(config['audio']['sample_rate'])
DEVICE_ID = int(config['audio']['device_id'])

# === グローバル ===
q = queue.Queue()
recognizer = None

# === 音声認識スレッド ===
def audio_thread(label):
    global recognizer

    model = Model(MODEL_PATH)
    recognizer = KaldiRecognizer(model, SAMPLE_RATE)

    def callback(indata, frames, time, status):
        if status:
            print("Status:", status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=callback, device=DEVICE_ID):
        while True:
            if not q.empty():
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get("text", "")
                    if text:
                        label.config(text=text)
                        new_width = root.winfo_width()
                        label.config(wraplength=new_width)
            else:
                time.sleep(0.01)  # CPUを休ませる

# === GUIセットアップ ===
root = tk.Tk()
root.title("リアルタイム音声認識")
root.geometry(f"{window_width}x{window_height}")
root.configure(bg=background_color)  # ウィンドウ全体の背景を設定

# フォントサイズをコンフィグから設定
text_label = tk.Label(root, text="話してください...", font=(font_family, font_size),
                      justify="left", bg=background_color, fg=font_color, anchor="w")
text_label.place(x=0, y=0)

# 音声認識スタート（非同期）
threading.Thread(target=audio_thread, args=(text_label,), daemon=True).start()

root.mainloop()
