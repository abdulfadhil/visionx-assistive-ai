
import hashlib
import io
import json
import threading
import time
from collections import Counter
from pathlib import Path

import av
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError
from streamlit_webrtc import WebRtcMode, webrtc_streamer
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "yolo11n.pt"

LIVE_CONFIDENCE = 0.35
LIVE_IMAGE_SIZE = 416
ANNOUNCEMENT_COOLDOWN = 5.0
MAX_ANNOUNCEMENTS_PER_UPDATE = 4


st.set_page_config(
    page_title="VisionX | Assistive AI",
    layout="wide",
)

st.title("VisionX - Assistive AI")
st.write(
    "An assistive AI prototype that identifies objects using computer "
    "vision and provides spoken descriptions."
)

st.info(
    "This is an educational prototype, not a complete assistive device. "
    "Object detection can be inaccurate. Do not rely on it for safe "
    "navigation or as a substitute for a mobility aid."
)


@st.cache_resource
def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"YOLO model file not found: {MODEL_PATH}"
        )

    return YOLO(str(MODEL_PATH))


def describe_objects(names):
    counts = Counter(names)

    plural_forms = {
        "person": "people",
        "mouse": "mice",
        "sheep": "sheep",
        "sports ball": "sports balls",
        "traffic light": "traffic lights",
        "fire hydrant": "fire hydrants",
        "stop sign": "stop signs",
        "parking meter": "parking meters",
        "dining table": "dining tables",
        "potted plant": "potted plants",
        "cell phone": "cell phones",
        "hair drier": "hair driers",
        "toothbrush": "toothbrushes",
    }

    parts = []

    for name, count in counts.items():
        if count == 1:
            parts.append(f"one {name}")
        else:
            plural = plural_forms.get(
                name,
                name + (
                    "es"
                    if name.endswith(("s", "x", "ch", "sh"))
                    else "s"
                ),
            )
            parts.append(f"{count} {plural}")

    if not parts:
        return "I could not identify any objects."

    if len(parts) == 1:
        description = parts[0]
    elif len(parts) == 2:
        description = f"{parts[0]} and {parts[1]}"
    else:
        description = ", ".join(parts[:-1]) + f", and {parts[-1]}"

    return f"I detected {description}."


def get_detection_rows(result):
    rows = []

    if result.boxes is not None:
        for box in result.boxes:
            class_id = int(box.cls[0].item())
            confidence = float(box.conf[0].item())

            rows.append(
                {
                    "Object": result.names[class_id],
                    "Confidence": f"{confidence:.1%}",
                }
            )

    return rows


def show_spoken_description(description, component_key):
    st.subheader("Spoken description")
    st.write(description)

    speech_text = json.dumps(description)

    components.html(
        f"""
        <div style="font-family: sans-serif;">
            <button id="{component_key}-speak" style="
                padding: 10px 16px;
                border-radius: 6px;
                border: 1px solid #888;
                cursor: pointer;
                font-size: 15px;
            ">Read description aloud</button>
            <p id="{component_key}-status" aria-live="polite"></p>
        </div>
        <script>
            const button = document.getElementById(
                "{component_key}-speak"
            );
            const status = document.getElementById(
                "{component_key}-status"
            );
            const text = {speech_text};

            button.addEventListener("click", () => {{
                if (!("speechSynthesis" in window)) {{
                    status.textContent =
                        "Speech is not supported in this browser.";
                    return;
                }}

                window.speechSynthesis.cancel();

                const speech = new SpeechSynthesisUtterance(text);
                speech.lang = "en-IN";

                speech.onstart = () => {{
                    status.textContent = "Speaking...";
                }};

                speech.onend = () => {{
                    status.textContent = "Finished speaking.";
                }};

                speech.onerror = (event) => {{
                    status.textContent =
                        "Speech could not be completed: " + event.error;
                }};

                window.speechSynthesis.speak(speech);
            }});
        </script>
        """,
        height=100,
    )


def make_live_video_callback(model, shared_state):
    last_announced = {}
    last_state_update = 0.0

    def process_frame(frame):
        nonlocal last_state_update

        image = frame.to_ndarray(format="bgr24")

        try:
            results = model.predict(
                image,
                conf=LIVE_CONFIDENCE,
                imgsz=LIVE_IMAGE_SIZE,
                verbose=False,
            )

            result = results[0]
            annotated = result.plot()
            now = time.monotonic()

            names = []

            if result.boxes is not None:
                for box in result.boxes:
                    class_id = int(box.cls[0].item())
                    names.append(result.names[class_id])

            # Announce each detected class only after its cooldown.
            due_names = []

            for name in sorted(set(names)):
                previous = last_announced.get(name, 0.0)

                if now - previous >= ANNOUNCEMENT_COOLDOWN:
                    due_names.append(name)
                    last_announced[name] = now

            # Keep the shared update small and avoid writing on every frame.
            if due_names or now - last_state_update >= 1.0:
                with shared_state["lock"]:
                    shared_state["latest_objects"] = sorted(set(names))

                    if due_names:
                        shared_state["announcements"].append(
                            describe_objects(due_names)
                        )
                        shared_state["announcements"] = (
                            shared_state["announcements"][-10:]
                        )

                last_state_update = now

            return av.VideoFrame.from_ndarray(
                annotated,
                format="bgr24",
            )

        except Exception as error:
            with shared_state["lock"]:
                shared_state["error"] = str(error)

            return av.VideoFrame.from_ndarray(
                image,
                format="bgr24",
            )

    return process_frame


st.header("1. Image detection")

uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"],
)

camera_file = st.camera_input(
    "Or take a picture with your camera"
)

