#!/bin/zsh
# ============================================================
# auto-review.sh
# 집필 완료 후 품질 검증 + 회고 자동 실행
#
# 사용법:
#   ./auto-review.sh 수동
#   ./auto-review.sh 자동
#
# Phase 7: v1-chapter-reviewer (챕터별 독자 리뷰)
# Phase 8: v1-lab-reporter     (예제 코드 실행 검증)
# Phase 9: v1-retrospective    (전체 회고)
# ============================================================

MODE=${1:-"수동"}   # 수동 or 자동

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
TARGET_DIR="$PROJECT_DIR/$MODE"
LOG_FILE="$TARGET_DIR/review/auto-review.log"
REVIEW_STATUS_FILE="$TARGET_DIR/review/review_progress.json"

WAIT_MINUTES=300
MAX_RETRIES=6

# ── 헬퍼 함수 ────────────────────────────────────────────

log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
  echo "$msg"
  echo "$msg" >> "$LOG_FILE"
}

init_review_status() {
  if [ ! -f "$REVIEW_STATUS_FILE" ]; then
    python3 -c "
import json, os, glob

target = '$TARGET_DIR'
chapters_dir = os.path.join(target, 'chapters')
examples_dir = os.path.join(target, 'examples')

# 완료된 챕터 목록 수집
chapter_files = sorted(glob.glob(os.path.join(chapters_dir, 'CH*.md')))
chapters = []
for f in chapter_files:
    name = os.path.basename(f)
    num = name[:4]  # CH01, CH02 ...
    has_examples = os.path.isdir(os.path.join(examples_dir, '')) and \
                   len(glob.glob(os.path.join(examples_dir, num + '*'))) > 0
    chapters.append({'id': num, 'file': name, 'has_examples': has_examples})

status = {
    'mode': '$MODE',
    'phase_7_chapter_review': {'status': 'pending', 'completed_chapters': []},
    'phase_8_lab_report': {'status': 'pending', 'completed_chapters': []},
    'phase_9_retrospective': {'status': 'pending'},
    'chapters': chapters
}
with open('$REVIEW_STATUS_FILE', 'w') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)
print('review_progress.json 초기화 완료')
"
  fi
}

get_review_phase() {
  python3 -c "
import json
with open('$REVIEW_STATUS_FILE') as f:
    s = json.load(f)

if s['phase_7_chapter_review']['status'] != 'done':
    done = s['phase_7_chapter_review']['completed_chapters']
    total = len(s['chapters'])
    print(f'phase_7_chapter_review ({len(done)}/{total} 챕터 완료)')
elif s['phase_8_lab_report']['status'] != 'done':
    done = s['phase_8_lab_report']['completed_chapters']
    with_examples = [c for c in s['chapters'] if c['has_examples']]
    print(f'phase_8_lab_report ({len(done)}/{len(with_examples)} 챕터 완료)')
elif s['phase_9_retrospective']['status'] != 'done':
    print('phase_9_retrospective')
else:
    print('all_done')
"
}

is_all_done() {
  python3 -c "
import json
with open('$REVIEW_STATUS_FILE') as f:
    s = json.load(f)
all_done = (
    s['phase_7_chapter_review']['status'] == 'done' and
    s['phase_8_lab_report']['status'] == 'done' and
    s['phase_9_retrospective']['status'] == 'done'
)
print('true' if all_done else 'false')
"
}

