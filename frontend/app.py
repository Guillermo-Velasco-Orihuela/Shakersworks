import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="ShakersWorks Chat", layout="wide")

# Initialize chat history once
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I can answer questions about Shakers and give personalized recommendations. What can I help you with today?"
        }
    ]

mode = st.sidebar.radio("Mode", ["Chat (RAG)", "Recommendations"])

st.title("💬 ShakersWorks Chat")

# Render full history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Docked input
user_input = st.chat_input("Type your message here…")

if user_input:
    # Show user message immediately
    st.chat_message("user").write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Call backend
    try:
        if mode == "Chat (RAG)":
            resp = requests.post(
                f"{API_BASE}/query",
                json={"question": user_input},
                timeout=30
            )
            resp.raise_for_status()
            payload = resp.json()
            answer = payload.get("answer", "🤖 I got no answer.")
            sources = payload.get("source_docs", [])
            if sources:
                answer += "\n\n**Sources:**\n" + "\n".join(
                    f"- {d['title']} ({d.get('url','')})" for d in sources
                )

        else:  # Recommendations mode
            # Normalize user_id to lowercase to match backend profiles
            normalized = user_input.strip().lower()
            resp = requests.post(
                f"{API_BASE}/recommend",
                json={"user_id": normalized},
                timeout=30
            )
            resp.raise_for_status()
            recs = resp.json()
            if recs:
                answer = "Here are your personalized recommendations:\n" + "\n".join(
                    f"- **{r['title']}**: {r['explanation']}" for r in recs
                )
            else:
                answer = "I don't have any recommendations for that user yet."

    except Exception as e:
        answer = f"😔 Something went wrong. Please try again.\n\n{e}"

    # Show assistant reply
    st.chat_message("assistant").write(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
