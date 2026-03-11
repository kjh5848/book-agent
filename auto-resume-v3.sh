#!/bin/zsh
# ============================================================
# auto-resume-v3.sh
# RAG기술서 v3 — Phase 2~6 자동 연속 실행 스크립트
#
# 사용법:
#   chmod +x auto-resume-v3.sh
#   ./auto-resume-v3.sh
#
# 종료: Ctrl+C
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
V3_DIR="$PROJECT_DIR/projects/RAG기술서_v3"
PROGRESS_FILE="$V3_DIR/progress.json"
LOG_FILE="$V3_DIR/review/auto-resume.log"

WAIT_MINUTES=300     # 재시작 대기 시간 (분) — 사용량 초기화 5시간 기준
MAX_RETRIES=9        # Phase 2~6 + 리뷰(7~9)

# ── 헬퍼 함수 ────────────────────────────────────────────

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

get_book_status() {
  python3 -c "
import json
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
    phases = p.get('phases', {})
    for phase_name in ['phase_0','phase_1','phase_2','phase_3','phase_4','phase_5','phase_6']:
        status = phases.get(phase_name, 'unknown')
        if status in ('in_progress', 'pending'):
            print(f'{phase_name} ({status})')
            sys.exit(0)
    print('all_done')
except Exception as e:
    print('error')
"
}

build_prompt() {
  local phase
  phase=$(get_current_phase)

  python3 << 'PYEOF'
import json, os

progress_file = os.environ.get("PROGRESS_FILE_PATH", "")
if not progress_file:
    progress_file = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v3/progress.json"

with open(progress_file) as f:
    p = json.load(f)

phases = p.get("phases", {})
chapters = p.get("chapters", [])
lines = []
for c in chapters:
    ch = c["id"]
    lines.append(f'{ch}: plan={c.get("plan","pending")} code={c.get("code","pending")} toc={c.get("toc","pending")} writing={c.get("writing","pending")}')
chapter_status = "\n".join(lines)

print(f"""RAG기술서 v3 프로젝트를 이어서 진행해줘.

현재 상태:
- 프로젝트: projects/RAG기술서_v3/
- progress.json: projects/RAG기술서_v3/progress.json
- Phase 상태: {phases}
- 챕터 상태:
{chapter_status}

projects/RAG기술서_v3/CLAUDE.md 의 파이프라인 지침에 따라 현재 Phase부터 계속 진행해줘.
--dangerously-skip-permissions 모드이므로 모든 파일 생성/수정을 승인 없이 진행해줘.

=== 최우선 규칙: progress.json 업데이트 (반드시 준수) ===

progress.json 경로: projects/RAG기술서_v3/progress.json

아래 시점마다 즉시 progress.json을 파일로 업데이트해야 한다 (메모리에만 저장 금지):

1. Phase 시작 시: phases.phase_N = "in_progress", current_phase = "phase_N"
2. 챕터별 작업 완료 시: chapters[i].code/toc/writing = "done"
3. Phase 완료 시: phases.phase_N = "done", current_phase = 다음 Phase
4. 컨텍스트 한계 도달 시: 현재까지 진행 상태 반드시 저장

업데이트 방법:
  import json
  with open("projects/RAG기술서_v3/progress.json") as f: p = json.load(f)
  p["phases"]["phase_2"] = "done"
  with open("projects/RAG기술서_v3/progress.json", "w") as f: json.dump(p, f, ensure_ascii=False, indent=2)

progress.json 미업데이트 시 다음 실행에서 같은 작업 반복됨. 절대 빠뜨리지 말 것.

=== 기타 규칙 ===
1. 자동 배치 모드. AskUserQuestion 사용 금지. 모든 Phase 자동 진행.
2. 승인 게이트는 자동 승인.
3. Phase 4 집필은 CH01~CH10 순차 완료.

핵심 참조 파일:
- 설계서: projects/RAG기술서_v3/plan/plan.md
- 챕터 명세: projects/RAG기술서_v3/plan/chapter_spec_CH*.md
- 초안: projects/RAG기술서_v3/outline/draft.md
- 공유 스킬: .claude/skills/
- 공유 에이전트: .claude/agents/
- 레거시 코드: legacy/ex01-1/, legacy/ex02/, legacy/ex03/""")
PYEOF
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$V3_DIR/review" "$V3_DIR/examples" "$V3_DIR/chapters" "$V3_DIR/assets"
log "=== auto-resume-v3 시작 ==="
log "프로젝트: $V3_DIR"
log "재시작 간격: ${WAIT_MINUTES}분 | 최대 재시도: ${MAX_RETRIES}회"

RETRY=0

while [ $RETRY -lt $MAX_RETRIES ]; do
  log ""
  log "── 시도 $((RETRY+1))/$MAX_RETRIES ──"

  BOOK_STATUS=$(get_book_status)
  if [ "$BOOK_STATUS" = "done" ]; then
    log "집필 완료! 통합 원고 생성 중..."
    cd "$PROJECT_DIR"
    python3 .claude/skills/planning/scripts/merge_book.py "projects/RAG기술서_v3"
    if [ $? -eq 0 ]; then
      log "통합 원고 생성 완료: projects/RAG기술서_v3/book_final.md"
      log "품질 검증 파이프라인 시작..."
      bash "$PROJECT_DIR/auto-review-v3.sh"
    else
      log "통합 원고 생성 실패"
    fi
    break
  fi

  CURRENT_PHASE=$(get_current_phase)
  log "현재 Phase: $CURRENT_PHASE"

  if [ "$CURRENT_PHASE" = "all_done" ]; then
    log "모든 Phase 완료. status를 done으로 변경."
    python3 -c "
import json
with open('$PROGRESS_FILE') as f:
    p = json.load(f)
p['status'] = 'done'
with open('$PROGRESS_FILE', 'w') as f:
    json.dump(p, f, ensure_ascii=False, indent=2)
"
    break
  fi

  # 실행 전 상태 스냅샷
  PHASE_BEFORE=$(get_current_phase)
  HASH_BEFORE=$(md5 -q "$PROGRESS_FILE" 2>/dev/null || md5sum "$PROGRESS_FILE" | cut -d' ' -f1)

  PROMPT=$(build_prompt)
  log "Claude 실행 중..."

  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions -p "$PROMPT"
  EXIT_CODE=$?

  log "Claude 종료 (exit code: $EXIT_CODE)"

  # 실행 후 progress.json 변경 여부 검증
  HASH_AFTER=$(md5 -q "$PROGRESS_FILE" 2>/dev/null || md5sum "$PROGRESS_FILE" | cut -d' ' -f1)
  PHASE_AFTER=$(get_current_phase)

  if [ "$HASH_BEFORE" = "$HASH_AFTER" ]; then
    log "⚠️ 경고: progress.json이 변경되지 않음! Claude가 상태를 업데이트하지 않았을 가능성."
    log "  실행 전 Phase: $PHASE_BEFORE"
    log "  실행 후 Phase: $PHASE_AFTER"
  else
    log "✅ progress.json 업데이트 확인됨"
    log "  실행 전 Phase: $PHASE_BEFORE → 실행 후 Phase: $PHASE_AFTER"
  fi

  RETRY=$((RETRY+1))

  if [ $RETRY -lt $MAX_RETRIES ]; then
    # 완료 재확인
    BOOK_STATUS=$(get_book_status)
    if [ "$BOOK_STATUS" = "done" ]; then
      log "집필 완료!"
      continue  # 루프 상단에서 merge 처리
    fi

    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단 가능)"
    sleep $((WAIT_MINUTES * 60))
  fi

done

log "=== auto-resume-v3 종료 ==="
