from __future__ import annotations

from datetime import datetime
from pathlib import Path
import subprocess
from typing import TYPE_CHECKING, Any

import streamlit as st

if TYPE_CHECKING:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer


VISION_PATH = Path(__file__).with_name("SHIVAI_VISION.md")


def load_vision() -> str:
    if VISION_PATH.exists():
        return VISION_PATH.read_text(encoding="utf-8")
    return "SHIVAI vision document not found."


def classify_intent(prompt: str) -> str:
    lowered = prompt.lower().strip()
    if lowered.endswith("?") or lowered.startswith(("what", "why", "how", "when", "where")):
        return "query"
    if lowered.startswith(("do ", "run ", "execute ", "start ")):
        return "command"
    if any(keyword in lowered for keyword in ("task", "todo", "plan", "schedule")):
        return "task"
    return "reflection"


def choose_context_gate(intent: str, allow_fresh_info: bool) -> str:
    if intent == "query" and allow_fresh_info:
        return "fresh information"
    if intent in {"task", "command"}:
        return "memory retrieval"
    return "direct reply"


def generate_response(prompt: str, mode: str, intent: str, context_gate: str) -> str:
    mode_note = "exploration" if mode == "Exploration" else "exploitation"
    return (
        f"Mode: **{mode_note}**\n\n"
        f"Intent classified as **{intent}** with context gate **{context_gate}**.\n\n"
        "Proposed response:\n"
        f"- Acknowledge: _{prompt}_\n"
        "- Clarify constraints and confirm authorization before any action.\n"
        "- Suggest a next step aligned to your current focus."
    )


def append_log(entry: str) -> None:
    st.session_state.action_log.append(
        {"timestamp": datetime.utcnow().isoformat(timespec="seconds"), "entry": entry}
    )


def ensure_state() -> None:
    if "memory" not in st.session_state:
        st.session_state.memory = []
    if "action_log" not in st.session_state:
        st.session_state.action_log = []


@st.cache_resource(show_spinner="Loading local Sarvam-1 model...")
def load_local_model(model_path: str) -> tuple[Any, Any]:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)
    model.eval()
    if torch.cuda.is_available():
        model.to("cuda")
    return tokenizer, model


def generate_local_model_response(
    model_path: str,
    prompt: str,
    mode: str,
    intent: str,
    context_gate: str,
    max_tokens: int,
) -> str:
    try:
        tokenizer, model = load_local_model(model_path)
        device = model.device
        system_prompt = (
            "You are SHIVAI, an offline-first cognitive companion. "
            f"Mode: {mode}. Intent: {intent}. Context gate: {context_gate}. "
            "Respond concisely with governance-first guidance."
        )
        input_text = f"{system_prompt}\nUser: {prompt}\nSHIVAI:"
        inputs = tokenizer(input_text, return_tensors="pt").to(device)
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            do_sample=False,
        )
        decoded = tokenizer.decode(outputs[0], skip_special_tokens=True)
        return decoded.split("SHIVAI:", 1)[-1].strip()
    except (OSError, ValueError, ModuleNotFoundError) as error:
        return (
            "Local Sarvam-1 model could not be loaded. "
            f"Check the model path and files. ({error})"
        )


def current_git_sha() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
    return result.stdout.strip()


st.set_page_config(page_title="SHIVAI", page_icon="🧠", layout="wide")
ensure_state()
st.title("🧠 SHIVAI — Cognitive & Growth Assistant (Local Prototype)")
st.caption(
    "Offline-first, agentic, and governed. This demo showcases intent classification, "
    "context gating, and a transparent action log."
)
st.caption(f"Running locally from: `{Path(__file__).resolve()}`")
st.caption(f"Build: `{current_git_sha()}`")

with st.sidebar:
    st.header("Governance Controls")
    mode = st.radio("Mode", ["Exploration", "Exploitation"], horizontal=True)
    allow_tools = st.toggle("Allow tool execution", value=False)
    allow_fresh_info = st.toggle("Allow fresh information", value=False)
    store_memory = st.toggle("Store to memory", value=True)
    use_local_model = st.toggle("Use local Sarvam-1 model", value=False)
    model_path = st.text_input("Local model path", value="models/sarvam-1")
    max_tokens = st.slider("Max new tokens", min_value=64, max_value=512, value=192)
    st.divider()
    st.subheader("Memory")
    if st.button("Clear memory"):
        st.session_state.memory = []
        append_log("Memory cleared by user.")

left, right = st.columns([2, 1])

with left:
    st.subheader("Agentic Loop")
    prompt = st.text_area(
        "Input",
        placeholder="Describe a task, ask a question, or share a reflection.",
        height=140,
    )

    if st.button("Run SHIVAI loop"):
        if prompt.strip():
            intent = classify_intent(prompt)
            context_gate = choose_context_gate(intent, allow_fresh_info)
            if use_local_model:
                response_text = generate_local_model_response(
                    model_path,
                    prompt,
                    mode,
                    intent,
                    context_gate,
                    max_tokens,
                )
                response = f"{response_text}"
            else:
                response = generate_response(prompt, mode, intent, context_gate)
            st.markdown(response)
            append_log(f"Loop executed with intent '{intent}' and gate '{context_gate}'.")
            if store_memory:
                st.session_state.memory.append(
                    {
                        "timestamp": datetime.utcnow().isoformat(timespec="seconds"),
                        "entry": prompt.strip(),
                        "intent": intent,
                    }
                )
                append_log("Memory updated with latest input.")
            if allow_tools and intent in {"task", "command"}:
                st.success("Tool execution authorized (simulated).")
                append_log("Tool execution approved (simulated).")
        else:
            st.warning("Please provide input to run the loop.")

with right:
    st.subheader("Action Log")
    if st.session_state.action_log:
        for item in reversed(st.session_state.action_log):
            st.write(f"{item['timestamp']} — {item['entry']}")
    else:
        st.caption("No actions yet.")

    st.subheader("Memory Vault")
    if st.session_state.memory:
        for memory_item in reversed(st.session_state.memory):
            st.write(
                f"{memory_item['timestamp']} — {memory_item['intent']}: {memory_item['entry']}"
            )
    else:
        st.caption("Memory is empty.")

st.divider()
with st.expander("SHIVAI Vision (source of truth)", expanded=False):
    st.markdown(load_vision())
