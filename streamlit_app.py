import streamlit as st
import sys
import os
import json
from datetime import datetime
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from chatbot import MedicalChatbot
except ImportError:
    st.error("⚠️ Could not import chatbot module. Make sure chatbot.py is in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Medical Assistant Chatbot",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for medical theme
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2E86AB, #A23B72);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .chat-container {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        min-height: 400px;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .user-message {
        background: #007bff;
        color: white;
        padding: 0.8rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
        text-align: right;
    }
    
    .bot-message {
        background: #ffffff;
        color: #333;
        padding: 0.8rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 8px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .stButton > button {
        background: #007bff;
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.75rem 1rem;
        font-weight: bold;
        min-height: 50px;
        width: 100%;
        font-size: 14px;
        line-height: 1.2;
        white-space: normal;
        word-wrap: break-word;
    }
    
    .stButton > button:hover {
        background: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stTextInput > div > div > input {
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    """Initialize session state variables"""
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'session_id' not in st.session_state:
        st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if 'chatbot_initialized' not in st.session_state:
        st.session_state.chatbot_initialized = False
    if 'current_symptoms' not in st.session_state:
        st.session_state.current_symptoms = []
    if 'disease_candidates' not in st.session_state:
        st.session_state.disease_candidates = []

def load_chatbot():
    """Load the medical chatbot"""
    try:
        if not st.session_state.chatbot_initialized:
            with st.spinner("🔄 Initializing Medical Assistant..."):
                st.session_state.chatbot = MedicalChatbot("medical_rag_indexes")
                st.session_state.chatbot_initialized = True
                st.success("✅ Medical Assistant ready!")
        return True
    except Exception as e:
        st.error(f"❌ Failed to initialize chatbot: {str(e)}")
        st.error("Make sure your RAG indexes are created and saved as 'medical_rag_indexes'")
        return False

def display_chat_message(message, is_user=True):
    """Display a chat message with proper styling"""
    if is_user:
        st.markdown(f"""
        <div class="user-message">
            <strong>👤 You:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="bot-message">
            <strong>🤖 Medical Assistant:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

def display_chat_history():
    """Display the chat history"""
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Only show chat history if there are messages, no default welcome message
    for message in st.session_state.chat_history:
        display_chat_message(message['content'], message['is_user'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def process_user_input(user_input):
    """Process user input and get bot response"""
    if not user_input.strip():
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        'content': user_input,
        'is_user': True,
        'timestamp': datetime.now()
    })
    
    # Get bot response
    try:
        with st.spinner("🤔 Analyzing your symptoms..."):
            response = st.session_state.chatbot.process_user_message(user_input)
        
        # Add bot response to history
        st.session_state.chat_history.append({
            'content': response,
            'is_user': False,
            'timestamp': datetime.now()
        })
        
        # Update session state with current info
        summary = st.session_state.chatbot.get_conversation_summary()
        st.session_state.current_symptoms = summary['extracted_symptoms']
        st.session_state.disease_candidates = summary['top_disease_candidates']
        
    except Exception as e:
        st.error(f"❌ Error processing your message: {str(e)}")

def display_sidebar():
    """Display sidebar with conversation info and controls"""
    st.sidebar.markdown("## 🏥 Medical Assistant")
    
    # Session info
    st.sidebar.markdown(f"**Session ID:** `{st.session_state.session_id}`")
    
    if st.session_state.chatbot_initialized:
        summary = st.session_state.chatbot.get_conversation_summary()
        
        # Current state
        st.sidebar.markdown(f"**Current State:** `{summary['current_state']}`")
        
        # Current symptoms
        if summary['extracted_symptoms']:
            st.sidebar.markdown("### 🩺 Current Symptoms")
            for symptom in summary['extracted_symptoms']:
                st.sidebar.markdown(f"• {symptom.title()}")
        
        # Top disease candidates
        if summary['top_disease_candidates']:
            st.sidebar.markdown("### 🔍 Top Conditions")
            
            # Get max confidence for relative scoring
            max_confidence = max(candidate['confidence'] for candidate in summary['top_disease_candidates'])
            
            for i, candidate in enumerate(summary['top_disease_candidates'][:3], 1):
                confidence = candidate['confidence']
                disease = candidate['disease'].title()
                
                # Color code by relative confidence
                relative_confidence = confidence / max_confidence if max_confidence > 0 else 0
                if relative_confidence > 0.7:
                    color = "🟢"
                elif relative_confidence > 0.4:
                    color = "🟡"
                else:
                    color = "🔴"
                
                st.sidebar.markdown(f"{color} **{disease}**")
                st.sidebar.markdown(f"   Score: {confidence:.2f}")
        
        # Conversation stats
        st.sidebar.markdown("### 📊 Session Stats")
        col1, col2 = st.sidebar.columns(2)
        with col1:
            st.metric("Messages", len(st.session_state.chat_history))
        with col2:
            st.metric("Questions", summary['question_count'])
    
    # Control buttons
    st.sidebar.markdown("### 🔧 Controls")
    
    if st.sidebar.button("🔄 Reset Conversation", use_container_width=True):
        if st.session_state.chatbot:
            st.session_state.chatbot.reset_conversation()
        st.session_state.chat_history = []
        st.session_state.current_symptoms = []
        st.session_state.disease_candidates = []
        st.experimental_rerun()
    
    if st.sidebar.button("💾 Export Conversation", use_container_width=True):
        export_conversation()
    
    # Emergency contacts
    st.sidebar.markdown("### 🚨 Emergency")
    st.sidebar.error("""
    **Seek immediate medical attention if:**
    • Severe difficulty breathing
    • Chest pain or pressure
    • Severe headache with neck stiffness
    • High fever (>103°F/39.4°C)
    • Loss of consciousness
    • Severe abdominal pain
    """)
    
    st.sidebar.markdown("### ℹ️ Disclaimer")
    st.sidebar.warning("""
    This is an AI assistant for informational purposes only. 
    It does NOT provide medical diagnosis. 
    Always consult healthcare professionals for medical advice.
    """)

def export_conversation():
    """Export conversation to JSON"""
    if st.session_state.chat_history:
        export_data = {
            'session_id': st.session_state.session_id,
            'export_time': datetime.now().isoformat(),
            'conversation': st.session_state.chat_history,
            'summary': st.session_state.chatbot.get_conversation_summary() if st.session_state.chatbot else {}
        }
        
        json_str = json.dumps(export_data, indent=2, default=str)
        st.sidebar.download_button(
            label="📄 Download JSON",
            data=json_str,
            file_name=f"medical_conversation_{st.session_state.session_id}.json",
            mime="application/json"
        )

def display_quick_symptoms():
    """Display quick symptom buttons"""
    st.markdown("### 🚀 Quick Start - Common Symptoms")
    
    # Common symptom categories
    symptom_categories = {
        "🤒 Fever & Flu": ["fever", "headache", "body aches", "fatigue"],
        "🤢 Digestive Issues": ["nausea", "stomach pain", "diarrhea", "vomiting"],
        "😷 Respiratory": ["cough", "sore throat", "runny nose", "congestion"],
        "💊 Pain & Aches": ["headache", "back pain", "joint pain", "muscle pain"],
        "🌡️ Cold Symptoms": ["runny nose", "sneezing", "mild fever", "congestion"],
        "🦠 Viral Symptoms": ["fatigue", "body aches", "low fever", "weakness"]
    }
    
    # Display in a 2x3 grid
    col1, col2 = st.columns(2)
    
    categories_list = list(symptom_categories.items())
    
    with col1:
        for i in range(0, len(categories_list), 2):
            category, symptoms = categories_list[i]
            if st.button(category, key=f"symptom_btn_{i}", use_container_width=True):
                symptom_text = f"I have {', '.join(symptoms)}"
                process_user_input(symptom_text)
                st.experimental_rerun()
            st.markdown("<br>", unsafe_allow_html=True)
    
    with col2:
        for i in range(1, len(categories_list), 2):
            if i < len(categories_list):
                category, symptoms = categories_list[i]
                if st.button(category, key=f"symptom_btn_{i}", use_container_width=True):
                    symptom_text = f"I have {', '.join(symptoms)}"
                    process_user_input(symptom_text)
                    st.experimental_rerun()
                st.markdown("<br>", unsafe_allow_html=True)

def main():
    """Main application function"""
    # Initialize session state
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 Medical Assistant Chatbot</h1>
        <p>AI-powered symptom analysis and health guidance</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load chatbot
    if not load_chatbot():
        st.stop()
    
    # Sidebar
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # User input first - clean and prominent
        st.markdown("## 💬 Describe Your Symptoms")
        
        # Create input form
        with st.form(key="user_input_form", clear_on_submit=True):
            user_input = st.text_area(
                "Describe your symptoms or ask a question",
                placeholder="e.g., I have a fever and headache for 2 days...",
                height=100,
                key="user_message",
                label_visibility="collapsed"
            )
            
            col_a, col_b, col_c = st.columns([1, 1, 3])
            with col_a:
                submit_button = st.form_submit_button("Send 📤", use_container_width=True)
            with col_b:
                clear_button = st.form_submit_button("Clear 🗑️", use_container_width=True)
            
            if submit_button and user_input:
                process_user_input(user_input)
                st.experimental_rerun()
            
            if clear_button:
                st.experimental_rerun()
        
        # Show quick symptoms only if no conversation started
        if not st.session_state.chat_history:
            st.markdown("---")
            display_quick_symptoms()
        
        # Chat history below input
        if st.session_state.chat_history:
            st.markdown("---")
            st.markdown("## 💬 Conversation History")
            display_chat_history()
    
    with col2:
        # Welcome message for first-time users
        if not st.session_state.chat_history:
            st.markdown("### 🏥 Welcome!")
            st.info("""
            **I'm your medical assistant!**
            
            I can help you:
            • Understand your symptoms
            • Ask relevant follow-up questions  
            • Provide preliminary health guidance
            • Suggest when to see a doctor
            
            **Important:** I provide guidance only - always consult healthcare professionals for diagnosis.
            """)
        
        # Current analysis panel (only show during conversation)
        if st.session_state.current_symptoms:
            st.markdown("### 🔬 Current Analysis")
            
            # Symptoms summary
            st.markdown("**Reported Symptoms:**")
            for symptom in st.session_state.current_symptoms:
                st.markdown(f"• {symptom.title()}")
            
            # Disease candidates
            if st.session_state.disease_candidates:
                st.markdown("**Possible Conditions:**")
                
                # Get max confidence for normalization
                max_confidence = max(candidate['confidence'] for candidate in st.session_state.disease_candidates)
                
                for candidate in st.session_state.disease_candidates[:3]:
                    confidence = candidate['confidence']
                    disease = candidate['disease'].title()
                    
                    # Normalize confidence to 0-1 range for progress bar
                    normalized_confidence = min(confidence / max_confidence, 1.0) if max_confidence > 0 else 0.0
                    
                    # Color code by confidence level
                    if confidence > max_confidence * 0.7:
                        color = "🟢"
                    elif confidence > max_confidence * 0.4:
                        color = "🟡"
                    else:
                        color = "🔴"
                    
                    st.markdown(f"{color} **{disease}**")
                    st.progress(normalized_confidence)
                    st.caption(f"Score: {confidence:.2f}")
        
        # Health tips (only show during active conversation)
        if len(st.session_state.chat_history) > 2:
            st.markdown("### 💡 General Health Tips")
            st.info("""
            **While waiting for medical consultation:**
            • Stay hydrated
            • Get adequate rest
            • Monitor your symptoms
            • Take your temperature regularly
            • Avoid self-medication
            """)

def display_analytics():
    """Display conversation analytics (optional page)"""
    st.title("📈 Conversation Analytics")
    
    if not st.session_state.chat_history:
        st.info("No conversation data available yet.")
        return
    
    # Basic metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Messages", len(st.session_state.chat_history))
    
    with col2:
        user_messages = sum(1 for msg in st.session_state.chat_history if msg['is_user'])
        st.metric("User Messages", user_messages)
    
    with col3:
        st.metric("Bot Messages", len(st.session_state.chat_history) - user_messages)
    
    with col4:
        if st.session_state.current_symptoms:
            st.metric("Symptoms Found", len(st.session_state.current_symptoms))
    
    # Conversation timeline
    if st.session_state.chat_history:
        st.markdown("### 📅 Conversation Timeline")
        for i, msg in enumerate(st.session_state.chat_history):
            timestamp = msg.get('timestamp', 'Unknown')
            speaker = "👤 You" if msg['is_user'] else "🤖 Bot"
            content_preview = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            st.markdown(f"**{speaker}** _{timestamp}_: {content_preview}")

if __name__ == "__main__":
    main()