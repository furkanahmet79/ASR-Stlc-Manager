import uvicorn
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from stlc.code_review import router as code_review_router
from routers.test_scenario_generation_router import router as test_scenario_router
from stlc.test_scenario_generation import generate_prompt
import logging
from routers.code_review_router import router as code_review_prompt_router
from routers.requirement_analysis_router import router as requirement_analysis_prompt_router
from stlc.requirement_analysis import router as requirement_analysis_router
from routers.test_planning_router import router as test_planning_router
from stlc.test_planning import router as test_planning_process_router
from stlc.environment_setup import router as environment_setup_router
from routers.environment_setup_router import router as environment_setup_prompt_router

app = FastAPI(
    title="STLC Manager Backend",
    description="STLC Manager Backend API",
    version="0.1.0"
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React uygulamanızın çalıştığı port
        "http://127.0.0.1:3000",
        "*"  # Geliştirme aşamasında tüm originlere izin vermek için
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Router ekleme
app.include_router(code_review_router, prefix="/api/processes/code-review")
app.include_router(test_scenario_router, prefix="/api/processes/test-scenario-generation")
app.include_router(code_review_prompt_router)  # code_review prompt router
app.include_router(requirement_analysis_prompt_router)  # requirement_analysis prompt router
app.include_router(requirement_analysis_router, prefix="/api/processes/requirement_analysis")
app.include_router(test_planning_router)  # test planning prompt router
app.include_router(test_planning_process_router, prefix="/api/processes/test-planning")
app.include_router(environment_setup_router, prefix="/api/processes/environment-setup")
app.include_router(environment_setup_prompt_router)  # environment_setup prompt router

@app.get("/")
def read_root():
    return {"message": "STLC Manager Backend is running!"}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
