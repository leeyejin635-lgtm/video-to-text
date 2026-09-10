import streamlit as st
import os
import tempfile
import uuid
from groq import Groq

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

st.set_page_config(page_title="인공지능 대량 원고 추출기", page_icon="🎬")
st.title("🎬 인공지능 대량 원고 추출 웹사이트")
st.write("여러 개의 영상 파일을 한 번에 드래그해서 올리면 순서대로 화면에 원고를 띄워줍니다!")

api_key = "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" 

uploaded_files = st.file_uploader("영상을 여러 개 드래그해서 놓으세요 (.mp4)", type=["mp4", "mov", "avi"], accept_multiple_files=True)

if uploaded_files:
    client = Groq(api_key=api_key)
    
    for uploaded_file in uploaded_files:
        st.markdown(f"⏳ **{uploaded_file.name}** 작업 중...")
        
        with st.spinner("영상을 분석하고 원고를 작성 중입니다..."):
            try:
                # 완벽한 영문/숫자 조합의 고유 임시 파일 경로 생성
                random_filename = str(uuid.uuid4())
                video_path = os.path.join(tempfile.gettempdir(), f"{random_filename}.mp4")
                audio_path = os.path.join(tempfile.gettempdir(), f"{random_filename}.mp3")

                with open(video_path, "wb") as f:
                    f.write(uploaded_file.read())

                # 🛠️ ASCII 인코딩 충돌을 방지하기 위해 강제로 문자열 인코딩 처리
                safe_video_path = str(video_path)
                safe_audio_path = str(audio_path)

                clip = VideoFileClip(safe_video_path, audio_fps=16000, target_resolution=None)
                clip.audio.write_audiofile(safe_audio_path, bitrate="48k", logger=None)
                clip.close()

                with open(safe_audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(safe_audio_path, file.read()),
                        model="whisper-large-v3",
                        language="ko"
                    )

                result_text = transcription.text
                st.success(f"🎉 [{uploaded_file.name}] 추출 완료!")
                st.write(result_text)
                
                # 임시 파일 정리
                if os.path.exists(safe_video_path):
                    os.remove(safe_video_path)
                if os.path.exists(safe_audio_path):
                    os.remove(safe_audio_path)
                
            except Exception as e:
                st.error(f"[{uploaded_file.name}] 처리 중 에러가 발생했습니다: {e}")
