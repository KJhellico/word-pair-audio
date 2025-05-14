import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
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
repeat_count = st.slider("Кількість повторів", 1, 100, 20, 1)
one_by_one = st.checkbox("Читати по слову з кожної мови", value=True)

words1 = st.text_area("Список слів мовою 1 (по одному в рядок)").strip().splitlines()
words2 = st.text_area("Список слів мовою 2 (по одному в рядок)").strip().splitlines()


def make_audio_list(words: list[str], lang: str) -> list:
    result = []
    for w in words:
        tts = gTTS(text=w, lang=lang, slow=slow)
        tts.save("tmp.mp3")
        audio = AudioSegment.from_file("tmp.mp3")
        result.append(audio)
    return result


if st.button("🔊 Згенерувати аудіо"):
    if words1 and words2 and len(words1) != len(words2):
        st.error("❌ Списки повинні бути однакової довжини.")
    else:
        segments = []
        pause = AudioSegment.silent(duration=pause_ms)
        length = len(words1) or len(words2)

        audio_1 = make_audio_list(words1, lang_code1)
        audio_2 = make_audio_list(words2, lang_code2)

        if one_by_one:
            for i in range(length):
                if words1:
                    segments.extend([audio_1[i], pause])
                if words2:
                    segments.extend([audio_2[i], pause])
        else:
            if words1:
                for i in range(length):
                    segments.extend([audio_1[i], pause])
            if words2:
                for i in range(length):
                    segments.extend([audio_2[i], pause])

        segments *= repeat_count
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
