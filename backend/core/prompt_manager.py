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
    # Yeni koleksiyon adı: code_review_prompt
    if "code_review_prompt" not in db.list_collection_names():
        db.create_collection("code_review_prompt")
        print("code_review_prompt koleksiyonu oluşturuldu.")
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
    existing = db.code_review_prompt.find_one({"process_type": "code_review"})
    if not existing:
        db.code_review_prompt.insert_one(prompt)
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
    Belirtilen süreç için ilgili _prompt koleksiyonundan temel prompt'u çeker.
    """
    logger.info(f"{process_type} süreci için temel prompt çekiliyor.")
    try:
        db = get_db()
        collection_name = f"{process_type}_prompt"
        collection = db[collection_name]
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
    Her session_id için tek bir doküman, code_review için şu alanları kaydeder/günceller:
    - output: code review çıktısı
    - edited_prompt: base prompt değişti mi (True/False)
    - used_prompt: kullanılan prompt metni
    - used_model: kullanılan AI model
    """
    logger.info("Session verisi kaydediliyor/güncelleniyor (code_review için özel alanlar).")
    try:
        db = get_db()
        collection = db["session_history"]
        session_id = session_data.get("session_id")
        output = session_data.get("output")
        edited_prompt = session_data.get("edited_prompt")
        used_prompt = session_data.get("used_prompt")
        used_model = session_data.get("used_model")

        if not session_id or output is None or edited_prompt is None or used_prompt is None:
            logger.warning("Eksik session verisi: session_id, output, edited_prompt veya used_prompt yok.")
            return None

        # Güncellenecek alan: processes.code_review
        update_field = {
            "processes.code_review": {
                "output": output,
                "edited_prompt": edited_prompt,
                "used_prompt": used_prompt,
                "used_model": used_model,
                "timestamp": datetime.now()
            }
        }

        # Upsert işlemi: varsa güncelle, yoksa oluştur
        result = collection.update_one(
            {"session_id": session_id},
            {
                "$set": update_field,
                "$setOnInsert": {
                    "session_id": session_id,
                    "created_at": datetime.now()
                }
            },
            upsert=True
        )
        logger.info(f"Session güncellendi/upsert edildi. session_id: {session_id}, process: code_review")
        return result.upserted_id or result.modified_count
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
        collection = db["code_review_prompt"]
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
    Sadece yeni bir base prompt ekler. Eğer process_type için zaten bir base prompt varsa, hiçbir değişiklik yapmaz.
    Kullanıcılar base promptu değiştiremez.
    :param process_type: Prompt'un ilişkili olduğu süreç türü (ör: code_review)
    :param prompt_text: Kaydedilecek prompt metni
    :return: İşlemin başarılı olup olmadığını belirten boolean değer
    """
    logger.info(f"{process_type} süreci için base prompt ekleniyor (varsa güncellenmeyecek).")
    try:
        db = get_db()
        collection_name = f"{process_type}_prompt"
        collection = db[collection_name]
        # Mevcut prompt'u ara
        existing = collection.find_one({"process_type": process_type})
        if existing:
            logger.warning(f"{process_type} için base prompt zaten mevcut, değiştirilmeyecek.")
            return False
        else:
            # Yeni prompt ekle
            result = collection.insert_one({
                "process_type": process_type,
                "prompt_text": prompt_text,
                "description": f"Base prompt for {process_type} process",
                "created_at": datetime.now()
            })
            success = result.acknowledged
        if success:
            logger.info(f"{process_type} süreci için base prompt başarıyla eklendi.")
        else:
            logger.warning(f"{process_type} süreci için base prompt eklenemedi.")
        return success
    except Exception as e:
        logger.error(f"Base prompt eklenirken hata oluştu: {str(e)}")
        return False