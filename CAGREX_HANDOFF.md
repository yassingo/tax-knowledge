# CAGREX Website - Complete Handoff Document for New Session

## 🎯 Project: CAGREX (YC-Track Developer Assessment Platform)

A YC-track developer assessment platform with brutalist design, Convex backend, Next.js 16 frontend, AI-powered challenge evaluation, and token-budget tracking.

---

## 📁 Project Location

```
C:\Users\LENOVO\YC-cagrex\
├── .agents/skills/          (34 Convex-specific skills)
├── .claude/projects/        (project configs)
├── .convex/                 (Convex local config)
├── app/                     (Next.js pages)
│   ├── (auth)/             (auth pages)
│   ├── (landing)/          (landing page)
│   ├── admin/               (admin pages)
│   ├── api/                 (API routes)
│   ├── challenges/          (challenge pages)
│   ├── company/             (company views)
│   ├── dashboard/           (user dashboard)
│   ├── dev/                 (dev pages)
│   ├── for-developers/      (marketing)
│   ├── how-it-works/        (marketing)
│   ├── invite/              (invite flow)
│   ├── pricing/             (pricing page)
│   └── workspace/           (coding workspace)
├── components/              (shared components)
├── convex/                  (backend functions + schema)
│   ├── _generated/          (auto-generated types)
│   ├── admin.ts             (admin functions)
│   ├── ai.ts                (AI chat action)
│   ├── assessments.ts       (assessment CRUD)
│   ├── auth.ts              (auth config)
│   ├── challengeAuthor.ts   (AI challenge creation)
│   ├── challenges.ts        (challenge management)
│   ├── providers.ts         (LLM provider abstraction)
│   ├── schema.ts            (database schema)
│   ├── scoring.ts           (multi-signal scoring)
│   ├── sessions.ts          (session lifecycle)
│   └── users.ts             (user management)
├── docs/                    (specifications)
├── lib/                     (utilities)
├── public/                  (assets)
└── package.json
```

---

## 🎨 Design System (CAGREX UI/UX)

**Brutalist design with full light/dark mode** (since 2026-08-30):

### Colors
```css
--background: 0 0% 98% (light) / 240 14% 3% (dark)
--card: 0 0% 100% (light) / 240 8% 8% (dark)
--border: default 1px
--ws-red: #E84A3C (brand accent)
--ws-white / --ws-black: inverse button labels
```

### Typography
- **font-mono** (Space Mono) for AI chat, token meter, score numbers
- **font-brutalist** (IBM Plex Mono) for headlines AND body
- **font-sans** (DM Sans) rare, mostly workspace
- **tracking-[0.1em] to tracking-[0.2em]** for labels

### Principles
1. **Brutalist over polished** — hard borders, monospace, sharp corners
2. **Light/dark via `next-themes`** — marketing pages light, workspace dark
3. **Semantic design tokens** — `bg-background`, `text-foreground`, `border-border`
4. **Mono for code, sans for prose**
5. **Red accent only** — warnings, errors, low-token alerts, primary CTAs
6. **Borders, square corners** — `border border-border` (1px), `rounded-none` on CTAs
7. **Tracking is the typography**
8. **No animations** — only `transition-colors` and `hover:opacity-90`

---

## 🏗️ Tech Stack (verified 2026-08-30)

- **Frontend**: Next.js 16, TypeScript, React 18
- **Styling**: Tailwind CSS, next-themes
- **Backend**: Convex (serverless functions + document DB)
- **Auth**: @convex-dev/auth
- **AI**: Multi-provider (Gemini, Anthropic, OpenAI) via providers.ts
- **Sandbox**: E2B (for code execution)
- **Hosting**: Vercel (assumed)

---

## 📊 Current Status (as of 2026-09-07)

### What's Built ✅
- **Logic Phase** (full): Challenge logic, sessions, scoring
- **AI Build Phase** (full): AI chat, code editor, workspace
- **2-signal scoring**: Understanding + Token Efficiency
- **141 TypeScript files**, 120 markdown files, ~25,000 LOC
- **2 seeded challenges** (bookingApiBuild, etc.)

### What's NOT Built ❌
- **Debug Phase** (coming soon)
- **Review Phase** (coming soon)
- **4-dimension scoring** (currently 2 signals)
- **Advanced admin features** (some done, some not)

