import streamlit as st
import os
import tempfile
from moviepy import VideoFileClip
from groq import Groq

# 1. 🔥 여기에 본인의 진짜 API 키를 적어두면 화면에는 보이지 않고 컴퓨터만 몰래 사용합니다.
api_key = "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"  # 반드시 본인의 키로 변경하세요!

# 웹사이트 제목
st.set_page_config(page_title="인공지능 대량 원고 추출기", page_icon="🎬")
st.title("🎬 인공지능 대량 원고 추출 웹사이트")
st.write("여러 개의 영상 파일을 한 번에 드래그해서 올리면 순서대로 화면에 원고를 띄워줍니다!")

# 파일 업로드 칸
uploaded_files = st.file_uploader("영상을 여러 개 드래그해서 놓으세요 (.mp4)", type=["mp4", "mov"], accept_multiple_files=True)

if st.button("🚀 대량 원고 추출 시작"):
    if not uploaded_files:
        st.warning("영상 파일을 한 개 이상 업로드해 주세요!")
    else:
        client = Groq(api_key=api_key)
        
        for uploaded_file in uploaded_files:
            st.markdown(f"### ⏳ **{uploaded_file.name}** 작업 중...")
            
            with st.spinner("영상을 분석하고 원고를 작성 중입니다..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
                        temp_video.write(uploaded_file.read())
                        video_path = temp_video.name
                    
                    audio_path = video_path.replace('.mp4', '.mp3')

                    clip = VideoFileClip(video_path)
                    clip.audio.write_audiofile(audio_path, logger=None)
                    clip.close()

                    with open(audio_path, "rb") as file:
                        transcription = client.audio.transcriptions.create(
                            file=(audio_path, file.read()),
                            model="whisper-large-v3",
                            language="ko"
                        )
                    
                    result_text = transcription.text
                    st.success(f"🎉 [{uploaded_file.name}] 추출 완료!")
                    
                    # 🔥 다운로드 대신 웹사이트 화면에 원고를 바로 띄워주는 부분
                    st.text_area(
                        label=f"📝 {uploaded_file.name} 원고 내용", 
                        value=result_text, 
                        height=250, # 박스의 세로 크기 (숫자를 키우면 더 길어집니다)
                        key=uploaded_file.name + "text" # 여러 개일 때 엉키지 않게 고유 이름표 붙이기
                    )

                    os.remove(video_path)
                    os.remove(audio_path)

                except Exception as e:
                    st.error(f"❌ [{uploaded_file.name}] 처리 중 에러가 발생했습니다: {e}")
        
        st.info("✅ 모든 영상의 원고 작업이 끝났습니다!")