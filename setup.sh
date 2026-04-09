#!/bin/bash

# ディレクトリの作成
mkdir -p specs/domain
mkdir -p specs/data
mkdir -p specs/integrations
mkdir -p design
mkdir -p implementation/contracts
mkdir -p implementation/tasks/scout
mkdir -p implementation/tasks/worker
mkdir -p implementation/tasks/llm
mkdir -p implementation/prompts
mkdir -p tests/fixtures
mkdir -p configs
mkdir -p .github

# ルート直下のファイル作成
touch README.md
touch AGENTS.md
touch TASKS.md
touch ARCHITECTURE.md

# specs/ 以下のファイル作成
touch specs/SST.md
touch specs/domain/identification.md
touch specs/domain/tagging.md
touch specs/domain/pipeline.md
touch specs/domain/retry_policy.md
touch specs/domain/state_machine.md
touch specs/data/metadata_schema.md
touch specs/data/id3_mapping.md
touch specs/data/scoring_rules.md
touch specs/integrations/steam_api.md
touch specs/integrations/vgmdb.md
touch specs/integrations/musicbrainz.md
touch specs/integrations/acoustid.md

# design/ 以下のファイル作成
touch design/system_design.md
touch design/worker_design.md
touch design/llm_node_design.md
touch design/storage_design.md

# implementation/ 以下のファイル作成
touch implementation/contracts/interfaces.md
touch implementation/contracts/api_contracts.md
touch implementation/contracts/error_model.md
touch implementation/tasks/scout/scan_steam.md
touch implementation/tasks/scout/detect_soundtrack.md
touch implementation/tasks/worker/fetch_steam.md
touch implementation/tasks/worker/vgmdb_search.md
touch implementation/tasks/worker/musicbrainz_search.md
touch implementation/tasks/worker/acoustid.md
touch implementation/tasks/worker/scoring.md
touch implementation/tasks/worker/tagging.md
touch implementation/tasks/worker/storage.md
touch implementation/tasks/llm/normalization.md
touch implementation/tasks/llm/validation.md
touch implementation/prompts/codegen.md
touch implementation/prompts/review.md

# その他（tests, configs, .github）
touch tests/test_cases.md
touch configs/config.schema.json
touch configs/example.yaml
touch .github/copilot-instructions.md

echo "SST project structure has been created successfully."