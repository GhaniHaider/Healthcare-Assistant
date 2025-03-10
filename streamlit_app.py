import streamlit as st

import requests

import json


# Streamlit Page Configuration

st.set_page_config(page_title="Healthcare Assistant", page_icon="🏥")


# Title and Description

st.title("Healthcare Assistant Chatbot")

st.write(

    "This chatbot provides healthcare-related information."

)


# Gemini API Key Input

gemini_api_key = st.text_input("Enter your Gemini API Key", type="password")


if not gemini_api_key:

    st.warning("Please enter your Gemini API Key to continue.")

else:

    # Gemini API Endpoint

    GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_api_key}"


    # Session State for Chat History

    if "messages" not in st.session_state:

        st.session_state.messages = []


    # Display the previous chat messages via `st.chat_message`

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])


    # Function for short responses to greetings

    def get_short_response(user_input):

        basic_responses = {

            "hi": "Hello! How can I assist you today?",

            "hello": "Hi there! How can I help you with your healthcare query?",

            "how are you": "I'm here to assist you! How can I help today?",

        }

        return basic_responses.get(user_input.lower(), None)


    # Function for handling general health-related queries (e.g., "I am not feeling good")

    def handle_general_health_query(user_input):

        if "not feeling good" in user_input.lower():

            return "I'm sorry to hear you're not feeling well. Can you describe your symptoms in more detail? For example, are you feeling dizzy, nauseous, or experiencing pain?"

        return None


    # Function to check if the query is health-related

    def is_health_related(user_input):

        health_keywords = ["health", "doctor", "medicine", "treatment", "symptom", "fever", "cough", "headache", "pain", "disease", "illness", "clinic", "tumor"]

        return any(keyword in user_input.lower() for keyword in health_keywords)


    # Create a chat input field to allow the user to enter a message.

    user_input = st.chat_input("Ask a healthcare question...")


    if user_input:

        # Store and display the current user's input message

        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.chat_message("user"):

            st.markdown(user_input)


        # Handle simple greetings

        short_response = get_short_response(user_input)

        if short_response:

            with st.chat_message("assistant"):

                st.markdown(short_response)

            st.session_state.messages.append({"role": "assistant", "content": short_response})

        else:

            # Check if the query is health-related

            if is_health_related(user_input):

                # Handle general health-related queries

                general_health_response = handle_general_health_query(user_input)

                if general_health_response:

                    with st.chat_message("assistant"):

                        st.markdown(general_health_response)

                    st.session_state.messages.append({"role": "assistant", "content": general_health_response})

                else:

                    # Handle other general health queries using Gemini API

                    # Few-shot Examples for Better Responses

                    few_shot_examples = [

                        {"role": "user", "content": "What are the symptoms of diabetes?"},

                        {"role": "assistant", "content": "Common symptoms include increased thirst, frequent urination, extreme hunger, and fatigue."},

                        {"role": "user", "content": "How can I reduce my cholesterol naturally?"},

                        {"role": "assistant", "content": "Reduce cholesterol by eating healthy fats, increasing fiber intake, and exercising regularly."},

                    ]


                    # Prepare the request payload for Gemini

                    payload = {

                        "contents": [{"parts": [{"text": example["content"]} for example in few_shot_examples] + [{"text": user_input}]}]

                    }


                    # Send the request to the Gemini API

                    response = requests.post(

                        GEMINI_API_URL,

                        headers={"Content-Type": "application/json"},

                        data=json.dumps(payload),

                    )


                    # Check the response

                    if response.status_code == 200:

                        response_data = response.json()

                        if "candidates" in response_data:

                            gemini_response = response_data["candidates"][0]["content"]["parts"][0]["text"]

                            if gemini_response:

                                # Display Assistant's Response

                                with st.chat_message("assistant"):

                                    st.markdown(gemini_response)

                                st.session_state.messages.append({"role": "assistant", "content": gemini_response})

                            else:

                                st.error("No response text found in Gemini API output.")

                        else:

                            st.error("Unexpected response structure from Gemini API.")

                    else:

                        st.error(f"Error with Gemini API: {response.status_code} - {response.text}")

            else:

                # If the input is not health-related, respond with a message

                non_health_response = "Sorry, I can only assist with health-related questions. Please ask about health or medical topics."

                with st.chat_message("assistant"):

                    st.markdown(non_health_response)

                st.session_state.messages.append({"role": "assistant", "content": non_health_response})


        # Check if the input is related to image generation

        def is_image_query(user_input):

            return any(keyword in user_input.lower() for keyword in ["image", "show me", "diagram", "picture"])


        # Text-to-Image Generation Based on Query

        if is_image_query(user_input):

            st.write("Generating relevant medical image...")

            try:

                image_payload = {

                    "contents": [{"parts": [{"text": f"Generate an image of {user_input}"}]}]

                }

                image_response = requests.post(

                    GEMINI_API_URL,

                    headers={"Content-Type": "application/json"},

                    data=json.dumps(image_payload),

                )

                if image_response.status_code == 200:

                    image_data = image_response.json()

                    if "candidates" in image_data:

                        image_url = image_data["candidates"][0]["content"]["parts"][0]["text"]

                        st.image(image_url, caption="Generated Medical Image")

                    else:

                        st.error("No image URL found in response.")

                else:

                    st.error(f"Image generation failed: {image_response.status_code}")

            except Exception as e:

                st.error(f"Image generation failed: {e}")
