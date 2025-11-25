import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import re
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="GlobalAdSync", 
    page_icon="🌍", 
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --danger-color: #ef4444;
        --bg-light: #f8fafc;
        --bg-white: #ffffff;
        --text-dark: #000000;
        --text-muted: #000000;
        --border-color: #e2e8f0;
    }
        
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 2px solid var(--border-color);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem;
    }
    
    /* Sidebar title */
    [data-testid="stSidebar"] .element-container:first-child h1 {
        color: var(--primary-color);
        font-size: 1.5rem !important;
        font-weight: 700;
        margin-bottom: 2rem;
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
    }
            
    header[data-testid="stHeader"] {
        display: none !important;
    }

    /* fully remove top decoration bar */
    [data-testid="stDecoration"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
        border: none !important;
    }
    
    /* Cards */
    .content-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: #E2C958;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button:hover {
        background-color: green;
        color: #f4f5f7;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: none;
        padding: 0.75rem;
        font-size: 1rem;
        background: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        background: white;
    }

    .st-ey {
    -webkit-text-fill-color: black; /* any color you want */
    }
            
    .st-gi{
        -webkit-text-fill-color: black;
    }
    
    .st-af {
    position: relative;
    background-color: #f8f8f8 !important;
    }
    
    .st-af:hover {
     background-color: beige !important;
    }
            
    .st-dl{
        background-color:#f8f8f8 !important;        
    }
    
    .st-dl:hover{
        background-color:beige !important;        
    }
            
            
    /* Expander */
    .streamlit-expanderHeader {
        background: white;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        padding: 1rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        border-color: var(--primary-color);
        background: #f8fafc;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: #d1fae5;
        border-left: 4px solid var(--success-color);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background: #fee2e2;
        border-left: 4px solid var(--danger-color);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background: #fef3c7;
        border-left: 4px solid var(--warning-color);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* Quality score badges */
    .quality-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
    }
    
    .quality-high {
        background: #d1fae5;
        color: #047857;
    }
    
    .quality-medium {
        background: #fef3c7;
        color: #b45309;
    }
    
    .quality-low {
        background: #fee2e2;
        color: #b91c1c;
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-color);
    }
                
/* General input styling */
input, textarea, select,
.stTextInput input,
.stTextArea textarea,
.stSelectbox select {
    background-color: #f4f5f7 !important;
    color: #000000 !important;        /* Inner text black */
    caret-color: #000000 !important;  /* Cursor visible */
}

/* Deeply nested input selectors for Streamlit */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > select {
    background-color: #f4f5f7 !important;
    color: #000000 !important;
    caret-color: #000000 !important;
}

/* MultiSelect support */
.stMultiSelect div[data-baseweb="select"] > div,
.stMultiSelect input,
[data-baseweb="select"] span,    /* selected items */
[data-baseweb="tag"] span {      /* tags inside multiselect */
    background-color: #f4f5f7 !important;
    color: #000000 !important;
    caret-color: #000000 !important;
}
            

/* Optional: consistent placeholder color */
input::placeholder,
textarea::placeholder,
.stMultiSelect input::placeholder {
    color: #888888 !important; /* Lighter gray placeholder */
}

    /* Block container */
    .main .block-container {
        padding: 2rem 4rem !important;
        margin-top: 0 !important;
    }

    /* Tabs container */
    .stTabs {
        position: relative !important;
    }

    /* Wrapper around tab list */
    .stTabs > div:first-child {
        position: -webkit-sticky !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 9999 !important;
        background: transparent !important;
    }

    /* Tab list - make it sticky */
    .stTabs [data-baseweb="tab-list"] {
        justify-content: center !important;
        background: #fffaf0 !important;
        padding: 8px 12px !important;
        border-radius: 9999px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        gap: 12px !important;
        margin: 0 auto 1rem auto !important;
        position: relative !important;
        z-index: 9999 !important;
        max-width: fit-content !important;
    }

    /* Individual tabs */
    .stTabs [data-baseweb="tab"] {
        border-radius: 9999px !important;        /* pill shape */
        padding: 0.75rem 2rem !important;        /* bigger padding */
        font-weight: 600;
        font-size: 1.25rem !important;           /* bigger font */
        background: transparent;
        color: #000 !important;
        transition: all 0.2s ease;
    }

    /* Active tab */
    .stTabs [aria-selected="true"] {
        background: #E2C958 !important;          /* warm yellow for active tab */
        color: #000 !important;
    }

    ::placeholder {
    color: #555 !important;
    }
            
