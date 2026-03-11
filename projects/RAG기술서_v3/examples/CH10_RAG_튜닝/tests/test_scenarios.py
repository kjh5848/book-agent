"""CH10 대표 시나리오 테스트.

CH09의 테스트를 그대로 유지하며,
CH10 고유 기능(eval_framework, 실험 모듈)을 추가 검증한다.

실행 방법:
    python -m pytest tests/test_scenarios.py -v
또는:
    python tests/test_scenarios.py
"""

from __future__ import annotations

import sys
import os
import unittest

# 프로젝트 루트를 sys.path에 추가
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from src.router import QueryRouter


# ---------------------------------------------------------------------------
# 1. QueryRouter 테스트 (CH08 그대로)
# ---------------------------------------------------------------------------

class TestQueryRouter(unittest.TestCase):
    """QueryRouter 3단계 라우팅 전략 테스트."""

    def setUp(self) -> None:
        """LLM 없이 라우터를 초기화한다."""
        self.router = QueryRouter(llm=None)

    def test_step1_structured_keyword(self) -> None:
        """Step 1: 정형 키워드(연차)를 올바르게 분류한다."""
        result = self.router.classify_query("김민준 연차 잔여일수 알려줘")
        self.assertEqual(result, "structured")

    def test_step1_unstructured_keyword(self) -> None:
        """Step 1: 비정형 키워드(온보딩)를 올바르게 분류한다."""
        result = self.router.classify_query("온보딩 절차가 어떻게 되나요?")
        self.assertEqual(result, "unstructured")

    def test_step1_hybrid_keyword(self) -> None:
        """Step 1: 정형 + 비정형 키워드가 모두 있으면 hybrid로 분류한다."""
        result = self.router.classify_query("매출 합계와 출장 규정 모두 알려줘")
        self.assertEqual(result, "hybrid")

    def test_step1_sales_keyword(self) -> None:
        """Step 1: 매출 키워드를 정형으로 분류한다."""
        result = self.router.classify_query("영업부 11월 매출 합계가 얼마야?")
        self.assertEqual(result, "structured")

    def test_step1_security_keyword(self) -> None:
        """Step 1: 보안 정책 키워드를 비정형으로 분류한다."""
        result = self.router.classify_query("보안 정책에 대해 설명해줘")
        self.assertEqual(result, "unstructured")

    def test_step2_schema_term(self) -> None:
        """Step 2: DB 컬럼명(remaining_days)을 정형으로 분류한다."""
        result = self.router.classify_query("remaining_days가 0인 직원은?")
        self.assertEqual(result, "structured")

    def test_explain_routing_format(self) -> None:
        """explain_routing 반환 형식이 올바른지 확인한다."""
        result = self.router.explain_routing("연차 잔여일수 조회")
        self.assertIn("query", result)
        self.assertIn("step1", result)
        self.assertIn("step2", result)
        self.assertIn("route", result)
        self.assertIn(result["route"], ("structured", "unstructured", "hybrid"))

    def test_default_unstructured(self) -> None:
        """키워드 없는 질문은 기본값 unstructured로 분류된다."""
        result = self.router.classify_query("안녕하세요")
        self.assertEqual(result, "unstructured")


# ---------------------------------------------------------------------------
# 2. 도구 import 테스트 (CH09: mcp_tools → tools/ 분리)
# ---------------------------------------------------------------------------

class TestToolsImport(unittest.TestCase):
    """tools/ 패키지에서 4개 도구가 올바르게 import되는지 테스트."""

    def test_tools_package_import(self) -> None:
        """tools 패키지에서 4개 도구를 import할 수 있다."""
        from src.tools import get_leave_balance, get_sales_sum, list_employees, search_documents
        self.assertTrue(callable(get_leave_balance.invoke))
        self.assertTrue(callable(get_sales_sum.invoke))
        self.assertTrue(callable(list_employees.invoke))
        self.assertTrue(callable(search_documents.invoke))


# ---------------------------------------------------------------------------
# 3. 캐시 테스트 (CH09 신규)
# ---------------------------------------------------------------------------

class TestResponseCache(unittest.TestCase):
    """ResponseCache TTL 기반 캐시 테스트."""

    def test_cache_set_and_get(self) -> None:
        """캐시에 값을 저장하고 조회할 수 있다."""
        from src.cache import ResponseCache
        cache = ResponseCache(ttl=60, max_size=10)
        cache.set("테스트 질문", {"output": "테스트 답변"})
        result = cache.get("테스트 질문")
        self.assertIsNotNone(result)
        self.assertEqual(result["output"], "테스트 답변")

    def test_cache_miss(self) -> None:
        """저장하지 않은 키는 None을 반환한다."""
        from src.cache import ResponseCache
        cache = ResponseCache(ttl=60, max_size=10)
        result = cache.get("존재하지 않는 질문")
        self.assertIsNone(result)

    def test_cache_stats(self) -> None:
        """캐시 통계가 올바른 형식을 반환한다."""
        from src.cache import ResponseCache
        cache = ResponseCache(ttl=60, max_size=10)
        cache.get("miss1")
        cache.set("hit1", {"output": "값"})
        cache.get("hit1")
        stats = cache.stats()
        self.assertIn("hits", stats)
        self.assertIn("misses", stats)
        self.assertIn("hit_rate_percent", stats)
        self.assertEqual(stats["hits"], 1)
        self.assertEqual(stats["misses"], 1)


