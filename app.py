"""
Zava Insurance – On-Device AI Demo
==========================================
A Flask application showcasing on-device AI capabilities using
Microsoft Foundry Local on Copilot+ PCs with NPU acceleration.

Tabs:
  1. Claims AI       – Upload damage photos, get AI damage assessment
  2. Policy Assistant – Chat about insurance policies (on-device LLM)
  3. Document Analyzer– Paste/upload documents for AI summarisation
  4. NPU Dashboard    – Live NPU status, cost savings, offline proof
"""

import os
import sys
import json
import time
import uuid
import base64
import traceback
from datetime import datetime
from pathlib import Path

from flask import (
    Flask, render_template, request, jsonify, send_from_directory
)
from werkzeug.utils import secure_filename

# ---------------------------------------------------------------------------
# Foundry Local bootstrap
# ---------------------------------------------------------------------------
foundry_ok = False
client = None
model_id = None
manager = None

def init_foundry():
    """Initialise Foundry Local connection – tries NPU models first, then CPU fallback."""
    global foundry_ok, client, model_id, manager

    # NPU-first model priority chain (smallest/fastest first):
    #   1. qwen2.5-1.5b  → smallest NPU model (1.5B), fastest inference
    #   2. phi-3-mini-4k → small NPU model (3.8B), 4K context
    #   3. phi-3.5-mini  → NPU model (3.8B)
    #   4. phi-4-mini    → CPU-only fallback (larger, slower)
    NPU_MODELS = os.environ.get(
        "FOUNDRY_MODELS",
        "qwen2.5-1.5b,phi-3-mini-4k,phi-3.5-mini,phi-4-mini"
    ).split(",")

    try:
        from foundry_local_sdk import FoundryLocalManager
    except ImportError:
        from foundry_local import FoundryLocalManager
    from openai import OpenAI

    for alias in NPU_MODELS:
        alias = alias.strip()
        try:
            print(f"[STARTUP] Trying model: {alias} ...")
            manager = FoundryLocalManager(alias)
            client = OpenAI(base_url=manager.endpoint, api_key=manager.api_key)
            info = manager.get_model_info(alias)
            model_id = info.id
            is_npu = "npu" in model_id.lower()
            foundry_ok = True
            print(f"[STARTUP] Foundry Local connected – model: {model_id}")
            print(f"[STARTUP] Endpoint: {manager.endpoint}")
            print(f"[STARTUP] Running on: {'NPU ✓' if is_npu else 'CPU (no NPU variant available for this model)'}")
            return
        except Exception as exc:
            print(f"[STARTUP]   → {alias} failed: {exc}")
            continue

    print("[STARTUP] No models loaded. Running in UI-preview mode (no AI inference).")
    foundry_ok = False

init_foundry()

# ---------------------------------------------------------------------------
# Silent warmup – prime the model so the first demo inference is fast
# ---------------------------------------------------------------------------
if foundry_ok:
    try:
        print("[STARTUP] Warming up model (silent inference)...")
        _warmup = _run_inference("Reply OK.", "warmup", max_tokens=8)
        # Remove warmup from the inference log so dashboard starts clean
        if inference_log:
            inference_log.clear()
        print("[STARTUP] Warmup complete – model is hot and ready.")
    except Exception as exc:
        print(f"[STARTUP] Warmup skipped: {exc}")

# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "bmp"}

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
inference_log: list[dict] = []

def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English text (GPT-style)."""
    return max(1, len(text) // 4)


def _run_inference(system_prompt: str, user_prompt: str, max_tokens: int = 1024) -> dict:
    """Run a chat completion via Foundry Local and log metrics."""
    if not foundry_ok:
        return {
            "text": "[Demo mode – Foundry Local not connected. Install & start Foundry Local to enable on-device AI.]",
            "tokens": 0,
            "latency_ms": 0,
            "cloud_cost_saved": "$0.00",
        }

    t0 = time.perf_counter()
    try:
        resp = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
        )
    except Exception as exc:
        # Attempt reconnect once – Foundry Local port may have changed
        print(f"[INFERENCE] Connection failed, attempting reconnect: {exc}")
        try:
            init_foundry()
            resp = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
            )
        except Exception as exc2:
            return {
                "text": f"[Error: Could not reach Foundry Local – {exc2}]",
                "tokens": 0,
                "latency_ms": 0,
                "cloud_cost_saved": "$0.00",
            }

    elapsed_ms = round((time.perf_counter() - t0) * 1000)
    text = resp.choices[0].message.content or ""

    # Many Foundry Local / NPU models return usage=None or 0 tokens.
    # When that happens, estimate from the actual text lengths.
    prompt_tokens = 0
    completion_tokens = 0
    if resp.usage and resp.usage.total_tokens and resp.usage.total_tokens > 0:
        total_tokens = resp.usage.total_tokens
    else:
        prompt_tokens = _estimate_tokens(system_prompt + user_prompt)
        completion_tokens = _estimate_tokens(text)
        total_tokens = prompt_tokens + completion_tokens

    # Estimated cloud cost saved (Azure OpenAI GPT-4o pricing ~$5/$15 per 1M tokens)
    est_cost = round(total_tokens * 0.00001, 6)

    entry = {
        "id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now().isoformat(),
        "tokens": total_tokens,
        "latency_ms": elapsed_ms,
        "cloud_cost_saved": f"${est_cost:.4f}",
    }
    inference_log.append(entry)

    return {
        "text": text,
        "tokens": total_tokens,
        "latency_ms": elapsed_ms,
        "cloud_cost_saved": f"${est_cost:.4f}",
    }

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/status")
def api_status():
    """Return NPU / Foundry Local availability."""
    is_npu = foundry_ok and model_id and "npu" in model_id.lower()
    return jsonify({
        "foundry_connected": foundry_ok,
        "model": model_id or "N/A",
        "endpoint": str(manager.endpoint) if manager else "N/A",
        "mode": "on-device NPU" if is_npu else ("on-device CPU" if foundry_ok else "UI preview (no AI)"),
        "hardware": "NPU (QNN)" if is_npu else ("CPU" if foundry_ok else "none"),
    })


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Policy Assistant – general insurance chat."""
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify({"error": "Empty message"}), 400

    system = (
        "You are Zava Insurance's AI assistant. Be concise and professional. "
        "Answer insurance questions about policies, claims, coverage, and terminology."
    )
    result = _run_inference(system, user_msg, max_tokens=256)
    return jsonify(result)


