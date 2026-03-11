#!/bin/zsh
# ============================================================
# auto-review-v4.sh
# RAG기술서 v4 (스토리텔링) — 품질 검증 + 회고 자동 실행
#
# Phase 7: v1-chapter-reviewer (챕터별 독자 리뷰)
# Phase 8: v1-lab-reporter     (예제 코드 실행 검증)
# Phase 9: v1-retrospective    (전체 회고)
# ============================================================

PROJECT_DIR="/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude"
TARGET_DIR="$PROJECT_DIR/projects/RAG기술서_v4"
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
    python3 << 'PYEOF'
import json, os, glob

target = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4"
chapters_dir = os.path.join(target, "chapters")
examples_dir = os.path.join(target, "examples")
review_file = os.path.join(target, "review", "review_progress.json")

chapter_files = sorted(glob.glob(os.path.join(chapters_dir, "CH*.md")))
chapters = []
for f in chapter_files:
    name = os.path.basename(f)
    num = name[:4]
    has_examples = len(glob.glob(os.path.join(examples_dir, num + "*"))) > 0
    chapters.append({"id": num, "file": name, "has_examples": has_examples})

status = {
    "project": "RAG기술서_v4",
    "writing_concept": "storytelling",
    "story_persona": "메타코딩",
    "phase_7_chapter_review": {"status": "pending", "completed_chapters": []},
    "phase_8_lab_report": {"status": "pending", "completed_chapters": []},
    "phase_9_retrospective": {"status": "pending"},
    "chapters": chapters
}
with open(review_file, "w") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)
print("review_progress.json 초기화 완료")
PYEOF
  fi
}

get_review_phase() {
  python3 << 'PYEOF'
import json

review_file = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4/review/review_progress.json"
with open(review_file) as f:
    s = json.load(f)

if s["phase_7_chapter_review"]["status"] != "done":
    done = s["phase_7_chapter_review"]["completed_chapters"]
    total = len(s["chapters"])
    print(f"phase_7_chapter_review ({len(done)}/{total} 챕터 완료)")
elif s["phase_8_lab_report"]["status"] != "done":
    done = s["phase_8_lab_report"]["completed_chapters"]
    with_examples = [c for c in s["chapters"] if c["has_examples"]]
    print(f"phase_8_lab_report ({len(done)}/{len(with_examples)} 챕터 완료)")
elif s["phase_9_retrospective"]["status"] != "done":
    print("phase_9_retrospective")
else:
    print("all_done")
PYEOF
}

is_all_done() {
  python3 << 'PYEOF'
import json

review_file = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4/review/review_progress.json"
with open(review_file) as f:
    s = json.load(f)
all_done = (
    s["phase_7_chapter_review"]["status"] == "done" and
    s["phase_8_lab_report"]["status"] == "done" and
    s["phase_9_retrospective"]["status"] == "done"
)
print("true" if all_done else "false")
PYEOF
}

