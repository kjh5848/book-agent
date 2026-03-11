"""MCP 도구 모듈.

LangChain @tool 데코레이터로 정의된 4개의 MCP 도구를 제공한다.
PostgreSQL 연결이 불가능한 경우 인메모리 샘플 데이터로 자동 대체된다.

IPO 패턴:
  Input  - 각 도구별 파라미터 (emp_no, dept, start_date, end_date, query, k)
  Process - DB 조회 또는 인메모리 샘플 데이터 반환
  Output - 구조화된 딕셔너리 (JSON 직렬화 가능)
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional

# LangChain 도구 데코레이터
try:
    from langchain_core.tools import tool
except ImportError:
    def tool(func):  # type: ignore
        """langchain_core 없을 때 무해한 패스스루 데코레이터."""
        return func

# ---------------------------------------------------------------------------
# 1. DB 연결 헬퍼 (인메모리 폴백 포함)
# ---------------------------------------------------------------------------

def _run_query(sql: str, params: tuple = ()) -> list[dict]:
    """PostgreSQL 쿼리를 실행하고 결과를 반환한다.

    연결 실패 시 빈 리스트를 반환하여 인메모리 폴백을 활성화한다.

    Args:
        sql: 실행할 SQL 문자열.
        params: 쿼리 바인딩 파라미터 튜플.

    Returns:
        딕셔너리 리스트 또는 빈 리스트 (연결 실패 시).
    """
    try:
        import psycopg2
        import psycopg2.extras

        db_url = os.getenv("DATABASE_URL", "")
        if not db_url:
            host = os.getenv("POSTGRES_HOST", "localhost")
            port = os.getenv("POSTGRES_PORT", "5432")
            db = os.getenv("POSTGRES_DB", "rag_db")
            user = os.getenv("POSTGRES_USER", "rag_user")
            password = os.getenv("POSTGRES_PASSWORD", "")
            db_url = f"postgresql://{user}:{password}@{host}:{port}/{db}"

        conn = psycopg2.connect(db_url, connect_timeout=3)  # ①
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # ②
        cur.execute(sql, params)  # ③
        rows = [dict(row) for row in cur.fetchall()]  # ④
        cur.close()
        conn.close()
        return rows
    except Exception:
        return []  # DB 없으면 빈 리스트 → 인메모리 폴백 활성화


# ---------------------------------------------------------------------------
# 2. 인메모리 샘플 데이터 함수
# ---------------------------------------------------------------------------

def _get_sample_leave_data() -> list[dict]:
    """연차 잔여 샘플 데이터를 반환한다."""
    return [
        {"emp_no": "E001", "name": "김민준", "department": "영업부", "total_days": 15, "used_days": 7, "remaining_days": 8},
        {"emp_no": "E002", "name": "이서연", "department": "인사부", "total_days": 15, "used_days": 3, "remaining_days": 12},
        {"emp_no": "E003", "name": "박도윤", "department": "개발부", "total_days": 15, "used_days": 10, "remaining_days": 5},
        {"emp_no": "E004", "name": "최아린", "department": "마케팅부", "total_days": 15, "used_days": 5, "remaining_days": 10},
        {"emp_no": "E005", "name": "정시우", "department": "영업부", "total_days": 15, "used_days": 12, "remaining_days": 3},
    ]


def _get_sample_sales_data(dept: str = "", start_date: str = "", end_date: str = "") -> dict:
    """매출 합계 샘플 데이터를 반환한다."""
    all_sales = [
        {"dept": "영업부", "employee_name": "김민준", "amount": 5200000, "sale_date": "2024-11-10"},
        {"dept": "영업부", "employee_name": "정시우", "amount": 3800000, "sale_date": "2024-11-15"},
        {"dept": "마케팅부", "employee_name": "최아린", "amount": 2100000, "sale_date": "2024-11-20"},
        {"dept": "개발부", "employee_name": "박도윤", "amount": 1500000, "sale_date": "2024-11-25"},
        {"dept": "영업부", "employee_name": "김민준", "amount": 4300000, "sale_date": "2024-12-05"},
        {"dept": "마케팅부", "employee_name": "최아린", "amount": 3200000, "sale_date": "2024-12-10"},
    ]
    filtered = [s for s in all_sales if not dept or dept in s["dept"]]
    total = sum(s["amount"] for s in filtered)
    top5 = sorted(filtered, key=lambda x: x["amount"], reverse=True)[:5]
    return {
        "total_amount": total,
        "record_count": len(filtered),
        "dept_filter": dept or "전체",
        "period": f"{start_date or '2024-11-01'} ~ {end_date or '2024-12-31'}",
        "top5": top5,
    }


def _get_sample_employees(dept: str = "") -> list[dict]:
    """직원 목록 샘플 데이터를 반환한다."""
    employees = [
        {"emp_no": "E001", "name": "김민준", "department": "영업부", "position": "과장", "hire_date": "2020-03-02"},
        {"emp_no": "E002", "name": "이서연", "department": "인사부", "position": "대리", "hire_date": "2021-07-15"},
        {"emp_no": "E003", "name": "박도윤", "department": "개발부", "position": "선임", "hire_date": "2019-01-08"},
        {"emp_no": "E004", "name": "최아린", "department": "마케팅부", "position": "주임", "hire_date": "2022-04-11"},
        {"emp_no": "E005", "name": "정시우", "department": "영업부", "position": "사원", "hire_date": "2023-09-01"},
        {"emp_no": "E006", "name": "한지우", "department": "개발부", "position": "팀장", "hire_date": "2017-06-20"},
        {"emp_no": "E007", "name": "오수민", "department": "인사부", "position": "팀장", "hire_date": "2016-02-14"},
        {"emp_no": "E008", "name": "윤재원", "department": "마케팅부", "position": "과장", "hire_date": "2018-11-30"},
        {"emp_no": "E009", "name": "임나연", "department": "영업부", "position": "대리", "hire_date": "2020-08-17"},
        {"emp_no": "E010", "name": "강준호", "department": "개발부", "position": "사원", "hire_date": "2024-01-02"},
    ]
    if dept:
        return [e for e in employees if dept in e["department"]]
    return employees


def _inmemory_search(query: str, k: int = 3) -> list[dict]:
    """data/docs/ 원본 문서를 파싱하여 키워드 기반 검색을 수행한다.

    Args:
        query: 검색 쿼리 문자열.
        k: 반환할 최대 결과 수.

    Returns:
        관련도 순으로 정렬된 문서 딕셔너리 리스트.
    """
    docs_dir = Path(__file__).parent.parent / "data" / "docs"
    parsed_docs = _parse_docs_for_keyword_search(docs_dir)

    if not parsed_docs:
        return [{"content": "data/docs/에 문서가 없습니다.", "source": "system", "score": 0}]

    query_lower = query.lower()
    scored = []
    for doc in parsed_docs:
        score = sum(1 for word in query_lower.split() if word in doc["content"].lower())
        if score > 0:
            scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [
        {"content": d["content"][:300], "source": d["source"], "score": s}
        for s, d in scored[:k]
    ]


def _parse_docs_for_keyword_search(docs_dir: Path) -> list[dict]:
    """data/docs/의 원본 문서를 파싱하여 검색 가능한 딕셔너리 목록으로 반환한다."""
    import pypdf
    from docx import Document as DocxDocument
    import openpyxl

    docs: list[dict] = []
    if not docs_dir.exists():
        return docs

    for file_path in sorted(docs_dir.rglob("*")):
        suffix = file_path.suffix.lower()
        source = file_path.stem

        if suffix == ".pdf":
            try:
                with open(file_path, "rb") as f:
                    reader = pypdf.PdfReader(f)
                    for page in reader.pages:
                        text = (page.extract_text() or "").strip()
                        if text and len(text) > 30:
                            docs.append({"content": text, "source": source})
            except Exception:
                pass
        elif suffix == ".docx":
            try:
                doc = DocxDocument(str(file_path))
                text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
                if text:
                    docs.append({"content": text, "source": source})
            except Exception:
                pass
        elif suffix == ".xlsx":
            try:
                wb = openpyxl.load_workbook(str(file_path), data_only=True)
                for name in wb.sheetnames:
                    ws = wb[name]
                    rows = []
                    for row in ws.iter_rows():
                        cells = [str(c.value).strip() for c in row if c.value is not None]
                        if cells:
                            rows.append(" | ".join(cells))
                    if rows:
                        docs.append({"content": "\n".join(rows), "source": source})
            except Exception:
                pass

    return docs


# ---------------------------------------------------------------------------
# 3. MCP 도구 정의
# ---------------------------------------------------------------------------

@tool
def leave_balance(emp_no: str) -> dict:
    """직원의 연차 잔여 일수를 조회한다.

    직원 번호(E001 형식) 또는 이름으로 연차 정보를 반환한다.
    PostgreSQL 연결 불가 시 샘플 데이터를 반환한다.

    Args:
        emp_no: 직원 번호 (예: "E001") 또는 이름 (예: "김민준").

    Returns:
        직원 연차 정보 딕셔너리. 미발견 시 error 키 포함.
    """
    # ① DB 조회 시도 (이름 또는 번호)
    if emp_no.startswith("E") and emp_no[1:].isdigit():
        rows = _run_query(
            """
            SELECT e.emp_no, e.name, e.department,
                   l.total_days, l.used_days,
                   (l.total_days - l.used_days) AS remaining_days
            FROM employees e
            JOIN leave_balance l ON e.emp_no = l.emp_no
            WHERE e.emp_no = %s
            """,
            (emp_no,),
        )
    else:
        rows = _run_query(
            """
            SELECT e.emp_no, e.name, e.department,
                   l.total_days, l.used_days,
                   (l.total_days - l.used_days) AS remaining_days
            FROM employees e
            JOIN leave_balance l ON e.emp_no = l.emp_no
            WHERE e.name LIKE %s
            """,
            (f"%{emp_no}%",),
        )

    # ② DB 결과가 있으면 반환
    if rows:
        return rows[0]

    # ③ DB 없음 → 인메모리 폴백
    sample = _get_sample_leave_data()
    for record in sample:
        if emp_no in (record["emp_no"], record["name"]):
            return record

    # ④ 이름 부분 일치 검색
    for record in sample:
        if emp_no in record["name"]:
            return record

    return {"error": f"직원 '{emp_no}'을(를) 찾을 수 없습니다.", "available": [r["name"] for r in sample]}


@tool
def sales_sum(dept: str = "", start_date: str = "", end_date: str = "") -> dict:
    """부서별 또는 전체 매출 합계를 조회한다.

    기간 필터와 부서 필터를 적용한 매출 통계를 반환한다.
    PostgreSQL 연결 불가 시 샘플 데이터를 반환한다.

    Args:
        dept: 부서명 (예: "영업부"). 빈 문자열이면 전체 집계.
        start_date: 조회 시작일 (YYYY-MM-DD 형식, 기본값: 2024-11-01).
        end_date: 조회 종료일 (YYYY-MM-DD 형식, 기본값: 2024-12-31).

    Returns:
        total_amount, record_count, top5 등을 포함한 딕셔너리.
    """
    # ① 파라미터 기본값 처리
    start = start_date or "2024-11-01"  # ①
    end = end_date or "2024-12-31"

    # ② DB 조회 시도
    dept_filter = f"AND e.department LIKE '%{dept}%'" if dept else ""
    rows = _run_query(
        f"""
        SELECT e.department, e.name AS employee_name,
               SUM(s.amount) AS total_amount, COUNT(*) AS record_count
        FROM sales s
        JOIN employees e ON s.emp_no = e.emp_no
        WHERE s.sale_date BETWEEN %s AND %s {dept_filter}
        GROUP BY e.department, e.name
        ORDER BY total_amount DESC
        """,
        (start, end),
    )

    # ③ DB 결과 가공
    if rows:
        grand_total = sum(int(r.get("total_amount") or 0) for r in rows)
        return {
            "total_amount": grand_total,
            "record_count": len(rows),
            "dept_filter": dept or "전체",
            "period": f"{start} ~ {end}",
            "top5": rows[:5],
        }

    # ④ 인메모리 폴백
    return _get_sample_sales_data(dept, start, end)


@tool
def list_employees(dept: str = "") -> dict:
    """직원 목록을 조회한다.

    부서명 필터를 적용하여 직원 정보를 반환한다.
    PostgreSQL 연결 불가 시 샘플 데이터를 반환한다.

    Args:
        dept: 부서명 필터 (예: "영업부"). 빈 문자열이면 전체 조회.

    Returns:
        employees 리스트와 count를 포함한 딕셔너리.
    """
    # ① DB 조회 시도
    if dept:
        rows = _run_query(
            "SELECT emp_no, name, department, position, hire_date FROM employees WHERE department LIKE %s ORDER BY name",
            (f"%{dept}%",),
        )
    else:
        rows = _run_query(
            "SELECT emp_no, name, department, position, hire_date FROM employees ORDER BY department, name",
            (),
        )

    # ② DB 결과 반환
    if rows:
        return {"employees": rows, "count": len(rows), "dept_filter": dept or "전체"}

    # ③ 인메모리 폴백
    employees = _get_sample_employees(dept)
    return {
        "employees": employees,
        "count": len(employees),
        "dept_filter": dept or "전체",
    }


@tool
def search_documents(query: str, k: int = 3) -> dict:
    """사내 문서에서 관련 내용을 벡터 검색한다.

    ChromaDB 벡터 검색을 시도하며, 불가 시 키워드 기반 인메모리 검색을 수행한다.

    Args:
        query: 검색 쿼리 (자연어 질문).
        k: 반환할 최대 문서 수 (기본값: 3).

    Returns:
        results 리스트와 total_found를 포함한 딕셔너리.
    """
    # ① ChromaDB 벡터 검색 시도
    try:
        import chromadb
        from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction  # ①

        chroma_path = os.getenv("CHROMA_DB_PATH", "./data/chroma_db")
        client = chromadb.PersistentClient(path=chroma_path)
        collections = client.list_collections()
        if not collections:
            raise ValueError("ChromaDB 컬렉션 없음")

        ef = SentenceTransformerEmbeddingFunction(model_name="jhgan/ko-sroberta-multitask")
        collection = client.get_collection("documents", embedding_function=ef)
        results = collection.query(query_texts=[query], n_results=k)  # ②

        docs = []
        for i, doc in enumerate(results["documents"][0]):
            docs.append({
                "content": doc,
                "source": results["metadatas"][0][i].get("source", "unknown"),
                "score": 1 - results["distances"][0][i],
            })
        return {"results": docs, "total_found": len(docs), "search_mode": "vector"}
    except Exception:
        pass

    # ② 인메모리 키워드 검색 폴백
    docs = _inmemory_search(query, k)  # ②
    return {
        "results": docs,
        "total_found": len(docs),
        "search_mode": "inmemory_keyword",
    }


# ---------------------------------------------------------------------------
# 4. 도구 목록 (에이전트에 전달)
# ---------------------------------------------------------------------------

ALL_TOOLS = [leave_balance, sales_sum, list_employees, search_documents]