html, body, .stApp{
        font-family:'Figtree', sans-serif !important;
        background: linear-gradient(90deg, #ffffff 0%, #fff7cc 100%)
    }
            
    div, p, label {
        font-family:'Figtree', sans-serif !important;
        color: #000 !important;
    }
    
    summary{
        background: #f4f5f7;
        border-radius: 10px;
    }

    /* Beautiful headings */
    h1, h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }

    h1 {
        font-size: 3rem !important;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        font-size: 2rem !important;
        color: #1e293b !important;
        margin-bottom: 0.75rem !important;
    }

    h3 {
        font-size: 1.5rem !important;
        color: #334155 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Subtitle/description text */
    .subtitle {
        font-size: 1.1rem !important;
        color: #64748b !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        margin-bottom: 2rem !important;
    }
            
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
    display: none !important;
    }

    h1:hover a, h2:hover a, h3:hover a, h4:hover a, h5:hover a, h6:hover a {
        display: none !important;
    }

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'supabase_url' not in st.session_state:
    st.session_state.supabase_url = ""
if 'supabase_key' not in st.session_state:
    st.session_state.supabase_key = ""
if 'gemini_key' not in st.session_state:
    st.session_state.gemini_key = ""
if 'supabase_client' not in st.session_state:
    st.session_state.supabase_client = None

# Sidebar for API credentials
with st.sidebar:
    st.markdown("# ⚙️ Configure")
    st.markdown("---")
    
    st.markdown("### 🔐 API Credentials")
    supabase_url = st.text_input("Supabase URL", value=st.session_state.supabase_url, type="password", help="Enter your Supabase project URL")
    supabase_key = st.text_input("Supabase Key", value=st.session_state.supabase_key, type="password", help="Enter your Supabase anon/service key")
    gemini_key = st.text_input("Gemini API Key", value=st.session_state.gemini_key, type="password", help="Enter your Google Gemini API key")
    
    st.markdown("")
    if st.button("💾 Save Configuration", use_container_width=True):
        st.session_state.supabase_url = supabase_url
        st.session_state.supabase_key = supabase_key
        st.session_state.gemini_key = gemini_key
        
        # FIX: Only create client if BOTH url and key are provided AND not empty
        if supabase_url and supabase_key and supabase_url.strip() and supabase_key.strip():
            try:
                st.session_state.supabase_client = create_client(supabase_url, supabase_key)
                st.success("✅ Configured!")
            except Exception as e:
                st.error(f"❌ Failed to connect to Supabase: {str(e)}")
                st.session_state.supabase_client = None
        else:
            st.error("Please fill all fields with valid values")
    
    st.markdown("---")
    if st.session_state.supabase_client:
        try:
            supabase = st.session_state.supabase_client
            ad_count = len(supabase.table('ad_copies').select('id').execute().data)
            trans_count = len(supabase.table('translations').select('id').execute().data)
            country_count = len(supabase.table('country_prompts').select('id').execute().data)
            
            st.metric("Ad Copies", ad_count)
            st.metric("Translations", trans_count)
            st.metric("Countries", country_count)
        except Exception as e:
            st.warning(f"Could not fetch stats: {str(e)}")

# Helper functions
def get_supabase() -> Client:
    if st.session_state.supabase_client is None:
        st.error("⚠️ Please configure Supabase credentials in the sidebar")
        st.stop()
    return st.session_state.supabase_client

def get_gemini():
    if not st.session_state.gemini_key:
        st.error("⚠️ Please configure Gemini API key in the sidebar")
        st.stop()
    genai.configure(api_key=st.session_state.gemini_key)
    return genai.GenerativeModel('gemini-2.5-flash')

def extract_placeholders(text):
    """Extract all <placeholder> tags from text"""
    return re.findall(r'<[^>]+>', text)

