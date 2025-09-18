import os
import io
import json
import html
import requests
from flask import Flask, request, Response

TELEGRAM_CHAT_ID = -4947069491
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN env var")
TG_BASE = f"https://api.telegram.org/bot{TOKEN}"

app = Flask(__name__)

def _chunk(s: str, n: int = 3900):
    for i in range(0, len(s), n):
        yield s[i:i+n]

def send_text(text: str):
    for part in _chunk(text):
        r = requests.post(
            f"{TG_BASE}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": f"<pre>{html.escape(part)}</pre>",
                "parse_mode": "HTML",
                "disable_web_page_preview": True,
            },
            timeout=15,
        )
        r.raise_for_status()

def send_document(fileobj, filename: str, caption: str = None, mime: str = None):
    data = {"chat_id": TELEGRAM_CHAT_ID}
    if caption:
        data["caption"] = caption[:1024]
    files = {"document": (filename, fileobj, mime or "application/octet-stream")}
    r = requests.post(f"{TG_BASE}/sendDocument", data=data, files=files, timeout=120)
    r.raise_for_status()

@app.get("/")
def root_ok():
    return Response("ok", mimetype="text/plain")

@app.post("/post")
def post_handler():
    try:
        lines = []
        ctype = request.content_type or "-"
        lines.append(f"POST /post")
        lines.append(f"Content-Type: {ctype}")

        if request.args:
            lines.append("Query:")
            lines.append(json.dumps(request.args.to_dict(flat=False), ensure_ascii=False, indent=2))

        files_sent = 0
        body_summary = ""

        if request.is_json:
            data = request.get_json(silent=True)
            if data is None:
                body_summary = (request.get_data(as_text=True) or "").strip()
            else:
                body_summary = json.dumps(data, ensure_ascii=False, indent=2)

        elif request.mimetype == "application/x-www-form-urlencoded":
            form = request.form.to_dict(flat=False)
            body_summary = json.dumps(form, ensure_ascii=False, indent=2)

        elif request.mimetype and request.mimetype.startswith("multipart/"):
            form = request.form.to_dict(flat=False)
            if form:
                body_summary = json.dumps(form, ensure_ascii=False, indent=2)
            for key in request.files:
                for storage in request.files.getlist(key):
                    f = storage.stream
                    f.seek(0)
                    caption = f"{storage.filename or key} ({storage.content_type or 'application/octet-stream'})"
                    send_document(f, storage.filename or key, caption=caption, mime=storage.content_type)
                    files_sent += 1

        else:
            raw = request.get_data()
            try:
                txt = raw.decode("utf-8")
                if len(txt) > 4000:
                    body_summary = txt[:4000] + "\n...[truncated]"
                    send_document(io.BytesIO(raw), "payload.txt", caption="Raw payload")
                else:
                    body_summary = txt
            except UnicodeDecodeError:
                send_document(io.BytesIO(raw), "payload.bin", caption="Binary payload")
                body_summary = "(binary payload sent as document)"

        if body_summary:
            lines.append("Body:")
            lines.append(body_summary)

        send_text("\n\n".join(lines))
        return Response("ok", mimetype="text/plain", status=200)

    except requests.HTTPError:
        return Response("ok", mimetype="text/plain", status=502)
    except Exception:
        return Response("ok", mimetype="text/plain", status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8010)