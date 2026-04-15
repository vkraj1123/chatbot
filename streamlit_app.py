import streamlit as st
from openai import OpenAI


SYSTEM_PROMPT = """
You are SHIVAI, a governed personal cognitive assistant.

Core behavior constraints:
- Preserve user agency; never present yourself as an autonomous authority.
- Be explicit about assumptions and uncertainty.
- Prefer structured reasoning over flashy output.
- Support long-term continuity: summarize key decisions and next actions clearly.
- Do not suggest hidden actions or opaque self-modification.

Operating modes:
- Exploration: encourage curiosity, breadth, synthesis, and open inquiry.
- Exploitation: prioritize precision, planning, recall, and execution.
""".strip()


st.set_page_config(page_title="SHIVAI", page_icon="🧠", layout="wide")

st.title("🧠 SHIVAI")
st.caption("Personal Cognitive & Growth Assistant — governance-first, human-centered, continuity-aware")

with st.expander("Vision snapshot", expanded=True):
    st.markdown(
        """
- **Core stance:** offline-first, agentic, human-in-control intelligence.
- **Purpose:** improve focus, learning, decision quality, and long-term life continuity.
- **Guardrails:** no silent autonomy, no hidden actions, reversible learning, explicit governance.
- **Modes:** Exploration (curiosity) and Exploitation (execution).
        """
    )

mode = st.radio(
    "Operating mode",
    options=["Exploration", "Exploitation"],
    horizontal=True,
    help="Exploration favors ideation and synthesis. Exploitation favors precision and execution.",
)

openai_api_key = st.text_input("OpenAI API Key", type="password")

if not openai_api_key:
    st.info("Add your OpenAI API key to begin chatting with SHIVAI.", icon="🗝️")
    st.stop()

client = OpenAI(api_key=openai_api_key)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "I am SHIVAI. Tell me your mission or challenge, and I will help you think and act with clarity."
            ),
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("What do you want to focus on right now?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    mode_instruction = (
        "User selected Exploration mode. Favor open-ended inquiry, alternatives, and synthesis."
        if mode == "Exploration"
        else "User selected Exploitation mode. Favor concrete plans, prioritization, and execution steps."
    )

    api_messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "system", "content": mode_instruction}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=api_messages,
        stream=True,
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
