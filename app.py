import streamlit as st
import random
import os
import zipfile
import io
from datetime import datetime
from moviepy.editor import *
import numpy as np

# Page config
st.set_page_config(
    page_title="Short Creator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Short Creator")
st.caption("Simple - Fast - Works Every Time")

# Session state
if 'videos' not in st.session_state:
    st.session_state.videos = []

# ============================================
# HOOK TEXTS DATABASE
# ============================================
HOOK_TEXTS = {
    "funny": [
        "POV: You're trying to act professional at work",
        "When you realize it's Monday tomorrow",
        "Me trying to wake up for a 9 AM class",
        "That moment when nothing goes right",
        "Expectation vs reality be like",
    ],
    "motivation": [
        "Most people quit right before success",
        "You are closer than you think",
        "The only limit is the one you set in your mind",
        "Success doesn't come from comfort zones",
        "Discipline beats motivation every time",
    ],
    "shocking": [
        "90% of people quit right before their breakthrough",
        "The average person will spend 6 years on social media",
        "Everything you want is on the other side of fear",
    ],
    "life": [
        "Stop caring about what others think",
        "Invest in yourself first",
        "Your 20s are for building, not settling",
    ],
    "money": [
        "Stop trading time for money",
        "Broke people save. Rich people invest.",
        "Your degree won't make you rich",
    ],
}

ALL_HOOK_TEXTS = []
for texts in HOOK_TEXTS.values():
    ALL_HOOK_TEXTS.extend(texts)

# ============================================
# SIMPLE VIDEO CREATION - NO ERRORS
# ============================================

def create_simple_short(hook_text, reaction_type, output_path):
    """
    Creates a simple short with:
    - 8 seconds: Black screen with white text (hook)
    - 4 seconds: Colored screen with reaction text
    - Subscribe text at the end
    """
    
    # Hook part (8 seconds)
    hook_bg = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=8)
    hook_txt = TextClip(hook_text, fontsize=55, color='white', font='Arial', size=(900, None), method='caption')
    hook_txt = hook_txt.set_duration(8).set_position('center')
    hook_clip = CompositeVideoClip([hook_bg, hook_txt])
    
    # Reaction colors
    reaction_colors = {
        "nod": (76, 175, 80),      # Green
        "laugh": (255, 193, 7),    # Yellow/Orange
        "shocked": (244, 67, 54),  # Red
        "confused": (33, 150, 243), # Blue
        "dance": (156, 39, 176),   # Purple
    }
    
    # Reaction texts
    reaction_texts = {
        "nod": "👍 AGREE!",
        "laugh": "😂 FUNNY!",
        "shocked": "😮 NO WAY!",
        "confused": "🤔 HMM...",
        "dance": "💃 LET'S GO!",
    }
    
    # Get reaction type (remove 'scooby_' prefix if present)
    reaction_key = reaction_type.replace("scooby_", "")
    if reaction_key not in reaction_colors:
        reaction_key = "nod"
    
    color = reaction_colors.get(reaction_key, (76, 175, 80))
    react_text = reaction_texts.get(reaction_key, "👍")
    
    # Reaction part (4 seconds)
    react_bg = ColorClip(size=(1080, 1920), color=color, duration=4)
    react_txt = TextClip(react_text, fontsize=70, color='white', font='Arial', size=(900, None), method='caption')
    react_txt = react_txt.set_duration(4).set_position('center')
    react_clip = CompositeVideoClip([react_bg, react_txt])
    
    # Combine hook + reaction
    final = concatenate_videoclips([hook_clip, react_clip])
    
    # Add subscribe text at the end (last 3 seconds)
    sub_txt = TextClip("Subscribe 🔔", fontsize=50, color='#ff6666', font='Arial', size=(900, None), method='caption')
    sub_txt = sub_txt.set_duration(3).set_position(('center', 1700))
    sub_txt = sub_txt.set_start(final.duration - 3)
    final = CompositeVideoClip([final, sub_txt])
    
    # Export
    final.write_videofile(
        output_path,
        fps=24,
        codec='libx264',
        audio_codec='aac',
        threads=2,
        preset='fast',
        logger=None,
        verbose=False
    )
    
    final.close()
    return output_path

# ============================================
# UI TABS
# ============================================

tab1, tab2 = st.tabs(["🎬 CREATE ONE", "🤖 AUTO GENERATE"])

