#!/bin/zsh
# ============================================================
# auto-resume-v4-v3.sh
# v4 스토리텔링 집필 완료 → v3 나머지 작업 + 스크린샷
#
# 사용법:
#   chmod +x auto-resume-v4-v3.sh
#   ./auto-resume-v4-v3.sh
#
# 종료: Ctrl+C
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
V4_DIR="$PROJECT_DIR/projects/RAG기술서_v4"
V3_DIR="$PROJECT_DIR/projects/RAG기술서_v3"
V4_PROGRESS="$V4_DIR/progress.json"
LOG_FILE="$PROJECT_DIR/auto-resume-v4-v3.log"

WAIT_MINUTES=300     # 5시간 (사용량 초과 대기)
MAX_RETRIES=20       # 총 최대 재시도

# ── 헬퍼 함수 ────────────────────────────────────────────

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

get_v4_status() {
  python3 -c "
import json
try:
    with open('$V4_PROGRESS') as f:
        p = json.load(f)
    # 모든 챕터 writing이 done이면 완료
    chapters = p.get('chapters', [])
    pending = [c['id'] for c in chapters if c.get('writing') == 'pending']
    if not pending:
        print('done')
    else:
        print('writing_pending:' + ','.join(pending))
except Exception:
    print('error')
"
}

get_v4_next_chapter() {
  python3 -c "
import json
try:
    with open('$V4_PROGRESS') as f:
        p = json.load(f)
    for c in p.get('chapters', []):
        if c.get('writing') == 'pending':
            print(c['id'])
            break
    else:
        print('none')
except Exception:
    print('error')
"
}

build_v4_prompt() {
  python3 << 'PYEOF'
import json

progress_file = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4/progress.json"

with open(progress_file) as f:
    p = json.load(f)

chapters = p.get("chapters", [])
pending = [c["id"] for c in chapters if c.get("writing") == "pending"]
done = [c["id"] for c in chapters if c.get("writing") == "done"]

lines = []
for c in chapters:
    lines.append(f'{c["id"]}: writing={c.get("writing","pending")}')
chapter_status = "\n".join(lines)

print(f"""RAG기술서 v4 프로젝트(스토리텔링 버전) Phase 4 집필을 이어서 진행해줘.

현재 상태:
- 프로젝트: projects/RAG기술서_v4/
- 집필 컨셉: storytelling (주인공: 메타코딩, 1인 개발자)
- 집필 완료: {', '.join(done)}
- 집필 대기: {', '.join(pending)}
- 챕터별 상태:
{chapter_status}

=== 작업 지시 ===

1. 대기 중인 챕터를 순서대로 집필해줘.
2. 각 챕터 집필 시:
   - plan/chapter_spec_CH{{N}}.md 를 먼저 읽어라
   - outline/TOC.md 에서 해당 챕터 목차를 확인해라
   - examples/CH{{N}}_{{제목}}/ 의 실제 코드를 참조해라
   - 이전 챕터(chapters/CH{{N-1}}_*.md)의 마지막 문단을 읽어 스토리 흐름을 이어라
   - .claude/skills/writing/SKILL.md 와 .claude/skills/writing-concept/SKILL.md 를 로드하여 스킬 규칙을 따라라
3. 집필 후 반드시 progress.json의 해당 챕터 writing을 "done"으로 업데이트해라.

=== 코드 진화 구조 (CH08 → CH09 → CH10) ===
이 세 챕터는 코드가 단계적으로 진화하는 구조다:

CH08(통합 에이전트 설계) = 베이스 코드
  → CH09(LangChain 연결) = CH08을 복사하여 LangChain으로 업그레이드
  → CH10(RAG 튜닝) = CH09를 복사하여 RAG 성능 튜닝 추가

CH09 집필 시:
- CH08 원고(chapters/CH08_*.md)를 먼저 읽고, CH08 코드를 복사한 뒤 LangChain으로 무엇이 달라지는지 대비하여 집필
- 기존 CH09 예제코드에 문제가 있을 수 있으니, CH08 예제코드를 기반으로 LangChain 확장 부분을 설명

CH10 집필 시:
- CH09 원고(chapters/CH09_*.md)를 먼저 읽고, CH09 코드를 복사한 뒤 RAG 튜닝으로 무엇이 달라지는지 대비하여 집필
- 기존 CH10 예제코드 참조하되, CH09 코드 기반으로 튜닝 부분을 설명

=== 스토리텔링 규칙 ===
1. 각 챕터 도입: 메타코딩이 직면한 문제 상황으로 시작
2. 본론: 기술 소개 → 코드 구현 → 실행 결과
3. 마무리: 문제 해결 결과 + before/after 수치 비교
4. 스토리 연속성: 이전 챕터의 결과물이 다음 챕터의 입력이 되는 흐름 유지

=== progress.json 업데이트 (반드시 준수) ===
progress.json 경로: projects/RAG기술서_v4/progress.json
각 챕터 집필 완료 시 즉시 파일로 업데이트:
  import json
  with open("projects/RAG기술서_v4/progress.json") as f: p = json.load(f)
  p["chapters"][N]["writing"] = "done"  # N = 챕터 인덱스
  with open("projects/RAG기술서_v4/progress.json", "w") as f: json.dump(p, f, ensure_ascii=False, indent=2)

=== 기타 규칙 ===
- 자동 배치 모드. AskUserQuestion 사용 금지. 모든 작업 자동 진행.
- 한 세션에서 가능한 만큼 최대한 많은 챕터를 집필해라.
- 컨텍스트 한계 접근 시 반드시 progress.json을 저장하고 종료해라.""")
PYEOF
}