# ---------------------------------------------------------------------------
# 4. 모니터링 테스트 (CH09 신규)
# ---------------------------------------------------------------------------

class TestTokenTracker(unittest.TestCase):
    """TokenTracker 토큰 사용량 추적 테스트."""

    def test_record_and_summary(self) -> None:
        """토큰 사용량을 기록하고 요약을 조회할 수 있다."""
        from src.monitoring import TokenTracker
        tracker = TokenTracker()
        tracker.record(model="test-model", input_tokens=100, output_tokens=50, operation="test")
        summary = tracker.summary()
        self.assertEqual(summary["total_calls"], 1)
        self.assertEqual(summary["total_input_tokens"], 100)
        self.assertEqual(summary["total_output_tokens"], 50)

    def test_recent_records(self) -> None:
        """최근 기록을 조회할 수 있다."""
        from src.monitoring import TokenTracker
        tracker = TokenTracker()
        for i in range(3):
            tracker.record(model="test", input_tokens=10 * i, output_tokens=5 * i)
        recent = tracker.recent(n=2)
        self.assertEqual(len(recent), 2)


# ---------------------------------------------------------------------------
# 5. 평가 프레임워크 테스트 (CH10 신규)
# ---------------------------------------------------------------------------

class TestEvalFramework(unittest.TestCase):
    """eval_framework 모듈 import 및 기본 기능 테스트."""

    def test_eval_framework_import(self) -> None:
        """eval_framework 모듈을 import할 수 있다."""
        from src import eval_framework
        self.assertTrue(hasattr(eval_framework, "precision_at_k"))
        self.assertTrue(hasattr(eval_framework, "recall_at_k"))

    def test_precision_at_k(self) -> None:
        """Precision@k가 올바른 값을 반환한다."""
        from src.eval_framework import precision_at_k
        retrieved = ["doc1", "doc2", "doc3", "doc4", "doc5"]
        relevant = {"doc1", "doc3"}
        result = precision_at_k(retrieved, relevant, k=5)
        self.assertAlmostEqual(result, 0.4)

    def test_recall_at_k(self) -> None:
        """Recall@k가 올바른 값을 반환한다."""
        from src.eval_framework import recall_at_k
        retrieved = ["doc1", "doc2", "doc3"]
        relevant = {"doc1", "doc3", "doc5"}
        result = recall_at_k(retrieved, relevant, k=3)
        self.assertAlmostEqual(result, 2 / 3)

    def test_test_questions_file(self) -> None:
        """data/test_questions.json이 존재하고 로드할 수 있다."""
        import json
        questions_path = os.path.join(_ROOT, "data", "test_questions.json")
        self.assertTrue(os.path.exists(questions_path))
        with open(questions_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)


# ---------------------------------------------------------------------------
# 6. 튜닝 모듈 import 테스트 (CH10 신규)
# ---------------------------------------------------------------------------

class TestTuningImport(unittest.TestCase):
    """tuning/ 패키지의 핵심 모듈을 import할 수 있는지 테스트."""

    def test_tuning_package_exists(self) -> None:
        """tuning 패키지 디렉토리가 존재한다."""
        tuning_dir = os.path.join(_ROOT, "tuning")
        self.assertTrue(os.path.isdir(tuning_dir))

    def test_tuning_init_import(self) -> None:
        """tuning 패키지를 import할 수 있다."""
        import tuning
        self.assertIsNotNone(tuning)


# ---------------------------------------------------------------------------
# 7. 문서 파싱 모듈 테스트 (CH10 섹션 9)
# ---------------------------------------------------------------------------

