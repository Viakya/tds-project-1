# app/llm_generator.py
import os
import base64
import mimetypes
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

TMP_DIR = Path("/tmp/llm_attachments")
TMP_DIR.mkdir(parents=True, exist_ok=True)

def decode_attachments(attachments):
    """
    attachments: list of {name, url: data:<mime>;base64,<b64>}
    Saves files into /tmp/llm_attachments/<name>
    Returns list of dicts: {"name": name, "path": "/tmp/..", "mime": mime, "size": n}
    """
    saved = []
    for att in attachments or []:
        name = att.get("name") or "attachment"
        url = att.get("url", "")
        if not url.startswith("data:"):
            # Not a data URI: skip or handle as possible http url
            continue
        try:
            header, b64data = url.split(",", 1)
            # header like: data:image/png;base64
            mime = header.split(";")[0].replace("data:", "")
            data = base64.b64decode(b64data)
            path = TMP_DIR / name
            with open(path, "wb") as f:
                f.write(data)
            saved.append({
                "name": name,
                "path": str(path),
                "mime": mime,
                "size": len(data)
            })
        except Exception as e:
            print("Failed to decode attachment", name, e)
    return saved

def summarize_attachment_meta(saved):
    """
    saved is list from decode_attachments.
    Returns a short human-readable summary string for the prompt.
    For text-like files: include first ~300 characters; for CSV include header and first two rows.
    For binary (images) include name + size + mime.
    """
    summarizes = []
    for s in saved:
        nm = s["name"]
        p = s["path"]
        mime = s.get("mime", "")
        try:
            if mime.startswith("text") or nm.endswith((".md", ".txt", ".json", ".csv")):
                with open(p, "r", encoding="utf-8", errors="ignore") as f:
                    if nm.endswith(".csv"):
                        # quick CSV preview
                        lines = []
                        for i, line in enumerate(f):
                            lines.append(line.strip())
                            if i >= 3:
                                break
                        preview = "\\n".join(lines)
                    else:
                        data = f.read(1000)
                        preview = data.replace("\n", "\\n")[:1000]
                summarizes.append(f"- {nm} ({mime}): preview: {preview}")
            else:
                # binary (image, etc.)
                summarizes.append(f"- {nm} ({mime}): {s['size']} bytes")
        except Exception as e:
            summarizes.append(f"- {nm} ({mime}): (could not read preview: {e})")
    return "\\n".join(summarizes)

def _strip_code_block(text: str) -> str:
    """
    If text is inside triple-backticks, return inner contents. Otherwise return text as-is.
    """
    if "```" in text:
        # get content between first pair of triple backticks
        parts = text.split("```")
        # parts like: ["", "html\n<..>", "rest..."] or ["```html", "code", "```"]
        # Usually code is parts[1]
        if len(parts) >= 2:
            return parts[1].strip()
    return text.strip()

def generate_readme_fallback(brief: str, checks=None, attachments_meta=None) -> str:
    checks_text = "\\n".join(checks or [])
    att_text = attachments_meta or ""
    return f"""# Auto-generated README

**Project brief:** {brief}

**Attachments**:
{att_text}

**Checks to meet:**
{checks_text}

## Setup
1. Open `index.html` in a browser.
2. No build steps required.

## Notes
This README was generated as a fallback (OpenAI did not return an explicit README).
"""

def generate_app_code(brief: str, attachments=None, checks=None) -> dict:
    """
    Returns a dict of filename -> content,
    usually {"index.html": "<html>...</html>", "README.md": "..."}
    """
    saved = decode_attachments(attachments or [])
    attachments_meta = summarize_attachment_meta(saved)

    user_prompt = f"""
You are an assistant that generates a minimal, working single-page web application plus a professional README.
Brief:
{brief}

Attachments available (names and previews):
{attachments_meta}

Evaluation checks:
{checks or []}

Requirements:
- Produce a minimal single-file web app (index.html) that satisfies the brief and as many checks as possible.
- After the web app source, output a separator line exactly:
---README.md---
and then provide the complete README.md markdown content (Project Overview, Setup, Usage, License).
- Do NOT include any other commentary outside the two parts (app code then README).
- If you must include multiple files explain them briefly in the README, but keep the main runnable file as index.html.
"""

    try:
        response = client.responses.create(
            model="gpt-5",
            input=[
                {"role": "system", "content": "You are a helpful coding assistant that outputs runnable code."},
                {"role": "user", "content": user_prompt}
            ],
        )
        text = response.output_text or ""
        print("✅ Generated code using new OpenAI Responses API.")
    except Exception as e:
        print("⚠ OpenAI API failed, using fallback HTML instead:", e)
        text = f"""
<html>
  <head><title>Fallback App</title></head>
  <body>
    <h1>Hello (fallback)</h1>
    <p>The app was generated as a fallback because OpenAI failed. Brief: {brief}</p>
  </body>
</html>

---README.md---
{generate_readme_fallback(brief, checks, attachments_meta)}
"""

    # split by README delimiter
    if "---README.md---" in text:
        code_part, readme_part = text.split("---README.md---", 1)
        code_part = _strip_code_block(code_part)
        readme_part = _strip_code_block(readme_part)
    else:
        # no delimiter: assume the model returned only code; make fallback README
        code_part = _strip_code_block(text)
        readme_part = generate_readme_fallback(brief, checks, attachments_meta)

    # Return a dict files. Also return attachments saved so caller can commit them too.
    files = {
        "index.html": code_part,
        "README.md": readme_part
    }
    # include attachments info for caller to commit if they want
    return {"files": files, "attachments": saved}
