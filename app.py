import streamlit as st
import requests
import random
import os
import time
import shutil
from datetime import datetime
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import zipfile
import io

# Page config
st.set_page_config(
    page_title="Complete Shorts Studio",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Complete Shorts Studio")
st.caption("No API Keys | No ImageMagick | Fully Free | Works Instantly")

# Session state
if 'videos' not in st.session_state:
    st.session_state.videos = []

# ============================================
# 300+ HOOK TEXTS DATABASE
# ============================================
HOOK_TEXTS = {
    "funny": [
        "POV: You're trying to act professional at work",
        "When you realize it's Monday tomorrow",
        "Me trying to wake up for a 9 AM class",
        "That moment when nothing goes right",
        "Expectation vs reality be like",
        "When the food arrives at the restaurant",
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
# TEXT OVERLAY USING PIL (No ImageMagick)
# ============================================

def create_text_overlay(text, font_size=55, color=(255,255,255), height=400, width=1080):
    """Create text overlay using PIL - no ImageMagick needed"""
    try:
        # Create transparent image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Try to load a font
        font = None
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf",
        ]
        for path in font_paths:
            if os.path.exists(path):
                try:
                    font = ImageFont.truetype(path, font_size)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
        
        # Word wrap
        words = text.split()
        lines = []
        current_line = []
        for word in words:
            current_line.append(word)
            test_line = ' '.join(current_line)
            try:
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > width - 100:
                    current_line.pop()
                    lines.append(' '.join(current_line))
                    current_line = [word]
            except:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))
        
        # Draw each line
        y_offset = 0
        line_height = font_size + 10
        total_height = len(lines) * line_height
        start_y = (height - total_height) // 2
        
        for line in lines:
            try:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = (width - text_width) // 2
                y = start_y + y_offset
                
                # Draw outline
                for offset in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                    draw.text((x+offset[0], y+offset[1]), line, fill=(0, 0, 0), font=font)
                draw.text((x, y), line, fill=color, font=font)
                y_offset += line_height
            except:
                y_offset += line_height
        
        # Convert to numpy array for MoviePy
        return np.array(img)
    except Exception as e:
        print(f"Text creation error: {e}")
        # Return a simple colored rectangle as fallback
        fallback = Image.new('RGBA', (width, height), (0, 0, 0, 180))
        return np.array(fallback)

def create_text_image_simple(text, font_size=55, color=(255,255,255)):
    """Simple text image for reactions"""
    width, height = 500, 200
    img = Image.new('RGBA', (width, height), (0, 0, 0, 180))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = (height - 50) // 2
        draw.text((x, y), text, fill=color, font=font)
    except:
        pass
    
    return np.array(img)

# ============================================
# VIDEO CREATION FUNCTIONS
# ============================================

def make_vertical(clip):
    """Convert to 9:16 vertical format"""
    try:
        if clip.w / clip.h > 9/16:
            clip = clip.resize(height=1920)
            clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=1080, height=1920)
        else:
            clip = clip.resize(width=1080)
            clip = clip.crop(x_center=clip.w/2, y_center=clip.h/2, width=1080, height=1920)
    except:
        clip = clip.resize((1080, 1920))
    return clip

def create_colored_background(duration, color=(20, 20, 60)):
    """Create a colored background clip"""
    return ColorClip(size=(1080, 1920), color=color, duration=duration)

def create_reaction_clip(reaction_type, duration=3):
    """Create a reaction clip using colored background + text (no ImageMagick)"""
    colors = {
        "scooby_nod": (100, 200, 100),
        "scooby_laugh": (255, 200, 100),
        "scooby_shocked": (255, 150, 100),
        "scooby_confused": (100, 150, 255),
        "scooby_dance": (100, 255, 150),
    }
    
    color = colors.get(reaction_type, (100, 200, 100))
    clip = ColorClip(size=(1080, 1920), color=color, duration=duration)
    
    # Add text using PIL image overlay
    reaction_texts = {
        "scooby_nod": "👍 AGREE!",
        "scooby_laugh": "😂 HILARIOUS!",
        "scooby_shocked": "😮 NO WAY!",
        "scooby_confused": "🤔 WAIT WHAT?",
        "scooby_dance": "💃 LET'S GO!",
    }
    
    text = reaction_texts.get(reaction_type, "👍")
    
    # Create text as image overlay
    text_img = create_text_image_simple(text, 60, (255, 255, 255))
    text_clip = ImageClip(text_img, transparent=False, duration=duration)
    text_clip = text_clip.set_position(('center', 900))
    
    return CompositeVideoClip([clip, text_clip])

def create_hook_with_text(hook_text, duration=5, color=(20, 20, 80)):
    """Create hook video with text overlay"""
    clip = create_colored_background(duration, color)
    
    if hook_text:
        text_img = create_text_overlay(hook_text, 55, (255, 255, 255), 500)
        text_clip = ImageClip(text_img, transparent=False, duration=duration)
        text_clip = text_clip.set_position(('center', 400))
        clip = CompositeVideoClip([clip, text_clip])
    
    return clip

