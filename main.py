import streamlit as st
import requests
import time

# Sidebar for API Keys
# st.sidebar.title("Configuration")

# Input fields for various API keys

BLAND_API_KEY = 'org_8eabc93849311b46844d2ff69b684f544bf7adb1ed6a4b93b328e92791bfa79e1909301b43eadc679bde69'

# Task Scripts for Different Categories
TASK_SCRIPTS = {
    "Banks": """
// Step 1: Greet the Customer
Say: "Hello, this is [Bank Name] Customer Support. How can I assist you today?"

// Step 2: Address Common Bank Queries
If the user says "I want to check my account balance," respond:
    "Sure, I can help with that. May I know your account number and verify your registered phone number?"

If the user says "I need help with a transaction," respond:
    "I understand. Please provide the transaction ID or details, and I'll assist you right away."

// Step 3: Provide Resolution or Escalation
If the issue is unresolved:
    "I will escalate your concern to our senior support team. They will contact you shortly."

// Step 4: Closing
Say: "Thank you for contacting [Bank Name]. Have a great day!"
""",
    "Call Centres": """
// Step 1: Greet the Caller
Say: "Hello, thank you for calling [Company Name]. How may I assist you today?"

// Step 2: Identify and Address the Caller’s Concern
If the caller says "I need help with my account," respond:
    "Sure, let me pull up your account details. May I have your account ID or registered phone number?"

If the caller says "I have a billing issue," respond:
    "I understand. Please provide your billing statement or account ID, and I’ll look into it for you."

// Step 3: Provide Updates or Escalation
If more information is required:
    "I’ll forward this to our billing department for further assistance. They will contact you soon."

// Step 4: Closing
Say: "Thank you for choosing [Company Name]. Have a wonderful day!"
""",
    "Recovery Departments of Companies": """
// Step 1: Greet the Customer
Say: "Hello, this is [Recovery Department Name] from [Company Name]. I’m reaching out regarding an outstanding payment."

// Step 2: Address Payment Issues
If the user says "I can’t pay right now," respond:
    "I understand your situation. Let’s work together to find a feasible payment plan. Would you like to discuss options?"

If the user says "I’ve already made the payment," respond:
    "Thank you for informing us. Could you provide the transaction reference number so I can verify it?"

// Step 3: Offer Assistance
Say: "If you need any further assistance regarding your payment, feel free to let me know."

// Step 4: Closing
Say: "Thank you for your time. We value your partnership with [Company Name]. Have a good day!"
""",
    "Customer Services of Banks and Companies": """
// Step 1: Greet the Customer
Say: "Hello, this is [Customer Service Team] at [Bank/Company Name]. How can I assist you today?"

// Step 2: Identify the Concern
If the customer says "I need help with a product/service," respond:
    "I’m here to help. Can you share more details about the product or service you need assistance with?"

If the customer says "I want to file a complaint," respond:
    "I’m sorry for the inconvenience caused. Could you please provide details of the issue so we can address it promptly?"

// Step 3: Resolution or Escalation
Say: "I’ll make sure your issue is prioritized. Our team will contact you within [timeframe]."

// Step 4: Closing
Say: "Thank you for choosing [Bank/Company Name]. Have a great day!"
"""
}

# Streamlit UI
st.title("AutoSpeak - Transforming Communication with AI Intelligence")

# Dropdown for selecting the category
category = st.selectbox(
    "Select a Category:",
    ["Banks", "Call Centres", "Recovery Departments of Companies", "Customer Services of Banks and Companies"]
)

# Input fields for initiating call
st.header("Initiate Outbound Call")
phone_number = st.text_input("Phone Number")
name = st.text_input("Name")
email = st.text_input("Email")

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

# Function to initiate an outbound call
def initiate_outbound_call(phone_number, name, email, task_script):
    data = {
        "phone_number": phone_number,
        "task": task_script,
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

if st.button("Initiate Call"):
    task_script = TASK_SCRIPTS[category]
    call_response = initiate_outbound_call(phone_number, name, email, task_script)
    if call_response:  # Fixed indentation here
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
