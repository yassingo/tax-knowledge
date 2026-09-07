# Design Tools Setup - Complete Steps

## ✅ Already Installed (No Action Needed)

| Tool | Purpose | Status |
|------|---------|--------|
| `popular-web-designs` skill | 54 design templates (Stripe, Linear, Vercel, etc.) | ✅ Ready |
| `claude-design` skill | One-off HTML artifacts | ✅ Ready |
| `design-md` skill | Google DESIGN.md token specs | ✅ Ready |
| `architecture-diagram` skill | Dark-themed SVG diagrams | ✅ Ready |
| `p5js` skill | Creative browser demos | ✅ Ready |
| `fable-5.1` model | Claude Fable 5.1 via OpenRouter | ✅ Working |

---

## 🛠️ How to Use Each Tool

### 1. Generate a Landing Page (Stripe-style)

```powershell
cd C:\Users\LENOVO\tag-rag
.\venv\Scripts\activate
python smart_router.py --task "Build a Stripe-style landing page for a SaaS product with hero, features, and pricing" --quality 9 --type design
```

**OR via Hermes chat:**
```
@Fable 5.1 @popular-web-designs Create a Stripe-style landing page header with nav, hero, and CTA button
```

### 2. Quick Mockup (Cheap/Fast)

```powershell
python smart_router.py --task "Quick mockup of a login form" --quality 5 --type design --budget 0.001
```

**Will pick**: `gemma3-4b` (local, free, fast)

### 3. Premium Creative (Best Quality)

```powershell
python smart_router.py --task "Design a beautiful dashboard with charts" --quality 10 --type design
```

**Will pick**: `fable-5.1` (Claude Fable 5.1, $0.003/1k tokens)

### 4. AWS-Hosted Fable (If You Have AWS Credits)

```
@bedrock-fable hello
```

Uses `anthropic.claude-fable-5-1` on AWS Bedrock (subject to your $200 quota)

---

## 🎨 54 Available Design Templates (popular-web-designs skill)

Browse the templates: `C:\Users\LENOVO\AppData\Local\hermes\skills\popular-web-designs\templates\`

**Available styles include:**
- `stripe` - Financial infrastructure style (skewed gradient)
- `linear` - Modern SaaS (minimal, sharp)
- `vercel` - Developer-focused (black/white)
- `notion` - Collaborative tools (warm, friendly)
- `apple` - Premium consumer (hero typography)
- `airbnb` - Marketplace (warm coral)
- `figma` - Design tool (multi-color)
- `cursor` - AI editor (dark, purple)
- `claude` - Anthropic's brand (warm beige)
- `cohere`, `mistral`, `xai`, `nvidia`, `mongodb`, `supabase`, `posthog`, `sanity`, `sentry`, `raycast`, `replicate`, `resend`, `warp`, `webflow`, `wise`, `zapier`, etc.

**Example commands:**
```
@popular-web-designs templates/stripe.md Create a pricing page
@popular-web-designs templates/linear.md Build a settings UI
@popular-web-designs templates/vercel.md Design a deployment page
```

---

## 🤖 Smart Router - Choose the Best Model Automatically

The `smart_router.py` script picks the right model based on quality/cost needs.

### Usage:

```powershell
# Show all available models
python smart_router.py --list

# Premium quality (Fable 5.1)
python smart_router.py --task "your prompt" --quality 9

# Budget mode (Gemini Flash - very cheap)
python smart_router.py --task "your prompt" --budget 0.001

# Local only (free, slower)
python smart_router.py --task "your prompt" --local

# Auto-detect (balanced)
python smart_router.py --task "your prompt" --auto
```

### Quality Levels:
- **1-3**: Drafts, simple tasks → uses local Ollama
- **4-6**: Normal work → uses Gemini Flash or Ollama
- **7-8**: Quality work → uses DeepSeek, Qwen, or free cloud
- **9-10**: Premium → uses Fable 5.1, Sonnet 5, GPT-5.5

### Cost per 1k tokens (sorted by cost):
1. **FREE**: Ollama models, `minimax-m3-free`
2. **$0.0001**: `gemini-3.7-flash`, `deepseek-v4-pro`
3. **$0.0004**: `qwen3.8-max`
4. **$0.0015**: `fable-batch` (50% off)
5. **$0.0025-0.003**: `gpt-5.5-pro`, `fable-5.1`, `sonnet-5`
6. **$0.005**: `grok-4.6`

---

## 🔄 Using Fable 5.1 Through AWS (Alternative Path)

**Why might you want this?**
- Uses your $200 AWS credits instead of OpenRouter pay-per-token
- Same model, same quality
- Different billing path (already-paid credits)

**Available AWS Bedrock model IDs:**
- `anthropic.claude-fable-5` (configured in config.yaml)
- `anthropic.claude-fable-5-1` (configured as `bedrock-fable` alias)

**Issue**: AWS Bedrock models often require **inference profile ARNs**, and your account has had daily quota issues (ThrottlingException).

**To use AWS Fable 5.1:**
```
@bedrock-fable hello
```

Or in `ask_tax.py`:
```python
BEDROCK_MODEL_ID = "anthropic.claude-fable-5-1"
```

**Recommendation**: Use OpenRouter (fable-5.1 alias) by default, fall back to AWS Bedrock if needed.

---

## ✅ Verification - All Working Now

```bash
# Test Fable 5.1
python smart_router.py --list
python smart_router.py --task "Hello" --auto

# Test design skill
@popular-web-designs templates/stripe.md Show me the Stripe design system
```

All committed to `github.com/yassingo/tax-knowledge`.
