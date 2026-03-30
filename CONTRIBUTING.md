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

# Install dependencies
uv sync --group dev

# Install as a CLI tool (editable — source changes take effect immediately)
uv tool install -e --reinstall .

# Install pre-commit hooks
prek install

# Verify
agency --help
```