image_source = (
    uploaded_file
    if uploaded_file is not None
    else camera_file
)

if image_source is not None:
    image_bytes = image_source.getvalue()
    image_id = hashlib.sha256(image_bytes).hexdigest()

    try:
        image = Image.open(
            io.BytesIO(image_bytes)
        ).convert("RGB")

    except (UnidentifiedImageError, OSError, ValueError):
        st.error(
            "This image could not be opened. Please choose another."
        )
        st.stop()

    st.subheader("Image to analyze")
    st.image(image, width="stretch")

    if st.button("Detect objects", type="primary"):
        try:
            with st.spinner("Detecting objects..."):
                model = load_model()
                result = model.predict(
                    image,
                    conf=0.25,
                    verbose=False,
                )[0]

            st.session_state["visionx_result"] = result
            st.session_state["visionx_image_id"] = image_id

        except Exception as error:
            st.session_state.pop("visionx_result", None)
            st.session_state.pop("visionx_image_id", None)
            st.error(f"Object detection failed: {error}")

    result = st.session_state.get("visionx_result")
    result_image_id = st.session_state.get("visionx_image_id")

    if result is not None and result_image_id == image_id:
        st.subheader("Detection results")

        annotated_image = result.plot()[:, :, ::-1]
        st.image(annotated_image, width="stretch")

        rows = get_detection_rows(result)

        if not rows:
            st.warning("No objects were detected in this image.")
        else:
            st.subheader("Objects identified")
            st.dataframe(
                rows,
                hide_index=True,
                width="stretch",
            )

            description = describe_objects(
                [row["Object"] for row in rows]
            )

            show_spoken_description(
                description,
                "visionx-image",
            )


st.divider()
st.header("2. Continuous webcam detection")

st.write(
    "Live detection processes webcam frames and can announce detected "
    "objects using your browser's speech feature."
)

st.warning(
    "Live detection is experimental. It may miss objects or identify "
    "them incorrectly. Do not use it as the sole basis for navigation."
)

live_enabled = st.checkbox(
    "Enable live webcam detection",
    key="visionx_live_enabled",
)

if live_enabled:
    try:
        live_model = load_model()

        if "visionx_live_state" not in st.session_state:
            st.session_state["visionx_live_state"] = {
                "lock": threading.Lock(),
                "latest_objects": [],
                "announcements": [],
                "error": None,
            }

        shared_state = st.session_state["visionx_live_state"]

        st.caption(
            "Allow camera access. Start the video, then enable spoken "
            "announcements below. Browser speech must be permitted."
        )

        webrtc_streamer(
            key="visionx-live-camera",
            mode=WebRtcMode.SENDRECV,
            video_frame_callback=make_live_video_callback(
                live_model,
                shared_state,
            ),
            media_stream_constraints={
                "video": True,
                "audio": False,
            },
            async_processing=True,
        )

        with shared_state["lock"]:
            latest_objects = list(shared_state["latest_objects"])
            announcements = list(shared_state["announcements"])
            live_error = shared_state["error"]

        if live_error:
            st.error(f"Live detection error: {live_error}")

        st.subheader("Live objects")
        if latest_objects:
            st.write(", ".join(latest_objects))
        else:
            st.caption("No objects detected yet.")

        st.subheader("Live spoken feedback")

        auto_speech = st.checkbox(
            "Enable automatic spoken announcements",
            value=False,
            key="visionx_auto_speech",
        )

        # This component reads announcement updates from Streamlit.
        # It remembers the last spoken message to avoid replaying it
        # after an ordinary Streamlit rerun.
        speech_payload = json.dumps(announcements)

        components.html(
            f"""
            <div style="font-family: sans-serif;">
                <p id="visionx-live-speech-status" aria-live="polite">
                    {"Automatic speech is enabled." if auto_speech else "Automatic speech is off."}
                </p>
                <script>
                    const enabled = {json.dumps(auto_speech)};
                    const messages = {speech_payload};
                    const status = document.getElementById(
                        "visionx-live-speech-status"
                    );

                    if (enabled && messages.length > 0) {{
                        const latest = messages[messages.length - 1];

                        if (!window.parent.__visionxSpokenMessages) {{
                            window.parent.__visionxSpokenMessages = [];
                        }}

                        const spoken = window.parent.__visionxSpokenMessages;

                        if (!spoken.includes(latest)) {{
                            if ("speechSynthesis" in window.parent) {{
                                const utterance =
                                    new window.parent.SpeechSynthesisUtterance(
                                        latest
                                    );
                                utterance.lang = "en-IN";
                                utterance.onstart = () => {{
                                    status.textContent = "Speaking: " + latest;
                                }};
                                utterance.onerror = () => {{
                                    status.textContent =
                                        "Speech failed. Check browser speech support.";
                                }};

                                window.parent.speechSynthesis.speak(utterance);
                                spoken.push(latest);

                                if (spoken.length > 30) {{
                                    spoken.shift();
                                }}
                            }} else {{
                                status.textContent =
                                    "Speech is not supported in this browser.";
                            }}
                        }}
                    }}
                </script>
            </div>
            """,
            height=70,
        )

        if announcements:
            st.caption("Recent announcements")
            for message in announcements[-3:]:
                st.write(f"- {message}")

    except Exception as error:
        st.error(
            "Live webcam mode could not start. "
            f"Details: {error}"
        )

else:
    st.caption(
        "Live webcam mode is off. Your image-upload and photo-capture "
        "features remain available."
    )


st.divider()
st.caption(
    "VisionX is an educational prototype. Detection accuracy, "
    "performance, and accessibility must be evaluated before real-world use."
)
