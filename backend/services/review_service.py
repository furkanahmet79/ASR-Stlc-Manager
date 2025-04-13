from utils.file_handler import FileHandler
from utils.model_client import LLMClient
from utils.text_processor import TextProcessor
from core.prompt_manager import get_base_prompt, save_session_data
import logging
import os
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler('review_service.log')  # Dosyaya yazdırma
    ]
)

logger = logging.getLogger("ReviewService")
logger.debug("Test log message - If you see this, logging is working!")

class ReviewService:
    # Sabit tanımlı prompt kaldırıldı - tamamen veritabanından çekilecek

    def __init__(self):
        self.file_handler = FileHandler()
        self.model_client = LLMClient()
        self.text_processor = TextProcessor()
        self.logger = logging.getLogger(__name__)
        self.logger.debug("ReviewService initialized")

    async def run_code_review(self, files, model_key=None, custom_prompt=None):
        try:
            self.logger.debug(f"Starting code review for {len(files)} files with model: {model_key}")
            
            if not files:
                raise ValueError("No files provided for review")
                
            file_paths = await self.file_handler.save_files(files)
            self.logger.debug(f"Files saved: {file_paths}")
            
            if not file_paths:
                raise ValueError("Failed to save uploaded files")
            
            # Model seçimi için LLMClient oluştur
            model_client = LLMClient()
            self.logger.info(f"Model key: {model_key}")
            model_name = None
            if model_key:
                model_name = model_client.get_model_identifier(model_key)
                model_client = LLMClient(model_name)
                self.logger.info(f"Using model: {model_name} for review")
            else:
                self.logger.info("No model specified, using default model")
                
            combined_content = self._combine_file_contents(file_paths)
            self.logger.debug("Files combined successfully")
            
            if not combined_content.strip():
                raise ValueError("No content to review")
            
            # Prompt seçimi - yalnızca veritabanından
            used_prompt = None
            prompt_source = None
            
            if custom_prompt:
                used_prompt = custom_prompt
                prompt_source = "custom_parameter"
                self.logger.info("Using custom prompt provided by user in this request")
            else:
                # Veritabanından özel prompt çek
                db_base_prompt = get_base_prompt("code_review")
                if db_base_prompt:
                    used_prompt = db_base_prompt
                    prompt_source = "base_db"
                    self.logger.info("Using user-edited prompt")
                else:
                    # Veritabanından temel prompt çek
                    db_base_prompt = get_base_prompt("code_review")
                    if db_base_prompt:
                        used_prompt = db_base_prompt
                        prompt_source = "base_db"
                        self.logger.info("Using base prompt from database")
                    else:
                        # Veritabanında prompt yoksa hata fırlat
                        raise ValueError("No prompt found in database for code_review process. Please add a prompt to the database.")
            
            # Prompt'a kodu ekle
            review_prompt = used_prompt.format(code=combined_content)
            
            MAX_TOKENS = 4000
            if len(review_prompt.split()) > MAX_TOKENS:
                self.logger.debug(f"Token limit exceeded: {len(review_prompt.split())} > {MAX_TOKENS}")
                chunks = self.text_processor.chunk_text(review_prompt)
                all_reviews = []
                for i, chunk in enumerate(chunks):
                    self.logger.debug(f"Processing chunk {i+1}/{len(chunks)}")
                    review = await model_client.generate_response(chunk)
                    if review:
                        all_reviews.append(review)
                final_review = self._combine_reviews(all_reviews)
            else:
                self.logger.debug(f"Using single review. Token count: {len(review_prompt.split())}")
                final_review = await model_client.generate_response(review_prompt)
            
            if not final_review:
                raise ValueError("Failed to generate code review")
                
            file_names = [os.path.basename(path) for path in file_paths]
            files_header = "Files analyzed:\n" + "\n".join(file_names)
            
            # Session verilerini kaydet
            session_data = {
            "process_type": "code_review",
            "model_name": model_name,
            "uploaded_files": [
        {
            "file_name": name,
            "file_content": self.file_handler.read_file(path)
        } for name, path in zip(file_names, file_paths)
    ],
    "used_prompt": review_prompt,
    # Eğer custom prompt varsa edited_prompt olarak ekle
    "edited_prompt": custom_prompt if custom_prompt else None
            }
            
            # Prompt metni çok büyük olabileceği için sınırlı bir kısmını kaydet
            session_data["prompt_text_sample"] = used_prompt[:200] + "..." if len(used_prompt) > 200 else used_prompt
            
            # Session verisini kaydet ve session_id'yi al
            save_session_data(session_data)
            
            # Cleanup temporary files
            for path in file_paths:
                try:
                    if os.path.exists(path):
                        os.remove(path)
                except Exception as e:
                    self.logger.warning(f"Failed to remove temporary file {path}: {str(e)}")
            
            return {
                "status": "success",
                "reviews": [{
                    "files": files_header,
                    "review": final_review
                }],
                "prompt_info": {
                    "source": prompt_source
                },
                "session_id": session_data.get("session_id", "unknown")
            }

        except Exception as e:
            self.logger.error(f"Error in run_code_review: {str(e)}")
            raise

    def _combine_file_contents(self, file_paths):
        combined_content = ""
        for path in file_paths:
            code_content = self.file_handler.read_file(path)
            combined_content += f"\n\n### File: {os.path.basename(path)}\n\n{code_content}"
        return combined_content

    def _combine_reviews(self, reviews):
        combined = "\n\n".join(reviews)
        return "# Complete Code Review Summary\n\n" + combined