# ============================================
# TAB 1: CREATE ONE SHORT
# ============================================
with tab1:
    st.markdown("### Create a Short")
    st.caption("Type your text, choose a reaction, and click Create")
    
    col1, col2 = st.columns(2)
    
    with col1:
        user_text = st.text_area(
            "Your Text", 
            height=120,
            placeholder="Example: Most people quit right before success..."
        )
        
        use_template = st.checkbox("Use template instead")
        if use_template:
            category = st.selectbox("Category", list(HOOK_TEXTS.keys()))
            selected = st.selectbox("Select", HOOK_TEXTS[category])
            if selected:
                user_text = selected
    
    with col2:
        reaction_choice = st.selectbox(
            "Reaction", 
            ["nod", "laugh", "shocked", "confused", "dance"],
            format_func=lambda x: {
                "nod": "👍 Nod (Green)",
                "laugh": "😂 Laugh (Yellow)",
                "shocked": "😮 Shocked (Red)",
                "confused": "🤔 Confused (Blue)",
                "dance": "💃 Dance (Purple)"
            }.get(x, x)
        )
        
        st.info(f"Selected: {reaction_choice}")
    
    if st.button("🎬 CREATE SHORT", type="primary", use_container_width=True):
        if not user_text:
            st.warning("Please enter some text")
        else:
            with st.spinner("Creating your short... 10-15 seconds"):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"short_{timestamp}.mp4"
                
                create_simple_short(user_text, reaction_choice, output_path)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                st.success("✅ Short created successfully!")
                st.video(video_bytes)
                
                st.download_button(
                    "📥 Download Short",
                    video_bytes,
                    f"short_{timestamp}.mp4",
                    "video/mp4"
                )
                
                st.session_state.videos.append({
                    "name": f"short_{len(st.session_state.videos)+1}",
                    "bytes": video_bytes
                })
                
                os.remove(output_path)

# ============================================
# TAB 2: AUTO GENERATE SHORTS
# ============================================
with tab2:
    st.markdown("### Auto Generate Shorts")
    st.caption("Select how many shorts you want - system creates them automatically")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_shorts = st.slider("Number of Shorts", 1, 20, 5)
    
    with col2:
        auto_reaction = st.selectbox(
            "Reaction for all", 
            ["nod", "laugh", "shocked", "confused", "dance"],
            index=0,
            key="auto_reaction"
        )
    
    if st.button("🚀 GENERATE SHORTS", type="primary", use_container_width=True):
        with st.spinner(f"Creating {num_shorts} shorts..."):
            os.makedirs("auto_output", exist_ok=True)
            progress_bar = st.progress(0)
            shorts_data = []
            
            for i in range(num_shorts):
                hook = random.choice(ALL_HOOK_TEXTS)
                output_path = f"auto_output/short_{i+1:03d}.mp4"
                
                create_simple_short(hook, auto_reaction, output_path)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                shorts_data.append({
                    "num": i+1,
                    "text": hook,
                    "bytes": video_bytes,
                    "path": output_path
                })
                
                # Show each short as it completes
                with st.expander(f"✅ Short #{i+1}: {hook[:60]}...", expanded=False):
                    st.video(video_bytes)
                    st.download_button(
                        f"📥 Download", 
                        video_bytes, 
                        f"short_{i+1:03d}.mp4", 
                        "video/mp4",
                        key=f"auto_dl_{i}"
                    )
                
                progress_bar.progress((i + 1) / num_shorts)
            
            st.success(f"✅ Created {num_shorts} shorts!")
            st.balloons()
            
            # Create ZIP file
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for short in shorts_data:
                    zip_file.write(short['path'], f"short_{short['num']:03d}.mp4")
            
            zip_buffer.seek(0)
            st.download_button(
                "📦 DOWNLOAD ALL SHORTS (ZIP)",
                zip_buffer,
                f"shorts_{datetime.now().strftime('%Y%m%d')}.zip",
                "application/zip"
            )

# ============================================
# MY VIDEOS SECTION
# ============================================
if st.session_state.videos:
    st.divider()
    st.subheader("📦 Your Created Videos")
    
    for i, video in enumerate(st.session_state.videos):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.video(video["bytes"])
        with col2:
            st.download_button(
                "📥 Download", 
                video["bytes"], 
                f"{video['name']}.mp4", 
                "video/mp4", 
                key=f"my_vid_{i}"
            )
    
    if st.button("🗑️ Clear All Videos"):
        st.session_state.videos = []
        st.rerun()

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
### ✅ How to Use

| Mode | Steps |
| :--- | :--- |
| **CREATE ONE** | Type text → Choose reaction → Click Create → Download |
| **AUTO GENERATE** | Choose number → Click Generate → Download ZIP |

### 🎨 Reactions

| Reaction | Color | Text |
| :--- | :--- | :--- |
| Nod | 🟢 Green | 👍 AGREE! |
| Laugh | 🟡 Yellow | 😂 FUNNY! |
| Shocked | 🔴 Red | 😮 NO WAY! |
| Confused | 🔵 Blue | 🤔 HMM... |
| Dance | 🟣 Purple | 💃 LET'S GO! |

**No API keys needed. No complex setup. Works instantly.**
""")
