import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from datetime import datetime
import threading
import numpy as np
import pandas as pd
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

matplotlib.use('Agg')

LOG_DIR = "modbus_data"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

class ModbusApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modbus Data & Test Screen")
        self.sensor_count = tk.IntVar(value=1)
        self.running = False
        self.graph_data = {}
        self.log_frames = []   
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Sensör sayısı seçimi
        ttk.Label(left_panel, text="Sensör Sayısı:").pack(pady=5)
        self.sensor_selector = ttk.Combobox(left_panel, textvariable=self.sensor_count, values=[1,2,3,4], state="readonly")
        self.sensor_selector.pack(pady=3)
        self.sensor_selector.bind("<<ComboboxSelected>>", self.update_sensor_count)

        # Dinamik log alanları
        self.log_container = ttk.Frame(left_panel)
        self.log_container.pack(pady=10, fill=tk.X)

        self.create_log_frames()

        # Sağ Panel (Grafik)
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.ax.set_title("Transmitter Temperature")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Temperature")
        self.ax.grid(True)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        self.start_button = ttk.Button(bottom_frame, text="Start Test", command=self.start_fetching)
        self.start_button.pack(side=tk.LEFT, padx=10)
        self.stop_button = ttk.Button(bottom_frame, text="Stop Test", command=self.stop_fetching)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        self.quit_button = ttk.Button(bottom_frame, text="Quit", command=self.root.destroy)
        self.quit_button.pack(side=tk.RIGHT, padx=10)

    def create_log_frames(self):
        # Önceki log frame'leri sil
        for frame in self.log_frames:
            frame.destroy()
        self.log_frames.clear()
        self.graph_data.clear()
        for i in range(self.sensor_count.get()):
            frame = ttk.LabelFrame(self.log_container, text=f"Sensör {i+1} Log")
            frame.pack(pady=5, fill=tk.X)
            log_text = tk.Text(frame, height=5, width=40)
            log_text.pack(side=tk.LEFT, padx=5)
            load_btn = ttk.Button(frame, text="Logu Göster", command=lambda idx=i: self.load_log(idx))
            load_btn.pack(side=tk.LEFT, padx=5)
            self.log_frames.append(frame)
            self.graph_data[i] = []
    
    def update_sensor_count(self, event=None):
        self.create_log_frames()

    def load_log(self, idx):
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(LOG_DIR, f'sensor{idx+1}_log_{today}.csv')
        text_widget = self.log_frames[idx].winfo_children()[0]
        text_widget.delete("1.0", tk.END)
        if os.path.exists(log_file):
            df = pd.read_csv(log_file)
            text_widget.insert(tk.END, df.to_string())
        else:
            text_widget.insert(tk.END, "Log yok.")

    def start_fetching(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.fetch_data_loop, daemon=True).start()
            messagebox.showinfo("Info", "Test started.")

    def stop_fetching(self):
        self.running = False
        messagebox.showinfo("Info", "Test stopped.")

    def fetch_data_loop(self):
        t = 0
        while self.running:
            for idx in range(self.sensor_count.get()):
                temp = np.random.randint(100, 500)  # Burada modbus verisi kullanılabilir!
                self.graph_data[idx].append((t, temp))
                self.save_log(idx, t, temp)
            self.update_graph()
            t += 1
            self.root.after(1000)

    def save_log(self, idx, t, temp):
        today = datetime.now().strftime('%Y%m%d')
        log_file = os.path.join(LOG_DIR, f'sensor{idx+1}_log_{today}.csv')
        df_new = pd.DataFrame({"Time": [t], "Temperature": [temp]})
        if os.path.exists(log_file):
            df_old = pd.read_csv(log_file)
            df = pd.concat([df_old, df_new], ignore_index=True)
        else:
            df = df_new
        df.to_csv(log_file, index=False)

    def update_graph(self):
        self.ax.clear()
        self.ax.set_title("Transmitter Temperature")
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature")
        self.ax.grid(True)
        colors = ["cyan", "magenta", "orange", "lime"]
        for idx, data in self.graph_data.items():
            if data:
                x, y = zip(*data)
                self.ax.plot(x, y, color=colors[idx % len(colors)], label=f"Sensör {idx+1}")
        self.ax.legend()
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModbusApp(root)
    root.mainloop()
