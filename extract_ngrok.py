import zipfile, pathlib, sys

zip_path = pathlib.Path('ngrok.zip')
if not zip_path.is_file():
    print('ngrok.zip not found')
    sys.exit(1)

dest = pathlib.Path('.')
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall(dest)
print('Extraction complete')