def create_short(hook_text, reaction_type, output_path, hook_duration=8, reaction_duration=4):
    """Create complete short with hook + reaction"""
    
    # Create hook part
    hook_clip = create_hook_with_text(hook_text, hook_duration, (20, 20, 80))
    
    # Create reaction part
    reaction_clip = create_reaction_clip(reaction_type, reaction_duration)
    
    # Combine
    final = concatenate_videoclips([hook_clip, reaction_clip])
    
    # Add subscribe text at end
    sub_img = create_text_overlay("Subscribe 🔔 for more", 45, (255, 100, 100), 150)
    sub_clip = ImageClip(sub_img, transparent=False, duration=3)
    sub_clip = sub_clip.set_position(('center', 1750)).set_start(final.duration - 3)
    final = CompositeVideoClip([final, sub_clip])
    
    # Export
    final.write_videofile(output_path, fps=24, codec='libx264', threads=2, 
                         preset='fast', bitrate='1500k', logger=None, verbose=False)
    
    final.close()
    return output_path

def create_short_with_uploads(hook_file, reaction_file, hook_text, reaction_type, output_path):
    """Create short with user uploaded videos"""
    
    temp_files = []
    
    # Process hook video
    if hook_file is not None:
        hook_path = "temp_hook.mp4"
        with open(hook_path, "wb") as f:
            f.write(hook_file.getbuffer())
        temp_files.append(hook_path)
        try:
            hook_clip = VideoFileClip(hook_path)
            hook_clip = hook_clip.subclip(0, min(8, hook_clip.duration))
            hook_clip = make_vertical(hook_clip)
        except:
            hook_clip = create_hook_with_text(hook_text, 8, (20, 20, 80))
    else:
        hook_clip = create_hook_with_text(hook_text, 8, (20, 20, 80))
    
    # Process reaction video
    if reaction_file is not None:
        reaction_path = "temp_reaction.mp4"
        with open(reaction_path, "wb") as f:
            f.write(reaction_file.getbuffer())
        temp_files.append(reaction_path)
        try:
            reaction_clip = VideoFileClip(reaction_path)
            reaction_clip = reaction_clip.subclip(0, min(4, reaction_clip.duration))
            reaction_clip = make_vertical(reaction_clip)
        except:
            reaction_clip = create_reaction_clip(reaction_type, 4)
    else:
        reaction_clip = create_reaction_clip(reaction_type, 4)
    
    # Combine
    final = concatenate_videoclips([hook_clip, reaction_clip])
    
    # Add subscribe
    sub_img = create_text_overlay("Subscribe 🔔 for more", 45, (255, 100, 100), 150)
    sub_clip = ImageClip(sub_img, transparent=False, duration=3)
    sub_clip = sub_clip.set_position(('center', 1750)).set_start(final.duration - 3)
    final = CompositeVideoClip([final, sub_clip])
    
    # Export
    final.write_videofile(output_path, fps=24, codec='libx264', threads=2, 
                         preset='fast', bitrate='1500k', logger=None, verbose=False)
    
    final.close()
    hook_clip.close()
    reaction_clip.close()
    
    for f in temp_files:
        if os.path.exists(f):
            try: os.remove(f)
            except: pass
    
    return output_path

# ============================================
# UI TABS
# ============================================

tab1, tab2, tab3, tab4 = st.tabs([
    "🎬 SMART CREATE", 
    "🤖 AUTO MODE", 
    "✂️ EDIT VIDEO", 
    "📦 MY VIDEOS"
])

# ============================================
# TAB 1: SMART CREATE
# ============================================
with tab1:
    st.markdown("### 🎬 Smart Create")
    st.caption("Enter your hook text → Get a short instantly (no uploads needed)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        hook_text_input = st.text_area("Your Hook Text", height=100, 
                                        placeholder="e.g., Most people quit right before success...")
        
        use_template = st.checkbox("Use viral hook template")
        if use_template:
            category = st.selectbox("Category", list(HOOK_TEXTS.keys()), key="smart_cat")
            selected_hook = st.selectbox("Select hook", HOOK_TEXTS[category], key="smart_hook_sel")
            if selected_hook:
                hook_text_input = selected_hook
    
    with col2:
        reaction_type = st.selectbox("Reaction Type", 
                                      ["scooby_nod", "scooby_laugh", "scooby_shocked", "scooby_confused", "scooby_dance"])
        
        st.caption("🎨 Colors: Green=Nod, Orange=Laugh, Red=Shocked, Blue=Confused, Green=Dance")
    
    if st.button("🎬 CREATE SHORT", type="primary", use_container_width=True):
        if not hook_text_input:
            st.warning("Please enter hook text or use a template")
        else:
            with st.spinner("Creating your Short... 10-20 seconds"):
                output_path = f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
                
                create_short(hook_text_input, reaction_type, output_path, 8, 4)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                st.success("✅ Short created successfully!")
                st.video(video_bytes)
                
                st.download_button(
                    label="📥 Download Short",
                    data=video_bytes,
                    file_name=f"short_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4",
                    mime="video/mp4"
                )
                
                st.session_state.videos.append({
                    "name": f"short_{len(st.session_state.videos)+1}",
                    "bytes": video_bytes
                })
                
                os.remove(output_path)

