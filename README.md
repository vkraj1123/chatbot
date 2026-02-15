# 🧠 SHIVAI prototype (Streamlit)

An offline-first Streamlit prototype that demonstrates SHIVAI's governed agentic loop,
intent classification, context gating, and a transparent memory/action log. The roadmap
assumes an initial online model integration for validation, followed by a fully offline
model once the local stack is ready.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://chatbot-template.streamlit.app/)

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```

### Using Sarvam-1 offline

1. Download or copy the Sarvam-1 weights into a local folder, for example:

   ```
   models/sarvam-1/
   ```

2. (Optional) Enforce offline mode for Hugging Face loaders:

   ```
   $ export HF_HUB_OFFLINE=1
   ```

3. Install the local model dependencies if you have not already:

   ```
   $ pip install torch transformers
   ```

4. In the Streamlit sidebar, enable **Use local Sarvam-1 model** and set **Local model path**
   to the folder that contains the model files (e.g., `models/sarvam-1`).

If the model path is missing files, the app will fallback to the offline prototype response
until the weights are available.
