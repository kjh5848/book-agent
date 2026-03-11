# Large Download Warning Rules

<!-- 대용량 파일이 자동 다운로드되는 경우 독자가 오해하지 않도록 코드 블록 직전에 안내 박스를 삽입하는 규칙 -->

When a large file is automatically downloaded during installation or execution, insert a warning box **immediately before** the code block so readers do not mistake the process for being frozen.

## Trigger Conditions
<!-- 적용 트리거 -->

Apply unconditionally when the following patterns appear.

| Package Manager / Tool | Trigger Example |
|------------------------|-----------------|
| pip | `pip install sentence-transformers`, `pip install torch` |
| npm / npx | `npm install`, `npx playwright install` |
| brew | `brew install` (large formulae) |
| docker | `docker pull`, `docker-compose up` (first image pull) |
| ollama | `ollama pull llama3`, `ollama run` (first model run) |
| cargo | `cargo build` (first build) |
| Other | Cases where large files are downloaded directly via `wget` or `curl` |

## Box Format
<!-- 박스 형식 -->

```markdown
> **주의: First Run — Automatic {target} Download**
> {tool} will automatically download {target} ({size}) on first run.
> Depending on network speed, this may take {estimated time}. Subsequent runs
> will use the cache and start immediately.
```

## Writing Examples
<!-- 작성 예시 -->

### pip — Package Including ML Model
<!-- pip: ML 모델 포함 패키지 -->

```markdown
> **주의: 첫 실행 시 모델 파일 자동 다운로드**
> `sentence-transformers` 패키지는 첫 실행 시 다국어 임베딩 모델(약 470MB)을
> 자동으로 다운로드합니다. 네트워크 속도에 따라 3~10분 소요될 수 있으며,
> 이후 실행부터는 캐시를 사용하므로 즉시 시작됩니다.
```

### npm / npx — Browser Binary
<!-- npm/npx: 브라우저 바이너리 -->

```markdown
> **주의: 첫 실행 시 브라우저 바이너리 자동 다운로드**
> `npx playwright install`은 Chromium·Firefox·WebKit 바이너리(약 300MB)를
> 자동으로 다운로드합니다. 네트워크 속도에 따라 5~15분 소요될 수 있습니다.
```

### docker — First Image Pull
<!-- docker: 이미지 최초 pull -->

```markdown
> **주의: Docker 이미지 최초 다운로드**
> `docker-compose up` 첫 실행 시 필요한 이미지(합계 약 1.2GB)를 Docker Hub에서
> 다운로드합니다. 네트워크 속도에 따라 5~20분 소요될 수 있습니다.
```

### ollama — LLM Model Pull
<!-- ollama: LLM 모델 pull -->

```markdown
> **주의: Ollama 모델 최초 다운로드**
> `ollama pull llama3`는 LLM 모델 파일(약 4.7GB)을 다운로드합니다.
> 네트워크 속도에 따라 10~60분 소요될 수 있으며, 이후 실행부터는
> 로컬 캐시를 사용하므로 즉시 시작됩니다.
```

## Rule Summary
<!-- 규칙 요약 -->

1. **Size threshold**: Insert unconditionally if 100MB or more
2. **Position**: Immediately above the relevant code block (between the explanatory paragraph and the code block)
3. **Box type**: Use the `주의` (Caution) box
4. **Cache notice**: Explicitly state that re-download is not required on subsequent runs (to reassure readers)
5. **When size/time is unknown**: Use a range expression such as "tens to hundreds of MB"
