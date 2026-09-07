
"""Test Fable 5.1 + popular-web-designs together."""
import urllib.request
import json

# Get API key
with open(r"C:\Users\LENOVO\AppData\Local\hermes\.env") as f:
    for line in f:
        if 'OPENROUTER_API_KEY' in line and '=' in line and not line.strip().startswith('#'):
            api_key = line.split('=', 1)[1].strip()
            break

# Use Fable 5.1 with Stripe design system
req = urllib.request.Request(
    "https://openrouter.ai/api/v1/chat/completions",
    data=json.dumps({
        "model": "anthropic/claude-fable-5.1",
        "messages": [{
            "role": "user",
            "content": "Create a simple HTML landing page header using the Stripe design system. Include: top nav with logo + 3 links + CTA button, hero section with title + subtitle + CTA. Just the HTML with inline CSS."
        }],
        "max_tokens": 2000,
        "temperature": 0.7
    }).encode('utf-8'),
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(req, timeout=60) as response:
    data = json.loads(response.read())
    print("=" * 70)
    print("FABLE 5.1 + STRIPE DESIGN OUTPUT")
    print("=" * 70)
    content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
    print(content[:3000])
    print("...")
    usage = data.get('usage', {})
    print(f"\n[Usage] Tokens: {usage.get('total_tokens', 0)}, Cost: ${usage.get('cost', 0):.5f}")
    
    # Save to file
    with open(r"C:\Users\LENOVO\tag-rag\stripe_demo.html", "w") as f:
        f.write("<!DOCTYPE html><html><head><title>Stripe Demo - Fable 5.1</title></head><body>")
        f.write(content)
        f.write("</body></html>")
    print("\n✅ Saved to stripe_demo.html")
