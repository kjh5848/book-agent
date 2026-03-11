"""RAG 시스템 평가 모듈.

테스트셋 30개를 기반으로 Retrieval 정확도(Precision@k, Recall@k)와
답변 품질(키워드 포함 여부)을 측정하고 카테고리별 리포트를 생성합니다.
"""

import json
import os
from datetime import datetime
from typing import Optional

# ChromaDB 선택적 임포트
try:
    import chromadb

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "connecthr_docs")


class RAGEvaluator:
    """RAG 시스템 성능을 체계적으로 평가하는 클래스.

    테스트셋을 순서대로 실행하여 Retrieval 정확도와 답변 품질을
    측정하고, 카테고리별로 집계된 평가 리포트를 생성합니다.

    Attributes:
        chroma_client: ChromaDB 클라이언트 인스턴스
        collection: ChromaDB 컬렉션
        collection_name: 컬렉션 이름
        is_mock_mode: ChromaDB 미설치 시 Mock 모드 활성화 여부
    """

    def __init__(self, collection_name: str = CHROMA_COLLECTION) -> None:
        """RAGEvaluator를 초기화합니다.

        Args:
            collection_name: 평가에 사용할 ChromaDB 컬렉션 이름
        """

        # --- Input ---
        self.collection_name = collection_name
        self.chroma_client = None
        self.collection = None
        self.is_mock_mode = False

        # --- Process ---
        if CHROMADB_AVAILABLE:
            try:
                self.chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
                self.collection = self.chroma_client.get_or_create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
                print(f"  [RAGEvaluator] ChromaDB 연결 완료: {collection_name}")
            except Exception as e:
                print(f"  [경고] ChromaDB 연결 실패: {e}")
                print("  Mock 모드로 전환합니다.")
                self.is_mock_mode = True
        else:
            print("  [경고] chromadb 패키지가 설치되지 않았습니다. Mock 모드로 실행합니다.")
            self.is_mock_mode = True

        # --- Output ---
        # self.collection 또는 Mock 모드 설정 완료

    def evaluate_retrieval(
        self,
        question: str,
        expected_docs: list[str],
        k: int = 3,
    ) -> dict[str, float]:
        """단일 질문에 대한 Retrieval 정확도를 계산합니다.

        Args:
            question: 평가할 질문 문자열
            expected_docs: 기대되는 관련 문서 파일명 리스트 (예: ["leave_rules.txt"])
            k: 검색 결과 수 (기본값: 3)

        Returns:
            평가 결과 딕셔너리:
            - precision_at_k (float): Precision@k (0.0~1.0)
            - recall_at_k (float): Recall@k (0.0~1.0)
            - retrieved_docs (list[str]): 실제 검색된 문서명 리스트
        """

        # --- Input ---
        if self.is_mock_mode:
            # Mock 모드: 랜덤 유사 성능 시뮬레이션
            import random

            mock_retrieved = expected_docs[:] + ["mock_doc.txt"] * max(0, k - len(expected_docs))
            mock_retrieved = mock_retrieved[:k]
            relevant_retrieved = [d for d in mock_retrieved if d in expected_docs]
            precision = len(relevant_retrieved) / k if k > 0 else 0.0
            recall = len(relevant_retrieved) / len(expected_docs) if expected_docs else 0.0
            return {
                "precision_at_k": round(precision, 4),
                "recall_at_k": round(recall, 4),
                "retrieved_docs": mock_retrieved,
            }

        # --- Process ---
        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=min(k, max(1, self.collection.count())),
                include=["documents", "metadatas", "distances"],
            )

            # 검색된 문서의 소스 파일명 추출
            retrieved_sources: list[str] = []
            metadatas = results.get("metadatas", [[]])[0]
            for meta in metadatas:
                source = meta.get("source", "")
                # 파일 경로에서 파일명만 추출
                source_name = os.path.basename(source)
                retrieved_sources.append(source_name)

            # Precision@k: 검색된 k개 중 실제 관련 문서 비율
            relevant_retrieved = [s for s in retrieved_sources if s in expected_docs]
            precision = len(relevant_retrieved) / k if k > 0 else 0.0

            # Recall@k: 전체 관련 문서 중 검색된 비율
            recall = len(relevant_retrieved) / len(expected_docs) if expected_docs else 0.0

        except Exception as e:
            print(f"  [경고] Retrieval 평가 중 오류: {e}")
            return {"precision_at_k": 0.0, "recall_at_k": 0.0, "retrieved_docs": []}

        # --- Output ---
        return {
            "precision_at_k": round(precision, 4),
            "recall_at_k": round(recall, 4),
            "retrieved_docs": retrieved_sources,
        }

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        expected_keywords: list[str],
    ) -> dict[str, float]:
        """답변의 키워드 포함 여부로 답변 품질을 평가합니다.

        Args:
            question: 원본 질문 문자열
            answer: RAG 시스템이 생성한 답변 문자열
            expected_keywords: 답변에 포함되어야 할 키워드 리스트

        Returns:
            평가 결과 딕셔너리:
            - keyword_score (float): 키워드 포함 비율 (0.0~1.0)
            - found_keywords (list[str]): 답변에서 발견된 키워드 리스트
            - missing_keywords (list[str]): 답변에서 누락된 키워드 리스트
        """

        # --- Input ---
        if not answer or not expected_keywords:
            return {
                "keyword_score": 0.0,
                "found_keywords": [],
                "missing_keywords": expected_keywords,
            }

        # --- Process ---
        answer_lower = answer.lower()
        found_keywords: list[str] = []
        missing_keywords: list[str] = []

        for keyword in expected_keywords:
            if keyword.lower() in answer_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        keyword_score = len(found_keywords) / len(expected_keywords)

        # --- Output ---
        return {
            "keyword_score": round(keyword_score, 4),
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
        }

    def run_evaluation(
        self,
        test_cases: list[dict],
        rag_answers: Optional[dict[int, str]] = None,
        k: int = 3,
    ) -> list[dict]:
        """전체 테스트셋에 대해 평가를 실행합니다.

        Args:
            test_cases: 테스트 케이스 리스트 (test_cases.json 형식)
            rag_answers: 테스트 ID → 답변 문자열 딕셔너리. None이면 답변 평가 생략.
            k: Retrieval 검색 결과 수 (기본값: 3)

        Returns:
            각 테스트 케이스별 평가 결과 리스트. 각 항목:
            - id (int): 테스트 케이스 ID
            - question (str): 질문
            - category (str): 카테고리
            - retrieval (dict): Precision@k, Recall@k 결과
            - answer_quality (dict): 키워드 점수 결과 (rag_answers 제공 시)
        """

        # --- Input ---
        print(f"\n  [평가 시작] 총 {len(test_cases)}개 테스트 케이스, k={k}")
        results: list[dict] = []

        # --- Process ---
        for i, test_case in enumerate(test_cases, start=1):
            test_id = test_case["id"]
            question = test_case["question"]
            expected_docs = test_case.get("relevant_docs", [])
            expected_keywords = test_case.get("expected_keywords", [])
            category = test_case.get("category", "unknown")

            print(f"  평가 중 [{i}/{len(test_cases)}]: {question[:40]}...")

            # Retrieval 평가
            retrieval_result = self.evaluate_retrieval(
                question=question,
                expected_docs=expected_docs,
                k=k,
            )

            # 답변 품질 평가 (rag_answers 제공 시)
            answer_quality_result: Optional[dict] = None
            if rag_answers and test_id in rag_answers:
                answer = rag_answers[test_id]
                answer_quality_result = self.evaluate_answer(
                    question=question,
                    answer=answer,
                    expected_keywords=expected_keywords,
                )

            result_item = {
                "id": test_id,
                "question": question,
                "category": category,
                "retrieval": retrieval_result,
            }
            if answer_quality_result:
                result_item["answer_quality"] = answer_quality_result

            results.append(result_item)

        print(f"  [평가 완료] {len(results)}개 케이스 처리")

        # --- Output ---
        return results

    def generate_report(self, results: list[dict]) -> dict:
        """평가 결과를 카테고리별로 집계하여 리포트를 생성합니다.

        Args:
            results: run_evaluation()이 반환한 평가 결과 리스트

        Returns:
            리포트 딕셔너리:
            - summary (dict): 전체 평균 Precision@k, Recall@k, keyword_score
            - by_category (dict): 카테고리별 평균 점수
            - total_cases (int): 전체 테스트 케이스 수
            - generated_at (str): 리포트 생성 시각 (ISO 형식)
        """

        # --- Input ---
        if not results:
            return {"error": "평가 결과가 없습니다.", "total_cases": 0}

        # --- Process ---
        # 카테고리별 집계
        category_stats: dict[str, dict[str, list[float]]] = {}
        all_precisions: list[float] = []
        all_recalls: list[float] = []
        all_keyword_scores: list[float] = []

        for result in results:
            category = result.get("category", "unknown")
            if category not in category_stats:
                category_stats[category] = {
                    "precisions": [],
                    "recalls": [],
                    "keyword_scores": [],
                    "count": 0,
                }

            retrieval = result.get("retrieval", {})
            precision = retrieval.get("precision_at_k", 0.0)
            recall = retrieval.get("recall_at_k", 0.0)

            category_stats[category]["precisions"].append(precision)
            category_stats[category]["recalls"].append(recall)
            all_precisions.append(precision)
            all_recalls.append(recall)

            # 답변 품질 점수 (있는 경우만)
            answer_quality = result.get("answer_quality")
            if answer_quality:
                keyword_score = answer_quality.get("keyword_score", 0.0)
                category_stats[category]["keyword_scores"].append(keyword_score)
                all_keyword_scores.append(keyword_score)

        # 전체 요약 통계
        avg_precision = sum(all_precisions) / len(all_precisions) if all_precisions else 0.0
        avg_recall = sum(all_recalls) / len(all_recalls) if all_recalls else 0.0
        avg_keyword = sum(all_keyword_scores) / len(all_keyword_scores) if all_keyword_scores else 0.0

        # 카테고리별 요약
        by_category: dict[str, dict] = {}
        for category, stats in category_stats.items():
            precisions = stats["precisions"]
            recalls = stats["recalls"]
            keyword_scores = stats["keyword_scores"]
            by_category[category] = {
                "count": len(precisions),
                "avg_precision_at_k": round(
                    sum(precisions) / len(precisions) if precisions else 0.0, 4
                ),
                "avg_recall_at_k": round(sum(recalls) / len(recalls) if recalls else 0.0, 4),
                "avg_keyword_score": round(
                    sum(keyword_scores) / len(keyword_scores) if keyword_scores else 0.0, 4
                ),
            }

        report = {
            "total_cases": len(results),
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "avg_precision_at_k": round(avg_precision, 4),
                "avg_recall_at_k": round(avg_recall, 4),
                "avg_keyword_score": round(avg_keyword, 4),
                "overall_score": round((avg_precision + avg_recall) / 2, 4),
            },
            "by_category": by_category,
        }

        # --- Output ---
        return report

    def save_report(self, results: list[dict], output_path: str) -> None:
        """평가 리포트를 JSON 파일로 저장합니다.

        Args:
            results: run_evaluation()이 반환한 평가 결과 리스트
            output_path: 저장할 JSON 파일 경로

        Raises:
            OSError: 출력 경로에 파일을 생성할 수 없는 경우
        """

        # --- Input ---
        report = self.generate_report(results)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # --- Process ---
        save_data = {
            "report": report,
            "detailed_results": results,
        }

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            print(f"  [저장 완료] 리포트 저장: {output_path}")
        except OSError as e:
            raise OSError(
                f"리포트를 저장할 수 없습니다: {output_path}\n원인: {e}"
            ) from e

        # --- Output ---
        # output_path에 JSON 파일 저장 완료
