import pynput
from pynput.keyboard import Key, KeyCode, Controller as KeyboardController
from pynput.mouse import Button, Controller as MouseController
import keyboard
import time
import json
import threading
import pyautogui
import os
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog

LOOP_DELAY_SECONDS = 3
INITIAL_DELAY_SECONDS = 3
ACTION_DELAY_SECONDS = 0.02
script_dir = os.path.dirname(os.path.abspath(__file__))
MACRO_FOLDER = os.path.join(script_dir, "macros")

is_recording = False
is_playing = False
recorded_events = []
start_time = 0
recording_resolution = None
action_request = None
mouse = MouseController()
keyboard_controller = KeyboardController()
mouse_listener = None
keyboard_listener = None
playback_thread = None

hotkey_play = 'ctrl+1'
hotkey_record = 'ctrl+3'
hotkey_stop = 'esc'

def save_key_event(action, key):
    if not is_recording: return
    elapsed_time = time.time() - start_time
    try: key_to_save = key.char
    except AttributeError: key_to_save = str(key)
    if key_to_save is None: key_to_save = str(key)
    recorded_events.append({'action': action, 'key': key_to_save, 'time': elapsed_time})

def on_press_record(key): save_key_event('press', key)
def on_release_record(key): save_key_event('release', key)

def on_move_record(x, y):
    if is_recording:
        elapsed_time = time.time() - start_time
        recorded_events.append({'action': 'move', 'x': x / recording_resolution[0], 'y': y / recording_resolution[1], 'time': elapsed_time})

def on_click_record(x, y, button, pressed):
    if is_recording:
        elapsed_time = time.time() - start_time
        recorded_events.append({'action': 'press_btn' if pressed else 'release_btn', 'button': str(button), 'x': x / recording_resolution[0], 'y': y / recording_resolution[1], 'time': elapsed_time})

def on_scroll_record(x, y, dx, dy):
    if is_recording:
        recorded_events.append({'action': 'scroll', 'dx': dx, 'dy': dy, 'time': time.time() - start_time})

def toggle_recording():
    global is_recording, recorded_events, start_time, recording_resolution, mouse_listener, keyboard_listener, action_request
    if not is_recording:
        if is_playing: return print("Não é possível gravar durante a execução.")
        is_recording = True
        recorded_events, start_time = [], time.time()
        recording_resolution = pyautogui.size()
        mouse_listener = pynput.mouse.Listener(on_move=on_move_record, on_click=on_click_record, on_scroll=on_scroll_record)
        keyboard_listener = pynput.keyboard.Listener(on_press=on_press_record, on_release=on_release_record)
        mouse_listener.start(); keyboard_listener.start()
        print(f"\n--- [ GRAVAÇÃO INICIADA ] ---")
    else:
        is_recording = False
        if mouse_listener: mouse_listener.stop()
        if keyboard_listener: keyboard_listener.stop()
        print(f"--- [ GRAVAÇÃO FINALIZADA ] ---")
        action_request = "SAVE"

def request_play_macro():
    global action_request
    if is_recording or is_playing: return print("Ação ignorada: gravação ou execução em andamento.")
    action_request = "PLAY"
    
def stop_playback():
    global is_playing, action_request
    if is_playing:
        is_playing = False
        print("\nSinal de parada recebido. Finalizando o ciclo atual...")
    elif action_request:
        print("Pedido cancelado.")
        action_request = None

def play_worker(macro_data):
    global is_playing
    
    print(f"Execução começará em {INITIAL_DELAY_SECONDS} segundos...")
    time.sleep(INITIAL_DELAY_SECONDS)

    events = macro_data["events"]
    current_res = pyautogui.size()
    cycle_count = 1
    
    while is_playing:
        print(f"Iniciando ciclo de repetição #{cycle_count}...")
        last_time = 0.0
        for event in events:
            if not is_playing: break
            
            time.sleep(max(0, event['time'] - last_time))
            action = event['action']

            if action in ['move', 'press_btn', 'release_btn']:
                mouse.position = (int(event['x'] * current_res.width), int(event['y'] * current_res.height))
                if 'button' in event:
                    button = get_button_from_string(event['button'])
                    if action == 'press_btn': mouse.press(button)
                    else: mouse.release(button)
            elif action in ['press', 'release']:
                key = get_key_from_string(event['key'])
                if action == 'press': keyboard.press(key)
                else: keyboard.release(key)
            elif action == 'scroll':
                mouse.scroll(event['dx'], event['dy'])

            time.sleep(ACTION_DELAY_SECONDS)
            last_time = event['time']

        if not is_playing: break
        print(f"Ciclo #{cycle_count} concluído. Aguardando {LOOP_DELAY_SECONDS}s...")
        time.sleep(LOOP_DELAY_SECONDS)
        cycle_count += 1
    print("--- [ LOOP DE EXECUÇÃO FINALIZADO ] ---")

CONTROL_CHAR_MAP = {
    '\x01':'a', '\x02':'b', '\x03':'c', '\x04':'d', '\x05':'e', '\x06':'f', '\x07':'g', 
    '\x08':'h', '\x09':'i', '\x0a':'j', '\x0b':'k', '\x0c':'l', '\x0d':'m', '\x0e':'n', 
    '\x0f':'o', '\x10':'p', '\x11':'q', '\x12':'r', '\x13':'s', '\x14':'t', '\x15':'u', 
    '\x16':'v', '\x17':'w', '\x18':'x', '\x19':'y', '\x1a':'z'
}
def get_key_from_string(key_str):
    if key_str in CONTROL_CHAR_MAP: return CONTROL_CHAR_MAP[key_str]
    if key_str.startswith('Key.'): return getattr(Key, key_str.split('.')[1])
    if key_str.startswith('<') and key_str.endswith('>'):
        try: return KeyCode(vk=int(key_str[1:-1]))
        except (ValueError, TypeError): return key_str
    return key_str

