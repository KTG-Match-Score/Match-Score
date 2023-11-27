import os
from fastapi import UploadFile

def convert_binary(directory: str, filename: str):
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, f'../{directory}/{filename}')
    with open(path, 'rb') as file:
        binaryData = file.read()
    return binaryData          

def check_picture_exists(directory: str, filename: str):
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, f'../{directory}/{filename}')
    if os.path.isfile(f'{path}'):
        return True
    return 

def remove_picture(directory: str, filename: str):
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, f'../{directory}/{filename}')
    os.remove(path)

async def add_picture(file: UploadFile, directory: str, filename: str):
    cwd = os.path.dirname(__file__)
    path = os.path.join(cwd, f'../{directory}/{filename}')
    await file.seek(0)
    content = await file.read()
    with open(path, 'wb') as file:
        file.write(content)