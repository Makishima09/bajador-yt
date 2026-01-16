import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from yt_downloader import DownloadResult, download_from_links, extract_links_from_text


def handle_progress(result: DownloadResult, index: int, total: int) -> None:
    status_var.set(f'Procesado {index}/{total}: {result.status}')
    results_list.insert(
        '',
        tk.END,
        values=(str(index), result.url, result.status, result.message),
    )
    root.update_idletasks()

def handle_select_folder() -> None:
    current_path = output_folder_var.get().strip() or '.'
    selected_folder = filedialog.askdirectory(
        title='Selecciona la carpeta de salida',
        initialdir=current_path,
    )
    if not selected_folder:
        return
    output_folder_var.set(selected_folder)


def handle_download() -> None:
    urls_text = urls_textbox.get('1.0', tk.END)
    output_folder = output_folder_var.get().strip()
    allow_playlist = allow_playlist_var.get()
    audio_format = format_var.get()
    audio_quality = quality_var.get()

    links = extract_links_from_text(urls_text)
    if not links:
        messagebox.showerror('Error', 'Debes ingresar al menos una URL.')
        return

    if not output_folder:
        messagebox.showerror('Error', 'Debes definir una carpeta de salida.')
        return

    status_var.set('Descargando... por favor espera.')
    root.update_idletasks()
    results_list.delete(*results_list.get_children())

    results = download_from_links(
        links,
        output_folder,
        progress_callback=handle_progress,
        allow_playlist=allow_playlist,
        codec=audio_format,
        quality=audio_quality,
    )

    total = len(results)
    success_count = len([r for r in results if r.status == 'success'])
    skipped_count = len([r for r in results if r.status == 'skipped'])
    invalid_count = len([r for r in results if r.status == 'invalid'])
    error_count = len([r for r in results if r.status == 'error'])

    summary = (
        f'Total: {total}\n'
        f'Exitosas: {success_count}\n'
        f'Saltadas: {skipped_count}\n'
        f'Inválidas: {invalid_count}\n'
        f'Errores: {error_count}'
    )

    if error_count or invalid_count:
        status_var.set('Descarga finalizada con advertencias.')
        messagebox.showwarning('Resultado', summary)
        return

    status_var.set('Descarga completada.')
    messagebox.showinfo('Listo', summary)


root = tk.Tk()
root.title('Bajador YT - MP3')
root.geometry('720x560')
root.resizable(False, False)

title_label = tk.Label(
    root,
    text='Pegue una o varias URLs de YouTube (una por línea):',
    font=('Arial', 11, 'bold'),
)
title_label.pack(pady=(16, 6), padx=16, anchor='w')

urls_textbox = tk.Text(root, height=8, width=84)
urls_textbox.pack(padx=16, pady=(0, 12))

output_frame = tk.Frame(root)
output_frame.pack(padx=16, pady=(0, 12), fill='x')

output_label = tk.Label(output_frame, text='Carpeta de salida:')
output_label.pack(side='left')

output_folder_var = tk.StringVar(value='./downloads')
output_entry = tk.Entry(output_frame, textvariable=output_folder_var, width=52)
output_entry.pack(side='left', padx=(8, 6))

select_button = tk.Button(
    output_frame,
    text='Examinar',
    command=handle_select_folder,
    width=12,
)
select_button.pack(side='left')

options_frame = tk.Frame(root)
options_frame.pack(padx=16, pady=(0, 12), fill='x')

allow_playlist_var = tk.BooleanVar(value=False)
allow_playlist_check = tk.Checkbutton(
    options_frame,
    text='Permitir playlists',
    variable=allow_playlist_var,
)
allow_playlist_check.pack(anchor='w')

format_label = tk.Label(options_frame, text='Formato:')
format_label.pack(side='left', padx=(0, 6))

format_var = tk.StringVar(value='mp3')
format_select = ttk.Combobox(
    options_frame,
    textvariable=format_var,
    values=('mp3', 'm4a', 'opus', 'wav'),
    state='readonly',
    width=8,
)
format_select.pack(side='left', padx=(0, 16))

quality_label = tk.Label(options_frame, text='Calidad:')
quality_label.pack(side='left', padx=(0, 6))

quality_var = tk.StringVar(value='192')
quality_select = ttk.Combobox(
    options_frame,
    textvariable=quality_var,
    values=('128', '192', '256', '320'),
    state='readonly',
    width=8,
)
quality_select.pack(side='left')

download_button = tk.Button(
    root,
    text='Descargar audio',
    command=handle_download,
    width=20,
)
download_button.pack(pady=(4, 8))

results_frame = tk.Frame(root)
results_frame.pack(padx=16, pady=(0, 8), fill='both', expand=False)

results_label = tk.Label(results_frame, text='Estado por URL:')
results_label.pack(anchor='w')

columns = ('#', 'url', 'status', 'message')
results_list = ttk.Treeview(
    results_frame,
    columns=columns,
    show='headings',
    height=8,
)
results_list.heading('#', text='#')
results_list.heading('url', text='URL')
results_list.heading('status', text='Estado')
results_list.heading('message', text='Mensaje')
results_list.column('#', width=30, anchor='center')
results_list.column('url', width=360, anchor='w')
results_list.column('status', width=90, anchor='center')
results_list.column('message', width=190, anchor='w')

scrollbar = ttk.Scrollbar(results_frame, orient='vertical', command=results_list.yview)
results_list.configure(yscrollcommand=scrollbar.set)

results_list.pack(side='left', fill='x', expand=True)
scrollbar.pack(side='right', fill='y')

status_var = tk.StringVar(value='Listo para descargar.')
status_label = tk.Label(root, textvariable=status_var, fg='#1f2937')
status_label.pack(pady=(4, 0))

root.mainloop()
