from yt_downloader import download_from_csv

# Wrapper CLI: conserva la lógica original basada en CSV
csv_file = './url-list.csv'
output_folder = './downloads'
download_from_csv(csv_file, output_folder)
