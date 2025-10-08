# app/main.py
from fastapi import FastAPI, Request
import base64
import os
from dotenv import load_dotenv
from app.llm_generator import generate_app_code, decode_attachments
from app.github_utils import create_repo, create_or_update_file, enable_pages, generate_mit_license
from app.notify import notify_evaluation_server

load_dotenv()
USER_SECRET = os.getenv("USER_SECRET")
USERNAME = os.getenv("GITHUB_USERNAME")

app = FastAPI()

@app.post("/api-endpoint")
async def receive_request(request: Request):
    data = await request.json()
    print("📩 Received request:", data)

    # Step 0: Verify shared secret
    if data.get("secret") != USER_SECRET:
        print("❌ Invalid secret received.")
        return {"error": "Invalid secret"}

    # Step A: Decode attachments (saved to /tmp)
    attachments = data.get("attachments", [])
    # decode_attachments is available in llm_generator, but we import it here for clarity
    from app.llm_generator import decode_attachments as _decode
    saved_attachments = _decode(attachments)
    print("Attachments saved:", saved_attachments)

    # Step 1: Generate app code & README (single OpenAI call), get attachments metadata back too
    gen = generate_app_code(data["brief"], attachments=attachments, checks=data.get("checks", []))
    files = gen.get("files", {})
    saved_info = gen.get("attachments", [])  # list of decoded attachments metadata

    # Step 2: Create GitHub repo (name must match task)
    repo_name = data["task"]
    repo = create_repo(repo_name, description=f"Auto-generated app for task: {data.get('brief','')}")
    
    # Step 3: Commit attachments to repo (if any)
    for att in saved_info:
        path = att["name"]
        try:
            with open(att["path"], "rb") as f:
                content_bytes = f.read()
            
            if att["mime"].startswith("text") or att["name"].endswith((".md", ".csv", ".json", ".txt")):
                # Handle text files as before
                text = open(att["path"], "r", encoding="utf-8", errors="ignore").read()
                create_or_update_file(repo, path, text, f"Add attachment {path}")
            else:
                # NEW: Handle binary files directly using the new function
                from app.github_utils import create_or_update_binary_file
                # Store in the original path with original name
                create_or_update_binary_file(repo, path, content_bytes, f"Add binary attachment {path}")
                
                # ALSO keep the old b64 version for compatibility with evaluation scripts
                # This ensures backward compatibility with any existing evaluation systems
                import base64
                b64 = base64.b64encode(content_bytes).decode("utf-8")
                create_or_update_file(repo, f"attachments/{att['name']}.b64", b64, f"Add binary attachment backup {att['name']}.b64")
        except Exception as e:
            print("Failed to commit attachment", att["name"], e)

    # Step 4: Add generated files (index.html & README.md)
    for fname, content in files.items():
        create_or_update_file(repo, fname, content, f"Add {fname}")

    # Step 5: Add LICENSE (MIT)
    mit_text = generate_mit_license()
    create_or_update_file(repo, "LICENSE", mit_text, "Add MIT license")

    # Step 6: Enable Pages (attempt). The repo default branch should now contain files.
    pages_ok = enable_pages(repo_name)
    pages_url = f"https://{USERNAME}.github.io/{repo_name}/" if pages_ok else None

    # Step 7: Get latest commit SHA (first commit on branch)
    try:
        commit_sha = repo.get_commits()[0].sha
    except Exception:
        commit_sha = None

    # Step 8: Notify evaluation server (with exponential retry handled inside notify)
    payload = {
        "email": data.get("email"),
        "task": data.get("task"),
        "round": data.get("round"),
        "nonce": data.get("nonce"),
        "repo_url": repo.html_url,
        "commit_sha": commit_sha,
        "pages_url": pages_url
    }
    notify_evaluation_server(data.get("evaluation_url"), payload)

    # Step 9: respond success
    return {"status": "ok"}
