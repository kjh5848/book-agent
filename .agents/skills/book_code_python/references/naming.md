# 파이썬 실습 코드 작성 규칙 (네이밍 및 포맷팅)

안티그래비티가 `[프로젝트_출력_루트]/examples/` (예: `anti_v2_book/examples/`) 에 코드를 작성하거나 본문에 스니펫을 작성할 때 지켜야 할 파이썬 코드 규칙입니다.

### 1. 전역 원칙 (User Global Rules)
- **모든 주석은 한국어로 기입합니다.** (영어로 된 주석 절대 금지)
- 터미널이나 가상환경에서 스크립트를 테스트할 때는 반드시 해당 프로젝트의 가상 환경(venv, conda 등)에 접근해 명령어를 실행하십시오.

### 2. 코드 스타일 가이드
- **의존성 명시**: 파일 최상단에 주석으로 `pip install 구문`을 명시해 독자가 무엇부터 깔아야 하는지 알려줍니다.
- **가독성 타겟**: 초보자 지향이므로 너무 Pythonic 한 압축된 List Comprehension 등을 남발하기보다는, `for` 문이나 명시적인 `if` 문을 써서 동작 과정을 투명하게 보여주는 것을 우선합니다.
- **명명 규칙 (Naming)**:
  - 함수/단일 변수: `snake_case` (예: `extract_text_from_pdf`)
  - 클래스: `PascalCase` (예: `DocumentParser`)
  - 상수: `UPPER_SNAKE_CASE` (예: `MAX_RETRY_COUNT`)

### 3. 타입 힌트 (Type Hinting)
- 함수 파라미터와 리턴 값에는 최대한 타입 힌팅(Type Hinting)을 적어주어 초보자가 직관적으로 데이터 흐름을 추적할 수 있도록 돕습니다.
- 예: `def process_data(user_id: int) -> dict:`
