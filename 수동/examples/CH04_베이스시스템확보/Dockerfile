# =============================================================
# Dockerfile
# AI 업무 비서 구축: RAG + MCP 실전 가이드 - 4장 베이스 시스템 확보
#
# Python 3.11 슬림 이미지 기반 FastAPI CRUD 서버 컨테이너
# =============================================================

FROM python:3.11-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일만 먼저 복사하여 레이어 캐시를 활용합니다.
COPY requirements.txt .

# 의존성 설치 (캐시 파일 제거로 이미지 크기 최소화)
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 소스 복사
COPY app/ ./app/

# 포트 노출
EXPOSE 8000

# FastAPI 서버 실행 (uvicorn, 핫 리로드 활성화)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
