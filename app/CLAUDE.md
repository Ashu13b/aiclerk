# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
npm start              # dev server on port 8083 (web + native)
npx expo start --web --port 8083   # web only
npx tsc --noEmit       # type check (strict mode)
```

No test suite. Type check is the main correctness gate.

## Stack

Expo + React Native, TypeScript strict. Port **54321** (countdown — easy to remember, no conflicts). `react-native-svg` and `expo-linear-gradient` are the only UI extras.

## Navigation architecture

`App.tsx` owns screen state. Five tabs: `home`, `inbox`, `fill`, `search`, `settings`.

- `home` → `DashboardScreen` — vault overview, recent documents, per-person stats
- `inbox` → `InboxScreen` — low-confidence proposals awaiting approval
- `fill` → `FillScreen` — form fill report review and manual field entry
- `search`, `settings` → empty `<View>` placeholder (not yet implemented)

`Screen` type and `BottomNav` tabs are defined in `components/BottomNav.tsx`.

## Data layer (`data.ts`)

All aiclerk-specific types and mock data. Key exports:

- `Document`, `Person`, `VaultType` — core domain types matching `v2_metadata_results.json` schema
- `Proposal` — low-confidence ingest item (mirrors `review_queue.json` entries)
- `FillReport`, `FillField`, `FillSource` — form fill result types (mirrors `output/fill_reports/latest.json`)
- `KNOWN_PERSONS`, `RECENT_DOCUMENTS`, `PENDING_PROPOSALS`, `MOCK_FILL_REPORT` — static mock data for development

## Theme (`theme.ts`)

`getTheme(accent, dark)` returns a `Theme` object. All screens receive `t: Theme` as a prop. Current accent: `MED.green` (`#00e5a0`). Dark mode only.