# ============================================
# TAB 2: AUTO MODE
# ============================================
with tab2:
    st.markdown("### 🤖 Auto Mode - No Input Needed")
    st.caption("Click generate → System creates shorts automatically")
    
    col1, col2 = st.columns(2)
    
    with col1:
        num_videos = st.slider("Number of shorts", 1, 20, 5)
        reaction_auto = st.selectbox("Reaction type", 
                                      ["scooby_nod", "scooby_laugh", "scooby_shocked", "scooby_confused", "scooby_dance"],
                                      key="auto_reaction")
    
    with col2:
        category_auto = st.selectbox("Hook category", list(HOOK_TEXTS.keys()), key="auto_cat")
        st.caption(f"Using {len(HOOK_TEXTS[category_auto])} hooks")
    
    if st.button("🚀 GENERATE SHORTS", type="primary", use_container_width=True):
        with st.spinner(f"Creating {num_videos} shorts..."):
            
            os.makedirs("auto_output", exist_ok=True)
            progress = st.progress(0)
            videos_data = []
            
            for i in range(num_videos):
                hook_text = random.choice(HOOK_TEXTS[category_auto])
                output_path = f"auto_output/short_{i+1:03d}.mp4"
                
                create_short(hook_text, reaction_auto, output_path, 8, 4)
                
                with open(output_path, 'rb') as f:
                    video_bytes = f.read()
                
                videos_data.append({"num": i+1, "hook": hook_text[:40], "bytes": video_bytes, "path": output_path})
                
                with st.expander(f"✅ Short #{i+1}: {hook_text[:50]}...", expanded=False):
                    st.video(video_bytes)
                    st.download_button(f"📥 Download", video_bytes, f"short_{i+1:03d}.mp4", "video/mp4", key=f"auto_dl_{i}")
                
                progress.progress((i+1)/num_videos)
            
            st.success(f"✅ Created {num_videos} shorts!")
            st.balloons()
            
            # ZIP download
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, 'w') as zf:
                for v in videos_data:
                    zf.write(v['path'], f"short_{v['num']:03d}.mp4")
            zip_buf.seek(0)
            st.download_button("📦 DOWNLOAD ALL (ZIP)", zip_buf, f"shorts_{datetime.now().strftime('%Y%m%d')}.zip", "application/zip")

# ============================================
# TAB 3: EDIT VIDEO
# ============================================
with tab3:
    st.markdown("### ✂️ Simple Video Editor")
    st.caption("Upload a video to trim")
    
    edit_file = st.file_uploader("Upload video to edit", type=["mp4", "mov", "avi"], key="edit_upload")
    
    if edit_file:
        temp_edit = "temp_edit.mp4"
        with open(temp_edit, "wb") as f:
            f.write(edit_file.getbuffer())
        
        try:
            video = VideoFileClip(temp_edit)
            st.success(f"✅ Video loaded: {video.duration:.1f} seconds")
            
            start = st.slider("Start time (seconds)", 0.0, float(video.duration), 0.0)
            end = st.slider("End time (seconds)", 0.0, float(video.duration), float(video.duration))
            
            if st.button("✂️ TRIM VIDEO", type="primary"):
                with st.spinner("Trimming..."):
                    edited = video.subclip(start, end)
                    output_path = "trimmed_output.mp4"
                    edited.write_videofile(output_path, fps=24, codec='libx264', threads=2, 
                                          preset='fast', logger=None, verbose=False)
                    
                    with open(output_path, 'rb') as f:
                        st.video(f.read())
                        st.download_button("📥 Download Trimmed Video", f.read(), "trimmed_video.mp4", "video/mp4")
                    
                    video.close()
                    edited.close()
                    os.remove(temp_edit)
                    os.remove(output_path)
        except Exception as e:
            st.error(f"Error: {e}")

# ============================================
# TAB 4: MY VIDEOS
# ============================================
with tab4:
    st.markdown("### 📦 Your Created Videos")
    
    if st.session_state.videos:
        for i, video in enumerate(st.session_state.videos):
            st.video(video["bytes"])
            st.download_button(f"📥 Download {video['name']}", video["bytes"], f"{video['name']}.mp4", "video/mp4", key=f"saved_{i}")
        
        if st.button("🗑️ Clear All Videos"):
            st.session_state.videos = []
            st.rerun()
    else:
        st.info("No videos created yet. Go to SMART CREATE or AUTO MODE!")

# ============================================
# FOOTER
# ============================================
st.divider()
st.markdown("""
### ✅ Features Summary

| Mode | What you need | Result |
| :--- | :--- | :--- |
| **SMART CREATE** | Hook text only | 1 custom short |
| **AUTO MODE** | Nothing! | 5-20 shorts automatically |

### 🎯 Quick Start

1. **AUTO MODE**: Click generate → Get 5 shorts instantly
2. **SMART CREATE**: Type text → Click create → Download

**No API keys. No ImageMagick. No uploads needed. Works instantly!**
""")
