import streamlit as st
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import time
import urllib.parse

# --- Page Setup ---
st.set_page_config(page_title="Student Meme & Poster Creator", page_icon="🎓", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .category-card {
        padding: 1rem;
        border-radius: 10px;
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        margin-bottom: 1rem;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    .template-btn {
        width: 100%;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('''
<div class="main-header">
    <h1>🎓 AI Meme & Poster Creator for Students</h1>
    <p style="font-size: 1.2em; margin-top: 1rem;">Create stunning posters for college events, social media content, and fun memes - no design skills needed!</p>
</div>
''', unsafe_allow_html=True)

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'current_image' not in st.session_state:
    st.session_state.current_image = None
if 'saved_designs' not in st.session_state:
    st.session_state.saved_designs = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Design Settings")
    
    # Purpose selector
    st.subheader("🎯 What are you creating?")
    purpose = st.selectbox(
        "Select Purpose",
        ["College Event Poster", "Social Media Post", "Meme", "Announcement", "Workshop/Seminar", "Club Activity", "Motivational Poster", "Custom"],
        index=0
    )
    
    # Image settings
    st.subheader("📐 Size & Format")
    
    # Preset sizes for different platforms
    size_presets = {
        "Instagram Post (1:1)": (1080, 1080),
        "Instagram Story": (1080, 1920),
        "Facebook Post": (1200, 630),
        "Twitter Post": (1200, 675),
        "A4 Poster": (2480, 3508),
        "A3 Poster": (3508, 4961),
        "Custom": (1024, 1024)
    }
    
    size_preset = st.selectbox("Size Preset", list(size_presets.keys()), index=0)
    
    if size_preset == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            width = st.number_input("Width", 512, 4096, 1024, 128)
        with col2:
            height = st.number_input("Height", 512, 4096, 1024, 128)
    else:
        width, height = size_presets[size_preset]
        st.info(f"📏 Size: {width}x{height}px")
    
    # Style
    art_style = st.selectbox(
        "Visual Style",
        ["Modern Minimal", "Bold & Colorful", "Professional", "Vintage Retro", "Cyberpunk", "Anime", "Cartoon", "3D Render", "Realistic Photo"],
        index=0
    )
    
    # Text settings
    st.subheader("✍️ Text Options")
    text_position = st.radio("Text Position", ["Top", "Bottom", "Center", "Top & Bottom", "None"], index=0)
    text_size = st.slider("Text Size", 24, 100, 50)
    
    col1, col2 = st.columns(2)
    with col1:
        text_color = st.color_picker("Text Color", "#FFFFFF")
    with col2:
        outline_color = st.color_picker("Outline", "#000000")
    
    # Effects
    st.subheader("✨ Visual Effects")
    apply_effects = st.checkbox("Enable Effects")
    if apply_effects:
        brightness = st.slider("Brightness", 0.5, 1.5, 1.0, 0.1)
        contrast = st.slider("Contrast", 0.5, 1.5, 1.0, 0.1)
        saturation = st.slider("Saturation", 0.5, 1.5, 1.0, 0.1)

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["🎨 Create", "📋 Templates", "💾 My Designs", "💡 AI Caption Generator"])

with tab1:
    col_main, col_tips = st.columns([2, 1])
    
    with col_main:
        st.subheader("📝 Describe Your Poster/Meme")
        
        # Context-aware prompt helper
        if purpose != "Custom":
            st.info(f"💡 **Tip for {purpose}:** Be specific about the theme, colors, and mood you want!")
        
        prompt = st.text_area(
            "Image Description",
            placeholder="Example: A vibrant college fest poster with music notes, colorful lights, energetic crowd, modern design...",
            height=120,
            help="Describe what you want to see in your image"
        )
        
        # Quick prompt enhancer
        col_e1, col_e2, col_e3 = st.columns(3)
        with col_e1:
            add_energy = st.checkbox("Add Energy 🔥", help="Makes it more vibrant")
        with col_e2:
            add_professional = st.checkbox("Professional 💼", help="Makes it clean and formal")
        with col_e3:
            add_fun = st.checkbox("Fun & Playful 🎉", help="Makes it more casual")
        
        # Text inputs
        st.markdown("---")
        st.subheader("📝 Add Text to Your Design")
        
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            main_text = st.text_input("Main Headline", placeholder="COLLEGE FEST 2024")
            subtext = st.text_input("Subtitle/Details", placeholder="Join us for the biggest celebration!")
        with col_t2:
            bottom_text = st.text_input("Bottom Text (Optional)", placeholder="Date: Dec 25 | Venue: Campus Ground")
            contact_info = st.text_input("Contact/Info (Optional)", placeholder="Contact: +91 98765 43210")
        
        # Generate buttons
        st.markdown("---")
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            generate = st.button("🎨 Generate Design", type="primary", use_container_width=True)
        with col_btn2:
            if st.button("🎲 Surprise Me!", use_container_width=True):
                st.session_state.random_gen = True
        with col_btn3:
            if st.button("💡 AI Suggest", use_container_width=True):
                st.session_state.show_ai_suggest = True
        with col_btn4:
            if st.session_state.current_image:
                if st.button("🔄 Remix", use_container_width=True):
                    st.session_state.remix = True
    
    with col_tips:
        st.markdown('<div class="category-card">', unsafe_allow_html=True)
        st.markdown("### 🎯 Quick Tips")
        st.markdown("""
        **Great designs have:**
        - ✅ Clear main message
        - ✅ Eye-catching visuals
        - ✅ Readable text
        - ✅ Consistent colors
        - ✅ Purpose-driven style
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="category-card">', unsafe_allow_html=True)
        st.markdown("### 🔥 Trending Styles")
        st.markdown("""
        - **Neon Vibes** - Perfect for parties
        - **Minimal Clean** - Professional events
        - **Bold Typography** - Announcements
        - **Gradient Magic** - Modern look
        - **Retro Pop** - Fun activities
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="category-card">', unsafe_allow_html=True)
        st.markdown("### 📱 Best For")
        
        platform_tips = {
            "Instagram": "Square or Story format",
            "Facebook": "Landscape with bold text",
            "WhatsApp": "Compress for sharing",
            "Print": "Use A4/A3 sizes"
        }
        
        for platform, tip in platform_tips.items():
            st.markdown(f"**{platform}:** {tip}")
        st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("📋 Ready-to-Use Templates")
    st.write("Click any template to customize it for your needs!")
    
    # Categorized templates
    template_categories = {
        "🎉 College Events": {
            "Cultural Fest": "Vibrant college cultural festival poster with dancing silhouettes, colorful lights, stage performance, energetic crowd, modern design",
            "Sports Day": "Dynamic sports event poster with athletes running, jumping, playing, stadium background, energetic action shots",
            "Tech Fest": "Futuristic technology festival poster with circuit boards, robots, AI elements, holographic displays, cyberpunk style",
            "Fresher's Party": "Fun and colorful fresher's welcome party poster with confetti, balloons, excited students, celebration theme",
        },
        "📚 Academic": {
            "Workshop": "Professional workshop poster with learning elements, books, laptop, presentation screen, clean modern design",
            "Seminar": "Elegant seminar poster with microphone, audience, professional setting, academic theme",
            "Guest Lecture": "Sophisticated guest lecture poster with auditorium, speaker podium, formal academic atmosphere",
            "Exam Motivation": "Motivational study poster with books, coffee, determined student, inspirational quotes background",
        },
        "🎭 Club Activities": {
            "Music Club": "Musical performance poster with instruments, musical notes, stage lights, energetic concert vibe",
            "Drama Club": "Theatrical performance poster with stage curtains, masks, spotlight, dramatic atmosphere",
            "Photography Club": "Creative photography club poster with camera, lenses, beautiful landscapes, artistic composition",
            "Coding Club": "Tech coding club poster with computer code, algorithms, matrix style, hacker aesthetic",
        },
        "😂 Fun Memes": {
            "Study Life": "Relatable student studying late night with coffee, tired expression, messy desk, funny situation",
            "Exam Stress": "Stressed student before exams, panic mode, surrounded by books, comedic expression",
            "Campus Life": "Funny college daily life situation, students hanging out, casual campus setting",
            "Assignment Deadline": "Student rushing to complete assignment, laptop, panic, funny deadline situation",
        },
        "📢 Announcements": {
            "Registration Open": "Clean registration announcement poster with form icons, checkmarks, modern professional design",
            "Competition": "Exciting competition announcement with trophy, podium, competitive elements, bold design",
            "Deadline Notice": "Important deadline notice poster with clock, calendar, urgent warning style, clear information",
            "Results Out": "Results announcement poster with grades, achievement symbols, celebration or suspense theme",
        }
    }
    
    for category, templates in template_categories.items():
        with st.expander(category, expanded=True):
            cols = st.columns(2)
            for idx, (name, template_prompt) in enumerate(templates.items()):
                with cols[idx % 2]:
                    if st.button(f"📌 {name}", key=f"template_{category}_{name}", use_container_width=True):
                        st.session_state.selected_template = template_prompt
                        st.session_state.template_name = name
                        st.rerun()

with tab3:
    st.subheader("💾 My Saved Designs")
    
    if st.session_state.history:
        st.write(f"**Total creations: {len(st.session_state.history)}**")
        
        # Filter options
        col_f1, col_f2 = st.columns([3, 1])
        with col_f2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.history = []
                st.rerun()
        
        # Display history
        cols = st.columns(3)
        for idx, item in enumerate(reversed(st.session_state.history)):
            with cols[idx % 3]:
                st.image(item['image'], use_container_width=True)
                st.caption(f"🕐 {time.strftime('%I:%M %p', time.localtime(item['timestamp']))}")
                
                # Download button for each
                buf = BytesIO()
                item['image'].save(buf, format="PNG")
                st.download_button(
                    "⬇️ Download",
                    data=buf.getvalue(),
                    file_name=f"design_{idx}.png",
                    mime="image/png",
                    key=f"download_hist_{idx}",
                    use_container_width=True
                )
    else:
        st.info("📭 No designs yet. Create your first masterpiece!")
        st.image("https://via.placeholder.com/400x300/667eea/ffffff?text=Start+Creating!", use_container_width=True)

with tab4:
    st.subheader("💡 AI Caption & Text Generator")
    st.write("Let AI help you write catchy captions and text for your designs!")
    
    caption_type = st.selectbox(
        "What do you need?",
        ["Event Headline", "Catchy Tagline", "Call to Action", "Funny Meme Text", "Motivational Quote", "Event Details"]
    )
    
    caption_context = st.text_input("Tell us about your event/theme:", placeholder="E.g., Annual tech fest with coding competitions")
    
    if st.button("✨ Generate Caption Ideas", use_container_width=True):
        with st.spinner("Thinking..."):
            # Pre-generated suggestions based on type
            suggestions = {
                "Event Headline": [
                    f"🎯 {caption_context.upper() if caption_context else 'YOUR EVENT'} - DON'T MISS OUT!",
                    f"🔥 THE BIGGEST {caption_context.upper() if caption_context else 'EVENT'} OF THE YEAR",
                    f"⚡ {caption_context.upper() if caption_context else 'JOIN US'} - LIMITED SPOTS!",
                ],
                "Catchy Tagline": [
                    "Where Innovation Meets Celebration! 🚀",
                    "Making Memories, Building Futures! ✨",
                    "Your Journey Begins Here! 🎓",
                ],
                "Call to Action": [
                    "REGISTER NOW - Spots Filling Fast! 📝",
                    "Join Us & Be Part of Something Amazing! 🌟",
                    "Don't Wait - Secure Your Spot Today! ⚡",
                ],
                "Funny Meme Text": [
                    "WHEN THE DEADLINE IS TONIGHT\nBUT NETFLIX IS LIFE 😅",
                    "ME: I'LL START STUDYING\nALSO ME: *SCROLLS FOR 3 HOURS* 📱",
                    "ASSIGNMENT DUE TOMORROW\nME: TIME TO PANIC! 😱",
                ],
                "Motivational Quote": [
                    "Dream Big. Work Hard. Stay Focused. 💪",
                    "Success Begins Where Comfort Zone Ends! 🎯",
                    "Your Only Limit Is You! 🚀",
                ],
                "Event Details": [
                    f"📅 Date: [Your Date]\n📍 Venue: [Your Venue]\n⏰ Time: [Your Time]\n📞 Contact: [Your Number]",
                    f"🎯 What: {caption_context if caption_context else '[Event Name]'}\n🕐 When: [Date & Time]\n📍 Where: [Location]\n💰 Entry: [Free/Paid]",
                ]
            }
            
            st.success("✅ Here are your AI-generated suggestions:")
            for i, suggestion in enumerate(suggestions.get(caption_type, ["No suggestions"]), 1):
                st.info(f"**Option {i}:**\n{suggestion}")
                if st.button(f"📋 Copy Option {i}", key=f"copy_{i}"):
                    st.code(suggestion)

# Handle template selection
if hasattr(st.session_state, 'selected_template'):
    prompt = st.session_state.selected_template
    if hasattr(st.session_state, 'template_name'):
        st.toast(f"✅ Loaded template: {st.session_state.template_name}")
    del st.session_state.selected_template
    if hasattr(st.session_state, 'template_name'):
        del st.session_state.template_name

# Image generation function
def generate_image_pollinations(prompt, width=512, height=512, style=""):
    """Generate image using Pollinations.ai"""
    style_map = {
        "Modern Minimal": "minimalist modern design clean aesthetic",
        "Bold & Colorful": "vibrant bold colors energetic eye-catching",
        "Professional": "professional clean corporate elegant",
        "Vintage Retro": "vintage retro nostalgic 80s style",
        "Cyberpunk": "cyberpunk neon futuristic sci-fi",
        "Anime": "anime manga japanese animation style",
        "Cartoon": "cartoon illustrated playful fun",
        "3D Render": "3d rendered glossy modern cgi",
        "Realistic Photo": "photorealistic detailed professional photography"
    }
    
    full_prompt = f"{prompt}, {style_map.get(style, '')}"
    encoded_prompt = urllib.parse.quote(full_prompt)
    api_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&enhance=true"
    
    response = requests.get(api_url, timeout=30)
    if response.status_code == 200:
        return Image.open(BytesIO(response.content))
    raise Exception(f"Failed to generate image")

def add_text_to_image(image, texts, position, font_size, text_color, outline_color):
    """Add multiple text layers to image"""
    img = image.copy()
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(font_size * 0.6))
    except:
        font = ImageFont.load_default()
        small_font = font
    
    img_width, img_height = img.size
    y_positions = {
        "Top": 40,
        "Center": img_height // 2 - 50,
        "Bottom": img_height - 150,
    }
    
    current_y = y_positions.get(position, 40)
    
    for text_content, use_font in texts:
        if not text_content:
            continue
        
        text_upper = text_content.upper()
        bbox = draw.textbbox((0, 0), text_upper, font=use_font)
        text_width = bbox[2] - bbox[0]
        x = (img_width - text_width) // 2
        
        # Draw outline
        for adj in range(-3, 4):
            for adj_y in range(-3, 4):
                draw.text((x + adj, current_y + adj_y), text_upper, font=use_font, fill=outline_color)
        
        # Draw main text
        draw.text((x, current_y), text_upper, fill=text_color, font=use_font)
        current_y += bbox[3] - bbox[1] + 20
    
    return img

# Main generation
if generate and prompt:
    with st.spinner("🎨 Creating your design... This may take 10-20 seconds"):
        try:
            # Enhance prompt based on options
            enhanced_prompt = prompt
            if add_energy:
                enhanced_prompt += ", high energy vibrant dynamic"
            if add_professional:
                enhanced_prompt += ", professional clean elegant"
            if add_fun:
                enhanced_prompt += ", fun playful cheerful"
            
            # Generate
            image = generate_image_pollinations(enhanced_prompt, width, height, art_style)
            
            # Apply effects
            if apply_effects:
                if brightness != 1.0:
                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(brightness)
                if contrast != 1.0:
                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(contrast)
                if saturation != 1.0:
                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(saturation)
            
            # Add text
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", text_size)
                small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", int(text_size * 0.6))
            except:
                font = ImageFont.load_default()
                small_font = font
            
            if text_position != "None":
                texts_to_add = []
                if text_position in ["Top", "Top & Bottom"] and main_text:
                    texts_to_add.append((main_text, font))
                if subtext:
                    texts_to_add.append((subtext, small_font))
                if text_position in ["Bottom", "Top & Bottom"] and bottom_text:
                    texts_to_add.append((bottom_text, small_font))
                if contact_info:
                    texts_to_add.append((contact_info, small_font))
                
                if texts_to_add:
                    image = add_text_to_image(image, texts_to_add, text_position, text_size, text_color, outline_color)
            
            # Save to session
            st.session_state.current_image = image
            st.session_state.history.append({
                'image': image,
                'prompt': prompt,
                'timestamp': time.time()
            })
            
            # Display
            st.balloons()
            st.success("✅ Your design is ready!")
            st.image(image, use_container_width=True)
            
            # Download options
            col_d1, col_d2, col_d3, col_d4 = st.columns(4)
            
            with col_d1:
                buf = BytesIO()
                image.save(buf, format="PNG")
                st.download_button("📥 PNG (Best)", buf.getvalue(), "design.png", "image/png", use_container_width=True)
            
            with col_d2:
                buf = BytesIO()
                image.convert('RGB').save(buf, format="JPEG", quality=95)
                st.download_button("📥 JPG (Print)", buf.getvalue(), "design.jpg", "image/jpeg", use_container_width=True)
            
            with col_d3:
                thumb = image.copy()
                thumb.thumbnail((800, 800))
                buf = BytesIO()
                thumb.save(buf, format="PNG")
                st.download_button("📥 Web (Small)", buf.getvalue(), "design_web.png", "image/png", use_container_width=True)
            
            with col_d4:
                thumb = image.copy()
                thumb.thumbnail((400, 400))
                buf = BytesIO()
                thumb.save(buf, format="PNG")
                st.download_button("📥 WhatsApp", buf.getvalue(), "design_wa.png", "image/png", use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("💡 Try: Different prompt, smaller size, or wait a moment and retry")

elif generate:
    st.warning("⚠️ Please describe what you want to create!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
    <h3>🎓 Made for Students, By Innovation</h3>
    <p>Create. Share. Inspire. No design skills needed! 🚀</p>
    <p style='font-size: 0.9em; margin-top: 1rem;'>💡 Perfect for: College Events | Social Media | Memes | Announcements | Posters</p>
</div>
""", unsafe_allow_html=True)