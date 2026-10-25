# Codex Usage for GNOME

A GNOME Shell top-bar indicator for the remaining ChatGPT plan usage available to Codex. It displays the remaining 5-hour and weekly usage percentages, refreshes every five minutes, and provides a manual refresh in its menu.

## Requirements

- GNOME Shell 50
- Python 3
- Codex CLI signed in with a ChatGPT account (`~/.codex/auth.json`)

## Install

```sh
mkdir -p ~/.local/share/gnome-shell/extensions/codex-usage@local
cp extension.js metadata.json usage.py ~/.local/share/gnome-shell/extensions/codex-usage@local/
gnome-extensions enable codex-usage@local
```

On Wayland, log out and back in if the extension does not appear immediately. Click the top-bar indicator to view details or refresh.

## How it works

The extension runs `usage.py`, which reads the existing Codex ChatGPT sign-in from `~/.codex/auth.json` and requests usage from `chatgpt.com`. The token is sent only to that service over HTTPS; it is not saved, logged, or included in this project. No API key is needed.

The usage endpoint is an undocumented ChatGPT endpoint and may change. This project is independent and is not affiliated with or endorsed by OpenAI.

## License

MIT. See [LICENSE](LICENSE).
