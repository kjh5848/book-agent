"""LLaVA + EasyOCR 하이브리드 PDF 이미지 처리 모듈.

PDF 내 이미지와 도표를 처리합니다. 텍스트 추출이 불가능한 이미지는
EasyOCR로 텍스트를 추출하고, 설명이 필요한 경우 LLaVA(Ollama)로
이미지 내용을 자연어로 설명합니다. 두 방법 모두 실패 시 안내 메시지를 반환합니다.
"""

import base64
import os
from pathlib import Path
from typing import Optional

# EasyOCR 선택적 임포트
try:
    import easyocr

    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

# PyMuPDF 선택적 임포트 (PDF 이미지 추출용)
try:
    import fitz  # PyMuPDF

    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

# requests (LLaVA API 호출용)
try:
    import requests

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_VISION_MODEL = os.getenv("OLLAMA_VISION_MODEL", "llava")


class VisionExtractor:
    """LLaVA와 EasyOCR을 결합한 하이브리드 이미지 처리 클래스.

    PDF 이미지에서 텍스트를 추출하거나 이미지 내용을 설명합니다.
    EasyOCR은 이미지 내 텍스트 추출(OCR)에, LLaVA는 도표나 차트의
    의미적 설명 생성에 활용됩니다.

    Attributes:
        ocr_reader: EasyOCR Reader 인스턴스 (미설치 시 None)
        ollama_base_url: Ollama API 서버 주소
        vision_model: LLaVA 모델 이름
        easyocr_available: EasyOCR 사용 가능 여부
        llava_available: LLaVA(Ollama) 사용 가능 여부
    """

    def __init__(
        self,
        ocr_languages: list[str] = ["ko", "en"],
        ollama_base_url: str = OLLAMA_BASE_URL,
        vision_model: str = OLLAMA_VISION_MODEL,
    ) -> None:
        """VisionExtractor를 초기화합니다.

        Args:
            ocr_languages: EasyOCR에서 인식할 언어 코드 리스트 (기본값: ["ko", "en"])
            ollama_base_url: Ollama API 서버 주소
            vision_model: LLaVA 모델 이름 (기본값: "llava")
        """

        # --- Input ---
        self.ollama_base_url = ollama_base_url
        self.vision_model = vision_model
        self.ocr_reader = None
        self.easyocr_available = False
        self.llava_available = False

        # --- Process ---
        # EasyOCR 초기화
        if EASYOCR_AVAILABLE:
            try:
                print(f"  [VisionExtractor] EasyOCR 초기화 중... (언어: {ocr_languages})")
                self.ocr_reader = easyocr.Reader(
                    ocr_languages, gpu=False, verbose=False
                )
                self.easyocr_available = True
                print("  EasyOCR 초기화 완료")
            except Exception as e:
                print(f"  [경고] EasyOCR 초기화 실패: {e}")
        else:
            print("  [경고] easyocr 패키지가 설치되지 않았습니다.")
            print("  설치 명령어: pip install easyocr")

        # LLaVA 연결 확인
        if REQUESTS_AVAILABLE:
            self.llava_available = self._check_llava_available()
            if self.llava_available:
                print(f"  LLaVA 연결 확인 완료: {vision_model}")
            else:
                print(f"  [경고] LLaVA 연결 불가: Ollama({ollama_base_url})에 {vision_model} 모델이 없습니다.")
                print(f"  LLaVA 설치: ollama pull {vision_model}")

        # --- Output ---
        # self.ocr_reader 및 연결 상태 설정 완료

    def _check_llava_available(self) -> bool:
        """Ollama에서 LLaVA 모델 사용 가능 여부를 확인합니다.

        Returns:
            LLaVA 모델이 준비되어 있으면 True, 아니면 False
        """

        # --- Process ---
        try:
            resp = requests.get(f"{self.ollama_base_url}/api/tags", timeout=3)
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                model_names = [m.get("name", "") for m in models]
                return any(self.vision_model in name for name in model_names)
        except Exception:
            pass

        # --- Output ---
        return False

    def extract_with_llava(self, image_path: str) -> str:
        """LLaVA 모델로 이미지 내용을 자연어로 설명합니다.

        Args:
            image_path: 이미지 파일 경로 (JPEG, PNG 등)

        Returns:
            LLaVA가 생성한 이미지 설명 문자열.
            LLaVA 미설치 또는 연결 불가 시 안내 메시지를 반환합니다.
        """

        # --- Input ---
        if not self.llava_available:
            return (
                f"이미지 처리 불가 (LLaVA 필요): {os.path.basename(image_path)}\n"
                f"설치 방법: ollama pull {self.vision_model}"
            )

        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            return f"이미지 파일을 찾을 수 없습니다: {image_path}"

        # --- Process ---
        try:
            # 이미지를 base64로 인코딩
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            # Ollama LLaVA API 호출
            payload = {
                "model": self.vision_model,
                "prompt": (
                    "이 이미지에서 보이는 텍스트, 수치, 표, 차트의 내용을 "
                    "한국어로 상세히 설명해 주세요. 중요한 수치나 키워드를 포함하여 설명하십시오."
                ),
                "images": [image_data],
                "stream": False,
            }

            resp = requests.post(
                f"{self.ollama_base_url}/api/generate",
                json=payload,
                timeout=60,
            )

            if resp.status_code == 200:
                result = resp.json()
                description = result.get("response", "")
                if description:
                    return f"[LLaVA 이미지 설명] {description}"
                return "LLaVA 응답이 비어있습니다."
            else:
                return f"LLaVA API 오류 (HTTP {resp.status_code}): {resp.text[:200]}"

        except requests.exceptions.Timeout:
            return "LLaVA 요청 시간 초과 (60초). Ollama 서버 상태를 확인하십시오."
        except Exception as e:
            return f"LLaVA 처리 중 오류: {e}"

        # --- Output ---
        # LLaVA 생성 설명 문자열 반환

    def extract_with_easyocr(self, image_path: str) -> str:
        """EasyOCR로 이미지에서 텍스트를 추출합니다.

        Args:
            image_path: 이미지 파일 경로 (JPEG, PNG 등)

        Returns:
            OCR로 추출된 텍스트 문자열.
            EasyOCR 미설치 또는 텍스트 미검출 시 안내 메시지를 반환합니다.
        """

        # --- Input ---
        if not self.easyocr_available or not self.ocr_reader:
            return (
                f"이미지 처리 불가 (EasyOCR 필요): {os.path.basename(image_path)}\n"
                "설치 방법: pip install easyocr"
            )

        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            return f"이미지 파일을 찾을 수 없습니다: {image_path}"

        # --- Process ---
        try:
            results = self.ocr_reader.readtext(str(image_path))

            if not results:
                return f"텍스트를 감지할 수 없습니다: {os.path.basename(image_path)}"

            # 신뢰도 0.3 이상 텍스트만 추출
            extracted_texts = [
                text
                for _, text, confidence in results
                if confidence >= 0.3
            ]

            if not extracted_texts:
                return f"신뢰도 30% 이상의 텍스트가 없습니다: {os.path.basename(image_path)}"

            extracted = " ".join(extracted_texts)
            return f"[EasyOCR 추출] {extracted}"

        except Exception as e:
            return f"EasyOCR 처리 중 오류: {e}"

        # --- Output ---
        # OCR 추출 텍스트 문자열 반환

    def extract_hybrid(self, pdf_path: str, page_num: int = 0) -> str:
        """PDF 특정 페이지의 이미지를 하이브리드 방식으로 처리합니다.

        처리 순서:
        1. PyMuPDF로 해당 페이지에서 이미지 추출
        2. EasyOCR로 텍스트 추출 시도
        3. OCR 결과가 불충분하면 LLaVA로 이미지 설명 생성

        Args:
            pdf_path: PDF 파일 경로
            page_num: 처리할 페이지 번호 (0부터 시작, 기본값: 0)

        Returns:
            추출된 텍스트 또는 이미지 설명 문자열.
            처리 불가 시 안내 메시지를 반환합니다.
        """

        # --- Input ---
        if not PYMUPDF_AVAILABLE:
            return (
                "PDF 이미지 추출 불가 (PyMuPDF 필요)\n"
                "설치 방법: pip install pymupdf"
            )

        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            return f"PDF 파일을 찾을 수 없습니다: {pdf_path}"

        # --- Process ---
        try:
            doc = fitz.open(str(pdf_path))
            if page_num >= len(doc):
                return f"페이지 번호가 범위를 초과합니다: {page_num} (전체: {len(doc)}페이지)"

            page = doc[page_num]
            image_list = page.get_images(full=True)

            if not image_list:
                return f"페이지 {page_num + 1}에 이미지가 없습니다."

            results: list[str] = []

            for img_index, img_info in enumerate(image_list):
                xref = img_info[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]

                # 임시 이미지 파일 저장
                temp_dir = Path("./outputs/temp_images")
                temp_dir.mkdir(parents=True, exist_ok=True)
                temp_image_path = str(temp_dir / f"page{page_num}_img{img_index}.{image_ext}")

                with open(temp_image_path, "wb") as f:
                    f.write(image_bytes)

                print(f"  이미지 추출: {temp_image_path}")

                # 1단계: EasyOCR로 텍스트 추출 시도
                ocr_result = self.extract_with_easyocr(temp_image_path)

                if (
                    self.easyocr_available
                    and "[EasyOCR 추출]" in ocr_result
                    and len(ocr_result.replace("[EasyOCR 추출]", "").strip()) > 10
                ):
                    # OCR 결과가 충분하면 그대로 사용
                    results.append(ocr_result)
                    print(f"  OCR 성공 (이미지 {img_index + 1})")
                else:
                    # OCR 결과 불충분 → LLaVA로 이미지 설명 생성
                    print(f"  OCR 결과 불충분 → LLaVA로 이미지 설명 시도 (이미지 {img_index + 1})")
                    llava_result = self.extract_with_llava(temp_image_path)
                    results.append(llava_result)

            doc.close()
            final_result = "\n\n".join(results)

        except Exception as e:
            return f"PDF 하이브리드 처리 중 오류: {e}"

        # --- Output ---
        return final_result if final_result else "이미지에서 내용을 추출할 수 없습니다."
