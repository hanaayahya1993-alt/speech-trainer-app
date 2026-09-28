import streamlit as st
import os
import time
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder

# إعداد الصفحة وتطبيق CSS لتنسيق الواجهة
st.set_page_config(page_title="منصة تدريب الإلقاء الارتجالي", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    /* إعداد الاتجاه والخطوط */
    html, body, [class*="css"] {
        direction: rtl;
        text-align: right;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* عنوان الصفحة */
    .main-title {
        text-align: center;
        color: #1E293B;
        font-size: 28px;
        font-weight: bold;
        margin-bottom: 20px;
    }
    
    /* بطاقة السؤال والتحدي */
    .question-card {
        background-color: #EFF6FF;
        border-right: 6px solid #2563EB;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    .question-header {
        color: #1D4ED8;
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .question-body {
        color: #1E293B;
        font-size: 20px;
        font-weight: 700;
        line-height: 1.6;
    }

    /* محاذاة عناصر التسجيل والمؤقت في الوسط */
    .center-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# الهيدر الرئيسي
st.markdown("<div class='main-title'>🎙️ مدرب الإلقاء والارتجال السريع</div>", unsafe_allow_html=True)

# إدارة مفتاح API
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    openai_api_key = st.sidebar.text_input("أدخل OpenAI API Key الخاص بك:", type="password")

# قائمة المواضيع الارتجالية
TOPICS = [
    "لو أُتيحت لك الفرصة لتغيير عادة واحدة يمارسها أغلب الناس يومياً، ما هي هذه العادة؟ ولماذا؟",
    "ما هي أهم مهارة يحتاجها قائد المستقبل في ظل الذكاء الاصطناعي؟",
    "إذا كان بإمكانك إرسال رسالة نصية قصيرة إلى جميع سكان العالم في نفس اللحظة، ماذا ستكتب؟",
    "هل الشغف أم الانضباط هو السر الحقيقي للنجاح؟ وضح وجهة نظرك.",
    "تخيل أنك تُلقي كلمة وداع في مكان عملك الحالي، ما هو الدرس الأهم الذي ستشاركه معهم؟"
]

if "topic_index" not in st.session_state:
    st.session_state.topic_index = 0

current_topic = TOPICS[st.session_state.topic_index]

# عرض بطاقة السؤال التفاعلية بوضوح
st.markdown(f"""
    <div class='question-card'>
        <div class='question-header'>🎯 التحدي الارتجالي رقم ({st.session_state.topic_index + 1}):</div>
        <div class='question-body'>"{current_topic}"</div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ----------------- قسم المؤقت والتسجيل الصوتي -----------------
st.markdown("<h3 style='text-align: center; color: #334155;'>⏱️ مؤقت الإلقاء والمايكروفون</h3>", unsafe_allow_html=True)

# مكان عرض العداد الدائري في الوسط
timer_box = st.empty()

def render_circular_timer(seconds_left, total_seconds=40):
    percent = (seconds_left / total_seconds) * 100
    dashoffset = 283 - (283 * percent / 100)
    
    elapsed = total_seconds - seconds_left
    color = "#22C55E" # أخضر
    status_text = "🟢 المنطقة الآمنة (واصل حديثك)"
    if 20 <= elapsed < 30:
        color = "#EAB308" # أصفر
        status_text = "🟡 جهز الخاتمة"
    elif elapsed >= 30:
        color = "#EF4444" # أحمر
        status_text = "🔴 الخاتمة فوراً!"

    svg_html = f"""
    <div class="center-box">
        <div style="position: relative; width: 140px; height: 140px;">
            <svg width="140" height="140" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" stroke-width="8" />
                <circle cx="50" cy="50" r="45" fill="none" stroke="{color}" stroke-width="8"
                        stroke-dasharray="283" stroke-dashoffset="{dashoffset}"
                        stroke-linecap="round" transform="rotate(-90 50 50)" style="transition: all 1s linear;" />
            </svg>
            <div style="position: absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:bold; color:#1E293B;">
                {seconds_left} ثانية
            </div>
        </div>
        <div style="margin-top:8px; font-size:15px; font-weight:bold; color:{color};">{status_text}</div>
    </div>
    """
    return svg_html

# عرض الحالة الإبتدائية
timer_box.markdown(render_circular_timer(40), unsafe_allow_html=True)

col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b2:
    start_btn = st.button("▶️ تشغيل العداد الدائري (40 ثانية)", use_container_width=True)

if start_btn:
    for s in range(40, -1, -1):
        timer_box.markdown(render_circular_timer(s), unsafe_allow_html=True)
        time.sleep(1)

st.markdown("<br>", unsafe_allow_html=True)

# قسم التسجيل الصوتي
st.markdown("<h4 style='text-align: center; color: #475569;'>🎤 اضغط المايك وابدأ الحديث مباشرة:</h4>", unsafe_allow_html=True)

rec_col1, rec_col2, rec_col3 = st.columns([1, 1, 1])
with rec_col2:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#EF4444",
        neutral_color="#22C55E",
        icon_name="microphone",
        icon_size="3x"
    )

st.markdown("---")

# ----------------- قسم المعالجة والتقييم -----------------
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    if openai_api_key and st.button("تحليل وتقييم التسجيل الصوتي 🚀", use_container_width=True):
        client = OpenAI(api_key=openai_api_key)
        
        temp_audio_file = "temp_speech.wav"
        with open(temp_audio_file, "wb") as f:
            f.write(audio_bytes)
            
        with st.spinner("🎧 جاري تحويل الصوت إلى نص عبر Whisper API..."):
            try:
                with open(temp_audio_file, "rb") as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="ar"
                    )
                
                user_speech = transcription.text
                st.success("✅ تم تفريغ النص بنجاح!")
                st.markdown(f"**النص المفرغ من صوتك:**\n> *\"{user_speech}\"*")
                
            except Exception as e:
                st.error(f"حدث خطأ أثناء تفريغ الصوت: {e}")
                user_speech = ""
                
        if user_speech:
            with st.spinner("📊 جاري تقييم الإلقاء وفق المعايير..."):
                SYSTEM_PROMPT = """
                أنت مدرب خطابة وإلقاء ارتجالي خبير متمرس في التدريب على الارتجال السريع (40 Seconds Elevator Pitch).
                قيم خطبة المتدرب بناءً على السؤال المطروح والنص المفرغ من صوته.

                قدم التقييم بالتنسيق التالي حصراً:
                1. جدول تقييم من 10 لمعايير: قوة البداية، التركيز والتكثيف، وقوة الخاتمة.
                2. نقطتا تطور رئيسيتان للتكثيف.
                3. نموذج تحسيني مقترح لخطبته في أقل من 40 ثانية.
                """
                
                try:
                    prompt_content = f"الموضوع: \"{current_topic}\"\nإجابة المتدرب الصوتي: \"{user_speech}\""
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt_content}
                        ],
                        temperature=0.7
                    )
                    st.markdown("### 📝 التقييم والملاحظات:")
                    st.markdown(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التقييم: {e}")

# الانتقال إلى التحدي التالي
col_n1, col_n2, col_n3 = st.columns([1, 2, 1])
with col_n2:
    if st.button("التحدي التالي ⏭️", use_container_width=True):
        st.session_state.topic_index = (st.session_state.topic_index + 1) % len(TOPICS)
        st.rerun()
