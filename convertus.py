import pandas as pd
import sys
import py7zr
from sqlalchemy import create_engine
import zipfile
from PIL import Image
import os
import shutil
import patoolib
from moviepy.editor import VideoFileClip
import soundfile as sf
import hashlib
import ffmpeg
import subprocess


def main():
    print("Hi, I can convert files and data, hash, zip or unzip files.")
    print("Type: convert / convert folder / zip / unzip / hash")
    print("Type exit to exit")

    while True:
        operation = input("What do you want me to do? ").strip()
        if operation == "exit":
            sys.exit("Goodbye")

        try:
            # Convert compartment
            if operation == "convert":
                ext_from = input("Please specify the source file path: ")
                ext_to = input("Please specify the destination file path: ")
                file_converter(ext_from, ext_to)

            # Audio convert Folder compartment
            if operation == "convert folder":
                folder = input("Please specify the source folder path: ")
                ext_to = input("Please specify the desired extension: ")
                ext_to = ext_to.replace(".", "")
                folder = folder.replace('"', "")
                folder_files = [f for f in os.listdir(folder) if f.lower().endswith((".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".aif", ".au", ".ac3", ".mp2"))]
                for file in folder_files:
                    ext_from = os.path.join(folder, file)
                    output_file = os.path.join(folder, f"{os.path.splitext(file)[0]}.{ext_to}")
                    if ext_to.lower() in ["wav", "mp3", "ogg", "flac", "aac", "m4a", "wma", "aiff", "aif", "au", "ac3", "mp2"]:
                        file_converter(ext_from, output_file)
                    else:
                        print(f"Skipping file {file} - Unsupported output audio format")


            # Zip compartment
            if operation == "zip":
                print("zip / 7z / cbz")
                ext_from = input("Please specify the source folder: ")
                ext_to = input("Please specify the destination file path: ")
                ext_to = ext_to if ext_to.endswith((".zip", ".7z", ".cbz")) else ext_to + ".zip"  # Add extension if missing

                if ext_to.endswith(".cbz"):
                    cbz_maker(ext_from, ext_to)
                else:
                    zipper(ext_from, ext_to)

            # Unzip compartment
            elif operation == "unzip":
                ext_from = input("Please specify the source archive file: ")
                ext_to = input("Please specify the destination folder: ")
                unzipper(ext_from, ext_to)

            # Hash compartment
            elif operation == "hash":
                ext_from = input("Please specify the source file path: ")
                hash_algorithm = input("Please specify the hash algorithm (md5, sha1, sha256, etc.): ")
                hasher(ext_from, hash_algorithm)
        
        except Exception as e:
            print(f"An error occurred: {e}")



def file_converter(ext_from, ext_to):
    ext_from = os.path.abspath(ext_from.replace('"', ''))
    ext_to = os.path.abspath(ext_to.replace('"', ''))
# Read data

    #tabular_data
    if ext_from.endswith((".xlsx", ".xls")):
        file = pd.read_excel(ext_from)
    elif ext_from.endswith(".json"):
        file = pd.read_json(ext_from)
    elif ext_from.endswith(".csv"):
        file = pd.read_csv(ext_from)
    else:
    #image, movies and audio R&W
        filename, file_extension = os.path.splitext(ext_from)
    #image part
        if file_extension  in  ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.ico', '.webp', '.ppm', '.pgm', '.pbm', '.xvth', '.pcx', '.spi', '.sgi', '.xbm', '.eps', '.fits', '.fli', '.flc', '.xpm']:
            image = Image.open(ext_from)
            image = image.convert("RGB")
            image.save(ext_to)
            print("Image converted")
    #movie part
        elif file_extension  in ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm', '.mpeg', '.3gp', '.ogg', '.asf', '.vob', '.m2ts', '.ts']:
            clip = VideoFileClip(ext_from)
            print("Remember, video conversion is often longer than length of the video and takes a lot of system power")
            speed = input("Please specify speed of conversion (ultrafast / veryfast / fast / medium / slow) :  ")
            clip.write_videofile(ext_to, codec='libx264', preset=speed)
            print("Movie converted")
    #audio part
        if ext_from.lower().endswith(".flac") and ext_to.lower().endswith("mp3"):
            ffmpeg_command = f'ffmpeg -i "{ext_from}" "{ext_to}"'  
            subprocess.run(ffmpeg_command, shell=True)
            print(f"Audio converted to MP3")
        elif file_extension in [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".wma", ".aiff", ".aif", ".au", ".ac3", ".mp2"]:
            file_format = file_extension.replace(".", "")
            audio, sample_rate = sf.read(ext_from)
            sf.write(ext_to, audio, sample_rate, format=file_format)
            print(f"Audio converted to {file_format}")
# Write data
 
    #tabular_data_writing
    if ext_to.endswith((".xlsx", ".xls")):
        file.to_excel(ext_to, index=False)
        print("Data converted")
    elif ext_to.endswith(".json"):
        file.to_json(ext_to)
        print("Data converted")
    elif ext_to.endswith(".csv"):
        file.to_csv(ext_to)
        print("Data converted")
    elif ext_to.endswith(".sql"):
        db_engine = create_engine(f'sqlite:///{ext_to}')  
        file.to_sql(ext_from, con=db_engine, if_exists='replace', index=False)
        db_engine.dispose()
        print("Data converted")



#zip


#cbz_maker
def cbz_maker(folder, ext_to):
    folder = folder.replace('"', '')

    image_files = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    image_files.sort()
    with zipfile.ZipFile(ext_to, "w") as cbz:
        for image_file in image_files:
            image_path = os.path.join(folder, image_file)
            with Image.open(image_path) as img:
                img.save(image_file)
                cbz.write(image_file, os.path.basename(image_file))
        print("Images zipped to cbz")
    for image_file in image_files:
        os.remove(image_file)
    


#zipper
def zipper(folder, ext_to):

    folder = folder.replace('"', '')
    #zip
    if ext_to.endswith(".zip"):
        ext_to = ext_to.replace(".zip", "")
        shutil.make_archive(ext_to, "zip", folder)
        print("Files zipped")
    #7z
    elif ext_to.endswith(".7z"):
        with py7zr.SevenZipFile(ext_to, "w") as file:
            file.writeall(folder, "")
            print("Files zipped")

#unzipper
def unzipper(ext_from, folder):
    if not os.path.exists(folder):
        os.makedirs(folder)
    patoolib.extract_archive(ext_from, outdir=folder)

#hasher
def hasher(ext_from, hash_algorithm):
    ext_from = os.path.abspath(ext_from)

    if hash_algorithm in hashlib.algorithms_guaranteed:
        chunk_size = input("Please specify chunk size in bytes: ")
        hash_var = hashlib.new(hash_algorithm)

        with open(ext_from, 'rb') as file:
            while True:
                data = file.read(int(chunk_size))
                if not data:
                    break
                hash_var.update(data)

        print(hash_var.hexdigest())


        
    


if __name__ == "__main__":
    main()
