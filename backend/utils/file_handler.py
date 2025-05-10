import os
import xml.etree.ElementTree as ET
from utils.XmlParser import parse_uml_xml_to_json
import json

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class FileHandler:
    def __init__(self):
        pass

    async def save_files(self, files):
        file_paths = []
        for file in files:
            path = os.path.join(UPLOAD_DIR, file.filename)
            with open(path, "wb") as f:
                f.write(await file.read())
            file_paths.append(path)
        return file_paths

    def read_file(self, path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                if path.lower().endswith('.xml'):
                    # XML'i JSON'a çevir
                    json_obj = parse_uml_xml_to_json(content)
                    json_str = json.dumps(json_obj, ensure_ascii=False, indent=2)
                    print(f"[FileHandler] XML'den JSON üretildi (ilk 500 karakter):\n{json_str[:500]}")
                    return json_str
                else:
                    print(f"[FileHandler] Okunan dosya içeriği (ilk 500 karakter):\n{content[:500]}")
                return content
        except UnicodeDecodeError:
            # Farklı encoding ile tekrar dene
            with open(path, 'r', encoding='ISO-8859-9') as f:
                content = f.read()
                if path.lower().endswith('.xml'):
                    json_obj = parse_uml_xml_to_json(content)
                    json_str = json.dumps(json_obj, ensure_ascii=False, indent=2)
                    print(f"[FileHandler] XML'den JSON üretildi (ilk 500 karakter, ISO-8859-9):\n{json_str[:500]}")
                    return json_str
                else:
                    print(f"[FileHandler] Okunan dosya içeriği (ilk 500 karakter, ISO-8859-9):\n{content[:500]}")
                return content
        except Exception as e:
            print(f"[FileHandler] Dosya okunamadı: {str(e)}")
            return f"Dosya okunamadı: {str(e)}"

    def cleanup_files(self, file_paths):
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
