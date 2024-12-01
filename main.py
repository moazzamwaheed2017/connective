import streamlit as st
import requests
import jwt
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
llama_api_key = os.getenv("LLAMA_API_KEY")
toolhouse_sdk_key = os.getenv("TOOLHOUSE_SDK_KEY")
groq_api_key = os.getenv("GROQ_API_KEY")
jwt_secret = os.getenv("JWT_SECRET")

# Helper: Generate JWT Token
def generate_bearer_token():
    payload = {"service": "Connective"}
    return jwt.encode(payload, jwt_secret, algorithm="HS256")

# Helper: Preprocess User Query
def preprocess_query(query):
    return query.strip().lower()  # Example preprocessing logic

# Helper: Retrieve Data from Dataset (Toolhouse Integration)
def retrieve_data_from_dataset(processed_query):
    try:
        response = requests.post(
            "https://api.toolhouse.com/resource",
            json={"query": processed_query, "apiKey": toolhouse_sdk_key}
        )
        return response.json()
    except Exception as e:
        st.error(f"Error retrieving data: {e}")
        return None

# Helper: Generate AI Response using Llama 3
def generate_llama_response(query, dataset_response, user_context):
    try:
        prompt = f"""
        User Query: {query}
        Dataset Response: {dataset_response}
        User Context: {user_context}
        Provide a context-aware response for the user.
        """
        response = requests.post(
            "https://api.llama3.meta.com/v1/chat",
            json={"prompt": prompt, "apiKey": llama_api_key}
        )
        return response.json().get("response", "No response received.")
    except Exception as e:
        st.error(f"Error generating AI response: {e}")
        return None

# Streamlit App Interface
st.title("Connective API - Streamlit Version")

# Generate Token Section
st.header("Generate Bearer Token")
if st.button("Generate Token"):
    token = generate_bearer_token()
    st.success(f"Generated Token: {token}")

# Query Processing Section
st.header("User Query Processing")
query = st.text_input("Enter your query:")
user_context = st.text_area("Enter user context (JSON format):")
if st.button("Process Query"):
    if query:
        processed_query = preprocess_query(query)
        st.write(f"Processed Query: {processed_query}")

        dataset_response = retrieve_data_from_dataset(processed_query)
        if dataset_response:
            st.write("Dataset Response:", dataset_response)

            ai_response = generate_llama_response(processed_query, dataset_response, user_context)
            st.write("AI Response:", ai_response)
    else:
        st.warning("Please enter a query to process.")

# Real-Time Alerts Section
st.header("Real-Time Alerts")
resource_update = st.text_area("Enter resource update (JSON format):")
if st.button("Send Alert"):
    if resource_update:
        try:
            response = requests.post(
                "https://api.ai.ml.com/v1/alerts",
                json={
                    "update": resource_update,
                    "context": user_context,
                    "apiKey": os.getenv("AI_ML_API_KEY")
                }
            )
            st.success(f"Alert Sent: {response.json()}")
        except Exception as e:
            st.error(f"Error sending alert: {e}")
    else:
        st.warning("Please enter a resource update.")

# Status Section
st.header("Server Status")
if st.button("Check Server Status"):
    st.success("Connective API is running.")