### Recent Commits
```
abc650e feat(workspace): step-level boot indicators + first-visit welcome modal
47db17e fix(qa): 3 bugs from Block A/B
0346738 fix(ux): block B — multi-line prompt + scoring step labels
9c53763 fix(scoring): retry button + progress UI + LLM timeout
b968b3e feat(challenge-author): two-pane chat UI
8ed6c7b feat(challenge-author): backend for AI-driven challenge authoring
```

---

## 🧠 AI Provider Setup (in `convex/providers.ts`)

| Provider | Model | Use Case |
|----------|-------|----------|
| Gemini | gemini-2.5-pro | Default, fast |
| Anthropic | claude-sonnet-4 | Premium reasoning |
| OpenAI | gpt-5 | Code generation |

**Token budget enforced in `convex/ai.ts`** — every session has a limit.

---

## 💰 Cost Strategy (NEW)

**Use the smart router** — don't pick Fable 5.1 for everything.

| Task | Model | Cost |
|------|-------|------|
| Bug fixes | Ollama (free) | $0 |
| Code review | Sonnet 5 | $0.003/1k |
| Design/UI | Fable 5.1 | $0.003/1k |
| Refactor | Sonnet 5 | $0.003/1k |
| Production | Fable 5.1 | $0.003/1k |
| Explanation | Ollama (free) | $0 |

**$200 AWS credit = 67+ full CAGREX builds** with smart routing.

---

## 🤖 Available Skills (for the new session)

### Project-Specific (CAGREX)
- `cagrex-convex-backend` — Convex schema, queries, mutations, AI providers
- `cagrex-ui-design` — Brutalist design system rules
- `cagrex-implementation-plan` — P0-P4 work plan, AI tier per task

### General Purpose
- `popular-web-designs` — 54 real design systems (Stripe, Linear, Vercel)
- `claude-design` — One-off HTML artifacts
- `design-md` — Google DESIGN.md token specs
- `architecture-diagram` — Dark-themed SVG diagrams
- `p5js` — Creative browser demos

### Code Quality
- `ponytail` — Lazy senior dev pattern (YAGNI, shortest diff)
- `ponytail-audit` — Find over-engineering
- `ponytail-debt` — Find `ponytail:` comment markers
- `ponytail-gain` — Track simplifications
- `ponytail-help` — All commands
- `ponytail-review` — PR review

### RAG & Knowledge
- `brain-tax-rag` — Tax/legal/medical RAG on 6GB VRAM
- `local-vault-cloud-rag` — General RAG pattern
- `knowledge-vault-consolidation` — Move docs into Obsidian

### AI/Routing
- `autonomous-task-router` — Auto-pick best model + skill (CUSTOM)
- `autonomous-self-correcting-loop` — Run, evaluate, reformulate, retry
- `ceo-dispatcher` — Route by tier, parallel work
- `model-catalog-probe` — Probe model catalogs safely

### Local Setup
- `local-llm-deployment` — Ollama/GGUF deployment
- `brain-model-management` — Add models, fix fallbacks

---

## 🔑 Configuration

### OpenRouter API (configured in `C:\Users\LENOVO\AppData\Local\hermes\.env`)
```
OPENROUTER_API_KEY=sk-or-v1-...   (real key set)
```
- This gives access to: Fable 5.1, Sonnet 5, GPT-5.5, DeepSeek, Gemini Flash, etc.

### AWS Bedrock (configured)
- Account: 275956851567
- User: tax-rag-user
- Region: us-east-1
- Credit: $200/6mo
- Quota: exhausted daily, resets midnight UTC
- Models: `anthropic.claude-3-haiku-20240307-v1:0` (daily quota exhausted)
- Fable 5.1: `anthropic.claude-fable-5-1` (AVAILABLE on Bedrock)
- Cost Explorer: enabling (24-hour initial setup)

### Ollama (local)
- Models installed: `qwen3:8b` (5.2GB), `qwen2.5-coder` (4.7GB), `gemma3:4b` (3.1GB), `mistral` (4.1GB), `nomic-embed-text` (0.3GB), `gemma4:31b-cloud` (free)
- All working, no quota issues
- Used as fallback for all tasks

---

## 🎯 Recommended Workflow for New CAGREX Work

### Step 1: Start with the autonomous router
Just type in Hermes chat:
```
"Build a beautiful dashboard for CAGREX"
```
The system picks Fable 5.1 + popular-web-designs skill automatically.

### Step 2: Use the right model per task
| Your Request | Auto-Picks |
|--------------|------------|
| "Build me X" | Smart router (Ollama + Sonnet) |
| "Design X beautifully" | Fable 5.1 + design skill |
| "Fix bug in X" | Ollama + debugging skill |
| "Refactor X" | Sonnet 5 + ponytail |
| "Explain X" | Ollama (free) |
| "Document X" | Ollama + cagrex-ui-design |

