from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from services.qa_service import qa_service

router = APIRouter(prefix="/admin/qa", tags=["QA"])
templates = Jinja2Templates(directory="app/templates")

class QueryRequest(BaseModel):
    query: str

@router.get("/", response_class=HTMLResponse)
async def qa_page(request: Request):
    return templates.TemplateResponse("qa.html", {
        "request": request,
        "active_page": "qa",
        "results": None
    })

@router.post("/query")
async def query_qa(request: QueryRequest):
    try:
        # 1. 하이브리드 검색 수행
        search_results = qa_service.hybrid_search(request.query)
        
        # 2. 답변 생성
        answer = qa_service.get_ai_answer(request.query, search_results)
        
        return {
            "query": request.query,
            "answer": answer,
            "route": search_results["route"],
            "structured_data": search_results["structured"],
            "unstructured_data": search_results["unstructured"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent")
async def query_agent(request: QueryRequest):
    """MCP 에이전트 모드 질문 처리"""
    try:
        result = qa_service.run_agent_mode(request.query)
        return {
            "query": request.query,
            "answer": result["answer"],
            "unstructured_data": result["unstructured"],
            "structured_data": result["structured"],
            "mode": "agent"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