@app.route("/api/assess-claim", methods=["POST"])
def api_assess_claim():
    """Claims AI – analyse uploaded damage photo description."""
    data = request.get_json(force=True)
    description = data.get("description", "").strip()
    damage_type = data.get("damage_type", "property")

    if not description:
        return jsonify({"error": "No damage description provided"}), 400

    system = (
        "You are a Zava Insurance claims analyst. Assess this damage report. "
        "Reply with: Severity (Minor/Moderate/Severe/Total Loss), Estimated Repair Cost, "
        "2 Next Steps, Coverage Note, Priority (Routine/Expedited/Emergency). Be brief."
    )
    # Truncate long descriptions to keep prompt within NPU-friendly token budget
    desc_truncated = description[:600]
    user_prompt = f"{damage_type} damage: {desc_truncated}"
    result = _run_inference(system, user_prompt, max_tokens=350)
    return jsonify(result)


@app.route("/api/analyze-document", methods=["POST"])
def api_analyze_document():
    """Document Analyzer – summarise/extract from pasted text."""
    data = request.get_json(force=True)
    doc_text = data.get("text", "").strip()
    task = data.get("task", "summarize")  # summarize | extract | review

    if not doc_text:
        return jsonify({"error": "No document text provided"}), 400

    task_prompts = {
        "summarize": (
            "Summarize this insurance document in 3-5 bullet points. "
            "Focus on: coverage limits, deductibles, exclusions, key dates."
        ),
        "extract": (
            "Extract key data: policy number, insured name, coverage type, "
            "dates, limits, deductibles, premium, endorsements. "
            "Return as a structured list."
        ),
        "review": (
            "Review this insurance document for potential issues: gaps in coverage, "
            "unusual exclusions, compliance concerns, or items that need clarification. "
            "Provide a brief risk assessment."
        ),
    }

    system = "Zava Insurance document analyst. " + task_prompts.get(task, task_prompts["summarize"])
    # Truncate document to keep within NPU context window
    doc_truncated = doc_text[:1500]
    result = _run_inference(system, doc_truncated, max_tokens=350)
    return jsonify(result)


@app.route("/api/metrics")
def api_metrics():
    """Return cumulative inference metrics for the dashboard."""
    total_tokens = sum(e["tokens"] for e in inference_log)
    total_cost = sum(float(e["cloud_cost_saved"].replace("$", "")) for e in inference_log)
    avg_latency = (
        round(sum(e["latency_ms"] for e in inference_log) / len(inference_log))
        if inference_log else 0
    )
    return jsonify({
        "total_inferences": len(inference_log),
        "total_tokens": total_tokens,
        "total_cloud_cost_saved": f"${total_cost:.4f}",
        "avg_latency_ms": avg_latency,
        "log": inference_log[-20:],  # last 20 entries
    })


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(str(UPLOAD_DIR), filename)


@app.route("/api/upload-image", methods=["POST"])
def upload_image():
    """Handle image upload for claims."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400
    f = request.files["file"]
    if not f or not f.filename:
        return jsonify({"error": "Empty file"}), 400
    if not _allowed_file(f.filename):
        return jsonify({"error": "File type not allowed"}), 400

    fname = secure_filename(f"{uuid.uuid4().hex[:8]}_{f.filename}")
    f.save(str(UPLOAD_DIR / fname))
    return jsonify({"filename": fname, "url": f"/uploads/{fname}"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  Zava Insurance – On-Device AI Demo")
    print("  Powered by Microsoft Surface + Foundry Local")
    print("=" * 60)
    print(f"  Model loading may take a moment on first run...")
    print(f"  Once ready, open \u2192 http://localhost:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=False)
