#!/usr/bin/env bash
# Generate a weekly Beijing-events digest with Codex CLI, publish it to Feishu,
# and send the resulting document link to the configured recipient.

set -Eeuo pipefail

readonly REPO_ROOT="/home/guosq/workspace/raspclaw-workspace"
readonly CODEX_BIN="/home/guosq/.npm-global/bin/codex"
readonly LARK_BIN="/home/guosq/.npm-global/bin/lark-cli"
readonly RECIPIENT_OPEN_ID="ou_30e6ef52bea660084a0a15cd9205c1f0"
readonly STATE_DIR="/home/guosq/.local/state/raspclaw-workspace"
readonly PROMPT_FILE="$REPO_ROOT/scripts/weekly-beijing-events-prompt.md"

export PATH="/home/guosq/.npm-global/bin:/usr/local/bin:/usr/bin:/bin"
export LARKSUITE_CLI_NO_UPDATE_NOTIFIER=1
export LARKSUITE_CLI_NO_SKILLS_NOTIFIER=1

mkdir -p "$STATE_DIR/logs" "$STATE_DIR/locks"
exec >>"$STATE_DIR/logs/weekly-beijing-events.log" 2>&1

exec 9>"$STATE_DIR/locks/weekly-beijing-events.lock"
flock -n 9 || exit 0

run_date="$(TZ=Asia/Shanghai date +%F)"
report_rel="knowledge/events/weekly/beijing-activities-${run_date}.md"
report_path="$REPO_ROOT/$report_rel"
summary_path="$STATE_DIR/codex-weekly-events-${run_date}.txt"
metadata_rel="knowledge/events/weekly/beijing-activities-${run_date}.json"
metadata_path="$REPO_ROOT/$metadata_rel"

codex_status="$("$CODEX_BIN" login status 2>&1 || true)"
if grep -qi 'not logged in' <<<"$codex_status"; then
  echo "${run_date} Codex CLI is not logged in; skipping weekly digest."
  exit 75
fi

mkdir -p "$(dirname "$report_path")"
if [[ -e "$report_path" ]]; then
  echo "${run_date} report already exists; refusing to create a duplicate."
  exit 0
fi

prompt="$(sed "s/__RUN_DATE__/${run_date}/g; s#__REPORT_PATH__#${report_rel}#g" "$PROMPT_FILE")"
"$CODEX_BIN" exec \
  --cd "$REPO_ROOT" \
  --sandbox workspace-write \
  --output-last-message "$summary_path" \
  "$prompt"

if [[ ! -s "$report_path" ]]; then
  echo "${run_date} Codex completed without creating ${report_rel}."
  exit 1
fi

create_json="$(cd "$REPO_ROOT" && "$LARK_BIN" docs +create --as bot --doc-format markdown --title "北京活动周报 · ${run_date}" --content "@./${report_rel}")"
doc_token="$(printf '%s\n' "$create_json" | sed -n 's/.*"document_id": "\([^"]*\)".*/\1/p' | head -n 1)"
doc_url="$(printf '%s\n' "$create_json" | sed -n 's/.*"url": "\([^"]*\)".*/\1/p' | head -n 1)"

if [[ -z "$doc_token" || -z "$doc_url" ]]; then
  echo "${run_date} Feishu document creation returned no document ID or URL."
  exit 1
fi

# The recipient explicitly requested this scheduled report. Grant view access to
# their own Feishu account so the link is usable even though the bot created it.
(cd "$REPO_ROOT" && "$LARK_BIN" drive +member-add --as bot --token "$doc_token" --type docx --member-id "$RECIPIENT_OPEN_ID" --member-type openid --perm view --yes)

printf '{\n  "date": "%s",\n  "local_source": "%s",\n  "feishu_document": "%s",\n  "feishu_token": "%s"\n}\n' \
  "$run_date" "$report_rel" "$doc_url" "$doc_token" >"$metadata_path"

cd "$REPO_ROOT"
git add "$report_rel" "$metadata_rel"
git commit -m "docs: add Beijing activities ${run_date}"
git push origin main
commit_id="$(git rev-parse --short HEAD)"

message=$'## 北京活动周报\n\n已生成并同步到飞书：\n'
message+="$doc_url"
message+=$'\n\n本地源稿已提交到 GitHub：`'
message+="$commit_id"
message+=$'`。'
"$LARK_BIN" im +messages-send --as bot --user-id "$RECIPIENT_OPEN_ID" --markdown "$message" --idempotency-key "bj-events-${run_date}"

echo "${run_date} published ${doc_url} at commit ${commit_id}."
