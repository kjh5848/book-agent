"""교차 인코더(Cross-Encoder) 기반 ReRanker 모듈.

벡터 검색으로 가져온 초기 검색 결과를 Cross-Encoder 모델로
재정렬(ReRank)하여 질문과의 관련성이 높은 문서를 상위에 배치합니다.
sentence-transformers 미설치 시 점수 기반 단순 정렬로 fallback합니다.
"""

import os
from typing import Optional

# sentence-transformers 선택적 임포트
try:
    from sentence_transformers import CrossEncoder

    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False

RERANKER_MODEL = os.getenv(
    "RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"
)


class CrossEncoderReRanker:
    """Cross-Encoder 모델을 사용한 검색 결과 재정렬 클래스.

    초기 벡터 검색 결과를 Cross-Encoder에 통과시켜 질문-문서 쌍의
    관련성 점수를 재계산한 뒤, 점수 순으로 상위 문서를 반환합니다.
    sentence-transformers 미설치 시 거리 기반 단순 정렬로 fallback합니다.

    Attributes:
        model_name: Cross-Encoder 모델 이름
        model: CrossEncoder 모델 인스턴스 (미설치 시 None)
        is_fallback_mode: Fallback 모드 활성화 여부
    """

    def __init__(self, model_name: str = RERANKER_MODEL) -> None:
        """CrossEncoderReRanker를 초기화합니다.

        Args:
            model_name: 사용할 Cross-Encoder 모델 이름
                        (기본값: "cross-encoder/ms-marco-MiniLM-L-6-v2")
        """

        # --- Input ---
        self.model_name = model_name
        self.model: Optional[object] = None
        self.is_fallback_mode = False

        # --- Process ---
        if CROSS_ENCODER_AVAILABLE:
            try:
                print(f"  [ReRanker] Cross-Encoder 모델 로딩: {model_name}")
                self.model = CrossEncoder(model_name)
                print(f"  [ReRanker] 모델 로딩 완료")
            except Exception as e:
                print(f"  [경고] Cross-Encoder 모델 로딩 실패: {e}")
                print("  점수 기반 단순 정렬(Fallback) 모드로 전환합니다.")
                self.is_fallback_mode = True
        else:
            print("  [경고] sentence-transformers 패키지가 설치되지 않았습니다.")
            print("  설치 명령어: pip install sentence-transformers")
            print("  점수 기반 단순 정렬(Fallback) 모드로 전환합니다.")
            self.is_fallback_mode = True

        # --- Output ---
        # self.model 또는 Fallback 모드 설정 완료

    def rerank(
        self,
        query: str,
        docs: list[dict],
        top_n: Optional[int] = None,
    ) -> list[dict]:
        """검색 결과를 Cross-Encoder 점수로 재정렬합니다.

        Args:
            query: 사용자 질문 문자열
            docs: 초기 벡터 검색 결과 리스트. 각 항목은 다음 키를 포함합니다:
                  - content (str): 문서 청크 텍스트
                  - source (str): 문서 출처 파일명
                  - score (float, optional): 벡터 검색 유사도 점수
            top_n: 반환할 상위 문서 수. None이면 전체 반환.

        Returns:
            재정렬된 문서 리스트. 각 항목에 rerank_score 키가 추가됩니다.
            rerank_score가 높을수록 질문과의 관련성이 높습니다.
        """

        # --- Input ---
        if not docs:
            return []

        if not query or not query.strip():
            return docs[:top_n] if top_n else docs

        # --- Process ---
        if self.is_fallback_mode:
            # Fallback: 기존 벡터 유사도 점수로 단순 정렬
            sorted_docs = sorted(
                docs,
                key=lambda x: x.get("score", 0.0),
                reverse=True,
            )
            for doc in sorted_docs:
                doc["rerank_score"] = doc.get("score", 0.0)
                doc["rerank_method"] = "fallback_score"

            result_docs = sorted_docs[:top_n] if top_n else sorted_docs
            print(f"  [ReRanker Fallback] {len(result_docs)}개 문서 점수 기반 정렬 완료")
            return result_docs

        # Cross-Encoder 재정렬
        # 질문-문서 쌍 구성
        sentence_pairs = [
            [query, doc.get("content", "")]
            for doc in docs
        ]

        # Cross-Encoder로 관련성 점수 계산
        try:
            scores = self.model.predict(sentence_pairs)
        except Exception as e:
            print(f"  [경고] Cross-Encoder 추론 실패: {e}. Fallback으로 처리합니다.")
            for doc in docs:
                doc["rerank_score"] = doc.get("score", 0.0)
                doc["rerank_method"] = "fallback_score"
            return docs[:top_n] if top_n else docs

        # 점수를 각 문서에 추가하고 내림차순 정렬
        scored_docs = []
        for doc, score in zip(docs, scores):
            doc_copy = doc.copy()
            doc_copy["rerank_score"] = float(score)
            doc_copy["rerank_method"] = "cross_encoder"
            scored_docs.append(doc_copy)

        reranked_docs = sorted(scored_docs, key=lambda x: x["rerank_score"], reverse=True)
        result_docs = reranked_docs[:top_n] if top_n else reranked_docs

        print(
            f"  [ReRanker] {len(docs)}개 → {len(result_docs)}개 재정렬 완료 "
            f"(최고 점수: {result_docs[0]['rerank_score']:.4f})"
        )

        # --- Output ---
        return result_docs

    def compare_before_after(
        self,
        query: str,
        docs: list[dict],
        top_n: int = 3,
    ) -> dict:
        """ReRanking 적용 전후 결과를 비교합니다.

        Args:
            query: 사용자 질문 문자열
            docs: 초기 검색 결과 리스트
            top_n: 비교할 상위 문서 수 (기본값: 3)

        Returns:
            비교 결과 딕셔너리:
            - before (list[dict]): 재정렬 전 상위 top_n 문서
            - after (list[dict]): 재정렬 후 상위 top_n 문서
            - rank_changes (list[dict]): 순위 변화 정보
        """

        # --- Input ---
        before_docs = docs[:top_n]

        # --- Process ---
        after_docs = self.rerank(query=query, docs=docs.copy(), top_n=top_n)

        # 순위 변화 계산: content 앞 20자로 동일 source 내 문서를 고유 식별
        rank_changes: list[dict] = []
        for after_rank, after_doc in enumerate(after_docs, start=1):
            source = after_doc.get("source", "")
            content_key = after_doc.get("content", "")[:20]

            # 원본 docs에서 동일 content 위치로 재정렬 전 순위 탐색
            before_rank = next(
                (
                    i + 1
                    for i, d in enumerate(docs)
                    if d.get("content", "")[:20] == content_key
                ),
                -1,
            )
            change = before_rank - after_rank
            rank_changes.append({
                "source": source,
                "content_preview": content_key,
                "before_rank": before_rank,
                "after_rank": after_rank,
                "rank_change": change,
                "rerank_score": after_doc.get("rerank_score", 0.0),
            })

        # --- Output ---
        return {
            "before": before_docs,
            "after": after_docs,
            "rank_changes": rank_changes,
        }