build_v3_prompt() {
  cat << 'V3EOF'
RAG기술서 v3 프로젝트의 남은 작업을 진행해줘.

프로젝트: projects/RAG기술서_v3/

=== 남은 작업 목록 ===

1. CH09 집필 (chapters/CH09_LangChain_연결.md)
   - 코드 진화: CH08 → CH09 (CH08을 복사하여 LangChain으로 업그레이드)
   - CH08 원고(chapters/CH08_통합_에이전트_설계.md)를 먼저 읽고 대비 관점으로 작성
   - CH09 예제코드에 문제가 있으면 CH08 기반으로 수정
   - plan/chapter_spec_CH09.md, outline/TOC.md 참조

2. CH10 집필 (chapters/CH10_RAG_튜닝.md)
   - 코드 진화: CH09 → CH10 (CH09를 복사하여 RAG 튜닝 추가)
   - CH09 원고를 먼저 읽고 대비 관점으로 작성
   - plan/chapter_spec_CH10.md, outline/TOC.md 참조
   - examples/CH10_RAG_튜닝/ 코드 참조

3. 스크린샷 작업
   - 각 챕터의 터미널 실행 결과를 화이트 배경 PNG로 생성 (Playwright HTML→PNG)
   - 웹 UI가 있는 챕터는 브라우저 스크린샷도 생성
   - assets/CH{N}/ 폴더에 저장
   - 챕터 마크다운에 <img> 태그로 연동

4. 데이터 통일 작업 (CH07~09)
   - CH07~09의 인메모리 폴백/mock 데이터를 data/docs/ 실제 문서 파싱으로 대체
   - 상세 계획: .claude/plans/ 에 있는 plan 파일 참조

=== 집필 스타일 ===
- v3는 일반 기술서 스타일 (하십시오체)
- .claude/skills/writing/SKILL.md 규칙 따를 것

=== 규칙 ===
- 자동 배치 모드. AskUserQuestion 사용 금지.
- 한 세션에서 가능한 만큼 최대한 진행.
V3EOF
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$V4_DIR/review" "$V4_DIR/chapters" "$V4_DIR/assets"
log "=== auto-resume-v4-v3 시작 ==="
log "v4 프로젝트: $V4_DIR"
log "v3 프로젝트: $V3_DIR"
log "재시작 간격: ${WAIT_MINUTES}분 | 최대 재시도: ${MAX_RETRIES}회"

RETRY=0
PHASE="v4"  # v4 먼저, 완료되면 v3로 전환

while [ $RETRY -lt $MAX_RETRIES ]; do
  log ""
  log "── 시도 $((RETRY+1))/$MAX_RETRIES (Phase: $PHASE) ──"

  if [ "$PHASE" = "v4" ]; then
    V4_STATUS=$(get_v4_status)
    log "v4 상태: $V4_STATUS"

    if [[ "$V4_STATUS" == "done" ]]; then
      log "✅ v4 집필 완료! v3로 전환합니다."
      # v4 통합 원고 생성
      cd "$PROJECT_DIR"
      python3 .claude/skills/planning/scripts/merge_book.py "projects/RAG기술서_v4" 2>/dev/null
      if [ $? -eq 0 ]; then
        log "v4 통합 원고 생성 완료: book_final.md"
      fi
      PHASE="v3"
      continue
    fi

    NEXT_CH=$(get_v4_next_chapter)
    log "v4 다음 집필: $NEXT_CH"

    HASH_BEFORE=$(md5 -q "$V4_PROGRESS" 2>/dev/null)
    PROMPT=$(build_v4_prompt)
    log "Claude 실행 중... (v4 스토리텔링)"

    cd "$PROJECT_DIR"
    claude --dangerously-skip-permissions -p "$PROMPT" 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=$?

    log "Claude 종료 (exit: $EXIT_CODE)"

    HASH_AFTER=$(md5 -q "$V4_PROGRESS" 2>/dev/null)
    if [ "$HASH_BEFORE" = "$HASH_AFTER" ]; then
      log "⚠️ progress.json 변경 없음"
    else
      log "✅ progress.json 업데이트됨"
    fi

  elif [ "$PHASE" = "v3" ]; then
    log "v3 작업 진행 중..."

    PROMPT=$(build_v3_prompt)
    log "Claude 실행 중... (v3 나머지 + 스크린샷)"

    cd "$PROJECT_DIR"
    claude --dangerously-skip-permissions -p "$PROMPT" 2>&1 | tee -a "$LOG_FILE"
    EXIT_CODE=$?

    log "Claude 종료 (exit: $EXIT_CODE)"

    # v3는 progress.json 기반이 아니므로 반복 횟수로 관리
    if [ $EXIT_CODE -eq 0 ]; then
      log "v3 세션 완료. 다음 세션에서 남은 작업 이어서 진행."
    fi
  fi

  RETRY=$((RETRY+1))

  if [ $RETRY -lt $MAX_RETRIES ]; then
    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단)"
    sleep $((WAIT_MINUTES * 60))
  fi

done

log "=== auto-resume-v4-v3 종료 ==="