build_review_prompt() {
  python3 -c "
import json, os, glob

with open('$REVIEW_STATUS_FILE') as f:
    s = json.load(f)

mode = s['mode']
target = '$TARGET_DIR'

# Phase 7 상태
p7 = s['phase_7_chapter_review']
p7_done = p7['completed_chapters']
all_chapters = [c['id'] for c in s['chapters']]
p7_remaining = [c for c in all_chapters if c not in p7_done]

# Phase 8 상태
p8 = s['phase_8_lab_report']
p8_done = p8['completed_chapters']
example_chapters = [c['id'] for c in s['chapters'] if c['has_examples']]
p8_remaining = [c for c in example_chapters if c not in p8_done]

# Phase 9 상태
p9_done = s['phase_9_retrospective']['status'] == 'done'

prompt = f'''품질 검증 + 회고 파이프라인을 이어서 실행해줘.

프로젝트 폴더: {target}
review_progress.json: {target}/review/review_progress.json

=== 현재 상태 ===
- Phase 7 (챕터 리뷰): {len(p7_done)}/{len(all_chapters)} 완료 | 남은 챕터: {p7_remaining}
- Phase 8 (코드 검증): {len(p8_done)}/{len(example_chapters)} 완료 | 남은 챕터: {p8_remaining}
- Phase 9 (회고): {\"완료\" if p9_done else \"미완료\"}

=== 실행 규칙 ===
--dangerously-skip-permissions 모드. 사용자 승인 없이 자동 진행.

=== Phase 7: 챕터 독자 리뷰 (미완료 챕터만) ===
남은 챕터: {p7_remaining}
각 챕터마다 v1-chapter-reviewer 에이전트 호출:
- 챕터 원고: {target}/chapters/{{챕터ID}}_*.md
- 예제 코드: {target}/examples/{{챕터ID}}_*/
- 보고서 출력: {target}/review/chapter_review_{{챕터ID}}.md
- 스크린샷: {target}/assets/screenshots/{{챕터ID}}/
완료 시 review_progress.json의 phase_7_chapter_review.completed_chapters에 챕터ID 추가.
모든 챕터 완료 시 phase_7_chapter_review.status를 \"done\"으로 업데이트.

=== Phase 8: 예제 코드 실행 검증 (Phase 7 완료 후, 미완료 챕터만) ===
남은 챕터: {p8_remaining}
각 챕터마다 v1-lab-reporter 에이전트 호출:
- 예제 경로: {target}/examples/{{챕터ID}}_*/
- 보고서 출력: {target}/review/lab_report_{{챕터ID}}.md
완료 시 review_progress.json의 phase_8_lab_report.completed_chapters에 챕터ID 추가.
모든 챕터 완료 시 phase_8_lab_report.status를 \"done\"으로 업데이트.

=== Phase 9: 전체 회고 (Phase 8 완료 후) ===
v1-retrospective 에이전트 호출:
- 입력: {target}/review/ 폴더 전체 (verify_*.md, chapter_review_*.md, lab_report_*.md)
- 출력: {target}/review/retrospective.md
완료 시 review_progress.json의 phase_9_retrospective.status를 \"done\"으로 업데이트.
'''
print(prompt)
"
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$TARGET_DIR/review" "$TARGET_DIR/assets/screenshots"
log "=== auto-review 시작 (모드: $MODE) ==="

# book_final.md 존재 확인
if [ ! -f "$TARGET_DIR/book_final.md" ]; then
  log "❌ book_final.md 없음. 집필 완료 후 실행하십시오."
  exit 1
fi

init_review_status
log "대상: $TARGET_DIR"

RETRY=0
while [ $RETRY -lt $MAX_RETRIES ]; do
  log ""
  log "── 시도 $((RETRY+1))/$MAX_RETRIES ──"

  DONE=$(is_all_done)
  if [ "$DONE" = "true" ]; then
    log "✅ 모든 품질 검증 + 회고 완료!"
    break
  fi

  CURRENT_PHASE=$(get_review_phase)
  log "현재 Phase: $CURRENT_PHASE"

  PROMPT=$(build_review_prompt)
  log "Claude 실행 중... (품질 검증 파이프라인)"

  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions -p "$PROMPT"
  EXIT_CODE=$?
  log "Claude 종료 (exit code: $EXIT_CODE)"

  DONE=$(is_all_done)
  if [ "$DONE" = "true" ]; then
    log "✅ 모든 품질 검증 + 회고 완료!"
    break
  fi

  RETRY=$((RETRY+1))
  if [ $RETRY -lt $MAX_RETRIES ]; then
    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단 가능)"
    sleep $((WAIT_MINUTES * 60))
  fi
done

log "=== auto-review 종료 ==="
