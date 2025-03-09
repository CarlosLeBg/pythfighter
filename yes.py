import os
from PIL import Image

def convert_gif_to_pngs(gif_path, output_folder):
    # Ouvrir le fichier GIF
    im = Image.open(gif_path)

    # Créer le dossier de sortie s'il n'existe pas
    os.makedirs(output_folder, exist_ok=True)

    try:
        while True:
            # Sauvegarder chaque frame en tant qu'image PNG
            frame_image = im.copy().convert('RGBA')
            frame_filename = f'frame_{im.tell():02}_delay-0.1s.png'
            frame_image.save(os.path.join(output_folder, frame_filename))
            print(f"Saved {frame_filename} from {gif_path} to {output_folder}")

            # Passer à la frame suivante
            im.seek(im.tell() + 1)
    except EOFError:
        pass  # Fin du GIF

# Exemple d'utilisation
gif_directory = r'src\assets\characters\tank'
output_directory = r'src\assets\characters\tank_png'

# Convertir tous les GIFs dans le répertoire spécifié
for root, _, files in os.walk(gif_directory):
    for file in files:
        if file.endswith('.gif'):
            gif_path = os.path.join(root, file)
            # Créer un dossier distinct pour chaque action
            action_folder = os.path.basename(root)
            output_folder = os.path.join(output_directory, action_folder)
            convert_gif_to_pngs(gif_path, output_folder)
            print(f"Converted {gif_path} to PNGs in {output_folder}")
