import streamlit as st
import os
import tempfile
from groq import Groq

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    from moviepy import VideoFileClip

st.set_page_config(page_title="인공지능 대량 원고 추출기", page_icon="🎬")
st.title("🎬 인공지능 대량 원고 추출 웹사이트")
st.write("여러 개의 영상 파일을 한 번에 드래그해서 올리면 순서대로 화면에 원고를 띄워줍니다!")

api_key = "여기에_본인_API_키_입력" 

uploaded_files = st.file_uploader("영상을 여러 개 드래그해서 놓으세요 (.mp4)", type=["mp4", "mov", "avi"], accept_multiple_files=True)

if uploaded_files:
    client = Groq(api_key=api_key)
    
    for uploaded_file in uploaded_files:
        st.markdown(f"⏳ **{uploaded_file.name}** 작업 중...")
        
        with st.spinner("영상을 분석하고 원고를 작성 중입니다..."):
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                    temp_video.write(uploaded_file.read())
                    video_path = temp_video.name

                audio_path = video_path.replace('.mp4', '.mp3')

                # 속도 최적화: 비디오 전체를 로드하지 않고 오디오만 빠르게 추출하며 비트레이트를 낮춰 용량 감소
                clip = VideoFileClip(video_path, audio_fps=16000, target_resolution=None)
                clip.audio.write_audiofile(audio_path, bitrate="48k", logger=None)
                clip.close()

                with open(audio_path, "rb") as file:
                    transcription = client.audio.transcriptions.create(
                        file=(audio_path, file.read()),
                        model="whisper-large-v3",
                        language="ko"
                    )

                result_text = transcription.text
                st.success(f"🎉 [{uploaded_file.name}] 추출 완료!")
                st.write(result_text)
                
                # 사용한 임시 파일들 깔끔하게 삭제하여 서버 용량/부하 관리
                if os.path.exists(video_path):
                    os.remove(video_path)
                if os.path.exists(audio_path):
                    os.remove(audio_path)
                
            except Exception as e:
                st.error(f"[{uploaded_file.name}] 처리 중 에러가 발생했습니다: {e}")
