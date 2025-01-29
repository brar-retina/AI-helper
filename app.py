import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# Configure page
st.set_page_config(page_title="Clinical Case Analyzer", layout="wide")

# Initialize session state for storing the API key
if 'api_key_configured' not in st.session_state:
    st.session_state.api_key_configured = False

def configure_gemini(api_key):
    """Configure Gemini API with the provided key"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro-vision')
        st.session_state.api_key_configured = True
        st.session_state.model = model
        return True
    except Exception as e:
        st.error(f"Error configuring API: {str(e)}")
        return False

# API Key configuration section
with st.sidebar:
    st.title("⚙️ Configuration")
    api_key = st.text_input("Enter your Google API Key", type="password")
    if st.button("Configure API"):
        if api_key:
            configure_gemini(api_key)
        else:
            st.error("Please enter an API key")

# Main app
st.title("📋 Clinical Case Analyzer")
st.write("Upload clinical case details and images for AI-powered analysis")

# Main form
with st.form("analysis_form"):
    # Case text input
    case_text = st.text_area(
        "Case Description",
        height=200,
        placeholder="Enter the clinical case details here..."
    )
    
    # Image upload
    uploaded_files = st.file_uploader(
        "Upload relevant images (optional)",
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg']
    )
    
    # Submit button
    submit_button = st.form_submit_button("Analyze Case")

if submit_button:
    if not st.session_state.api_key_configured:
        st.error("Please configure your API key first")
    elif not case_text:
        st.error("Please enter case details")
    else:
        try:
            with st.spinner("Analyzing case..."):
                # Prepare images
                image_parts = []
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        image = Image.open(uploaded_file)
                        # Convert to JPEG format
                        if image.mode != 'RGB':
                            image = image.convert('RGB')
                        # Create byte stream
                        byte_stream = io.BytesIO()
                        image.save(byte_stream, format='JPEG')
                        image_bytes = byte_stream.getvalue()
                        image_parts.append({
                            "mime_type": "image/jpeg",
                            "data": image_bytes
                        })

                # Prepare prompt
                prompt = f"""
                Please analyze this clinical case and associated images:
                
                Case Description:
                {case_text}
                
                Please provide:
                1. Key findings from the images (if any)
                2. Potential diagnoses
                3. Recommended next steps
                4. Any additional considerations
                
                Be specific and thorough in your analysis.
                """

                # Generate response
                response = st.session_state.model.generate_content([prompt] + image_parts)
                
                # Display results
                st.success("Analysis complete!")
                st.markdown("### Analysis Results")
                st.write(response.text)
                
                # Display uploaded images
                if uploaded_files:
                    st.markdown("### Uploaded Images")
                    cols = st.columns(len(uploaded_files))
                    for idx, uploaded_file in enumerate(uploaded_files):
                        with cols[idx]:
                            st.image(uploaded_file, caption=f"Image {idx + 1}")

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

# Add usage instructions
with st.sidebar:
    st.markdown("### How to use")
    st.markdown("""
    1. Enter your Google API key
    2. Click 'Configure API'
    3. Enter case details
    4. Upload relevant images (optional)
    5. Click 'Analyze Case'
    """)
    
    st.markdown("### Privacy Notice")
    st.markdown("""
    - Ensure no PHI (Protected Health Information) is uploaded
    - Data is not stored and is only used for analysis
    - Use appropriate de-identification methods
    """)
