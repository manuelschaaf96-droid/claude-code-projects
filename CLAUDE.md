# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository structure

This is a monorepo of independent projects:

| Path | Type | Description |
|---|---|---|
| `top-down-shooter.html` | Browser game | Vanilla JS + Canvas2D, single file, no dependencies |
| `tic-tac-toe.html` | Browser game | Vanilla JS + Canvas2D, single file |
| `ai-class.html` | Browser app | Single-file HTML/CSS/JS |
| `ideas-app/index.html` | Browser app | Eisenhower Matrix idea manager, single file |
| `AeroSense/` | React Native app | TypeScript, React Native 0.85, bootstrapped with RN CLI |

## Browser projects (HTML files)

All single-file HTML projects share these conventions:
- Dark background palette (`#1a1a2e` base)
- Vanilla JS classes, no build step — open directly in browser
- Canvas2D rendering with `image-rendering: pixelated` for retro look
- All game state in a top-level `Game` class with a `requestAnimationFrame` loop

To run: `open <file>.html`

## AeroSense (React Native)

All commands run from `AeroSense/`:

```bash
# Install deps (first time)
npm install
bundle install          # Ruby/CocoaPods tooling
bundle exec pod install # iOS native deps

# Run
npm start               # Metro bundler
npm run android         # Android emulator/device
npm run ios             # iOS simulator

# Quality
npm run lint            # ESLint (@react-native config)
npm test                # Jest with @react-native/jest-preset

# Run a single test file
npx jest path/to/file.test.tsx
```

Requires React Native environment setup: https://reactnative.dev/docs/set-up-your-environment

Entry point: `AeroSense/App.tsx`. The app wraps content in `SafeAreaProvider` + `AppContent`; all new screens go inside `AppContent`.

## Git workflow

**Commit and push after every meaningful unit of work** — a completed feature, a bug fix, a new file, a significant edit. Never leave finished work uncommitted. This ensures no progress is ever lost.

Commit message format:
- One concise subject line (imperative mood: "Add", "Fix", "Update", not "Added" or "Adds")
- No body needed for small changes; add a short paragraph for anything non-obvious

After every commit, push immediately:
```bash
git add <specific files>
git commit -m "Short description of what changed and why"
git push
```

The nested `AeroSense/AeroSense/` directory (inner git repo) is gitignored — do not try to add it. `node_modules/` is also excluded.
