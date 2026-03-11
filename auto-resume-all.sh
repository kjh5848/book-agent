#!/bin/zsh
# ============================================================
# auto-resume-all.sh
# v3 (project-buildup) 완료 후 → v4 (storytelling) 자동 연속 실행
#
# 각 프로젝트: Phase 2~6 집필 → Phase 7~9 리뷰 (MAX_RETRIES=9)
#
# 사용법:
#   chmod +x auto-resume-all.sh
#   ./auto-resume-all.sh
#
# 종료: Ctrl+C
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
LOG_FILE="$PROJECT_DIR/auto-resume-all.log"

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

log "=== v3 + v4 연속 실행 시작 ==="
log "v3: Phase 2~6 집필 → Phase 7~9 리뷰"
log "v4: Phase 1~6 집필 → Phase 7~9 리뷰"

# ── v3 집필 + 리뷰 ──
log "── v3 (project-buildup) 집필 시작 ──"
bash "$PROJECT_DIR/auto-resume-v3.sh"
log "── v3 집필 + 리뷰 종료 ──"

# ── v4 집필 + 리뷰 ──
log "── v4 (storytelling / 메타코딩) 집필 시작 ──"
bash "$PROJECT_DIR/auto-resume-v4.sh"
log "── v4 집필 + 리뷰 종료 ──"

log "=== v3 + v4 연속 실행 완료 ==="
