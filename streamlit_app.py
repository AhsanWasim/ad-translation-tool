import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
import re
import json
from datetime import datetime

# Page config
st.set_page_config(page_title="Ad Translation Tool", page_icon="🌍", layout="wide")

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
    st.title("⚙️ Configuration")
    
    supabase_url = st.text_input("Supabase URL", value=st.session_state.supabase_url, type="password")
    supabase_key = st.text_input("Supabase Key", value=st.session_state.supabase_key, type="password")
    gemini_key = st.text_input("Gemini API Key", value=st.session_state.gemini_key, type="password")
    
    if st.button("💾 Save Configuration"):
        st.session_state.supabase_url = supabase_url
        st.session_state.supabase_key = supabase_key
        st.session_state.gemini_key = gemini_key
        
        if supabase_url and supabase_key:
            st.session_state.supabase_client = create_client(supabase_url, supabase_key)
            st.success("✅ Configuration saved!")
        else:
            st.error("Please fill in all fields")

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

# Main app
st.title("🌍 Ad Copy Translation Tool")

# Navigation
tab1, tab2, tab3, tab4 = st.tabs(["📝 Ad Copies", "🌐 Translations", "🧪 Test Prompts", "🗺️ Countries"])

# TAB 1: Ad Copies CRUD
with tab1:
    st.header("Ad Copy Manager")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Create New Ad Copy")
        
        with st.form("new_ad_copy"):
            headline = st.text_input("Headline*", placeholder="Get 50% off today!")
            body = st.text_area("Body*", placeholder="Shop now and save on <product>...")
            link_text = st.text_input("Link Text", placeholder="Shop Now")
            product = st.text_input("Product", placeholder="Premium Subscription")
            
            if st.form_submit_button("➕ Create Ad Copy"):
                if headline and body:
                    supabase = get_supabase()
                    result = supabase.table('ad_copies').insert({
                        'headline': headline,
                        'body': body,
                        'link_text': link_text,
                        'product': product
                    }).execute()
                    st.success("✅ Ad copy created!")
                    st.rerun()
                else:
                    st.error("Headline and Body are required")
    
    with col2:
        st.subheader("Existing Ad Copies")
        
        supabase = get_supabase()
        ad_copies = supabase.table('ad_copies').select('*').order('created_at', desc=True).execute()
        
        if ad_copies.data:
            for ad in ad_copies.data:
                with st.expander(f"📄 {ad['headline'][:50]}... (ID: {ad['id']})"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.text_input("Headline", value=ad['headline'], key=f"h_{ad['id']}", disabled=True)
                        st.text_area("Body", value=ad['body'], key=f"b_{ad['id']}", disabled=True)
                        st.text_input("Link Text", value=ad.get('link_text', ''), key=f"l_{ad['id']}", disabled=True)
                        st.text_input("Product", value=ad.get('product', ''), key=f"p_{ad['id']}", disabled=True)
                    
                    with col_b:
                        if st.button("🗑️ Delete", key=f"del_{ad['id']}"):
                            supabase.table('ad_copies').delete().eq('id', ad['id']).execute()
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No ad copies yet. Create one above!")

# TAB 2: Translations
with tab2:
    st.header("Translation Dashboard")
    
    supabase = get_supabase()
    ad_copies = supabase.table('ad_copies').select('*').execute()
    countries = supabase.table('country_prompts').select('*').execute()
    
    if not ad_copies.data:
        st.warning("⚠️ Please create ad copies first in the 'Ad Copies' tab")
    elif not countries.data:
        st.warning("⚠️ Please add countries first in the 'Countries' tab")
    else:
        col1, col2 = st.columns(2)
        
        with col1:
            selected_ads = st.multiselect(
                "Select Ad Copies (multiple)",
                options=ad_copies.data,
                format_func=lambda x: f"{x['headline'][:50]}... (ID: {x['id']})",
                default=[ad_copies.data[0]] if ad_copies.data else []
            )
        
        with col2:
            selected_countries = st.multiselect(
                "Select Countries to Translate",
                options=[c['country_code'] for c in countries.data],
                default=[c['country_code'] for c in countries.data[:2]]
            )
        
        if st.button("🚀 Translate to Selected Countries"):
            if selected_ads and selected_countries:
                model = get_gemini()
                
                total_tasks = len(selected_ads) * len(selected_countries)
                progress_bar = st.progress(0)
                status_text = st.empty()
                task_count = 0
                
                for ad in selected_ads:
                    for country_code in selected_countries:
                        status_text.text(f"Translating Ad ID {ad['id']} to {country_code}...")
                        
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
                st.success(f"✅ Translated {len(selected_ads)} ad copies to {len(selected_countries)} countries!")
                st.rerun()
        
        # Show existing translations
        st.subheader("📚 Existing Translations")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_country = st.selectbox("Filter by Country", ["All"] + [c['country_code'] for c in countries.data])
        with col2:
            filter_ad = st.selectbox("Filter by Ad Copy", ["All"] + [f"ID {a['id']}" for a in ad_copies.data])
        with col3:
            filter_quality = st.slider("Min Quality Score", 0, 100, 0)
        
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
                with st.expander(f"🌐 {trans['country_code']} - {trans['headline'][:40]}... (Score: {trans['quality_score']}%)"):
                    col_a, col_b = st.columns([3, 1])
                    
                    with col_a:
                        st.text_input("Headline", value=trans['headline'], key=f"th_{trans['id']}", disabled=True)
                        st.text_area("Body", value=trans['body'], key=f"tb_{trans['id']}", disabled=True)
                        st.text_input("Link Text", value=trans.get('link_text', ''), key=f"tl_{trans['id']}", disabled=True)
                        st.text_input("Product", value=trans.get('product', ''), key=f"tp_{trans['id']}", disabled=True)
                        
                        # Quality score badge
                        score = trans['quality_score']
                        color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                        st.markdown(f"{color} **Quality Score: {score}%**")
                    
                    with col_b:
                        if st.button("🗑️ Delete", key=f"tdel_{trans['id']}"):
                            supabase.table('translations').delete().eq('id', trans['id']).execute()
                            st.success("Deleted!")
                            st.rerun()
        else:
            st.info("No translations found. Create some above!")

# TAB 3: Test Prompts
with tab3:
    st.header("🧪 Prompt Testing")
    st.write("Test different prompts on sample texts before using them in production")
    
    supabase = get_supabase()
    countries = supabase.table('country_prompts').select('*').execute()
    
    if countries.data:
        selected_country = st.selectbox(
            "Select Country to Test",
            options=countries.data,
            format_func=lambda x: f"{x['country_code']} - {x['language']}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Prompts")
            test_system = st.text_area("System Prompt", value=selected_country['system_prompt'], height=100)
            test_user = st.text_area("User Prompt", value=selected_country['user_prompt'], height=100)
        
        with col2:
            st.subheader("Sample Text")
            sample_text = st.text_area("Test Text", value="Get <discount>% off on <product> today! Limited time offer.", height=100)
        
        if st.button("🧪 Test Translation"):
            model = get_gemini()
            
            with st.spinner("Translating..."):
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
            
            st.success("✅ Translation complete!")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Original")
                st.write(sample_text)
            with col2:
                st.subheader("Translation")
                st.write(corrected)
                
                score_color = "🟢" if score >= 80 else "🟡" if score >= 60 else "🔴"
                st.markdown(f"{score_color} **Quality Score: {score}%**")
                st.info(f"💬 {feedback}")
            
            if st.button("✅ Save These Prompts to Production"):
                supabase.table('country_prompts').update({
                    'system_prompt': test_system,
                    'user_prompt': test_user
                }).eq('id', selected_country['id']).execute()
                st.success("Prompts updated!")
                st.rerun()
    else:
        st.warning("No countries configured yet. Add one in the 'Countries' tab!")

# TAB 4: Country Manager
with tab4:
    st.header("🗺️ Country Manager")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Add New Country")
        
        with st.form("new_country"):
            country_code = st.text_input("Country Code*", placeholder="JP", max_chars=2).upper()
            language = st.text_input("Language*", placeholder="Japanese")
            system_prompt = st.text_area("System Prompt", value="You are a professional translator specializing in marketing copy.")
            user_prompt = st.text_area("User Prompt", placeholder="Translate to formal Japanese, maintain marketing tone")
            
            if st.form_submit_button("➕ Add Country"):
                if country_code and language:
                    supabase = get_supabase()
                    result = supabase.table('country_prompts').insert({
                        'country_code': country_code,
                        'language': language,
                        'system_prompt': system_prompt,
                        'user_prompt': user_prompt
                    }).execute()
                    st.success(f"✅ Country {country_code} added!")
                    st.rerun()
                else:
                    st.error("Country code and language are required")
    
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

# Footer
st.markdown("---")
st.markdown("🌍 **Ad Translation Tool** | Built with Streamlit + Supabase + Gemini")
