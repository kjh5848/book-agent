from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from services.ingest_service import ingest_service
import os

router = APIRouter(prefix="/admin", tags=["Ingest UI"])
templates = Jinja2Templates(directory="app/templates")

@router.get("/ingest", response_class=HTMLResponse)
async def ingest_page(request: Request):
    """인제스트 관리 페이지 (카테고리별 그룹화)"""
    categorized_files = ingest_service.get_categorized_status()
    return templates.TemplateResponse("ingest.html", {
        "request": request, 
        "categories": categorized_files,
        "active_page": "ingest"
    })

@router.post("/ingest/upload")
async def ingest_upload(category: str = Form(...), file: UploadFile = File(...)):
    """파일 업로드 및 카테고리별 저장"""
    content = await file.read()
    ingest_service.save_uploaded_file(content, file.filename, category)
    return RedirectResponse(url="/admin/ingest", status_code=303)

@router.post("/ingest/convert")
async def ingest_convert(file_path: str = Form(...)):
    """파일을 마크다운으로 변환합니다"""
    ingest_service.run_convert(file_path)
    return RedirectResponse(url="/admin/ingest", status_code=303)

@router.post("/ingest/embed")
async def ingest_embed(md_path: str = Form(...)):
    """마크다운 파일을 벡터 DB에 임베딩합니다"""
    ingest_service.run_embed()
    return RedirectResponse(url="/admin/ingest", status_code=303)
