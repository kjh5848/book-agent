"""CH04 서버 실행 스크립트."""

import os

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    import uvicorn

    host = os.getenv("FASTAPI_HOST", "0.0.0.0")
    port = int(os.getenv("FASTAPI_PORT", "8000"))

    print("=" * 55)
    print("  Q/A 사내 AI 사내 시스템 (CH04)")
    print(f"  Admin UI : http://localhost:{port}/admin/dashboard")
    print(f"  API 문서 : http://localhost:{port}/docs")
    print("=" * 55)

    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=True,
    )
