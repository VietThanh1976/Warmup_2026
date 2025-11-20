import streamlit as st
import speech_recognition as sr
import librosa
import soundfile as sf
from streamlit_mic_recorder import mic_recorder
import io
import os
from docx import Document # Thư viện cho file .docx
import time

# Khởi tạo đối tượng nhận dạng giọng nói
r = sr.Recognizer()

# Đặt tiêu đề cho ứng dụng
st.title("🎤 ỨNG DỤNG CHUYỂN ÂM THANH THÀNH VĂN BẢN Ver1.0")
st.markdown("----------------*************----------------")

def transcribe_audio_file(uploaded_file):
    """
    Sử dụng librosa và soundfile để xử lý các loại file âm thanh (MP3, WAV,...) 
    và chuyển đổi thành văn bản.
    """
    temp_input_path = "temp_input_audio" + os.path.splitext(uploaded_file.name)[1]
    temp_wav_path = "temp_converted_audio.wav"
    
    try:
        # 1. Lưu file đã tải lên vào tệp tạm thời
        
        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info("Đang xử lý và chuyển đổi định dạng âm thanh...")

        # 2. Đọc file bằng librosa (hỗ trợ nhiều định dạng)
        # y: mảng dữ liệu âm thanh, sr_librosa: tần số lấy mẫu
        y, sr_librosa = librosa.load(temp_input_path, sr=None) 

        # 3. Ghi dữ liệu âm thanh thành tệp WAV tạm thời bằng soundfile
        sf.write(temp_wav_path, y, sr_librosa)
        
        # 4. Sử dụng SpeechRecognition với tệp WAV
        with sr.AudioFile(temp_wav_path) as source:
            st.info("Đang nhận dạng giọng nói...")
            audio = r.record(source) 

        # Sử dụng Google Web Speech API để chuyển đổi (tiếng Việt)
        text = r.recognize_google(audio, language="vi-VN")
        return text
    
    except sr.UnknownValueError:
        return "Không thể nhận dạng giọng nói từ tệp âm thanh này."
    except sr.RequestError as e:
        return f"Lỗi kết nối hoặc API: {e}"
    except Exception as e:
        return f"Lỗi xử lý tệp: {e}. Vui lòng kiểm tra file đầu vào."
    finally:
        # Xóa các file tạm thời
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)
       
def create_docx(text, filename="transcribed_document.docx"):
    """Tạo một file DOCX từ văn bản đã chuyển đổi và trả về dưới dạng bytes."""
    document = Document()
    document.add_heading('Văn bản đã chuyển đổi', 0)
    document.add_paragraph(text)

    # Lưu document vào một đối tượng BytesIO
    docx_io = io.BytesIO()
    document.save(docx_io)
    docx_io.seek(0)
    return docx_io.read(), filename


def main():
  # --- Thanh phân cách ---
  st.markdown("---") 

  # Chọn phương thức nhập liệu
  method = st.radio(
    "Chọn phương thức nhập liệu:",
    ('Tải lên File Âm thanh', 'Ghi âm trực tiếp từ Micro')
  )

  transcribed_text = ""
  # Xử lý theo phương thức đã chọn
  if method == 'Tải lên File Âm thanh':
    uploaded_file = st.file_uploader(
        "Tải lên tệp âm thanh (ví dụ: .wav, .mp3):",
        type=['wav', 'mp3']
    )
    if uploaded_file is not None:
        if st.button('🚀 Chuyển đổi File thành Văn bản'):
            transcribed_text = transcribe_audio_file(uploaded_file)
          
  elif method == 'Ghi âm trực tiếp từ Micro':
    st.subheader("🎙️ Ghi Âm Trực Tiếp")
    st.caption("Sử dụng micro của trình duyệt (thay thế cho PyAudio).")

    # Sử dụng mic_recorder để ghi âm và trả về audio buffer
    audio_data = mic_recorder(
        start_prompt="Bắt đầu Ghi Âm",
        stop_prompt="Dừng Ghi Âm",
        key='mic_recorder',
        format="wav" # Quan trọng: Giúp SpeechRecognition xử lý tốt nhất
    )

    if audio_data:
        st.session_state.audio_buffer = audio_data['bytes']
        st.audio(st.session_state.audio_buffer, format='audio/wav') # Hiển thị player
        # ======================================================
        # 👉 PHẦN CODE MỚI: NÚT TẢI XUỐNG FILE ÂM THANH
        # ======================================================
        st.download_button(
            label="⬇️ Tải xuống File Âm thanh (.wav)",
            data=st.session_state.audio_buffer,
            file_name="ghi_am_mic.wav",
            mime="audio/wav" # Định dạng MIME cho tệp WAV
        )
        # ======================================================
            
    if (st.session_state.audio_buffer is not None) and st.button('✅ Chuyển đổi Giọng nói'):
        
        # Tạo file WAV tạm thời từ buffer
        temp_wav_path = "mic_recording_temp.wav"
        try:
            with open(temp_wav_path, "wb") as f:
                f.write(st.session_state.audio_buffer)

            # Sử dụng SpeechRecognition với file WAV tạm thời
            r = sr.Recognizer()
            with sr.AudioFile(temp_wav_path) as source:
                st.info("Đang nhận dạng giọng nói...")
                audio = r.record(source) 

            transcribed_text = r.recognize_google(audio, language="vi-VN")

        except sr.UnknownValueError:
            transcribed_text = "Không thể nhận dạng giọng nói."
        except sr.RequestError as e:
            transcribed_text = f"Lỗi kết nối hoặc API: {e}"
        finally:
            # Xóa file tạm thời
            if os.path.exists(temp_wav_path):
                os.remove(temp_wav_path)
            # Xóa buffer sau khi xử lý xong
            st.session_state.audio_buffer = None
          
  # --- Hiển thị Kết quả và Tùy chọn Tải xuống ---
  if transcribed_text:
    st.subheader("✅ Văn bản đã chuyển đổi:")
    st.text_area("Kết quả:", transcribed_text, height=250)

    st.markdown("---")

  # Tạo và cho phép tải xuống file DOCX
    if "Không thể" not in transcribed_text and "Lỗi" not in transcribed_text:
        docx_bytes, docx_filename = create_docx(transcribed_text)
        
        st.download_button(
            label="💾 Tải xuống dưới dạng MS Word (.docx)",
            data=docx_bytes,
            file_name=docx_filename,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
        # Tùy chọn tải xuống file TXT
        st.download_button(
            label="📝 Tải xuống dưới dạng Văn bản (.txt)",
            data=transcribed_text.encode('utf-8'),
            file_name="transcribed_text.txt",
            mime="text/plain"
        )
# Chú ý quan trọng cho Micro
  if method == 'Ghi âm trực tiếp từ Micro':
      st.caption("**LƯU Ý QUAN TRỌNG:** Để ghi âm bằng Micro, bạn cần có thư viện **PyAudio** đã cài đặt. Trên một số hệ điều hành (đặc biệt là Linux và macOS), bạn có thể cần cài đặt thêm các gói hệ thống như `portaudio`.")

if __name__ == "__main__":
  main()
  
