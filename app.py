---
import streamlit as st
import os
import time
from openai import OpenAI
from audio_recorder_streamlit import audio_recorder

# إعداد صفحة التطبيق
st.set_page_config(page_title="مدرب الإلقاء الارتجالي الصوتي", page_icon="🎙️", layout="centered")

st.title("🎙️ مدرب الإلقاء والارتجال الصوتي الذكي")
st.write("سجل إجابتك الصوتية بالمايكروفون. انتبه للمؤقت لتلتزم بالوقت المحدد (40 ثانية)!")

# إدارة مفتاح API
openai_api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    openai_api_key = st.sidebar.text_input("أدخل OpenAI API Key الخاص بك:", type="password")
    if not openai_api_key:
        st.warning("⚠️ يرجى إدخال مفتاح OpenAI API للبدء.")

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

st.markdown("---")
st.subheader(f"🎯 التحدي رقم ({st.session_state.topic_index + 1}):")
st.info(f"**\"{current_topic}\"**")

# ----------------- قسم المؤقت التفاعلي (40 ثانية) -----------------
st.markdown("### ⏱️ مؤقت الإلقاء الارتجالي (40 ثانية)")
st.caption("الحد الأقصى: 40 ثانية | الأخضر: 20ث | الأصفر: 30ث | الأحمر: 40ث")

col_timer_btn, col_timer_disp = st.columns([1, 2])

with col_timer_btn:
    start_timer = st.button("▶️ ابدأ المؤقت (40 ثانية)")

with col_timer_disp:
    timer_placeholder = st.empty()
    status_placeholder = st.empty()

if start_timer:
    TOTAL_SECONDS = 40
    for remaining in range(TOTAL_SECONDS, -1, -1):
        mins, secs = divmod(remaining, 60)
        time_format = f"{mins:02d}:{secs:02d}"
        
        elapsed = TOTAL_SECONDS - remaining
        if elapsed < 20:
            status_placeholder.markdown("🟢 **المنطقة الآمنة** (واصل حديثك)")
        elif 20 <= elapsed < 30:
            status_placeholder.markdown("🟡 **اقترب الوقت** (ابدأ بإنهاء الفكرة)")
        elif 30 <= elapsed <= 40:
            status_placeholder.markdown("🔴 **الخاتمة فوراً** (وصلت للحد الأعلى)")
        
        timer_placeholder.metric(label="الوقت المتبقي", value=time_format)
        time.sleep(1)
        
    status_placeholder.error("⏰ انتهى الوقت المحدد (40 ثانية)!")

st.markdown("---")

# ----------------- قسم التسجيل والتقييم -----------------
st.markdown("### 🎤 سجل إجابتك الصوتية:")
audio_bytes = audio_recorder(
    text="اضغط للتسجيل",
    recording_color="#e84c3d",
    neutral_color="#6aa84f",
    icon_name="microphone",
    icon_size="3x"
)

user_speech = ""

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    
    if openai_api_key and st.button("تحليل وتقييم التسجيل الصوتي 🚀"):
        client = OpenAI(api_key=openai_api_key)
        
        temp_audio_file = "temp_speech.wav"
        with open(temp_audio_file, "wb") as f:
            f.write(audio_bytes)
            
        with st.spinner("🎧 جاري تفريغ الصوت إلى نص عبر Whisper API..."):
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
                
        if user_speech:
            with st.spinner("📊 جاري تقييم الأداء وفق معايير الخطابة..."):
                SYSTEM_PROMPT = """
                أنت مدرب خطابة وإلقاء ارتجالي خبير متمرس في التدريب على الارتجال السريع (40 Seconds Elevator Pitch / Rapid Table Topics).
                دورك هو تقييم خطبة المتدرب الارتجالية القصيرة جداً بناءً على السؤال المطروح والنص المفرغ من صوته.

                ضع في اعتبارك أن زمن الخطبة هو 40 ثانية فقط، مما يتطلب تكثيفاً عالياً واستبعاد المداخل الطويلة.

                يرجى تقديم التقييم بدقة ووضوح باستخدام تنسيق Markdown وفق العناصر التالية حصراً:

                1. جدول تقييم بالأرقام (من 10) يغطي المعايير التالية:
                   - قوة البداية والسرعة (Hook & Rapid Impact) - مدى سرعة الدخول في الموضوع دون مقدمات مستهلكة.
                   - التركيز والتكثيف (Focus & Clarity) - إيصال فكرة جوهرية واحدة بوضوح خلال الزمن الوجيز.
                   - قوة الخاتمة والإيجاز (Punchy Ending) - اختتام الكلام بجملة قوية ومباشرة قبل انتهاء الـ 40 ثانية.
                   (ضع نقطة قوة بارزة واحدة أمام كل معيار).

                2. نقاط التطور الرئيسية (Key Improvement Areas) - نقطتان فقط تركزان على التكثيف وحذف الفوائض.

                3. نموذج تحسيني مقترح (40-Second Refinement) - إعادة صياغة مقتضبة ومثالية لخطبته تناسب إلقاءها كاملاً في أقل من 40 ثانية.

                اجعل نبرتك مشجعة، حازمة، ومباشرة.
                """
                
                try:
                    prompt_content = f"الموضوع: \"{current_topic}\"\nإجابة المتدرب الصوتي (مفرغة): \"{user_speech}\""
                    
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": SYSTEM_PROMPT},
                            {"role": "user", "content": prompt_content}
                        ],
                        temperature=0.7
                    )
                    
                    st.markdown("---")
                    st.markdown("### 📝 التقييم والملاحظات:")
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"حدث خطأ أثناء التقييم: {e}")

# زر الانتقال للتحدي التالي
st.markdown("---")
if st.button("التحدي التالي ⏭️"):
    st.session_state.topic_index = (st.session_state.topic_index + 1) % len(TOPICS)
    st.rerun()