def translate_text(text, target_language, user_prompt, system_prompt, model):
    """Translate text while preserving placeholders"""
    if not text:
        return text
    
    placeholders = extract_placeholders(text)
    
    # Replace placeholders with markers
    temp_text = text
    for i, placeholder in enumerate(placeholders):
        temp_text = temp_text.replace(placeholder, f"__PLACEHOLDER_{i}__")
    
    # Translate
    prompt = f"""{system_prompt}

{user_prompt}

Translate the following text to {target_language}. 
IMPORTANT: Keep __PLACEHOLDER_X__ markers exactly as they are, do not translate them.

Text to translate:
{temp_text}

Return ONLY the translated text, no explanations."""

    response = model.generate_content(prompt)
    translated = response.text.strip()
    
    # Restore placeholders
    for i, placeholder in enumerate(placeholders):
        translated = translated.replace(f"__PLACEHOLDER_{i}__", placeholder)
    
    return translated

def proofread_translation(original, translated, language, model):
    """Proofread translation and return quality score"""
    prompt = f"""You are a translation quality expert. Evaluate this translation from English to {language}.

Original: {original}
Translation: {translated}

Rate the translation quality from 0-100 based on:
- Accuracy (meaning preserved)
- Fluency (natural in target language)
- Marketing tone (persuasive and engaging)
- Grammar and spelling

If there are errors, provide a corrected version.

Respond ONLY in this JSON format:
{{"score": <0-100>, "corrected": "<corrected translation or original if good>", "feedback": "<brief feedback>"}}"""

    response = model.generate_content(prompt)
    result_text = response.text.strip()
    
    # Extract JSON
    json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
    if json_match:
        result = json.loads(json_match.group())
        return result['score'], result['corrected'], result.get('feedback', '')
    
    return 85, translated, "Auto-approved"

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["Ad Copies", "Translations", "Test Prompts", "Countries"])

# TAB 1: Ad Copies CRUD
with tab1:
    st.markdown("""
    <h2 style='text-align: center;'>GlobalAdSync</h2>
    <p style='text-align: center;'>⭐AI-powered translation that understands context, not just words⭐</p>
    """, unsafe_allow_html=True)
    st.markdown("")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ➕ Create New Ad Copy")
        
        with st.form("new_ad_copy"):
            headline = st.text_input("Headline*", placeholder="e.g Get 50% off today!", help="Main attention-grabbing text")
            body = st.text_area("Body*", placeholder="e.g Shop now and save on <product>...", help="Main ad content. Use <placeholder> for dynamic content")
            link_text = st.text_input("Link Text", placeholder="e.g Link to product", help="Call-to-action button text")
            product = st.text_input("Product", placeholder="e.g Car Care Product", help="Product or service name")
            
            submitted = st.form_submit_button("Create Ad Copy", use_container_width=True)
            if submitted:
                if headline and body:
                    supabase = get_supabase()
                    result = supabase.table('ad_copies').insert({
                        'headline': headline,
                        'body': body,
                        'link_text': link_text,
                        'product': product
                    }).execute()
                    st.success("✅ Ad copy created successfully!")
                    st.rerun()
                else:
                    st.error("⚠️ Headline and Body are required fields")
    
    with col2:
        st.markdown("### 📚 Existing Ad Copies")
        
        supabase = get_supabase()
        ad_copies = supabase.table('ad_copies').select('*').order('created_at', desc=True).execute()
        
        if ad_copies.data:
            for ad in ad_copies.data:
                with st.expander(f"📄 {ad['headline'][:60]}... (ID: {ad['id']})", expanded=False):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        new_headline = st.text_input("Headline", value=ad['headline'], key=f"h_{ad['id']}")
                        new_body = st.text_area("Body", value=ad['body'], key=f"b_{ad['id']}", height=100)
                        new_link_text = st.text_input("Link Text", value=ad.get('link_text', ''), key=f"l_{ad['id']}")
                        new_product = st.text_input("Product", value=ad.get('product', ''), key=f"p_{ad['id']}")

                    with col_b:
                            st.markdown("")
                            st.markdown("")
                            if st.button("💾 Update", key=f"upd_{ad['id']}", use_container_width=True):
                                supabase.table('ad_copies').update({
                                    'headline': new_headline,
                                    'body': new_body,
                                    'link_text': new_link_text,
                                    'product': new_product
                                }).eq('id', ad['id']).execute()
                                st.success("✅ Updated!")
                                st.rerun()
                            
                            if st.button("🗑️ Delete", key=f"del_{ad['id']}", use_container_width=True):
                                supabase.table('ad_copies').delete().eq('id', ad['id']).execute()
                                st.success("🗑️ Deleted!")
                                st.rerun()
        else:
            st.info("📭 No ad copies yet. Create your first one using the form on the left!")

