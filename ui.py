import streamlit as st
import requests
import json
import base64

# URLs
n8n_URL = "https://caic-n8n-stage.k8s.stage.ix.statsperform.cloud/webhook/ai.digest"
template_URL = "https://raw.githubusercontent.com/asher2609/ai-digest/main/SP.template.png"

# Topics
topics = [
    "GenAI in Sports",
    "AI-Powered Technology in Sports",
    "Sports and Technology Innovation",
    "AI and Innovation in Major Sports",
    "AI in Sports Betting",
    "Automated Content Creation in Sports",
    "Computer Vision in Sports",
    "Use of AI in Sports Fan Engagement"
]

# Initialize session state
if "responses" not in st.session_state:
    st.session_state.responses = {}
if "visibility" not in st.session_state:
    st.session_state.visibility = {topic: False for topic in topics}
if "search_topic" not in st.session_state:
    st.session_state.search_topic = ""
if "search_response" not in st.session_state:
    st.session_state.search_response = None
if "search_visible" not in st.session_state:
    st.session_state.search_visible = False

# Background template
def set_template(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            bg_base64 = base64.b64encode(response.content).decode()
            st.markdown(
                f"""
                <style>
                .stApp {{
                    background-image: url("data:image/png;base64,{bg_base64}");
                    background-size: cover;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    background-position: center;
                }}
                .main > div {{
                    background-color: rgba(0, 0, 0, 0.6); 
                    padding: 2rem; 
                    border-radius: 10px;
                }}
                html, body {{
                    color: white !important;
                    font-family: 'Segoe UI', sans-serif;
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning(f"Failed to fetch background template (status: {response.status_code})")
    except Exception as e:
        st.error(f"Error fetching background: {e}")

# Connect to n8n webhook
def get_topic(topic):
    try:
        with st.spinner(f"Fetching results for '{topic}'..."):
            response = requests.post(n8n_URL, json={"topic": topic}, timeout=10)
            return response.text if response.status_code == 200 else f"Failed with status code: {response.status_code}"
    except Exception as e:
        return json.dumps({"error": str(e)})

# Results
def get_results(data_text):
    try:
        data = json.loads(data_text)
        if isinstance(data, str):
            data = json.loads(data)  

        if isinstance(data, list) and data:
            for item in data:
                st.markdown(f"### {item.get('Title', 'No Title')}")
                st.markdown(f"**Date:** {item.get('Date', 'No Date')}")
                st.markdown(item.get('Summary', 'No Summary'))
                st.markdown(f"[Read more]({item.get('Link', '#')})")
                st.markdown("---")
        elif isinstance(data, dict) and "error" in data:
            st.error(f"n8n Error: {data['error']}")
        else:
            st.warning("No results found.")
    except json.JSONDecodeError:
        st.error("Invalid JSON received.")
        st.text(data_text)

# Set background
set_template(template_URL)

# UI
st.title("AI Sports Digest")
st.markdown("Here are the latest insights on the following topics:")
st.markdown("---")

# Topic buttons
for topic in topics:
    if st.button(topic):
        st.session_state.visibility[topic] = not st.session_state.visibility[topic]
        if st.session_state.visibility[topic] and topic not in st.session_state.responses:
            st.session_state.responses[topic] = get_topic(topic)

    if st.session_state.visibility.get(topic) and topic in st.session_state.responses:
        get_results(st.session_state.responses[topic])

# Search
st.markdown("---")
st.markdown("### Search")
search_input = st.text_input("Enter a topic")

if st.button("Search"):
    if search_input:
        st.session_state.search_topic = search_input
        st.session_state.search_visible = True
        st.session_state.search_response = get_topic(search_input)

# Search results
if st.session_state.search_visible and st.session_state.search_response:
    st.markdown(f"## Results for: _{st.session_state.search_topic}_")
    get_results(st.session_state.search_response)


