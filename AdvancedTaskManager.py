import psutil
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import threading
import time


cpu_percentages = []


def update_cpu_usage():
    if root.winfo_exists():  

        cpu_usage = psutil.cpu_percent(interval=False)  
        cpu_label.config(text=f"Utilisation CPU : {cpu_usage}%")


        cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
        core_usage_text = "\n".join([f"Cœur {i + 1}: {usage}%" for i, usage in enumerate(cpu_per_core)])
        cpu_core_label.config(text=core_usage_text)

        if len(cpu_percentages) > 50:  
            cpu_percentages.pop(0)

        cpu_percentages.append(cpu_usage)
        root.after(1000, update_cpu_usage)  


def update_memory_usage():
    if root.winfo_exists(): 
        memory_info = psutil.virtual_memory()
        memory_label.config(text=f"Utilisation Mémoire : {memory_info.percent}% ({memory_info.used / (1024 ** 3):.2f} Go/{memory_info.total / (1024 ** 3):.2f} Go)")
        root.after(1000, update_memory_usage)


def update_process_list():
    while root.winfo_exists(): 

        for item in tree.get_children():
            tree.delete(item)


        for proc in psutil.process_iter(['pid', 'name']):
            try:
               
                proc.cpu_percent(interval=0.1)  
                time.sleep(0.1)  
                cpu_usage = proc.cpu_percent(interval=0)  
                
                tree.insert('', tk.END, values=(proc.info['pid'], proc.info['name'], cpu_usage))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue  
        

        time.sleep(2)


def start_process_update_thread():
    process_thread = threading.Thread(target=update_process_list)
    process_thread.daemon = True  
    process_thread.start()


def kill_process():
    selected_item = tree.selection()
    if selected_item:
        pid = tree.item(selected_item)['values'][0]
        try:
            p = psutil.Process(pid)
            p.terminate()
        except Exception as e:
            print(f"Erreur lors de la terminaison du processus {pid}: {e}")


def animate(i):
    ax.clear()
    ax.plot(cpu_percentages, label='Utilisation CPU (%)', color='r')
    ax.set_ylim(0, 100)
    ax.set_title('Utilisation de la CPU')
    ax.set_ylabel('Pourcentage (%)')
    ax.set_xlabel('Temps (secondes)')
    ax.legend(loc='upper right')


def on_closing():
    root.quit()
    root.destroy()


root = tk.Tk()
root.title("Gestionnaire des tâches")
root.geometry("800x600")


root.protocol("WM_DELETE_WINDOW", on_closing)


info_frame = tk.Frame(root)
info_frame.pack(fill=tk.X, padx=10, pady=10)


cpu_label = tk.Label(info_frame, text="Utilisation CPU : ", font=("Arial", 14))
cpu_label.pack(pady=5)


cpu_core_label = tk.Label(info_frame, text="", font=("Arial", 12))
cpu_core_label.pack(pady=5)


update_cpu_usage()


memory_label = tk.Label(info_frame, text="Utilisation Mémoire : ", font=("Arial", 14))
memory_label.pack(pady=5)
update_memory_usage()


process_frame = tk.Frame(root)
process_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)


tree = ttk.Treeview(process_frame, columns=('PID', 'Nom', 'Utilisation CPU (%)'), show='headings')
tree.heading('PID', text='PID')
tree.heading('Nom', text='Nom du processus')
tree.heading('Utilisation CPU (%)', text='Utilisation CPU (%)')
tree.pack(fill=tk.BOTH, expand=True)


kill_button = tk.Button(root, text="Terminer le processus", command=kill_process)
kill_button.pack(pady=10)


fig, ax = plt.subplots(figsize=(5, 3))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


ani = animation.FuncAnimation(fig, animate, interval=1000)


start_process_update_thread()


root.mainloop()