# TAB 2: Translations
with tab2:
    st.markdown("## 🌐 Translation Dashboard")
    st.markdown("Translate your ad copies to multiple languages and manage all translations in one place.")
    st.markdown("")
    
    supabase = get_supabase()
    ad_copies = supabase.table('ad_copies').select('*').execute()
    countries = supabase.table('country_prompts').select('*').execute()
    
    if not ad_copies.data:
        st.warning("⚠️ Please create ad copies first in the 'Ad Copies' tab")
    elif not countries.data:
        st.warning("⚠️ Please add countries first in the 'Countries' tab")
    else:
        st.markdown("### 🚀 Bulk Translation")
        col1, col2 = st.columns(2)
        
        with col1:
            selected_ads = st.multiselect(
                "Select Ad Copies",
                options=ad_copies.data,
                format_func=lambda x: f"{x['headline'][:50]}... (ID: {x['id']})",
                default=[ad_copies.data[0]] if ad_copies.data else [],
                help="Choose one or more ad copies to translate"
            )
        
        with col2:
            selected_countries = st.multiselect(
                "Select Target Countries",
                options=[c['country_code'] for c in countries.data],
                default=[c['country_code'] for c in countries.data[:2]],
                help="Choose destination languages"
            )
        
        if st.button("🚀 Start Translation", use_container_width=True, type="primary"):
            if selected_ads and selected_countries:
                model = get_gemini()
                
                total_tasks = len(selected_ads) * len(selected_countries)
                progress_bar = st.progress(0)
                status_text = st.empty()
                task_count = 0
                
                for ad in selected_ads:
                    for country_code in selected_countries:
                        status_text.text(f"🔄 Translating Ad ID {ad['id']} to {country_code}...")
                        
                        # Get country prompts
                        country = next((c for c in countries.data if c['country_code'] == country_code), None)
                        
                        # Translate each field
                        headline_trans = translate_text(
                            ad['headline'],
                            country['language'],
                            country['user_prompt'],
                            country['system_prompt'],
                            model
                        )
                        
                        body_trans = translate_text(
                            ad['body'],
                            country['language'],
                            country['user_prompt'],
                            country['system_prompt'],
                            model
                        )
                        
                        link_trans = translate_text(
                            ad.get('link_text', ''),
                            country['language'],
                            country['user_prompt'],
                            country['system_prompt'],
                            model
                        ) if ad.get('link_text') else ''
                        
                        product_trans = translate_text(
                            ad.get('product', ''),
                            country['language'],
                            country['user_prompt'],
                            country['system_prompt'],
                            model
                        ) if ad.get('product') else ''
                        
                        # Proofread
                        score, corrected_body, feedback = proofread_translation(
                            ad['body'],
                            body_trans,
                            country['language'],
                            model
                        )
                        
                        # Save translation
                        supabase.table('translations').insert({
                            'ad_copy_id': ad['id'],
                            'country_code': country_code,
                            'language': country['language'],
                            'headline': headline_trans,
                            'body': corrected_body,
                            'link_text': link_trans,
                            'product': product_trans,
                            'quality_score': score
                        }).execute()
                        
                        task_count += 1
                        progress_bar.progress(task_count / total_tasks)
                
                status_text.text("✅ Translation complete!")
                st.success(f"✅ Successfully translated {len(selected_ads)} ad copies to {len(selected_countries)} countries!")
                st.balloons()
                st.rerun()
        
        st.markdown("---")
        st.markdown("### 📚 Translation Library")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_country = st.selectbox("🌍 Filter by Country", ["All"] + [c['country_code'] for c in countries.data])
        with col2:
            filter_ad = st.selectbox("📄 Filter by Ad Copy", ["All"] + [f"ID {a['id']}" for a in ad_copies.data])
        with col3:
            filter_quality = st.slider("⭐ Min Quality Score", 0, 100, 0)
        
        # Fetch translations
        query = supabase.table('translations').select('*')
        
        if filter_country != "All":
            query = query.eq('country_code', filter_country)
        
        if filter_ad != "All":
            ad_id = int(filter_ad.split()[1])
            query = query.eq('ad_copy_id', ad_id)
        
        translations = query.gte('quality_score', filter_quality).order('created_at', desc=True).execute()
        
        if translations.data:
            for trans in translations.data:
                score = trans['quality_score']
                score_emoji = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                
                with st.expander(f"{score_emoji} {trans['country_code']} • {trans['headline'][:50]}... • Score: {score}%"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        new_headline_trans = st.text_input("Headline", value=trans['headline'], key=f"th_{trans['id']}")
                        new_body_trans = st.text_area("Body", value=trans['body'], key=f"tb_{trans['id']}", height=100)
                        new_link_text_trans = st.text_input("Link Text", value=trans.get('link_text', ''), key=f"tl_{trans['id']}")
                        new_product_trans = st.text_input("Product", value=trans.get('product', ''), key=f"tp_{trans['id']}")
                        
                        # Quality score display
                        quality_class = "quality-high" if score >= 80 else "quality-medium" if score >= 60 else "quality-low"
                        st.markdown(f'<div class="quality-badge {quality_class}">Quality Score: {score}%</div>', unsafe_allow_html=True)

                    with col_b:
                        st.markdown("")
                        st.markdown("")
                        if st.button("💾 Update", key=f"tupd_{trans['id']}", use_container_width=True):
                            supabase.table('translations').update({
                                'headline': new_headline_trans,
                                'body': new_body_trans,
                                'link_text': new_link_text_trans,
                                'product': new_product_trans
                            }).eq('id', trans['id']).execute()
                            st.success("✅ Updated!")
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"tdel_{trans['id']}", use_container_width=True):
                            supabase.table('translations').delete().eq('id', trans['id']).execute()
                            st.success("🗑️ Deleted!")
                            st.rerun()

        else:
            st.info("🔍 No translations found matching your filters. Try adjusting the filters or create new translations above!")

