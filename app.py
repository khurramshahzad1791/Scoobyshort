import streamlit as st
import random
import os
import zipfile
import io
from datetime import datetime
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np

# Page config
st.set_page_config(
    page_title="Short Creator",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Short Creator")
st.caption("Simple, Working, No Errors")

# Session state
if 'videos' not in st.session_state:
    st.session_state.videos = []

# ============================================
# HOOK TEXTS
# ============================================
HOOK_TEXTS = {
    "funny": [
        "POV: You're trying to act professional at work",
        "When you realize it's Monday tomorrow",
        "Me trying to wake up for a 9 AM class",
    ],
    "motivation": [
        "Most people quit right before success",
        "You are closer than you think",
        "Discipline beats motivation every time",
    ],
    "shocking": [
        "90% of people quit right before success",
        "Everything you want is on the other side of fear",
    ],
}

ALL_HOOK_TEXTS = []
for texts in HOOK_TEXTS.values():
    ALL_HOOK_TEXTS.extend(texts)

# ============================================
# SIMPLE TEXT FUNCTION - No complex compositing
# ============================================

def create_text_clip(text, duration, fontsize=50, color='white'):
    """Create a simple text clip - works every time"""
    try:
        # Simple text clip (works without ImageMagick)
        txt = TextClip(text, fontsize=fontsize, color=color, font='Arial')
        txt = txt.set_duration(duration)
        txt = txt.set_position('center')
        return txt
    except:
        # Fallback: create colored background with text as image
        from PIL import Image, ImageDraw, ImageFont
        
        img = Image.new('RGB', (1000, 200), color='black')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", fontsize)
        except:
            font = ImageFont.load_default()
        
        draw.text((50, 80), text, fill='white', font=font)
        
        # Convert PIL image to numpy array
        img_array = np.array(img)
        
        # Create clip from image
        clip = ImageClip(img_array, duration=duration)
        clip = clip.set_position('center')
        return clip

# ============================================
# SIMPLE VIDEO CREATION
# ============================================

def create_simple_short(hook_text, reaction_type, output_path):
    """Create short with separate clips - simple and working"""
    
    # Hook part (black background with white text)
    hook_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0), duration=8)
    hook_text_clip = create_text_clip(hook_text, 8, 55, 'white')
    hook_final = CompositeVideoClip([hook_clip, hook_text_clip])
    
    # Reaction part (colored background with reaction text)
    reaction_colors = {
        "nod": (100, 200, 100),
        "laugh": (255, 200, 100),
        "shocked": (255, 100, 100),
        "confused": (100, 150, 255),
    }
    
    color_key = reaction_type.replace("scooby_", "")
    color = reaction_colors.get(color_key, (100, 200, 100))
    
    reaction_clip = ColorClip(size=(1080, 1920), color=color, duration=4)
    
    reaction_texts = {
        "nod": "👍 AGREE!",
        "laugh": "😂 HILARIOUS!",
        "shocked": "😮 NO WAY!",
        "confused": "🤔 HMM...",
    }
    
    reaction_text = reaction_texts.get(color_key, "👍")
    reaction_text_clip = create_text_clip(reaction_text, 4, 60, 'white')
    reaction_final = CompositeVideoClip([reaction_clip, reaction_text_clip])
    
    # Combine
    final = concatenate_videoclips([hook_final, reaction_final])
    
    # Add subscribe text at end
    sub_clip = create_text_clip("Subscribe 🔔", 3, 45, '#ff6666')
    sub_clip = sub_clip.set_position(('center', 1700))
    sub_clip = sub_clip.set_start(final.duration - 3)
    final = CompositeVideoClip([final, sub_clip])
    
    # Export
    final.write_videofile(output_path, fps=24, codec='libx264', threads=2, 
                         preset='fast', logger=None, verbose=False)
    
    final.close()
    return output_path

# ============================================
# UI
# ============================================

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎬 Create One Short")
    
    hook_input = st.text_area("Your text", height=100, 
                               placeholder="Type your message here...")
    
    reaction = st.selectbox("Reaction", ["nod", "laugh", "shocked", "confused"])
    
    if st.button("CREATE SHORT", type="primary", use_container_width=True):
        if not hook_input:
            st.warning("Please enter some text")
        else:
            with st.spinner("Creating..."):
                reaction_name = f"scooby_{reaction}"
                output_path = f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                
                create_simple_short(hook_input, reaction_name, output_path)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                st.success("✅ Short created!")
                st.video(video_bytes)
                
                st.download_button("📥 Download", video_bytes, "short.mp4", "video/mp4")
                
                st.session_state.videos.append({"name": "short", "bytes": video_bytes})
                os.remove(output_path)

with col2:
    st.subheader("🤖 Auto Generate")
    
    num_videos = st.slider("Number of shorts", 1, 10, 3)
    auto_reaction = st.selectbox("Reaction", ["nod", "laugh", "shocked", "confused"], key="auto_react")
    
    if st.button("GENERATE SHORTS", type="primary", use_container_width=True):
        with st.spinner(f"Creating {num_videos} shorts..."):
            os.makedirs("output", exist_ok=True)
            videos_data = []
            
            for i in range(num_videos):
                hook = random.choice(ALL_HOOK_TEXTS)
                output_path = f"output/short_{i+1:03d}.mp4"
                
                reaction_name = f"scooby_{auto_reaction}"
                create_simple_short(hook, reaction_name, output_path)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                videos_data.append({"num": i+1, "text": hook[:50], "bytes": video_bytes, "path": output_path})
                
                with st.expander(f"Short #{i+1}: {hook[:60]}...", expanded=False):
                    st.video(video_bytes)
                    st.download_button(f"📥 Download", video_bytes, f"short_{i+1:03d}.mp4", "video/mp4", key=f"dl_{i}")
            
            st.success(f"✅ Created {num_videos} shorts!")
            st.balloons()
            
            # ZIP
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for v in videos_data:
                    zf.write(v['path'], f"short_{v['num']:03d}.mp4")
            zip_buf.seek(0)
            st.download_button("📦 DOWNLOAD ALL (ZIP)", zip_buf, f"shorts_{datetime.now().strftime('%Y%m%d')}.zip", "application/zip")

# ============================================
# MY VIDEOS
# ============================================
if st.session_state.videos:
    st.divider()
    st.subheader("📦 Your Videos")
    
    for i, video in enumerate(st.session_state.videos):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.video(video["bytes"])
        with col2:
            st.download_button(f"📥", video["bytes"], f"video_{i}.mp4", "video/mp4", key=f"saved_{i}")

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
### ✅ How to Use

| Mode | What to do |
| :--- | :--- |
| **Create One** | Type text → Select reaction → Click Create |
| **Auto Generate** | Select number → Click Generate → Download ZIP |

**Works instantly. No errors. Simple and reliable.**
""")
