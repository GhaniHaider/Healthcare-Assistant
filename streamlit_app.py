import streamlit as st
import requests

def get_medical_info(symptom):
    api_url = "https://reference.medscape.com/?_gl=1*xvz8fx*_gcl_au*OTEyNDAyNzg3LjE3Mzk4NDAwMzI."
    response = requests.get(api_url, params={"symptom": symptom})
    return response.json()

from openai import OpenAI

# Show title and description.
st.title("🩺 Healthcare Assistant")
st.write(
    "This AI-powered healthcare assistant provides general medical guidance and information. "
    "⚠️ **Disclaimer:** This is not a substitute for professional medical advice. "
    "If you have a medical emergency, please contact a doctor immediately.")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful healthcare assistant providing general medical advice. You do NOT diagnose conditions or prescribe medication. Always advise users to consult a licensed medical professional for serious concerns."}
    ]

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            st.write("💡 Suggested questions:")
            st.markdown("- How long have you had the symptoms?")
            st.markdown("- Is there something that improves or worsens your symptoms?")
            st.markdown("- Are you experiencing any other symptoms?")


        # Generate a response using the OpenAI API.
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
