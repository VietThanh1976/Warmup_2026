import streamlit as st
import speech_recognition as sr
import librosa
import soundfile as sf
import io
import os
from docx import Document # Thư viện cho file .docx
import time

# Khởi tạo đối tượng nhận dạng giọng nói
r = sr.Recognizer()

# Đặt tiêu đề cho ứng dụng
st.title("🎤 Ứng Dụng Chuyển Giọng Nói Thành Văn Bản")
st.markdown("Sử dụng **Streamlit** và thư viện **SpeechRecognition**")

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

def transcribe_from_microphone():
    """Ghi âm từ micro và chuyển đổi thành văn bản."""
    with sr.Microphone() as source:
        st.info("Bấm vào nút **'Bắt đầu ghi âm'** và nói rõ ràng.")
        st.info("Đang lắng nghe... Vui lòng nói trong 5 giây.")
        
        # Điều chỉnh độ nhạy (quan trọng để loại bỏ tiếng ồn ban đầu)
        r.adjust_for_ambient_noise(source, duration=0.5) 
        
        # Ghi âm trong 5 giây
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            st.success("Đã hoàn thành ghi âm. Đang xử lý...")
            
            # Sử dụng Google Web Speech API
            text = r.recognize_google(audio, language="vi-VN")
            return text
        
        except sr.WaitTimeoutError:
            return "Không tìm thấy giọng nói trong thời gian cho phép."
        except sr.UnknownValueError:
            return "Không thể nhận dạng giọng nói."
        except sr.RequestError as e:
            return f"Lỗi kết nối hoặc API: {e}"
          
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
    if st.button('🎙️ Bắt đầu ghi âm (5 giây)'):
        # Biến trạng thái để hiển thị thông báo trong quá trình xử lý
        with st.spinner('Đang ghi âm và xử lý...'):
            transcribed_text = transcribe_from_microphone()
          
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
  
