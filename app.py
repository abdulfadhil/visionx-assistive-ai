
import hashlib
import io
import json
from collections import Counter
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, UnidentifiedImageError
from ultralytics import YOLO


PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "yolo11n.pt"


st.set_page_config(
    page_title="VisionX | Assistive AI",
    layout="wide",
)

st.title("VisionX — Assistive AI")
st.write(
    "An assistive-AI prototype that uses computer vision "
    "and spoken feedback to make visual information more accessible."
)

st.info(
    "Upload an image to identify objects and hear a spoken description. "
    "This prototype is not a complete assistive device and must not "
    "be relied upon for safe navigation."
)


@st.cache_resource
def load_model():
    if not MODEL_PATH.is_file():
        raise FileNotFoundError(
            f"The YOLO model file was not found at: {MODEL_PATH}"
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

    if len(parts) == 1:
        description = parts[0]
    elif len(parts) == 2:
        description = f"{parts[0]} and {parts[1]}"
    else:
        description = ", ".join(parts[:-1]) + f", and {parts[-1]}"

    return f"I detected {description}."



uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"],
)

camera_file = st.camera_input("Or take a picture with your camera")

image_source = uploaded_file if uploaded_file is not None else camera_file

if image_source is not None:
    image_bytes = image_source.getvalue()

    image_id = hashlib.sha256(image_bytes).hexdigest()

    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError):
        st.error("This image could not be opened. Please choose another.")
        st.stop()

    st.subheader("Uploaded image")
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

        except Exception:
            st.session_state.pop("visionx_result", None)
            st.session_state.pop("visionx_image_id", None)
            st.error(
                "Object detection failed. Check that the model file "
                "exists and that the application dependencies are installed."
            )
            st.stop()

    result = st.session_state.get("visionx_result")
    result_image_id = st.session_state.get("visionx_image_id")

    if result is not None and result_image_id == image_id:
        st.subheader("Detection results")

        annotated_image = result.plot()[:, :, ::-1]
        st.image(annotated_image, width="stretch")

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

            st.subheader("Spoken description")
            st.write(description)

            speech_text = json.dumps(description)

            components.html(
                f"""
                <div style="font-family: sans-serif;">
                    <button id="visionx-speak" style="
                        padding: 10px 16px;
                        border-radius: 6px;
                        border: 1px solid #888;
                        cursor: pointer;
                        font-size: 15px;
                    ">Read description aloud</button>
                    <p id="visionx-status" aria-live="polite"></p>
                </div>
                <script>
                    const button = document.getElementById("visionx-speak");
                    const status = document.getElementById("visionx-status");
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

st.divider()
st.caption(
    "Educational prototype. Object detection may be inaccurate and "
    "must not be used as the sole basis for navigation or safety decisions."
)