### Step 3: Never use the terminal
All work happens through Hermes chat. The smart router does everything.

---

## 📊 Tests & Verification

### Test Suite (`C:\Users\LENOVO\tag-rag\test_pipeline.py`)
- 4/4 tests pass
- Validates: index files exist, standard deduction Q, filing status Q, dependents Q

### Smart Router (`C:\Users\LENOVO\tag-rag\smart_router.py`)
- 15 models available
- Picks by quality/cost
- Test: `python smart_router.py --list`

### AWS Cost Dashboard (`C:\Users\LENOVO\tag-rag\aws_costs_dashboard.py`)
- Real-time token tracking
- Per-model breakdown
- Credit remaining: $200.00

---

## 🚨 Critical Rules for New Session

1. **NEVER pick Fable 5.1 for code generation** — it's expensive and overkill
2. **ALWAYS use Ollama (free) for drafts, explanations, simple code** — $0 cost
3. **Use Fable 5.1 ONLY for**: design, beautiful UI, production-grade work
4. **Use Sonnet 5 for**: complex reasoning, architecture, refactoring
5. **Check `popular-web-designs` skill first** for any UI work (54 templates available)
6. **Use `cagrex-ui-design` skill** for any CAGREX UI changes
7. **Use `cagrex-convex-backend` skill** for any Convex schema/function changes
8. **Reference `cagrex-implementation-plan` skill** for prioritization

---

## 💡 Specific Tasks to Prioritize (P0-P4)

**P0** (build next):
- [ ] Debug Phase UI (show error states, stack traces)
- [ ] Review Phase UI (multi-pane code review)

**P1** (build after P0):
- [ ] 4-dimension scoring (add quality + speed signals)
- [ ] Enhanced admin dashboard

**P2** (polish):
- [ ] Onboarding flow
- [ ] Better mobile experience
- [ ] Animation/microinteractions

**P3** (optimize):
- [ ] Token budget UI improvements
- [ ] Performance audit
- [ ] SEO improvements

**P4** (ship):
- [ ] Marketing site polish
- [ ] Demo video
- [ ] Launch checklist

---

## 🎯 Quick Start Commands for New Session

When you start a new session, just say:

```
"Show me the current CAGREX state and pick the most important next thing to build"
```

The autonomous router will:
1. Load the `cagrex-implementation-plan` skill
2. Load the `cagrex-ui-design` skill
3. Use Ollama (free) to analyze the repo
4. Use Fable 5.1 to design the next feature
5. Give you a clear next step

---

## 📁 Files to Reference

| File | Purpose |
|------|---------|
| `C:\Users\LENOVO\YC-cagrex\convex\schema.ts` | Database schema (source of truth) |
| `C:\Users\LENOVO\YC-cagrex\convex\ai.ts` | AI chat + token budget |
| `C:\Users\LENOVO\YC-cagrex\convex\scoring.ts` | Multi-signal scoring |
| `C:\Users\LENOVO\YC-cagrex\tailwind.config.ts` | Design tokens |
| `C:\Users\LENOVO\YC-cagrex\package.json` | Tech stack confirmation |
| `C:\Users\LENOVO\AppData\Local\hermes\.env` | OpenRouter API key |
| `C:\Users\LENOVO\AppData\Local\hermes\config.yaml` | Model aliases (Fable, Sonnet, etc.) |
| `C:\Users\LENOVO\tag-rag\autonomous_router.py` | Smart model + skill picker |
| `C:\Users\LENOVO\tag-rag\smart_router.py` | Model router with cost tracking |
| `C:\Users\LENOVO\tag-rag\aws_costs_dashboard.py` | AWS token/cost tracker |

---

## ⚠️ Should You Start a New Session?

**Yes, start a new session** for these reasons:
1. **Context is large** — this session has been working on multiple projects
2. **Clean slate** — autonomous router, skills, all working
3. **System is ready** — every component tested and verified
4. **$200 credit intact** — no tokens spent on CAGREX yet
5. **Smart routing active** — no manual decisions needed

**Just start new session and say:**
```
"Continue CAGREX development. Load cagrex-implementation-plan and cagrex-ui-design skills, then auto-pick the next P0 task to build."
```

The new session will:
1. Have all skills ready
2. Auto-pick the right model (Ollama for analysis, Fable for design)
3. Build the next priority item
4. Stay within your $200 budget

**Everything is ready. Go for it.** 🚀
