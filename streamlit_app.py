import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import tempfile
import os
from io import BytesIO

AVAILABLE_LANGS = {
    "Французька": "fr",
    "Російська": "ru",
    "Українська": "uk"
}

if "history" not in st.session_state:
    st.session_state.history = []

st.title("Озвучення пар слів двома мовами")

col1, col2 = st.columns(2)
with col1:
    lang1 = st.selectbox("Мова списку 1", list(AVAILABLE_LANGS.keys()), index=0)
with col2:
    lang2 = st.selectbox("Мова списку 2", list(AVAILABLE_LANGS.keys()), index=1)

lang_code1 = AVAILABLE_LANGS[lang1]
lang_code2 = AVAILABLE_LANGS[lang2]

slow = st.checkbox("Повільне читання", value=True)
pause_ms = st.slider("Пауза між словами (мс)", 200, 2000, 500, 100)

words1 = st.text_area("Список слів мовою 1 (по одному в рядок)").strip().splitlines()
words2 = st.text_area("Список слів мовою 2 (по одному в рядок)").strip().splitlines()

if st.button("🔊 Згенерувати аудіо"):
    if len(words1) != len(words2):
        st.error("❌ Списки повинні бути однакової довжини.")
    elif not words1 or not words2:
        st.warning("⚠️ Обидва списки мають бути непорожні.")
    else:
        segments = []
        with tempfile.TemporaryDirectory() as tmpdir:
            for i, (w1, w2) in enumerate(zip(words1, words2)):
                tts1 = gTTS(text=w1, lang=lang_code1, slow=slow)
                tts2 = gTTS(text=w2, lang=lang_code2, slow=slow)

                path1 = os.path.join(tmpdir, f"{i}_1.mp3")
                path2 = os.path.join(tmpdir, f"{i}_2.mp3")
                tts1.save(path1)
                tts2.save(path2)

                audio1 = AudioSegment.from_file(path1)
                audio2 = AudioSegment.from_file(path2)
                pause = AudioSegment.silent(duration=pause_ms)

                segments.extend([audio1, pause, audio2, pause])

            final_audio = sum(segments)
            buffer = BytesIO()
            final_audio.export(buffer, format="mp3")
            buffer.seek(0)

            st.session_state.history.append({
                "lang1": lang1,
                "lang2": lang2,
                "words1": words1,
                "words2": words2,
                "audio": buffer.getvalue()
            })

            st.success("✅ Аудіо згенеровано!")
            st.audio(buffer, format="audio/mp3")
            st.download_button("⬇️ Завантажити MP3", buffer, file_name="translated_words.mp3")

if st.session_state.history:
    st.markdown("## 🕘 Історія")
    for idx, item in enumerate(reversed(st.session_state.history)):
        st.markdown(f"**Пара {len(st.session_state.history)-idx}: {item["lang1"]} → {item["lang2"]}**")
        st.audio(item["audio"], format="audio/mp3")
        st.download_button(
            label="⬇️ Завантажити",
            data=item["audio"],
            file_name=f"history_{len(st.session_state.history)-idx}.mp3",
            key=f"download_{idx}"
        )