class TestDocumentParser(unittest.TestCase):
    """tuning/document_parser 모듈 테스트."""

    def test_import(self) -> None:
        """document_parser 모듈을 import할 수 있다."""
        from tuning import document_parser
        self.assertTrue(hasattr(document_parser, "parse_pdf_library"))
        self.assertTrue(hasattr(document_parser, "parse_pdf_vllm"))
        self.assertTrue(hasattr(document_parser, "compare_strategies"))
        self.assertTrue(hasattr(document_parser, "run_parser_comparison"))

    def test_parse_functions_exist(self) -> None:
        """DOCX, XLSX 파싱 함수가 존재한다."""
        from tuning import document_parser
        self.assertTrue(hasattr(document_parser, "parse_docx_library"))
        self.assertTrue(hasattr(document_parser, "parse_docx_vllm"))
        self.assertTrue(hasattr(document_parser, "parse_xlsx_library"))
        self.assertTrue(hasattr(document_parser, "parse_xlsx_vllm"))

    def test_library_parse_missing_file(self) -> None:
        """존재하지 않는 파일 파싱 시 빈 결과를 반환한다."""
        from tuning.document_parser import parse_pdf_library
        from pathlib import Path
        result = parse_pdf_library(Path("/nonexistent/file.pdf"))
        self.assertIn("strategy", result)
        self.assertEqual(result["strategy"], "library")


# ---------------------------------------------------------------------------
# 8. 문서 캡처 모듈 테스트 (CH10 섹션 10)
# ---------------------------------------------------------------------------

class TestDocumentCapture(unittest.TestCase):
    """tuning/document_capture 모듈 테스트."""

    def test_import(self) -> None:
        """document_capture 모듈을 import할 수 있다."""
        from tuning import document_capture
        self.assertTrue(hasattr(document_capture, "capture_pdf_pages"))
        self.assertTrue(hasattr(document_capture, "capture_docx_images"))
        self.assertTrue(hasattr(document_capture, "capture_xlsx_sheets"))
        self.assertTrue(hasattr(document_capture, "extract_metadata"))
        self.assertTrue(hasattr(document_capture, "ingest_to_vectordb"))
        self.assertTrue(hasattr(document_capture, "run_capture_pipeline"))

    def test_extract_metadata_existing_file(self) -> None:
        """기존 파일의 메타데이터를 추출할 수 있다."""
        from tuning.document_capture import extract_metadata
        from pathlib import Path
        # test_scenarios.py 자체를 테스트 대상으로 사용
        meta = extract_metadata(Path(__file__))
        self.assertIn("filename", meta)
        self.assertIn("size_bytes", meta)
        self.assertGreater(meta["size_bytes"], 0)

    def test_captured_dir_structure(self) -> None:
        """data/captured/ 디렉토리 구조가 존재한다."""
        captured_dir = os.path.join(_ROOT, "data", "captured")
        self.assertTrue(os.path.isdir(captured_dir))


# ---------------------------------------------------------------------------
# 9. 답변 근거 모듈 테스트 (CH10 섹션 11)
# ---------------------------------------------------------------------------

class TestEvidencePipeline(unittest.TestCase):
    """tuning/evidence_pipeline 모듈 테스트."""

    def test_import(self) -> None:
        """evidence_pipeline 모듈을 import할 수 있다."""
        from tuning import evidence_pipeline
        self.assertTrue(hasattr(evidence_pipeline, "retrieve_with_evidence"))
        self.assertTrue(hasattr(evidence_pipeline, "format_evidence_response"))
        self.assertTrue(hasattr(evidence_pipeline, "run_evidence_demo"))

    def test_structured_evidence(self) -> None:
        """정형 질문에 대해 근거를 반환한다."""
        from tuning.evidence_pipeline import retrieve_with_evidence
        result = retrieve_with_evidence("김민준 연차 잔여일수", query_type="structured")
        self.assertIn("answer", result)
        self.assertIn("evidence", result)
        self.assertEqual(result["query_type"], "structured")

    def test_unstructured_evidence(self) -> None:
        """비정형 질문에 대해 근거를 반환한다."""
        from tuning.evidence_pipeline import retrieve_with_evidence
        result = retrieve_with_evidence("연차 사용 규정", query_type="unstructured")
        self.assertIn("answer", result)
        self.assertIn("evidence", result)

    def test_format_evidence(self) -> None:
        """근거 응답 포맷이 올바른 형식을 반환한다."""
        from tuning.evidence_pipeline import retrieve_with_evidence, format_evidence_response
        result = retrieve_with_evidence("연차 규정", query_type="unstructured")
        formatted = format_evidence_response(result)
        self.assertIn("answer", formatted)
        self.assertIn("evidence", formatted)
        self.assertIsInstance(formatted["evidence"], list)


# ---------------------------------------------------------------------------
# 10. 실행 진입점
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestQueryRouter))
    suite.addTests(loader.loadTestsFromTestCase(TestToolsImport))
    suite.addTests(loader.loadTestsFromTestCase(TestResponseCache))
    suite.addTests(loader.loadTestsFromTestCase(TestTokenTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestEvalFramework))
    suite.addTests(loader.loadTestsFromTestCase(TestTuningImport))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentParser))
    suite.addTests(loader.loadTestsFromTestCase(TestDocumentCapture))
    suite.addTests(loader.loadTestsFromTestCase(TestEvidencePipeline))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
