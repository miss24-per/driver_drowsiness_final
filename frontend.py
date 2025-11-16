from app import *
import streamlit as st
import cv2
import numpy as np
import time
import threading
from playsound import playsound


st.set_page_config(page_title="Driver Drowsiness Detection", page_icon="🚘", layout="wide")


st.markdown("""
    <style>
        body {
            background-color: #D8E4BC;
        }
        .main-title {
            text-align: center;
            font-size: 40px;
            color: #1e3a8a;
            font-weight: bold;
        }
        .subtitle {
            text-align: center;
            font-size: 18px;
            color: #475569;
            margin-bottom: 30px;
        }
        .footer {
            background-color:#000000;
            text-align: center;
            font-size: 15px;
            color:#FFFFFF;
            margin-top: 400px;
            padding-top: 10px;
            border-top: 5px solid #94a3b8;
        }
        .developer {
            text-align: center;
            color: #FFFFFF;
            font-size: 15px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)


st.markdown('<div class="main-title">Driver Drowsiness Detection System</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">“Alert Today, Alive Tomorrow.”</div>', unsafe_allow_html=True)


option = st.sidebar.radio(
    "🔍 Select Mode",
    ["Upload File", "Use Camera", "Live Tracking"]
)

# Function to play buzzer sound
def buzzer_alert():
    try:
        audio_file = open("buzzer.wav", "rb")  
        audio_bytes = audio_file.read()
        st.audio(audio_bytes, format="audio/wav", start_time=0)
    except Exception as e:
        st.warning(f"⚠️ Could not play buzzer sound: {e}")

def preprocess_image(image):
    image = cv2.resize(image, (224, 224))
    image = np.expand_dims(image, axis=0)
    image = image / 255.0
    return image



# --- Upload Video Mode ---
if option == "Upload File":
    uploaded_video = st.file_uploader("📁 Upload a video", type=["mp4", "avi", "mov"])
    
    if uploaded_video is not None:
        # Save uploaded video temporarily
        temp_video_path = "temp_video.mp4"
        with open(temp_video_path, "wb") as f:
            f.write(uploaded_video.read())

        st.video(temp_video_path)

        st.info("🎬 Processing video... Please wait.")
        cap = cv2.VideoCapture(temp_video_path)
        FRAME_WINDOW = st.image([])

        frame_count = 0
        drowsy_frames = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_count += 1
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # ====== Dummy prediction (replace with model prediction later) ======
            prediction = np.random.choice([0, 1], p=[0.85, 0.15])  # mostly alert, some drowsy
            label = "😴 Drowsy" if prediction == 1 else "😊 Alert"
            color = (0, 0, 255) if label == "😴 Drowsy" else (0, 255, 0)
            cv2.putText(frame_rgb, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            # Display the frame
            FRAME_WINDOW.image(frame_rgb)

            # Count drowsy frames for alert
            if label == "😴 Drowsy":
                drowsy_frames += 1
                if drowsy_frames % 10 == 0:  # trigger buzzer every 10 drowsy frames
                    buzzer_alert()

            time.sleep(0.05)

        cap.release()
        st.success("✅ Video processing completed.")

        st.write(f"📊 Total Frames: {frame_count}")
        st.write(f"😴 Drowsy Frames Detected: {drowsy_frames}")


# --- Camera Capture Mode ---
elif option == "Use Camera":
    st.info("📸 Capture a photo for testing.")
    camera_input = st.camera_input("Take a picture")

    if camera_input:
        file_bytes = np.asarray(bytearray(camera_input.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, 1)
        st.image(cv2.cvtColor(image, cv2.COLOR_BGR2RGB), caption="Captured Image", use_container_width=True)

        prediction = np.random.choice([1])
        label = "😴 Drowsy" if prediction == 1 else "😊 Alert"
        st.subheader(f"Prediction: {label}")

        if label == "😴 Drowsy":
            st.error("⚠️ Driver is Drowsy! Sound Alert Triggered.")
            buzzer_alert()

# --- Live Tracking Mode ---
# --- Live Tracking Mode ---
elif option == "Live Tracking":
    st.info("🎥 Live Tracking mode: Click the checkbox below to start.")
    FRAME_WINDOW = st.image([])
    run = st.checkbox("▶️ Start Live Tracking")

    camera = cv2.VideoCapture(0)
    last_buzzer_time = 0  # Track last time buzzer played

    while run:
        ret, frame = camera.read()
        if not ret:
            st.warning("⚠️ Failed to access webcam.")
            break

        # Random mock prediction (replace later with model)
        prediction = np.random.choice([0, 1], p=[0.8, 0.2])  # mostly alert, sometimes drowsy
        label = "😴 Drowsy" if prediction == 1 else "😊 Alert"

        color = (0, 0, 255) if label == "😴 Drowsy" else (0, 255, 0)
        cv2.putText(frame, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

        FRAME_WINDOW.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # 🔊 Play buzzer once every 5 seconds if drowsy
        current_time = time.time()
        if label == "😴 Drowsy" and (current_time - last_buzzer_time) > 5:
            buzzer_alert()
            last_buzzer_time = current_time  # update timer

        time.sleep(0.3)

    camera.release()
    st.success("✅ Live tracking stopped.")


# =========================
# FOOTER
# =========================
st.markdown("""
    <div class="footer">
        <b>🚘 Stay Alert — Save Lives.</b><br>
        <div class="developer">Developed by Aarav Chaudhary, Sachi Gupta And Ishan Agarwal</div>
    </div>
""", unsafe_allow_html=True)