# TAB 3: Test Prompts
with tab3:
    st.markdown("## 🧪 Prompt Testing Lab")
    st.markdown("Test and refine your translation prompts before using them in production to ensure optimal results.")
    st.markdown("")
    
    supabase = get_supabase()
    countries = supabase.table('country_prompts').select('*').execute()
    
    if countries.data:
        selected_country = st.selectbox(
            "🌍 Select Country to Test",
            options=countries.data,
            format_func=lambda x: f"{x['country_code']} - {x['language']}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📝 Translation Prompts")
            test_system = st.text_area("System Prompt", value=selected_country['system_prompt'], height=120, help="Defines the translator's role and expertise")
            test_user = st.text_area("User Prompt", value=selected_country['user_prompt'], height=120, help="Specific instructions for this translation")
        
        with col2:
            st.markdown("### 📄 Sample Text")
            sample_text = st.text_area("Test Text", value="Get <discount>% off on <product> today! Limited time offer.", height=120, help="Enter text with <placeholders> to test")
        
        if st.button("🧪 Run Test Translation", use_container_width=True, type="primary"):
            model = get_gemini()
            
            with st.spinner("🔄 Translating and analyzing..."):
                translated = translate_text(
                    sample_text,
                    selected_country['language'],
                    test_user,
                    test_system,
                    model
                )
                
                score, corrected, feedback = proofread_translation(
                    sample_text,
                    translated,
                    selected_country['language'],
                    model
                )
            
            st.success("✅ Test complete!")
            st.markdown("")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### 📤 Original")
                st.info(sample_text)
            with col2:
                st.markdown("### 📥 Translation")
                st.success(corrected)
                
                score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                quality_class = "quality-high" if score >= 80 else "quality-medium" if score >= 60 else "quality-low"
                st.markdown(f'<div class="quality-badge {quality_class}">{score_color} Quality Score: {score}%</div>', unsafe_allow_html=True)
                st.markdown(f"**💬 Feedback:** {feedback}")
            
            st.markdown("")
            if st.button("✅ Save These Prompts to Production", use_container_width=True):
                supabase.table('country_prompts').update({
                    'system_prompt': test_system,
                    'user_prompt': test_user
                }).eq('id', selected_country['id']).execute()
                st.success("✅ Prompts updated in production!")
                st.rerun()
    else:
        st.warning("⚠️ No countries configured yet. Add one in the 'Countries' tab first!")

