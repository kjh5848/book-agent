# [Category 06] 복합 레이아웃(Complex Layout) RAG 최적화 보고서

본 보고서는 **복합 레이아웃(Complex Layout)** 문서에서 발생하는 주요 파싱 문제와, 이를 해결하기 위한 **RAG 최적화 전처리 전략**의 전후 비교를 다룹니다.

---

## 1. Case 1: 영역 분할 (Zone Splitting)
다단 본문 사이에 표가 끼어들어, 텍스트 추출 시 표 데이터와 본문 문장이 뒤섞이는 현상입니다.

| 구분 | 기본 파서 (Default) | RAG 최적화 (Optimized) |
| :--- | :--- | :--- |
| **문제점** | 표의 숫자들이 본문 텍스트 사이에 삽입되어 **문맥 파괴**. | 표 영역을 보호 구역으로 설정하고 페이지를 분할 추출. |

| **결과** | 정보 간섭 (Context Scramble) | **논리적 구조 보존** 및 테이블 포맷 복원. |

### 🔑 Key Code (Solution)
```python
# 표 위치를 기준으로 페이지를 상/중/하로 분할
tables = page.find_tables()
if tables:
    table_bbox = tables[0].bbox
    # 상단 본문 (Zone A)
    zone_a = page.crop((0, 0, width, table_bbox[1]))
    # 하단 본문 (Zone C)
    zone_c = page.crop((0, table_bbox[3], width, height))
```

---

## 2. Case 2: 통합 복합 보고서 (Integrated Complex)
다단, 투명표, 이어지는 표, 사이드바 등 모든 도전 과제가 집약된 5페이지 분량의 문서입니다.

| 구분 | 기본 파서 (Default) | RAG 최적화 (Optimized) |
| :--- | :--- | :--- |
| **문제점** | 페이지가 넘어갈 때 표 헤더가 사라져 **데이터 의미 상실**. | **Header Caching** 기술을 통해 이전 페이지 헤더 복구. |

| **결과** | 검색 및 답변 불가능 (Broken Context) | **고성능 하이브리드 RAG** 구현 가능. |

### 🛠️ 기술 분석 (Technical Analysis)
| 구분 | 내용 (Content) |
| :--- | :--- |
| **Challenges** | Multi-Column, Invisible Table, Continuous Table, Sidebar Noise |
| **Key Tech** | **Layout Orchestration**: 좌표 기반 영역 필터링 및 컬럼 데이터 구조 유지 |
| **Outcome** | 마크다운 내에서 본문과 표, 사이드바가 명확히 분리되어 LLM 몰입도 향상 |
| **Upgrade** | 사용자 피드백을 반영하여 **정보 밀도를 극대화**한 리뉴얼 버전 적용 |

---

## 3. Case 3: 실전 정부공고문 (Government Announcement)
실제 15페이지 분량의 정부 지원사업 공고문을 파싱하여, 중첩된 표 구조와 복잡한 요건 리스트를 논리적으로 재구성합니다.

| 구분 | 기본 파서 (Default) | RAG 최적화 (Optimized) |
| :--- | :--- | :--- |
| **문제점** | 지원 자격과 제외 요건 표가 단순 텍스트로 추출되어 **조건 해석 오류** 발생. | **Table Isolation & Pandas Bridge** 전략으로 표 구조를 Markdown Table로 완벽 복원. |

| **결과** | 지원 금액 및 요건 매칭 실패 (Logic Break) | **정규 규격 마크다운**을 통한 LLM 추론 정확도 극대화. |

### 🔑 Key Code (Solution)
```python
# 표와 본문의 기하학적 격리
tables = page.find_tables()
table_bboxes = [t.bbox for t in tables]
def is_not_in_table(obj):
    return all(not (b[0] <= obj["x0"] <= b[2] and b[1] <= obj["top"] <= b[3]) for b in table_bboxes)

# Pandas를 통한 마크다운 표 변환
df = pd.DataFrame(table_data)
md_table = df.to_markdown(index=False)
```
