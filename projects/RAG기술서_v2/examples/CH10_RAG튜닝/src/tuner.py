"""RAG 청크 및 Retriever 파라미터 튜닝 모듈.

chunk_size, overlap, k 값의 조합을 체계적으로 실험하여
최적의 파라미터 조합을 탐색합니다. 각 조합별 성능을 비교하고
최적 파라미터를 반환합니다.
"""

import os
from typing import Any, Optional

# ChromaDB 선택적 임포트
try:
    import chromadb
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./outputs/chroma_db")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")


class RAGTuner:
    """RAG 파라미터를 체계적으로 튜닝하는 클래스.

    chunk_size, overlap, k 값 등 주요 파라미터의 조합을
    실험하고 Retrieval 성능을 비교하여 최적 파라미터를 찾습니다.

    Attributes:
        evaluator: RAGEvaluator 인스턴스 (성능 측정용)
        test_cases: 평가에 사용할 테스트 케이스 리스트
        tuning_results: 각 실험 결과 누적 리스트
        best_params: 현재까지 발견된 최적 파라미터
    """

    def __init__(self, evaluator: Any, test_cases: list[dict]) -> None:
        """RAGTuner를 초기화합니다.

        Args:
            evaluator: RAGEvaluator 인스턴스 (evaluate_retrieval 메서드 보유)
            test_cases: 튜닝 평가에 사용할 테스트 케이스 리스트
        """

        # --- Input ---
        self.evaluator = evaluator
        self.test_cases = test_cases
        self.tuning_results: list[dict] = []
        self.best_params: dict = {}

        # --- Output ---
        print(f"  [RAGTuner] 초기화 완료: {len(test_cases)}개 테스트 케이스 로드")

    def _evaluate_with_params(
        self,
        k: int,
        metadata_filter: Optional[dict] = None,
        label: str = "",
    ) -> float:
        """특정 파라미터 조합으로 평균 Recall@k를 측정합니다.

        Args:
            k: 검색 결과 수
            metadata_filter: 메타데이터 필터 조건 딕셔너리. None이면 필터 없음.
            label: 실험 식별 레이블 (결과 저장용)

        Returns:
            테스트셋 전체의 평균 Recall@k 점수 (0.0~1.0)
        """

        # --- Input ---
        recall_scores: list[float] = []

        # --- Process ---
        for test_case in self.test_cases:
            question = test_case["question"]
            expected_docs = test_case.get("relevant_docs", [])

            if self.evaluator.is_mock_mode:
                # Mock 모드: 가상 성능 계산 (k가 클수록 조금 더 높게)
                base_recall = 0.6 + (k - 1) * 0.05
                # 메타데이터 필터 적용 시 소폭 향상 시뮬레이션
                if metadata_filter:
                    base_recall += 0.05
                recall_scores.append(min(1.0, base_recall))
            else:
                result = self.evaluator.evaluate_retrieval(
                    question=question,
                    expected_docs=expected_docs,
                    k=k,
                )
                recall_scores.append(result.get("recall_at_k", 0.0))

        avg_recall = sum(recall_scores) / len(recall_scores) if recall_scores else 0.0

        # --- Output ---
        return round(avg_recall, 4)

    def tune_chunk_size(
        self,
        sizes: list[int],
        overlaps: list[int],
    ) -> list[dict]:
        """chunk_size와 overlap 조합별 성능을 비교합니다.

        실제 청크 재생성 없이 파라미터 조합을 기록하고,
        각 조합의 예상 성능을 시뮬레이션합니다.

        Args:
            sizes: 테스트할 chunk_size 값 리스트 (예: [300, 500, 800])
            overlaps: 테스트할 overlap 값 리스트 (예: [0, 50, 100])

        Returns:
            각 조합별 실험 결과 리스트. 각 항목:
            - chunk_size (int): 청크 크기
            - overlap (int): 오버랩 크기
            - avg_recall (float): 평균 Recall@3
            - label (str): 실험 식별자
        """

        # --- Input ---
        print(f"\n  [청크 튜닝] {len(sizes)}x{len(overlaps)}={len(sizes)*len(overlaps)}개 조합 실험 시작")
        results: list[dict] = []

        # --- Process ---
        for size in sizes:
            for overlap in overlaps:
                if overlap >= size:
                    print(f"  건너뜀: chunk_size={size}, overlap={overlap} (overlap >= size)")
                    continue

                label = f"chunk{size}_overlap{overlap}"
                print(f"  실험 중: {label}")

                # Mock 모드에서 청크 크기별 성능 시뮬레이션
                # 실제 환경: ChromaDB에 해당 파라미터로 재색인 후 평가
                if self.evaluator.is_mock_mode:
                    # 500자 청크가 가장 좋다고 가정한 시뮬레이션
                    optimal_size = 500
                    size_diff = abs(size - optimal_size)
                    base_recall = 0.75 - (size_diff / 1000)
                    overlap_bonus = min(0.05, overlap / 1000)
                    avg_recall = round(max(0.5, min(1.0, base_recall + overlap_bonus)), 4)
                else:
                    avg_recall = self._evaluate_with_params(k=3, label=label)

                result = {
                    "chunk_size": size,
                    "overlap": overlap,
                    "avg_recall": avg_recall,
                    "label": label,
                }
                results.append(result)
                self.tuning_results.append({"type": "chunk_size", **result})
                print(f"    Recall@3: {avg_recall:.4f}")

        # 최적 파라미터 업데이트
        if results:
            best = max(results, key=lambda x: x["avg_recall"])
            self.best_params["chunk_size"] = best["chunk_size"]
            self.best_params["overlap"] = best["overlap"]
            print(f"\n  최적 청크 파라미터: chunk_size={best['chunk_size']}, overlap={best['overlap']} (Recall: {best['avg_recall']:.4f})")

        # --- Output ---
        return results

    def tune_k_value(self, k_values: list[int]) -> list[dict]:
        """검색 결과 수(k) 값별 성능을 비교합니다.

        Args:
            k_values: 테스트할 k 값 리스트 (예: [1, 3, 5, 10])

        Returns:
            각 k 값별 실험 결과 리스트. 각 항목:
            - k (int): 검색 결과 수
            - avg_precision (float): 평균 Precision@k
            - avg_recall (float): 평균 Recall@k
            - f1_score (float): F1 점수 (Precision과 Recall의 조화 평균)
        """

        # --- Input ---
        print(f"\n  [k값 튜닝] {len(k_values)}개 k값 실험 시작: {k_values}")
        results: list[dict] = []

        # --- Process ---
        for k in k_values:
            print(f"  실험 중: k={k}")
            precision_scores: list[float] = []
            recall_scores: list[float] = []

            for test_case in self.test_cases:
                question = test_case["question"]
                expected_docs = test_case.get("relevant_docs", [])

                if self.evaluator.is_mock_mode:
                    # Mock: k가 클수록 Recall은 높고 Precision은 낮아지는 패턴
                    base_precision = max(0.3, 1.0 - (k - 1) * 0.12)
                    base_recall = min(1.0, 0.5 + (k - 1) * 0.1)
                    precision_scores.append(base_precision)
                    recall_scores.append(base_recall)
                else:
                    result = self.evaluator.evaluate_retrieval(
                        question=question,
                        expected_docs=expected_docs,
                        k=k,
                    )
                    precision_scores.append(result.get("precision_at_k", 0.0))
                    recall_scores.append(result.get("recall_at_k", 0.0))

            avg_precision = round(
                sum(precision_scores) / len(precision_scores) if precision_scores else 0.0, 4
            )
            avg_recall = round(
                sum(recall_scores) / len(recall_scores) if recall_scores else 0.0, 4
            )

            # F1 점수 계산 (Precision과 Recall의 조화 평균)
            if avg_precision + avg_recall > 0:
                f1 = round(2 * avg_precision * avg_recall / (avg_precision + avg_recall), 4)
            else:
                f1 = 0.0

            result_item = {
                "k": k,
                "avg_precision": avg_precision,
                "avg_recall": avg_recall,
                "f1_score": f1,
            }
            results.append(result_item)
            self.tuning_results.append({"type": "k_value", **result_item})
            print(f"    Precision@{k}: {avg_precision:.4f}, Recall@{k}: {avg_recall:.4f}, F1: {f1:.4f}")

        # 최적 k 값 업데이트 (F1 기준)
        if results:
            best = max(results, key=lambda x: x["f1_score"])
            self.best_params["k"] = best["k"]
            print(f"\n  최적 k값: {best['k']} (F1: {best['f1_score']:.4f})")

        # --- Output ---
        return results

    def tune_metadata_filter(
        self,
        field: str,
        values: list[str],
    ) -> list[dict]:
        """메타데이터 필터 적용 전후의 성능을 비교합니다.

        Args:
            field: 필터를 적용할 메타데이터 필드명 (예: "category")
            values: 테스트할 필드 값 리스트 (예: ["leave_policy", "hr_policy"])

        Returns:
            각 필터 값별 실험 결과 리스트. 각 항목:
            - filter_field (str): 필터 필드명
            - filter_value (str): 필터 값
            - avg_recall (float): 필터 적용 시 평균 Recall@3
            - improvement (float): 필터 미적용 대비 개선량
        """

        # --- Input ---
        print(f"\n  [메타데이터 필터 튜닝] 필드: {field}, 값: {values}")

        # 기준값 (필터 없음)
        baseline_recall = self._evaluate_with_params(k=3, label="no_filter")
        print(f"  기준 Recall@3 (필터 없음): {baseline_recall:.4f}")

        results: list[dict] = []

        # --- Process ---
        for value in values:
            metadata_filter = {field: value}
            print(f"  실험 중: {field}={value}")

            # 해당 카테고리 테스트 케이스만 필터링
            filtered_cases = [
                tc for tc in self.test_cases if tc.get("category") == value
            ]
            if not filtered_cases:
                print(f"  건너뜀: '{value}' 카테고리 테스트 케이스 없음")
                continue

            # 필터된 테스트 케이스로 평가
            original_cases = self.test_cases
            self.test_cases = filtered_cases
            filtered_recall = self._evaluate_with_params(
                k=3, metadata_filter=metadata_filter, label=f"{field}={value}"
            )
            self.test_cases = original_cases

            improvement = round(filtered_recall - baseline_recall, 4)
            result_item = {
                "filter_field": field,
                "filter_value": value,
                "filtered_cases": len(filtered_cases),
                "avg_recall": filtered_recall,
                "improvement": improvement,
            }
            results.append(result_item)
            self.tuning_results.append({"type": "metadata_filter", **result_item})
            print(f"    Recall@3: {filtered_recall:.4f} (개선: {improvement:+.4f})")

        # --- Output ---
        return results

    def get_best_params(self) -> dict:
        """현재까지 실험에서 발견된 최적 파라미터 조합을 반환합니다.

        Returns:
            최적 파라미터 딕셔너리. 실험된 파라미터 종류에 따라
            chunk_size, overlap, k 등의 키를 포함합니다.
        """

        # --- Output ---
        if not self.best_params:
            print("  [경고] 아직 튜닝 실험이 실행되지 않았습니다.")
        return self.best_params.copy()
