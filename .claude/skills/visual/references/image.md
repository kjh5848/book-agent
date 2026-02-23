# 이미지 생성 및 관리 규칙

## 0. 시각 자료 유형별 도구 선택

| 시각 자료 유형 | 도구 | 생성 시점 |
|--------------|------|---------|
| 흐름도·아키텍처·시퀀스 다이어그램 | **Mermaid** | 집필 시 즉시 |
| 개념 설명 삽화·은유 이미지 | **Gemini 이미지** | 집필 완료 후 일괄 생성 |
| 실습 결과 스크린샷 (터미널·UI) | **직접 캡처** | 예제 코드 실행 후 캡처 |

집필 시점에는 Gemini 이미지와 실습 캡처가 없으므로 유형에 맞는 **플레이스홀더**를 삽입한다.
캡션은 집필 시 미리 작성해 둔다.

---

## 1. 플레이스홀더 삽입 (3가지 방식)

### 방식 A — 개념 이미지: 텍스트 설명 플레이스홀더

구체적인 Gemini 프롬프트를 아직 모를 때 사용한다.

```markdown
<!-- [IMAGE PLACEHOLDER: {장번호}_{식별자} — {이미지가 보여줄 내용 한 줄 설명}] -->
*그림 {장번호}-{순번}: {캡션}*
```

**예시:**
```markdown
<!-- [IMAGE PLACEHOLDER: 02_concept_overview — 시스템 전체 구성요소와 데이터 흐름 개요] -->
*그림 2-1: 시스템 전체 구성 개요*
```

### 방식 B — 개념 이미지: Gemini 프롬프트 플레이스홀더

프로젝트 아이콘 사전(§2)을 참고하여 프롬프트까지 확정했을 때 사용한다.

```markdown
<!-- [GEMINI PROMPT: {장번호}_{식별자}]
{§3의 베이스 스타일 + 프로젝트의 아이콘 사전(outline/image-guide.md)을 조합한 완전한 프롬프트}
-->
*그림 {장번호}-{순번}: {캡션}*
```

### 방식 C — 실습 결과: 캡처 필요 플레이스홀더

실습 섹션에서 실제 실행 결과 화면을 캡처해야 할 위치에 삽입한다.
Gemini 이미지가 아니므로 프롬프트 없이 **무엇을 캡처해야 하는지**만 명시한다.

```markdown
<!-- [CAPTURE NEEDED: {장번호}_{식별자} — {캡처할 화면 설명: 어떤 명령어 실행 후 어떤 상태}] -->
*그림 {장번호}-{순번}: {캡션}*
```

**예시:**
```markdown
<!-- [CAPTURE NEEDED: 03_ollama-run — `ollama run deepseek-r1` 실행 직후 터미널 전체 화면 (모델 로딩 완료 프롬프트 표시 상태)] -->
*그림 3-1: Ollama 모델 실행 성공 화면*
```

```markdown
<!-- [CAPTURE NEEDED: 06_query-result — `python src/main.py` 실행 후 터미널에 출력된 질의 응답 결과 전체] -->
*그림 6-2: RAG 질의 응답 결과*
```

---

## 2. 캡처 가이드라인 (방식 C)

실습 캡처 시 아래 기준을 준수한다.

| 항목 | 기준 |
|------|------|
| 캡처 범위 | 터미널 전체 화면 (명령어 입력 줄 포함) |
| 해상도 | Retina/HiDPI 권장, 최소 1280px 너비 |
| 터미널 테마 | 밝거나 어두운 배경 모두 허용, 인쇄 시 흑백 변환 고려 |
| 오류 화면 | 의도적 오류 예시는 빨간 텍스트가 포함된 화면 그대로 캡처 |
| 민감 정보 | API 키, 비밀번호 등 실제 값은 블러 처리 후 캡처 |

---

## 3. Gemini 이미지 베이스 스타일

모든 개념 이미지는 아래 베이스 프롬프트를 기반으로 생성한다.

**베이스 프롬프트:**
```
A minimalist black and white technical diagram with a strict 16:9 aspect ratio
on a solid white background. No shading, no 3D effects, only clean thin line art.
The entire assembly of icons, lines, and text is perfectly centered globally
within the 16:9 frame, leaving generous and equal white space on all sides.
```

### 공통 심볼 패턴

| 대상 | 프롬프트 패턴 |
|------|-------------|
| 사람·사용자 | `minimalist line-art person icon labeled '{레이블}'` |
| 서버·컴퓨터 | `minimalist line-art server rack icon labeled '{레이블}'` |
| 데이터베이스 | `minimalist line-art cylinder database icon labeled '{레이블}'` |
| 문서·파일 더미 | `minimalist line-art stack of papers icon labeled '{레이블}'` |
| AI·모델 | `minimalist line-art brain icon labeled '{레이블}'` |
| 클라우드 | `minimalist line-art cloud icon labeled '{레이블}'` |

> **프로젝트 특화 아이콘**: 레이블·추가 심볼은 `outline/image-guide.md`에 정의한다.

---

## 4. 구도 및 여백 규칙 (Gemini 이미지)

- **Safety Margin**: 도식 전체가 캔버스의 60~70% 내외만 차지
- **Global Centering**: 전체 조립체의 무게 중심을 16:9 프레임 정중앙에 배치

---

## 5. 파일 삽입 및 캡션 규칙 (이미지 준비 완료 후)

플레이스홀더를 실제 이미지로 교체할 때 아래 형식을 사용한다.

```markdown
![{이미지 설명}](./images/{장번호}_{이미지식별자}.png)
*그림 {장번호}-{순번}: {집필 시 미리 작성한 캡션}*
```

- **경로 규칙**: `./images/{N}장_{식별자}.png`
- **파일명 형식**: 영문 소문자, 하이픈 허용 (예: `03장_ollama-run.png`)
- **캡션**: 집필 시 플레이스홀더에 미리 작성한 것을 그대로 사용
