"""
Prompt yönetimi için API endpoint'leri
"""

from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Dict, Any
from core.prompt_manager import (
    get_base_prompt, 
    initialize_base_prompts, 
    save_custom_prompt  # Bu satırı ekleyin
)

router = APIRouter(tags=["prompts"])

class PromptSaveResponse(BaseModel):
    status: str
    message: str
    process_type: str

@router.post("/api/prompts/{process_type}", response_model=PromptSaveResponse)
async def save_prompt(process_type: str, data: Dict[str, Any] = Body(...)):
    try:
        # process_type'ı veritabanındaki karşılığına çevir
        db_process_type = process_type.replace('-', '_')
        
        custom_prompt = data.get("prompt")
        if not custom_prompt:
            raise HTTPException(status_code=400, detail="Prompt content is required")
        
        result = save_custom_prompt(db_process_type, custom_prompt)
        
        if result:
            return {
                "status": "success", 
                "message": "Prompt saved successfully",
                "process_type": process_type
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save prompt")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Gereksiz olan ikinci save_prompt fonksiyonunu kaldırın

class PromptResponse(BaseModel):
    prompt: str
    process_type: str

@router.get("/api/prompts/{process_type}", response_model=PromptResponse)
async def get_prompt(process_type: str):
    """
    Belirli bir process için prompt'u döndürür.
    """
    # process_type'ı veritabanındaki karşılığına çevir
    db_process_type = process_type.replace('-', '_')
    
    # Temel prompt'u kontrol et
    base_prompt = get_base_prompt(db_process_type)
    
    if base_prompt:
        return {"prompt": base_prompt, "process_type": process_type}
    
    # Hiçbir prompt bulunamazsa hata ver
    raise HTTPException(status_code=404, detail=f"Prompt for {process_type} not found")

@router.post("/api/prompts/init", status_code=201)
async def init_prompts():
    """
    Veritabanını temel promptlarla başlatır
    """
    result = initialize_base_prompts()
    
    if result:
        return {"message": "Base prompts initialized successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to initialize base prompts")