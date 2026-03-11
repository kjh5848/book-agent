#!/bin/zsh
# ============================================================
# auto-resume-auto.sh
# 자동 모드 — 스토리텔링 버전 집필 자동 시작 스크립트
#
# 사용법:
#   chmod +x auto-resume-auto.sh
#   ./auto-resume-auto.sh
#
# 종료: Ctrl+C
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
PROGRESS_FILE="$PROJECT_DIR/자동/progress.json"
LOG_FILE="$PROJECT_DIR/자동/auto-resume.log"

WAIT_MINUTES=300     # 재시작 대기 시간 (분) — 사용량 초기화 5시간 기준
MAX_RETRIES=8        # 자동 모드는 Phase 수가 많으므로 여유 있게 설정

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
writing_concept = p.get('writing_concept', 'storytelling')
story_persona = p.get('story_persona', '스타트업 AI팀')

prompt = f'''자동 모드 집필 프로젝트(스토리텔링 버전)를 이어서 진행해줘.

현재 상태:
- progress.json 위치: 자동/progress.json
- 집필 컨셉: {writing_concept}
- 주인공 팀: {story_persona}
- 현재 Phase: $phase
- Phase 상태: {phase_statuses}
- 챕터 상태: {chapter_statuses}

자동/CLAUDE.md 의 자동 파이프라인 지침에 따라 현재 Phase부터 계속 진행해줘.
--dangerously-skip-permissions 모드이므로 모든 파일 생성/수정을 승인 없이 진행해줘.
Phase 0은 이미 완료됨. 자동/outline/draft.md 가 이미 생성되어 있음.
Phase 1 (기획)부터 시작해줘.

중요: 이 버전은 스토리텔링 컨셉이므로
- plan.md에 writing_concept: storytelling 기록 필수
- plan.md에 story_persona 항목 기록 필수
- 각 챕터 집필 시 storytelling.md 규칙 적용 필수'''

print(prompt)
"
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$(dirname "$LOG_FILE")"
log "=== auto-resume-auto (스토리텔링 버전) 시작 ==="
log "프로젝트: $PROJECT_DIR/자동/"
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
  log "Claude 실행 중... (자동 모드 / 스토리텔링)"

  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions -p "$PROMPT"
  EXIT_CODE=$?

  log "Claude 종료 (exit code: $EXIT_CODE)"

  # 완료 재확인
  BOOK_STATUS=$(get_book_status)
  if [ "$BOOK_STATUS" = "done" ]; then
    log "집필 완료! 통합 원고 생성 중..."
    cd "$PROJECT_DIR"
    python3 .claude/skills/planning/scripts/merge_book.py 자동
    if [ $? -eq 0 ]; then
      log "통합 원고 생성 완료: 자동/book_final.md"
      log "품질 검증 파이프라인 시작..."
      bash "$PROJECT_DIR/auto-review.sh" 자동
    else
      log "통합 원고 생성 실패 — 수동으로 실행: python .claude/skills/planning/scripts/merge_book.py 자동"
    fi
    break
  fi

  RETRY=$((RETRY+1))

  if [ $RETRY -lt $MAX_RETRIES ]; then
    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단 가능)"
    sleep $((WAIT_MINUTES * 60))
  fi

done

log "=== auto-resume-auto 종료 ==="
