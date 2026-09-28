import streamlit as st
import os
import time
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder

# إعداد الصفحة
st.set_page_config(page_title="مدرب الإلقاء الارتجالي", page_icon="🎙️", layout="centered")

st.markdown("""
    <style>
    .main-title { text-align: center; color: #1E293B; margin-bottom: 10px; }
    .stApp { background-color: #F8FAFC; }
    .timer-container { display: flex; justify-content: center; align-items: center; margin: 20px 0; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>🎙️ مدرب الإلقاء والارتجال السريع</h1>", unsafe_allow_html=True)
st.write("سجل إجابتك الصوتية بالمايكروفون. انتبه للمؤقت لتلتزم بالوقت المحدد (40 ثانية)!")

# إدارة مفتاح API
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    openai_api_key = st.sidebar.text_input("أدخل OpenAI API Key الخاص بك:", type="password")

# المواضيع الارتجالية
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

st.markdown("---")
st.subheader(f"🎯 التحدي رقم ({st.session_state.topic_index + 1}):")
st.info(f"**\"{current_topic}\"**")

# ----------------- العداد الدائري والتسجيل في المنتصف -----------------
st.markdown("<h3 style='text-align: center;'>⏱️ المؤقت التفاعلي (40 ثانية)</h3>", unsafe_allow_html=True)

# مكان عرض العداد الدائري في الوسط
timer_box = st.empty()

def render_circular_timer(seconds_left, total_seconds=40):
    percent = (seconds_left / total_seconds) * 100
    dashoffset = 283 - (283 * percent / 100)
    
    # تحديد اللون حسب التوقيت
    elapsed = total_seconds - seconds_left
    color = "#22C55E" # أخضر
    status_text = "🟢 المنطقة الآمنة"
    if 20 <= elapsed < 30:
        color = "#EAB308" # أصفر
        status_text = "🟡 جهز الخاتمة"
    elif elapsed >= 30:
        color = "#EF4444" # أحمر
        status_text = "🔴 الخاتمة فوراً!"

    svg_html = f"""
    <div style="display:flex; flex-direction:column; align-items:center; justify-content:center;">
        <div style="position: relative; width: 150px; height: 150px;">
            <svg width="150" height="150" viewBox="0 0 100 100">
                <circle cx="50" cy="50" r="45" fill="none" stroke="#E2E8F0" stroke-width="8" />
                <circle cx="50" cy="50" r="45" fill="none" stroke="{color}" stroke-width="8"
                        stroke-dasharray="283" stroke-dashoffset="{dashoffset}"
                        stroke-linecap="round" transform="rotate(-90 50 50)" style="transition: all 1s linear;" />
            </svg>
            <div style="position: absolute; top:0; left:0; width:100%; height:100%; display:flex; align-items:center; justify-content:center; font-size:26px; font-weight:bold; color:#1E293B;">
                {seconds_left}s
            </div>
        </div>
        <div style="margin-top:10px; font-size:16px; font-weight:bold; color:{color};">{status_text}</div>
    </div>
    """
    return svg_html

# عرض الحالة الابتدائية 40 ثانية
timer_box.markdown(render_circular_timer(40), unsafe_allow_html=True)

col_center = st.columns([1, 2, 1])

with col_center[1]:
    start_btn = st.button("▶️ ابدأ العداد الدائري", use_container_width=True)

if start_btn:
    for s in range(40, -1, -1):
        timer_box.markdown(render_circular_timer(s), unsafe_allow_html=True)
        time.sleep(1)

st.markdown("<h4 style='text-align: center; margin-top:20px;'>🎤 اضغط المايك وابدأ الحديث:</h4>", unsafe_allow_html=True)

# وضع التسجيل في منتصف الصفحة
c1, c2, c3 = st.columns([1, 1, 1])
with c2:
    audio_bytes = audio_recorder(
        text="",
        recording_color="#EF4444",
        neutral_color="#22C55E",
        icon_name="microphone",
        icon_size="3x"
    )

st.markdown("---")

# ----------------- قسم التقييم -----------------
if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    if openai_api_key and st.button("تحليل وتقييم التسجيل الصوتي 🚀", use_container_width=True):
        client = OpenAI(api_key=openai_api_key)
        
        temp_audio_file = "temp_speech.wav"
        with open(temp_audio_file, "wb") as f:
            f.write(audio_bytes)
            
        with st.spinner("🎧 جاري تفريغ الصوت عبر Whisper API..."):
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
            with st.spinner("📊 جاري تقييم الأداء وفق معايير الخطابة الارتجالية..."):
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

# زر التحدي التالي
st.markdown("---")
if st.button("التحدي التالي ⏭️", use_container_width=True):
    st.session_state.topic_index = (st.session_state.topic_index + 1) % len(TOPICS)
    st.rerun()
