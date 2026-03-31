# Contributing

## Requirements

- [uv](https://docs.astral.sh/uv/)
- [gh](https://cli.github.com/) (authenticated)
- [claude](https://docs.anthropic.com/en/docs/claude-cli) CLI

## Install

```bash
# Clone and enter the repo
git clone https://github.com/ooloth/agency.git
cd agency

# Install dependencies (overwriting any existing ones)
uv sync --all-extras --reinstall

# Install pre-commit hooks (overwriting any existing ones)
uv run prek install --overwrite

# Install as a CLI tool (editable — source changes take effect immediately)
uv tool install -e --reinstall .

# Verify
agency --help
```
