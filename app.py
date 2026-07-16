import os
import streamlit as st
import json
import re
from datetime import datetime

# Import our robust backend engine functions directly from main.py
from main import (
    extract_audio,
    transcribe_audio,
    analyze_content,
    generate_content,
    save_transcript,
    save_analysis,
    save_output,
    cleanup_temp_files
)
# Import our brand-new vertical clipping function from clipper.py
from clipper import create_video_clip
from config import OUTPUT_DIR

# Set up page configurations
st.set_page_config(
    page_title="AI Social Media Generator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
    <style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #1E88E5; margin-bottom: 0.5rem; }
    .subtitle { font-size: 1.1rem; color: #555; margin-bottom: 2rem; }
    </style>
""", unsafe_allow_html=True)

# Sidebar configurations
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=150", width=150)
    st.markdown("### Settings")
    st.info("⚡ **Optimized Mode:** Running locally on your CPU using **Whisper** (Base) & **Llama 3.2** (3B) with safety thread constraints to prevent system crashes.")
    
    if st.button("🧹 Clear Output Directory"):
        try:
            for file in os.listdir(OUTPUT_DIR):
                file_path = os.path.join(OUTPUT_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            st.sidebar.success("Output directory cleared!")
        except Exception as e:
            st.sidebar.error(f"Error clearing files: {e}")

# Main Layout
st.markdown('<div class="main-title">🚀 AI Social Media Content Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Drag & drop your podcast or video clips to transcribe, analyze, and generate social posts instantly.</div>', unsafe_allow_html=True)

# Drag & Drop File Upload Control
uploaded_file = st.file_uploader("Upload an MP4 Video File", type=["mp4"])

if uploaded_file is not None:
    # Save uploaded file temporarily on disk
    temp_video_path = os.path.join(OUTPUT_DIR, "temp_uploaded_video.mp4")
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    st.success(f"File uploaded successfully: **{uploaded_file.name}**")
    
    # Process Trigger Button
    if st.button("🔥 Run AI Generation Pipeline", type="primary"):
        status_container = st.empty()
        
        with st.status("Processing your video... Please wait.", expanded=True) as status:
            try:
                # Step 1: Extract Audio
                status.write("🎬 Extracting audio tracks via FFmpeg...")
                audio_file = extract_audio(temp_video_path)
                if not audio_file:
                    st.error("Audio extraction failed.")
                    st.stop()
                
                # Step 2: Transcribe Audio
                status.write("🎤 Running Whisper Speech-to-Text transcription (4 CPU Threads constraint active)...")
                transcript = transcribe_audio(audio_file)
                if not transcript:
                    st.error("Speech transcription failed.")
                    st.stop()
                
                # Save transcription
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_transcript(transcript, uploaded_file.name)
                
                # Step 3: Analyze Themes (Llama 3.2:3b step)
                status.write("🔍 Running structural semantic analysis on CPU...")
                analysis = analyze_content(transcript)
                if analysis:
                    save_analysis(analysis, uploaded_file.name, timestamp)
                
                # Step 4: Write Posts
                status.write("🤖 Formatting tailored platform copy...")
                generated_content = generate_content(transcript)
                
                # Step 5: Save everything
                if generated_content and analysis:
                    save_output(transcript, analysis, generated_content, uploaded_file.name)
                
                # Store results in Session State to prevent losing them during browser refreshes
                st.session_state["transcript"] = transcript
                st.session_state["analysis"] = analysis
                st.session_state["generated_content"] = generated_content
                
                status.update(label="Processing complete!", state="complete", expanded=False)
                
            except Exception as e:
                st.error(f"Pipeline crashed: {e}")
                st.stop()
            finally:
                cleanup_temp_files()

# Show results if they exist in the session state
if "generated_content" in st.session_state:
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📝 Video Transcript")
        st.text_area("Original Spoken Text", st.session_state["transcript"], height=250)
        
        st.subheader("📊 Structured Metadata Extraction")
        if st.session_state["analysis"]:
            st.json(st.session_state["analysis"])
        else:
            st.warning("Analysis metadata was not generated.")
            
    with col2:
        st.subheader("📱 Generated Social Copy")
        raw_copy = st.session_state["generated_content"]
        
        # Regex to match headers like: **Post 1: Twitter...** or **Post 1 - Twitter...** or Post 1: Twitter
        pattern = r"(\*\*Post \d+[\s\S]*?\*\*|Post \d+[\s\S]*?)(?=\n\n|\n\*\*Post|\nPost|$)"
        blocks = re.findall(pattern, raw_copy, re.IGNORECASE)
        
        if blocks:
            for block in blocks:
                block_stripped = block.strip()
                if not block_stripped:
                    continue
                
                # Separate the header line from the rest of the text
                lines = block_stripped.split("\n", 1)
                header = lines[0].replace("**", "").replace(":", " - ").strip()
                content = lines[1].strip() if len(lines) > 1 else block_stripped
                
                # Display in an expandable block with a copy container
                with st.expander(f"📋 Click to copy {header}", expanded=True):
                    st.code(content, language="markdown")
        else:
            # Safe Fallback if the regex parser doesn't find matches
            st.info("Direct Copy Block:")
            st.code(raw_copy, language="markdown")

    # 🎬 SECTION: Vertical Short Video Generator
    st.markdown("---")
    st.subheader("🎬 Generate Vertical Short Video Clip")
    st.markdown("Select your start time and choose how long you want your cropped 9:16 mobile video to be.")
    
    video_col1, video_col2 = st.columns([1, 1])
    
    with video_col1:
        st.markdown("#### Clip Configuration")
        # Start Time numeric input
        start_sec = st.number_input("Start Time (seconds):", min_value=0, value=0, step=1)
        # Duration slider
        clip_duration = st.slider("Clip Duration (seconds):", min_value=5, max_value=60, value=15, step=1)
        
        if st.button("✂️ Slice and Crop Video", type="primary"):
            temp_video_path = os.path.join(OUTPUT_DIR, "temp_uploaded_video.mp4")
            if os.path.exists(temp_video_path):
                with st.spinner("Processing video layers... Rendering vertical 9:16 format..."):
                    generated_clip_path = create_video_clip(temp_video_path, start_time=start_sec, duration=clip_duration)
                    if generated_clip_path and os.path.exists(generated_clip_path):
                        st.session_state["generated_clip_path"] = generated_clip_path
                        st.success("Vertical video clip generated successfully!")
                    else:
                        st.error("Failed to process the video clip.")
            else:
                st.error("Uploaded video file source not found. Please upload your video file first.")

    with video_col2:
        st.markdown("#### Clip Preview")
        if "generated_clip_path" in st.session_state and os.path.exists(st.session_state["generated_clip_path"]):
            # Preview player directly in-browser
            st.video(st.session_state["generated_clip_path"])
            
            # Browser native download button
            with open(st.session_state["generated_clip_path"], "rb") as file:
                st.download_button(
                    label="📥 Download Vertical Video",
                    data=file,
                    file_name=os.path.basename(st.session_state["generated_clip_path"]),
                    mime="video/mp4"
                )
        else:
            st.info("Your cropped vertical video will show up here as soon as it is generated.")