# TAB 4: Country Manager
with tab4:
    st.markdown("## 🗺️ Country Configuration")
    st.markdown("Manage target languages and customize translation behavior for each market.")
    st.markdown("")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### ➕ Add New Country")
        
        with st.form("new_country"):
            country_code = st.text_input("Country Code*", placeholder="JP", max_chars=2, help="2-letter ISO code (e.g., JP, DE, FR)").upper()
            language = st.text_input("Language*", placeholder="Japanese", help="Target language name")
            system_prompt = st.text_area("System Prompt", value="You are a professional translator specializing in marketing copy.", height=100)
            user_prompt = st.text_area("User Prompt", placeholder="Translate to formal Japanese, maintain marketing tone", height=100)
            
            submitted = st.form_submit_button("➕ Add Country", use_container_width=True)
            if submitted:
                if country_code and language:
                    supabase = get_supabase()
                    result = supabase.table('country_prompts').insert({
                        'country_code': country_code,
                        'language': language,
                        'system_prompt': system_prompt,
                        'user_prompt': user_prompt
                    }).execute()
                    st.success(f"✅ Country {country_code} added successfully!")
                    st.rerun()
                else:
                    st.error("⚠️ Country code and language are required")
    
    with col2:
        st.subheader("Existing Countries")
        
        supabase = get_supabase()
        countries = supabase.table('country_prompts').select('*').execute()
        
        if countries.data:
            for country in countries.data:
                with st.expander(f"🌍 {country['country_code']} - {country['language']}"):
                    st.text_area("System Prompt", value=country['system_prompt'], key=f"cs_{country['id']}", disabled=True)
                    st.text_area("User Prompt", value=country['user_prompt'], key=f"cu_{country['id']}", disabled=True)
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button(f"🔄 Translate All Ad Copies to {country['country_code']}", key=f"trans_all_{country['id']}"):
                            model = get_gemini()
                            ad_copies = supabase.table('ad_copies').select('*').execute()
                            
                            progress_bar = st.progress(0)
                            for idx, ad in enumerate(ad_copies.data):
                                # Check if translation exists
                                existing = supabase.table('translations').select('id').eq('ad_copy_id', ad['id']).eq('country_code', country['country_code']).execute()
                                
                                if not existing.data:
                                    headline_trans = translate_text(ad['headline'], country['language'], country['user_prompt'], country['system_prompt'], model)
                                    body_trans = translate_text(ad['body'], country['language'], country['user_prompt'], country['system_prompt'], model)
                                    link_trans = translate_text(ad.get('link_text', ''), country['language'], country['user_prompt'], country['system_prompt'], model) if ad.get('link_text') else ''
                                    product_trans = translate_text(ad.get('product', ''), country['language'], country['user_prompt'], country['system_prompt'], model) if ad.get('product') else ''
                                    
                                    score, corrected_body, _ = proofread_translation(ad['body'], body_trans, country['language'], model)
                                    
                                    supabase.table('translations').insert({
                                        'ad_copy_id': ad['id'],
                                        'country_code': country['country_code'],
                                        'language': country['language'],
                                        'headline': headline_trans,
                                        'body': corrected_body,
                                        'link_text': link_trans,
                                        'product': product_trans,
                                        'quality_score': score
                                    }).execute()
                                
                                progress_bar.progress((idx + 1) / len(ad_copies.data))
                            
                            st.success(f"✅ All ad copies translated to {country['country_code']}!")
                            st.rerun()
                    
                    with col_b:
                        if st.button("🗑️ Delete Country", key=f"cdel_{country['id']}"):
                            supabase.table('country_prompts').delete().eq('id', country['id']).execute()
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No countries configured yet. Add one above!")
            
