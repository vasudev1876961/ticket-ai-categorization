import streamlit as st
import pandas as pd
from classifier import TicketClassifier
from actions import resolve_ticket, MOCK_EMPLOYEE_DB

# Set page layout and configuration
st.set_page_config(
    page_title="AutoTicket AI Dashboard",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    .main-title {
        font-size: 2.6rem;
        font-weight: 700;
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #888888;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .metric-label {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #8a8d90;
        margin-bottom: 0.5rem;
    }
    .metric-val {
        font-size: 1.6rem;
        font-weight: 600;
        color: #4D96FF;
    }
    .response-container {
        border-left: 5px solid #6BCB77;
        background: #0e1117;
        padding: 1.5rem;
        border-radius: 4px 12px 12px 4px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize Classifier in session state so it trains once on startup
if "classifier" not in st.session_state:
    st.session_state.classifier = TicketClassifier()

# Sidebar Configuration Controls
st.sidebar.markdown("## ⚙️ Settings")
employee_name = st.sidebar.selectbox(
    "Active Simulated User",
    options=list(MOCK_EMPLOYEE_DB.keys()),
    index=0,
    help="Choose who is logged in and sending the query. This dynamically alters simulated HR database returns."
)

threshold = st.sidebar.slider(
    "Confidence Threshold",
    min_value=0.0,
    max_value=1.0,
    value=0.45,
    step=0.05,
    help="If classification probability is below this threshold, the ticket is routed to human support instead of auto-answering."
)

st.sidebar.markdown("---")
st.sidebar.markdown("""
### 💡 How the AI Engine Works:
1. **Feature Extraction**: Incoming tickets are preprocessed and vectorized using TF-IDF.
2. **Intent Classification**: A trained Logistic Regression classifier predicts the category.
3. **Guardrails**: If prediction confidence is below the threshold, it escalates to Human Agent mode.
4. **Resolution Router**: Triggers appropriate backend workflows (like SSPR email tokens or database queries).
""")

# Main Content Layout
st.markdown('<div class="main-title">🎫 AutoTicket AI System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">A secure self-contained machine learning classifier and workflow router for internal IT & HR tickets.</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1.1, 1.2], gap="large")

with col_left:
    st.subheader("📥 Support Ticket Input")
    
    # Quick Template Buttons
    st.markdown("**Quick templates (click to test):**")
    t1 = "I forgot my password, how to reset it?"
    t2 = "I can't log in, as password is incorrect."
    t3 = "How to see leave balance?"
    t4 = "My computer screen is black and won't turn on."
    
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        btn_t1 = st.button("🔑 Forgot Password", use_container_width=True)
        btn_t3 = st.button("📅 Leave Balance Query", use_container_width=True)
    with c_btn2:
        btn_t2 = st.button("❌ Incorrect Password", use_container_width=True)
        btn_t4 = st.button("💻 Screen Issue (Escalate)", use_container_width=True)
        
    selected_text = ""
    if btn_t1:
        selected_text = t1
    elif btn_t2:
        selected_text = t2
    elif btn_t3:
        selected_text = t3
    elif btn_t4:
        selected_text = t4
        
    ticket_text = st.text_area(
        "Type or edit ticket text:",
        value=selected_text,
        height=150,
        placeholder="Type a question (e.g., 'Forgot password...', 'How much PTO do I have?')..."
    )
    
    process_btn = st.button("🚀 Process with AI", type="primary", use_container_width=True)

with col_right:
    if ticket_text or process_btn:
        st.subheader("⚡ Processing Analysis")
        
        # Classify the ticket
        raw_category, confidence, prob_dict = st.session_state.classifier.classify(ticket_text)
        
        # Apply Confidence Threshold check
        category = raw_category
        if confidence < threshold and raw_category != "human_escalation":
            category = "human_escalation"
            status_text = "Alert: Confidence level below threshold. Escalate ticket directly to human agent."
        else:
            status_text = f"Confidence level is {confidence:.1%} (Threshold is {threshold:.1%}). Router approved automatic response."
            
        # Display Metrics
        m_col1, m_col2 = st.columns(2)
        with m_col1:
            cat_display = {
                "password_issue": "🔑 Password Reset",
                "leave_issue": "📅 HR / Leave Balance",
                "human_escalation": "👤 Human Escalation"
            }.get(category, category)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Assigned Route</div>
                <div class="metric-val">{cat_display}</div>
            </div>
            """, unsafe_allow_html=True)
            
        with m_col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">Model Confidence</div>
                <div class="metric-val">{confidence:.1%}</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Display Log
        with st.expander("🛠️ Execution Pipeline Logs", expanded=True):
            st.code(f"""
[PIPELINE] Input String: "{ticket_text}"
[PIPELINE] Extracted TF-IDF vector features
[PIPELINE] Classifier predictions:
           - Password Issue probability: {prob_dict.get('password_issue', 0.0):.1%}
           - Leave Issue probability:    {prob_dict.get('leave_issue', 0.0):.1%}
           - Human Escalation fallback:  {prob_dict.get('human_escalation', 0.0):.1%}
[PIPELINE] Predicted Intent: '{raw_category}' ({confidence:.1%})
[PIPELINE] Routing check: {status_text}
            """.strip())
            
        # Resolve ticket based on determined category
        result = resolve_ticket(category, ticket_text, employee_name)
        
        st.markdown(f"**Automated Workflow Executed:** `{result['action_taken']}`")
        st.markdown(f"**Resolution Status:** `{result['status']}`")
        
        st.markdown("### ✉️ Formulated Response:")
        st.markdown(f'<div class="response-container">{result["response_md"]}</div>', unsafe_allow_html=True)
        
        # Display probability distribution graph
        st.write("---")
        st.write("**Model Probability Distribution:**")
        prob_df = pd.DataFrame({
            "Category": [
                "Password Issue (🔑)",
                "HR / Leave Balance (📅)",
                "Human Escalation (👤)"
            ],
            "Probability": [
                prob_dict.get("password_issue", 0.0),
                prob_dict.get("leave_issue", 0.0),
                prob_dict.get("human_escalation", 0.0)
            ]
        }).set_index("Category")
        st.bar_chart(prob_df, height=180)
        
    else:
        st.info("👈 Choose a template button on the left or type your query to process the ticket.")

# Show Training Set Data in dropdown
st.write("---")
with st.expander("📊 View Training Corpus & Examples (Dataset Details)"):
    st.write("This machine learning model trains on startup using the following mock examples:")
    train_df = pd.DataFrame(st.session_state.classifier.training_data, columns=["Ticket Query Text", "Target Label"])
    st.dataframe(train_df, use_container_width=True)