build_review_prompt() {
  python3 << 'PYEOF'
import json

target = "/Users/nomadlab/Desktop/김주혁/workspace/coding-study/집필에이전트-claude/projects/RAG기술서_v4"
review_file = target + "/review/review_progress.json"

with open(review_file) as f:
    s = json.load(f)

p7 = s["phase_7_chapter_review"]
p7_done = p7["completed_chapters"]
all_chapters = [c["id"] for c in s["chapters"]]
p7_remaining = [c for c in all_chapters if c not in p7_done]

p8 = s["phase_8_lab_report"]
p8_done = p8["completed_chapters"]
example_chapters = [c["id"] for c in s["chapters"] if c["has_examples"]]
p8_remaining = [c for c in example_chapters if c not in p8_done]

p9_done = s["phase_9_retrospective"]["status"] == "done"

print(f"""품질 검증 + 회고 파이프라인을 이어서 실행해줘. (스토리텔링 버전 / 메타코딩)

프로젝트 폴더: {target}
review_progress.json: {target}/review/review_progress.json
집필 컨셉: storytelling (주인공: 메타코딩)

=== 현재 상태 ===
- Phase 7 (챕터 리뷰): {len(p7_done)}/{len(all_chapters)} 완료 | 남은 챕터: {p7_remaining}
- Phase 8 (코드 검증): {len(p8_done)}/{len(example_chapters)} 완료 | 남은 챕터: {p8_remaining}
- Phase 9 (회고): {"완료" if p9_done else "미완료"}

=== 실행 규칙 ===
--dangerously-skip-permissions 모드. 사용자 승인 없이 자동 진행.
AskUserQuestion 사용 금지.

=== 최우선 규칙: review_progress.json 업데이트 (반드시 준수) ===

review_progress.json 경로: {target}/review/review_progress.json

아래 시점마다 즉시 review_progress.json을 파일로 업데이트해야 한다 (메모리에만 저장 금지):

1. 챕터별 리뷰/검증 완료 시: completed_chapters 배열에 챕터ID 추가
2. Phase 전체 완료 시: status를 "done"으로 변경
3. 컨텍스트 한계 도달 시: 현재까지 진행 상태 반드시 저장

업데이트 방법:
  import json
  with open("{target}/review/review_progress.json") as f: s = json.load(f)
  s["phase_7_chapter_review"]["completed_chapters"].append("CH01")
  with open("{target}/review/review_progress.json", "w") as f: json.dump(s, f, ensure_ascii=False, indent=2)

=== Phase 7: 챕터 독자 리뷰 (미완료 챕터만) ===
남은 챕터: {p7_remaining}
각 챕터마다 v1-chapter-reviewer 에이전트 호출:
- 챕터 원고: {target}/chapters/{{챕터ID}}_*.md
- 예제 코드: {target}/examples/{{챕터ID}}_*/
- 보고서 출력: {target}/review/chapter_review_{{챕터ID}}.md
- 스토리텔링 관점 추가 확인: 메타코딩 페르소나 일관성, 문제-해결 구조
완료 시 review_progress.json 업데이트.

=== Phase 8: 예제 코드 실행 검증 (Phase 7 완료 후, 미완료 챕터만) ===
남은 챕터: {p8_remaining}
각 챕터마다 v1-lab-reporter 에이전트 호출:
- 예제 경로: {target}/examples/{{챕터ID}}_*/
- 보고서 출력: {target}/review/lab_report_{{챕터ID}}.md
완료 시 review_progress.json 업데이트.

=== Phase 9: 전체 회고 (Phase 8 완료 후) ===
v1-retrospective 에이전트 호출:
- 입력: {target}/review/ 폴더 전체
- 출력: {target}/review/retrospective.md
- 스토리텔링 컨셉 효과성도 회고에 포함
완료 시 review_progress.json 업데이트.""")
PYEOF
}

# ── 메인 루프 ────────────────────────────────────────────

mkdir -p "$TARGET_DIR/review" "$TARGET_DIR/assets/screenshots"
log "=== auto-review-v4 시작 (스토리텔링 / 메타코딩) ==="

if [ ! -f "$TARGET_DIR/book_final.md" ]; then
  log "book_final.md 없음. 집필 완료 후 실행하십시오."
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
    log "모든 품질 검증 + 회고 완료!"
    break
  fi

  CURRENT_PHASE=$(get_review_phase)
  log "현재 Phase: $CURRENT_PHASE"

  HASH_BEFORE=$(md5 -q "$REVIEW_STATUS_FILE" 2>/dev/null || md5sum "$REVIEW_STATUS_FILE" | cut -d' ' -f1)

  PROMPT=$(build_review_prompt)
  log "Claude 실행 중... (품질 검증 파이프라인)"

  cd "$PROJECT_DIR"
  claude --dangerously-skip-permissions -p "$PROMPT"
  EXIT_CODE=$?
  log "Claude 종료 (exit code: $EXIT_CODE)"

  HASH_AFTER=$(md5 -q "$REVIEW_STATUS_FILE" 2>/dev/null || md5sum "$REVIEW_STATUS_FILE" | cut -d' ' -f1)
  if [ "$HASH_BEFORE" = "$HASH_AFTER" ]; then
    log "경고: review_progress.json이 변경되지 않음!"
  else
    log "review_progress.json 업데이트 확인됨"
  fi

  DONE=$(is_all_done)
  if [ "$DONE" = "true" ]; then
    log "모든 품질 검증 + 회고 완료!"
    break
  fi

  RETRY=$((RETRY+1))
  if [ $RETRY -lt $MAX_RETRIES ]; then
    log "${WAIT_MINUTES}분 후 재시작... (Ctrl+C 로 중단 가능)"
    sleep $((WAIT_MINUTES * 60))
  fi
done

log "=== auto-review-v4 종료 ==="
