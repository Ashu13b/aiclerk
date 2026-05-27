# medqa-app UI TODO

## Architecture (done)
- [x] Remove duplicate subject selector from QuizScreen — Bank is the entry point
- [x] QuizScreen is now session-only — receives QuizConfig from Bank/Home
- [x] Question type extended: is_pyq, exam_source, exam_year, mbbs_year
- [x] ExamProfile type + EXAM_PROFILES (NEET-PG, AIIMS-PG, PGI, DNB, INICET, FMGE)
- [x] QuizConfig type — count, mode, label, subject, is_pyq, exam_source, mbbs_year
- [x] App.tsx wires profile + quizConfig state, passes launchQuiz() to screens
- [x] Session counts derived from ExamProfile (no hardcoded 10/15/200)

## Navigation (done)
- [x] BottomNav active indicator — accent line at top of active tab
- [x] Nav restructured: Home / Bank / Social / Profile (4 tabs)
- [x] Social tab (⚔️) — hub screen for Battles + Groups
- [x] Profile tab (⚙️) — SettingsScreen with profile card, exam selector, login, prefs
- [x] Battle and Groups demoted to sub-screens of SocialScreen (internal routing)
- [x] DuelScreen + GroupsScreen get onBack prop — back button to social hub

## SocialScreen hub (done)
- [x] Incoming challenge banner at top
- [x] Two action cards: Battles → DuelScreen, Groups → GroupsScreen
- [x] Recent activity feed (mixed battle results + group events)

## SettingsScreen (done)
- [x] Profile card: avatar, name, exam badge, level/XP/streak stats
- [x] Exam profile selector — 6 chips, tapping changes profile live
- [x] Mock Google login / sign out
- [x] Notification / sound / haptic toggles (functional toggle UI)

## BankScreen (done)
- [x] Tab labels: By Year → MBBS Year, By Type → Subject Type
- [x] MBBS Year sub-tabs: [1st] [2nd] [3rd] [Final] — single year shown at a time
- [x] Subject Type sub-tabs: [Basic Science] [Long Course] [Short Course] — single type shown
- [x] PYQ / Exams tab — exam name tabs (AIIMS-PG, NEET-PG…) derived by stripping year suffix
- [x] Selecting exam reveals year chips below ([All Years] [2019] [2020]…)
- [x] Practice card updates label + count dynamically from exam × year selection
- [x] PYQ toggle filter chip in questions list
- [x] Empty state: icon + "Clear filters" button
- [x] Question cards show exam source for PYQs

## QuizScreen (done)
- [x] Peer mnemonics shown below explanation after answer
- [x] PYQ/exam_source tag shown on question card
- [x] Result screen shows separate App XP and Q.Score columns
- [x] Session label shown in header

## HomeScreen (done)
- [x] Daily goal ring in header (amber, shows today's X/target progress)
- [x] Daily goal card with Continue button
- [x] Quick Start presets derived from ExamProfile
- [x] Profile name tag (shows current exam)
- [x] Greeting from real time (morning/afternoon/evening)
- [x] XPBar — Lv badge + "X XP to next level"
- [x] BY YEAR cards use per-year colors (cyan/violet/amber/red)
- [x] Subject progress bars 5px → 8px

## XP / Ranking (done)
- [x] LeaderboardEntry: separate score (question performance) and xp (engagement)
- [x] RankScreen: Performance / Engagement toggle with explanation text
- [x] HomeScreen: "Q.Rank #4" label (not raw XP rank)
- [x] XPBar labelled "App Level" — clearly engagement, not performance

## Platform architecture — planned (next)
- [ ] Create `config/types.ts` — AppConfig type
- [ ] Create `config/medqa.ts` — extract all MBBS-specific data/branding from data.ts + App.tsx
- [ ] Create `core/ConfigContext.tsx` — React context + useConfig() hook
- [ ] Thread config through App.tsx as context provider
- [ ] BankScreen reads subjectGrouping from config (mbbs-year | category | flat)
- [ ] HomeScreen reads studentTitle from config ("Dr." vs "")
- [ ] config/ias.ts stub for future IAS app (UPSC, GS papers, different profiles)

## Medium effort — still pending
- [ ] 5. SR flip card animation — Animated Y-axis rotation
- [ ] 7. Timer as circular arc — replace flat bar with countdown arc
- [ ] Streak badge glow — pulsing amber shadow on streak pill
- [ ] Profile selector screen — now covered by SettingsScreen exam chips

## Three-pillar philosophy — pending
- [ ] Engagement: daily lives system (5 hearts, lose on wrong answer)
- [ ] Engagement: weekly XP race resets Sunday midnight
- [ ] Learning: interleaved mode — rotate subject after profile.interleave_after Qs
- [ ] Learning: difficulty ladder — easy first, revisit medium/hard automatically
- [ ] Learning: "3 wrong in same topic" → suggest focused drill
- [ ] Community: peer mnemonics likes (interactive)
- [ ] Community: "friend just got this wrong" nudge on questions
- [ ] Community: daily auto-generated duel challenge

## Backend needed
- [ ] Real question data from medqa DB (FastAPI → React Native)
- [ ] Real spaced repetition scheduling (SM-2 algorithm)
- [ ] Real streak / XP persistence
- [ ] Push notifications for streak at risk
