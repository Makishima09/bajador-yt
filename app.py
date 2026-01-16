import tkinter as tk
from tkinter import messagebox

from yt_downloader import download_from_links, extract_links_from_text


def handle_download() -> None:
    urls_text = urls_textbox.get('1.0', tk.END)
    output_folder = output_folder_var.get().strip()

    links = extract_links_from_text(urls_text)
    if not links:
        messagebox.showerror('Error', 'Debes ingresar al menos una URL.')
        return

    if not output_folder:
        messagebox.showerror('Error', 'Debes definir una carpeta de salida.')
        return

    status_var.set('Descargando... por favor espera.')
    root.update_idletasks()

    try:
        download_from_links(links, output_folder)
    except Exception as error:
        status_var.set('Ocurrió un error durante la descarga.')
        messagebox.showerror('Error', str(error))
        return

    status_var.set('Descarga completada.')
    messagebox.showinfo('Listo', 'Descarga completada.')


root = tk.Tk()
root.title('Bajador YT - MP3')
root.geometry('520x420')
root.resizable(False, False)

title_label = tk.Label(
    root,
    text='Pegue una o varias URLs de YouTube (una por línea):',
    font=('Arial', 11, 'bold'),
)
title_label.pack(pady=(16, 6), padx=16, anchor='w')

urls_textbox = tk.Text(root, height=10, width=60)
urls_textbox.pack(padx=16, pady=(0, 12))

output_frame = tk.Frame(root)
output_frame.pack(padx=16, pady=(0, 12), fill='x')

output_label = tk.Label(output_frame, text='Carpeta de salida:')
output_label.pack(side='left')

output_folder_var = tk.StringVar(value='./downloads')
output_entry = tk.Entry(output_frame, textvariable=output_folder_var, width=40)
output_entry.pack(side='left', padx=(8, 0))

download_button = tk.Button(
    root,
    text='Descargar MP3',
    command=handle_download,
    width=20,
)
download_button.pack(pady=(4, 8))

status_var = tk.StringVar(value='Listo para descargar.')
status_label = tk.Label(root, textvariable=status_var, fg='#1f2937')
status_label.pack(pady=(4, 0))

root.mainloop()
