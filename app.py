
import io
import json

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
from ultralytics import YOLO

st.set_page_config(
    page_title="VisionX | Assistive AI",
    page_icon="👁️",
    layout="wide",
)

st.title("VisionX — Assistive AI")
st.write(
    "An assistive-AI prototype exploring how computer vision "
    "and spoken feedback can make visual information more accessible."
)

st.info(
    "Upload an image to detect objects and hear a spoken summary. "
    "This prototype is not a complete assistive device and must not "
    "be relied upon for safe navigation."
)


@st.cache_resource
def load_model():
    return YOLO("yolo11n.pt")


uploaded_file = st.file_uploader(
    "Upload an image",
    type=["jpg", "jpeg", "png", "webp"],
)

if uploaded_file:
    try:
        image = Image.open(
            io.BytesIO(uploaded_file.getvalue())
        ).convert("RGB")
    except Exception:
        st.error("Could not open this image. Please try another.")
        st.stop()

    st.subheader("Uploaded image")
    st.image(image, use_container_width=True)

    if st.button("Detect objects", type="primary"):
        with st.spinner("Detecting objects..."):
            model = load_model()
            result = model.predict(
                image, conf=0.25, verbose=False
            )[0]

        st.session_state["visionx_result"] = result
        st.session_state["visionx_image_name"] = uploaded_file.name

    result = st.session_state.get("visionx_result")

    if result is not None and st.session_state.get(
        "visionx_image_name"
    ) == uploaded_file.name:
        annotated = result.plot()[:, :, ::-1]

        st.subheader("Detection results")
        st.image(annotated, use_container_width=True)

        names = []
        if result.boxes is not None:
            for box in result.boxes:
                class_id = int(box.cls[0].item())
                names.append(result.names[class_id])

        if not names:
            st.warning("No objects were detected.")
        else:
            from collections import Counter

            counts = Counter(names)

            rows = [
                {
                    "Object": result.names[class_id],
                    "Confidence": f"{float(box.conf[0].item()):.1%}",
                }
                for box in result.boxes
                for class_id in [int(box.cls[0].item())]
            ]

            st.subheader("Objects identified")
            st.dataframe(rows, hide_index=True, use_container_width=True)

            parts = [
                f"{count} {name}" if count > 1 else f"one {name}"
                for name, count in counts.items()
            ]
            description = "Detected objects include " + ", ".join(parts) + "."

            st.subheader("Spoken description")
            st.write(description)

            # Keep the speech button and JavaScript together in one
            # component so a separate Streamlit button doesn't rerun
            # and destroy the speech component before it can run.
            components.html(
                f"""
                <div style="font-family: sans-serif;">
                  <button id="visionx-speak" style="
                    padding: 12px 18px;
                    border-radius: 8px;
                    border: 1px solid #888;
                    cursor: pointer;
                    font-size: 16px;">
                    🔊 Read description aloud
                  </button>
                  <p id="visionx-status" aria-live="polite"></p>
                </div>
                <script>
                  const btn = document.getElementById("visionx-speak");
                  const status = document.getElementById("visionx-status");
                  const text = {json.dumps(description)};

                  btn.addEventListener("click", () => {{
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
                        "Speech error: " + event.error;
                    }};

                    window.speechSynthesis.speak(speech);
                  }});
                </script>
                """,
                height=100,
            )

st.divider()
st.caption(
    "Educational prototype inspired by an academic assistive-AI concept. "
    "Detection may be inaccurate and must not be used for navigation "
    "or safety decisions."
)
