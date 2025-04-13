"""
prompt_manager.py
-----------------
Her STLC adımı için MongoDB'den system prompt ve query_str gibi verileri çekmeye yarar.
Ayrıca structured_output formatı gibi ilave bilgileri de buradan alabilirsiniz.
"""

import logging
from core.database import get_db
from datetime import datetime

# Logger ayarları
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def initialize_prompt():
    db = get_db()
    
    # Koleksiyonu kontrol et, yoksa oluştur
    if "base_prompts" not in db.list_collection_names():
        db.create_collection("base_prompts")
        print("base_prompts koleksiyonu oluşturuldu.")
    
    # Prompt'u ekle
    prompt = {
        "process_type": "code_review",
        "prompt_text": """Please perform a comprehensive code review of the following codebase. 
Focus on:
1. Overall architecture and code organization
2. Code quality and best practices
3. Potential bugs and issues
4. Security considerations
5. Performance implications
6. Suggestions for improvement

Please provide specific examples and recommendations where applicable.

Code to review:
{code}""",
        "description": "Base prompt for code review process",
        "created_at": datetime.now()
    }
    
    # Koleksiyonu kontrol et
    existing = db.base_prompts.find_one({"process_type": "code_review"})
    if not existing:
        db.base_prompts.insert_one(prompt)
        print("Code review prompt eklendi.")
    else:
        print("Code review prompt zaten mevcut.")
    
    if "session_history" not in db.list_collection_names():
        db.create_collection("session_history")
        print("session_history koleksiyonu oluşturuldu.")

# Bu fonksiyonu çalıştır
initialize_prompt()

def get_prompts_for_step(step_name: str):
    """
    Belirtilen STLC adımı için MongoDB'den prompt bilgilerini çeker.
    
    :param step_name: STLC adımı (örneğin, "test_planning").
    :return: system_prompt, query_str ve structured_output_schema içeren bir sözlük.
    """
    logger.info(f"{step_name} adımı için prompt bilgileri çekiliyor.")
    
    try:
        db = get_db()
        collection = db["test_scenario_generation_prompts"]  # Koleksiyon adı
        document = collection.find_one({"step": step_name})
        
        if document:
            logger.info(f"{step_name} adımı için prompt bilgileri bulundu.")
            return {
                "system_prompt": document.get("system_prompt", ""),
                "query_str": document.get("query_str", ""),
                "structured_output_schema": document.get("structured_output_schema", {})
            }
        else:
            logger.warning(f"{step_name} adımı için prompt bilgileri bulunamadı.")
            return {}
    except Exception as e:
        logger.error(f"Prompt bilgileri çekilirken hata oluştu: {str(e)}")
        return {}

def get_base_prompt(process_type: str):
    """
    Belirtilen süreç için veritabanından temel prompt'u çeker.
    """
    logger.info(f"{process_type} süreci için temel prompt çekiliyor.")
    
    try:
        db = get_db()
        collection = db["base_prompts"]
        document = collection.find_one({"process_type": process_type})
        
        if document:
            logger.info(f"{process_type} süreci için temel prompt bulundu.")
            return document.get("prompt_text", "")
        else:
            logger.warning(f"{process_type} süreci için temel prompt bulunamadı.")
            return None
    except Exception as e:
        logger.error(f"Temel prompt çekilirken hata oluştu: {str(e)}")
        return None

def save_session_data(session_data: dict):
    """
    Session verilerini veritabanına kaydeder.
    """
    logger.info("Session verisi kaydediliyor.")
    
    try:
        db = get_db()
        collection = db["session_history"]
        
        # Şimdiki zamanı al
        now = datetime.now()
        
        # Session data yapısını güncelle
        full_session_data = {
            "edited_prompt": session_data.get("edited_prompt", None),  # Kullanıcı tarafından düzenlenen prompt
            "used_ai_model": session_data.get("model_name", "default_model"),  # Kullanılan AI model
            "uploaded_files": session_data.get("uploaded_files", []),  # Dosya bilgileri
            "used_prompt": session_data.get("used_prompt", ""),  # Kullanılan prompt
            "process_type": session_data.get("process_type", "unknown"),
            "timestamp": now,
            "session_id": now.strftime("%d%m%Y%H%M%S")
        }
        
        result = collection.insert_one(full_session_data)
        if result.acknowledged:
            logger.info(f"Session verisi başarıyla kaydedildi: {result.inserted_id}")
            return result.inserted_id
        else:
            logger.warning("Session verisi kaydedilemedi.")
            return None
    except Exception as e:
        logger.error(f"Session verisi kaydedilirken hata oluştu: {str(e)}")
        return None

def initialize_base_prompts():
    """
    Veritabanına temel promptları ekler (sadece ilk kez çalıştırılmalı).
    """
    logger.info("Temel promptlar başlatılıyor.")
    
    try:
        db = get_db()
        collection = db["base_prompts"]
        
        # Koleksiyon boş mu kontrol et
        if collection.count_documents({}) > 0:
            logger.info("Temel promptlar zaten mevcut, yükleme atlanıyor.")
            return True
        
        # Code Review prompt'u
        code_review_prompt = """Please perform a comprehensive code review of the following codebase. 
Focus on:
1. Overall architecture and code organization
2. Code quality and best practices
3. Potential bugs and issues
4. Security considerations
5. Performance implications
6. Suggestions for improvement

Please provide specific examples and recommendations where applicable.

Code to review:
{code}
"""
        
        collection.insert_one({
            "process_type": "code_review",
            "prompt_text": code_review_prompt,
            "description": "Base prompt for code review process",
            "created_at": datetime.now()
        })
        
        logger.info("Temel promptlar başarıyla yüklendi.")
        return True
    except Exception as e:
        logger.error(f"Temel promptlar yüklenirken hata oluştu: {str(e)}")
        return False

def save_custom_prompt(process_type: str, prompt_text: str):
    """
    Özel bir prompt'u veritabanına kaydeder.
    
    :param process_type: Prompt'un ilişkili olduğu süreç türü (ör: code_review)
    :param prompt_text: Kaydedilecek prompt metni
    :return: İşlemin başarılı olup olmadığını belirten boolean değer
    """
    logger.info(f"{process_type} süreci için özel prompt kaydediliyor.")
    
    try:
        db = get_db()
        collection = db["base_prompts"]
        
        # Mevcut prompt'u ara
        existing = collection.find_one({"process_type": process_type})
        
        if existing:
            # Varolan prompt'u güncelle
            result = collection.update_one(
                {"process_type": process_type},
                {"$set": {"prompt_text": prompt_text, "updated_at": datetime.now()}}
            )
            success = result.modified_count > 0
        else:
            # Yeni prompt ekle
            result = collection.insert_one({
                "process_type": process_type,
                "prompt_text": prompt_text,
                "description": f"Custom prompt for {process_type} process",
                "created_at": datetime.now()
            })
            success = result.acknowledged
        
        if success:
            logger.info(f"{process_type} süreci için özel prompt başarıyla kaydedildi.")
        else:
            logger.warning(f"{process_type} süreci için özel prompt kaydedilemedi.")
        
        return success
    except Exception as e:
        logger.error(f"Özel prompt kaydedilirken hata oluştu: {str(e)}")
        return False