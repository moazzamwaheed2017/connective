import streamlit as st
import requests
import time

# Sidebar for API Keys
st.sidebar.title("Configuration")

# Input fields for various API keys
LLAMA_API_KEY = st.sidebar.text_input("Llama3.1 API Key", type="password")
TOOLHOUSE_API_KEY = st.sidebar.text_input("Toolhouse API Key", type="password")
AIML_API_KEY = st.sidebar.text_input("AI/ML API Key", type="password")
BLAND_API_KEY = st.sidebar.text_input("Groq API Key", type="password")

# Ensure all API keys are provided
if not (LLAMA_API_KEY and TOOLHOUSE_API_KEY and AIML_API_KEY and BLAND_API_KEY):
    st.error("Please provide all API keys in the sidebar.")
    st.stop()

# Task Script
TASK_SCRIPT = """
// Step 1: Wait and Prompt
If no response, say: "Hello, this is [Connective AI Voice Agent]. Can you hear me?"
(Pause briefly after saying "Hello?")

// Step 2: Confirm User's Name
If the user responds with "Hello," then say: "Hello, is this ${lead.name}?"
(Wait for user to respond 'Yes')

// Step 3: Proceed Based on Confirmation
If the user responds with "Yes":
    "${lead.name}, I’m calling from Connective, here to assist you with health-related services and resources available for work-related injuries or conditions. How can I help you today?"

// Step 4: Identifying the User's Needs
If the user says: "I have a work-related injury" or "I have pain in my shoulder/spine/etc.," then:
    "I understand you're experiencing a condition due to work-related activity. Let's get you the right help."

// Step 5: Query for the Type of Condition
Say: "Can you please tell me more about your condition? Is it related to shoulder pain, back pain, or another condition like carpal tunnel syndrome, hearing loss, or joint issues?"

// Step 6: Condition-Related Responses
If the user mentions shoulder pain or any condition from the dataset:
    "Thank you for sharing. Based on your condition, here are some options for support:"

    - **For Shoulder Pain (M75)**: "We found that shoulder pain is common in industries where repetitive motion is involved, such as construction and healthcare. You can visit **Rome Rehabilitation Clinic** at Via Roma 15, Rome. They specialize in treating shoulder injuries. Would you like more details?"

    - **For Spinal Disorders (M51.1)**: "It seems like your condition may involve the spine. The **Florence Spine Health Center** offers treatments for spinal conditions like herniated discs. They are located at Via Firenze 17, Florence. Would you like to schedule an appointment?"

    - **For Carpal Tunnel Syndrome (G56.0)**: "If you're experiencing symptoms of carpal tunnel syndrome, the **Naples NeuroClinic** at Piazza Napoli 22 specializes in treating repetitive strain injuries like this. Should I send you their contact details?"

    - **For Hearing Loss (H83.3)**: "If you're dealing with hearing loss, the **Venice Audiology Center** provides advanced hearing solutions. They are located at Calle Venezia 5, Venice. Would you like to hear more about their services?"

    - **For Joint Disorders (M65, M77.0)**: "If you're suffering from joint disorders, you may want to check with **Naples Joint Care Clinic**, which offers physical therapy and pain management. Their address is Piazza Napoli 30, Naples. Can I assist with scheduling an appointment?"

    - **For Respiratory Issues (J40, J45)**: "For respiratory conditions like asthma or bronchitis, the **Genoa Pulmonology Center** offers specialized care. Located at Piazza Genoa 5, Genoa, they are open to assist you. Should I connect you to their team?"

    - **Other Conditions**: "If your condition doesn't match any of the above, we still have resources available to support your recovery. I can provide more information based on your specific symptoms."

// Step 7: Offer Additional Services
Say: "In addition to medical support, we also provide services like career counseling and job retraining programs for individuals with work-related conditions."

    - **Career Transition Program** in Milan for those who need help with job placement and retraining.
    - **Vocational Rehabilitation** in Rome for those who need assistance returning to work after an injury.
    - **Family Assistance Network** in Naples for childcare and eldercare services.

Would you like more information on these services?

// Step 8: Final Decision and Contact Information
If the user confirms interest in any resource:
    "Great! I’ll send you the contact information right now. Please hold on."

If the user is unsure or needs more details:
    "No problem. I can provide additional information or help you make an appointment if you wish. Feel free to reach out to me anytime."

// Step 9: Closing the Call
Say: "Thank you for your time today, ${lead.name}. If you have further questions or need assistance, don’t hesitate to reach out. Have a great day and take care!"
"""

# Function to initiate an outbound call
def initiate_outbound_call(phone_number, name, email):
    data = {
        "phone_number": phone_number,
        "task": TASK_SCRIPT,
        "summarize": True,
        "record": True
    }

    headers = {"Authorization": f"Bearer {BLAND_API_KEY}", "Content-Type": "application/json"}
    response = requests.post("https://api.bland.ai/call", json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Failed to initiate call: {response.text}")
        return None

# Function to get call details by polling until the call status is 'complete'
def get_call_details(call_id):
    url = "https://api.bland.ai/logs"
    data = {"call_id": call_id}

    call_status = ''
    retries = 10  # Maximum number of attempts
    delay = 15  # Wait time between retries (in seconds)

    # Polling loop to check the call status
    for attempt in range(retries):
        st.write(f"Attempting to fetch call details for call ID: {call_id} (Attempt {attempt + 1} of {retries})")
        
        try:
            response = requests.post(url, json=data, headers={"Authorization": f"Bearer {BLAND_API_KEY}", "Content-Type": "application/json"})
            call_details = response.json()
            call_status = call_details.get('queue_status', '').lower()

            # Check if the call status is 'complete' or 'completed'
            if call_status in ['complete', 'completed']:
                st.write("Call is complete. Returning details.")
                return call_details  # Return the completed call details

        except Exception as e:
            st.error(f"Error fetching call details: {e}")
            return None

        st.write(f"Call status: {call_status}. Retrying in {delay} seconds...")
        time.sleep(delay)  # Wait before retrying

    st.error("Call did not complete within the allowed attempts.")
    return None

# Streamlit UI
st.title("Connective - Empowering Communities through AI Voice Technology")

# Input fields for initiating call
st.header("Initiate Outbound Call")
phone_number = st.text_input("Phone Number")
name = st.text_input("Name")
email = st.text_input("Email")

if st.button("Initiate Call"):
    call_response = initiate_outbound_call(phone_number, name, email)
    if call_response:
        st.success("Call initiated successfully!")
        st.json(call_response)

        # Fetch the call ID from the response and wait for call completion
        call_id = call_response.get("call_id")
        if call_id:
            st.write("Polling for call status...")
            call_details = get_call_details(call_id)

            if call_details:
                st.header("Call Details")
                st.json(call_details)
            else:
                st.error("Failed to retrieve complete call details.")