def get_button_from_string(button_str): return getattr(Button, button_str.split('.')[1])

def handle_save_request_gui():
    global action_request
    filename = simpledialog.askstring("Salvar Macro", "Digite o nome do arquivo para a macro (sem .json):")
    if filename:
        filepath = os.path.join(MACRO_FOLDER, f"{filename}.json")
        data_to_save = {"resolution": recording_resolution, "events": recorded_events}
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, indent=4)
        messagebox.showinfo("Sucesso", f"Macro salva em '{filepath}'")
    else:
        messagebox.showinfo("Cancelado", "Salvamento cancelado.")
    action_request = None


def handle_play_request_gui():
    global action_request, is_playing, playback_thread
    macros = [f for f in os.listdir(MACRO_FOLDER) if f.endswith('.json')]
    if not macros:
        messagebox.showinfo("Erro", "Nenhuma macro encontrada.")
        action_request = None
        return
    filename = filedialog.askopenfilename(initialdir=MACRO_FOLDER, title="Escolha a macro", filetypes=[("JSON files", "*.json")])
    if filename:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                macro_data = json.load(f)
            is_playing = True
            playback_thread = threading.Thread(target=play_worker, args=(macro_data,))
            playback_thread.start()
        except FileNotFoundError:
            messagebox.showerror("Erro", f"Arquivo '{filename}' não encontrado.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar a macro: {e}")
    else:
        messagebox.showinfo("Cancelado", "Execução cancelada.")
    action_request = None

def gui_main():
    if not os.path.exists(MACRO_FOLDER):
        os.makedirs(MACRO_FOLDER)

    def start_recording():
        if is_playing:
            messagebox.showinfo("Aviso", "Não é possível gravar durante a execução.")
            return
        if not is_recording:
            toggle_recording()
            btn_record.config(text="Parar Gravação")
        else:
            toggle_recording()
            btn_record.config(text="Gravar")
            handle_save_request_gui()

    def play_macro():
        if is_recording or is_playing:
            messagebox.showinfo("Aviso", "Ação ignorada: gravação ou execução em andamento.")
            return
        handle_play_request_gui()

    def stop_macro():
        stop_playback()

    def configure_hotkeys():
        global hotkey_play, hotkey_record, hotkey_stop
        config_win = tk.Toplevel(root)
        config_win.title("Configurar Atalhos")
        config_win.geometry("300x200")

        tk.Label(config_win, text="Playback/Stop").grid(row=0, column=0, padx=10, pady=10)
        entry_play = tk.Entry(config_win)
        entry_play.insert(0, hotkey_play)
        entry_play.grid(row=0, column=1)

        tk.Label(config_win, text="Record/Stop").grid(row=1, column=0, padx=10, pady=10)
        entry_record = tk.Entry(config_win)
        entry_record.insert(0, hotkey_record)
        entry_record.grid(row=1, column=1)

        tk.Label(config_win, text="Parar").grid(row=2, column=0, padx=10, pady=10)
        entry_stop = tk.Entry(config_win)
        entry_stop.insert(0, hotkey_stop)
        entry_stop.grid(row=2, column=1)

        def save_hotkeys():
            nonlocal entry_play, entry_record, entry_stop
            hotkey_play = entry_play.get()
            hotkey_record = entry_record.get()
            hotkey_stop = entry_stop.get()
            messagebox.showinfo("Configuração", "Atalhos atualizados!")
            config_win.destroy()

        tk.Button(config_win, text="Ok", command=save_hotkeys).grid(row=3, column=0, pady=20)
        tk.Button(config_win, text="Cancelar", command=config_win.destroy).grid(row=3, column=1)

    root = tk.Tk()
    root.title("Mouse Automático")
    root.geometry("900x250")
    root.attributes('-topmost', True)

    lbl = tk.Label(root, text="Mouse Automático", font=("Arial", 16))
    lbl.pack(pady=10)

    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)

    btn_record = tk.Button(btn_frame, text="Gravar", width=12, command=start_recording)
    btn_record.grid(row=0, column=0, padx=5)

    btn_play = tk.Button(btn_frame, text="Play Macro", width=12, command=play_macro)
    btn_play.grid(row=0, column=1, padx=5)

    btn_stop = tk.Button(btn_frame, text="Parar Execução", width=12, command=stop_macro)
    btn_stop.grid(row=0, column=2, padx=5)

    btn_config = tk.Button(btn_frame, text="Configurar Atalhos", width=15, command=configure_hotkeys)
    btn_config.grid(row=1, column=0, columnspan=3, pady=8)

    lbl_info = tk.Label(root, text=f"Macros salvas em:\n{MACRO_FOLDER}", font=("Arial", 8))
    lbl_info.pack(pady=10)

    lbl_dev = tk.Label(root, text="Desenvolvido por Malik Ribeiro Mourad", font=("Arial", 8))
    lbl_dev.pack(pady=2)

    def hotkey_play_func():
        if not is_playing and not is_recording:
            handle_play_request_gui()
    def hotkey_record_func():
        start_recording()
    def hotkey_stop_func():
        stop_macro()

    keyboard.add_hotkey(hotkey_play, hotkey_play_func)
    keyboard.add_hotkey(hotkey_record, hotkey_record_func)
    keyboard.add_hotkey(hotkey_stop, hotkey_stop_func)

    root.protocol("WM_DELETE_WINDOW", lambda: (keyboard.unhook_all_hotkeys(), root.destroy()))
    root.mainloop()

if __name__ == "__main__":
    gui_main()