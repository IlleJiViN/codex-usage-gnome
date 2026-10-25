# Codex Usage for GNOME

A GNOME Shell top-bar indicator for the remaining ChatGPT plan usage available to Codex. It displays the remaining 5-hour and weekly usage percentages, refreshes every five minutes, and provides a manual refresh in its menu.

The menu also lists OpenCode's favorited models with a context-use bar based on each model's latest recorded response and its context window. This is local context usage, not a provider billing or plan quota.

## Requirements

- GNOME Shell 50
- Python 3
- Codex CLI signed in with a ChatGPT account (`~/.codex/auth.json`)
- OpenCode 1.x (for favorite models and context usage)

## Install

```sh
mkdir -p ~/.local/share/gnome-shell/extensions/codex-usage@local
cp extension.js metadata.json usage.py opencode_usage.py ~/.local/share/gnome-shell/extensions/codex-usage@local/
gnome-extensions enable codex-usage@local
```

On Wayland, log out and back in if the extension does not appear immediately. Click the top-bar indicator to view details or refresh.

## How it works

The extension runs `usage.py`, which reads the existing Codex ChatGPT sign-in from `~/.codex/auth.json` and requests usage from `chatgpt.com`. The token is sent only to that service over HTTPS; it is not saved, logged, or included in this project. No API key is needed.

The Codex usage endpoint is an undocumented ChatGPT endpoint and may change. OpenCode favorites are read from `~/.local/state/opencode/model.json`; context usage is read locally from OpenCode's model cache and database in read-only mode. This project is independent and is not affiliated with or endorsed by OpenAI or OpenCode.

## License

MIT. See [LICENSE](LICENSE).
