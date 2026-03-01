#!/bin/bash
set -euo pipefail

# Only run in remote (claude.ai) environments
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Install Python dependencies (main + dev) in editable mode
pip install -e "${CLAUDE_PROJECT_DIR}[dev]"
