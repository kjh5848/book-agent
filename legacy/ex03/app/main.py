from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import sys

# 프로젝트 루트를 경로에 추가하여 scripts 등을 임포트할 수 있게 함
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from routers.employees import router as employees_router
from routers.leaves import router as leaves_router
from routers.sales import router as sales_router
from routers.ui import router as ui_router
from routers.ingest_ui import router as ingest_ui_router
from routers.qa import router as qa_router

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

app = FastAPI()

if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(ui_router)
app.include_router(ingest_ui_router)
app.include_router(qa_router)
app.include_router(employees_router)
app.include_router(leaves_router)
app.include_router(sales_router)


@app.get("/")
def root():
    return RedirectResponse(url="/admin/dashboard", status_code=302)


if __name__ == "__main__":
    import uvicorn

    print("FastAPI 서버 시작: http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
