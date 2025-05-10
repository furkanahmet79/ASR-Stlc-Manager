import os
import xml.etree.ElementTree as ET

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
                    # Sadece UML ile ilgili önemli etiketleri çek
                    content = self.extract_uml_elements_from_xml(content)
                    print(f"[FileHandler] UML etiketleri çekildi (ilk 500 karakter):\n{content[:500]}")
                else:
                    print(f"[FileHandler] Okunan dosya içeriği (ilk 500 karakter):\n{content[:500]}")
                return content
        except UnicodeDecodeError:
            # Farklı encoding ile tekrar dene
            with open(path, 'r', encoding='ISO-8859-9') as f:
                content = f.read()
                if path.lower().endswith('.xml'):
                    content = self.extract_uml_elements_from_xml(content)
                    print(f"[FileHandler] UML etiketleri çekildi (ilk 500 karakter, ISO-8859-9):\n{content[:500]}")
                else:
                    print(f"[FileHandler] Okunan dosya içeriği (ilk 500 karakter, ISO-8859-9):\n{content[:500]}")
                return content
        except Exception as e:
            print(f"[FileHandler] Dosya okunamadı: {str(e)}")
            return f"Dosya okunamadı: {str(e)}"

    def extract_uml_elements_from_xml(self, xml_content):
        try:
            root = ET.fromstring(xml_content)
            tags = [
                'Class', 'Attribute', 'Operation', 'ModelChildren',
                'DataType', 'Association', 'AssociationEnd', 'Generalization', 'Package'
            ]
            elements = []
            for tag in tags:
                for elem in root.findall(f'.//{tag}'):
                    elem_str = ET.tostring(elem, encoding='unicode')
                    elements.append(elem_str)
            return '\n'.join(elements)
        except Exception as e:
            print(f"[FileHandler] XML parse hatası: {str(e)}")
            return ""

    def cleanup_files(self, file_paths):
        for path in file_paths:
            if os.path.exists(path):
                os.remove(path)
