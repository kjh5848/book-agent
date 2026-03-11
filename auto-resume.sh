#!/bin/zsh
# ============================================================
# auto-resume.sh
# Claude 사용량 초기화 후 자동 재시작 스크립트
#
# 사용법:
#   chmod +x auto-resume.sh
#   ./auto-resume.sh
#
# 종료: Ctrl+C
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
PROGRESS_FILE="$PROJECT_DIR/수동/progress.json"
LOG_FILE="$PROJECT_DIR/수동/review/auto-resume.log"

WAIT_MINUTES=300     # 재시작 대기 시간 (분) — 사용량 초기화 5시간 기준으로 조정 가능
MAX_RETRIES=5      # 최대 재시도 횟수

# ── 헬퍼 함수 ────────────────────────────────────────────

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

get_book_status() {
  python3 -c "
import json, sys
try:
    with open('$PROGRESS_FILE') as f:
        p = json.load(f)
    print(p.get('status', 'unknown'))
except Exception as e:
    print('error')
"
}

get_current_phase() {
  python3 -c "
import json, sys
try:
    with open('$PROGRESS_FILE') as f:
        p = json.load(f)
    for phase, data in p['phases'].items():
        if data['status'] in ('in_progress', 'pending'):
            print(f'{phase} ({data[\"status\"]})')
            sys.exit(0)
    print('all_done')
except Exception as e:
    print('error')
"
}

build_prompt() {
  local phase
  phase=$(get_current_phase)

  python3 -c "
import json
with open('$PROGRESS_FILE') as f:
    p = json.load(f)

phase_statuses = {k: v['status'] for k, v in p['phases'].items()}
chapter_statuses = {c['number']: c['status'] for c in p.get('chapters', [])}

prompt = f'''수동 모드 집필 프로젝트를 이어서 진행해줘.

현재 상태:
- progress.json 위치: 수동/progress.json
- 현재 Phase: $phase
- Phase 상태: {phase_statuses}
- 챕터 상태: {chapter_statuses}

수동/CLAUDE.md 의 파이프라인 지침에 따라 현재 Phase부터 계속 진행해줘.
--dangerously-skip-permissions 모드이므로 모든 파일 생성/수정을 승인 없이 진행해줘.

중요: 이 실행은 자동 배치 모드다. 사용자에게 승인을 묻지 말고 모든 Phase를 자동으로 진행해줘.
AskUserQuestion 도구를 사용하지 말고, 승인 게이트가 나오면 자동으로 "승인"으로 처리해줘.
Phase 4 집필도 CH01부터 CH10까지 순차적으로 모두 완료해줘.'''

print(prompt)
"
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$(dirname "$LOG_FILE")"
log "=== auto-resume 시작 ==="
log "프로젝트: $PROJECT_DIR"
log "재시작 간격: ${WAIT_MINUTES}분 | 최대 재시도: ${MAX_RETRIES}회"

RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
  log ""
  log "── 시도 $((RETRY+1))/$MAX_RETRIES ──"

  BOOK_STATUS=$(get_book_status)
  if [ "$BOOK_STATUS" = "done" ]; then
    log "집필 완료! 스크립트를 종료합니다."
    break
  fi

  CURRENT_PHASE=$(get_current_phase)
  log "현재 Phase: $CURRENT_PHASE"

  PROMPT=$(build_prompt)
  log "Claude 실행 중..."

  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions -p "$PROMPT"
  EXIT_CODE=$?

  log "Claude 종료 (exit code: $EXIT_CODE)"

  # 완료 재확인
  BOOK_STATUS=$(get_book_status)
  if [ "$BOOK_STATUS" = "done" ]; then
    log "집필 완료! 통합 원고 생성 중..."
    cd "$PROJECT_DIR"
    python3 .claude/skills/planning/scripts/merge_book.py 수동
    if [ $? -eq 0 ]; then
      log "통합 원고 생성 완료: 수동/book_final.md"
      log "품질 검증 파이프라인 시작..."
      bash "$PROJECT_DIR/auto-review.sh" 수동
    else
      log "통합 원고 생성 실패 — 수동으로 실행: python .claude/skills/planning/scripts/merge_book.py 수동"
    fi
    break
  fi

  RETRY=$((RETRY+1))

  if [ $RETRY -lt $MAX_RETRIES ]; then
    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단 가능)"
    sleep $((WAIT_MINUTES * 60))
  fi

done

log "=== auto-resume 종료 ==="
