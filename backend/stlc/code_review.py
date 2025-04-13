from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from services.review_service import ReviewService
import logging
from typing import Optional, List

router = APIRouter()
logger = logging.getLogger("code_review")
review_service = ReviewService()

@router.post("/run")
async def process_code_review(
    files: List[UploadFile] = File(...),
    model: Optional[str] = Form(None),
    custom_prompt: Optional[str] = Form(None)  # Yeni eklenen parametre
):
    try:
        if not files:
            raise HTTPException(status_code=400, detail="No files uploaded.")
        
        logger.info(f"Code review requested with model: {model}")
        # custom_prompt parametresini de geçiriyoruz
        results = await review_service.run_code_review(files, model, custom_prompt)
        return results
    except Exception as e:
        logger.error(f"Code Review Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))