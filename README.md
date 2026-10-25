\# VisionX — Assistive AI



VisionX is a laptop-based assistive-AI prototype inspired by an academic project exploring how artificial intelligence could help people with visual impairments better understand their surroundings.



The current prototype combines pretrained object detection with spoken descriptions. Users can upload an image, view detected objects and bounding boxes, and listen to a spoken summary of the detected objects.



\## Why VisionX?



For a person with visual impairments, knowing what is around them can be valuable. VisionX explores how computer vision and audio feedback could make visual information more accessible.



Object detection is only one part of that goal. This prototype demonstrates an initial step toward the broader assistive concept.



\## Features



\- Upload images in JPG, JPEG, PNG, or WEBP format.

\- Detect supported objects using a pretrained YOLO model.

\- View bounding boxes and object labels on the image.

\- Review detected objects and model confidence scores.

\- Generate a simple text description of detected objects.

\- Hear the description using the browser's speech synthesis feature.

\- Run locally on a computer without dedicated hardware.



\## How It Works



1\. Upload an image through the Streamlit interface.

2\. Select \*\*Detect objects\*\*.

3\. VisionX processes the image using a pretrained YOLO model.

4\. View the annotated image and detection results.

5\. Select \*\*Read description aloud\*\* to hear the summary.



The first run may download the pretrained model weights if they are not already available.



\## Technology



\- Python

\- Streamlit

\- Ultralytics YOLO

\- Pillow

\- Browser Speech Synthesis API



\## Getting Started



\### Requirements



\- Python installed on your computer

\- Internet access to install dependencies and download the pretrained model on the first run

\- A supported modern browser for speech playback



\### Installation



Clone this repository and open the project directory in a terminal.



Create a virtual environment:



```bash

python -m venv .venv

```



Activate it on Windows PowerShell:



```powershell

.\\.venv\\Scripts\\Activate.ps1

```



Install dependencies:



```bash

python -m pip install -r requirements.txt

```



Run the app:



```bash

streamlit run app.py

```



Open the local URL shown in the terminal, usually `http://localhost:8501`.



If PowerShell blocks virtual-environment activation, use the environment's Python executable directly:



```powershell

.\\.venv\\Scripts\\python.exe -m streamlit run app.py

```



\### Speech Support



Spoken descriptions use the browser's built-in speech synthesis. Voice availability and playback depend on browser and device settings.



\## Current Scope



This version supports image upload, object detection, visual detection results, and spoken summaries.



It does not currently implement live camera processing, voice commands, wearable hardware, obstacle-distance measurement, route guidance, or a complete assistive navigation system.



\## Limitations and Safety



\- Objects may be missed or incorrectly identified.

\- Confidence scores are estimates, not guarantees of correctness.

\- The spoken summary reports detected object labels; it does not understand the full scene or reliably explain spatial relationships.

\- The prototype has not been validated for independent navigation or safety-critical use.

\- Do not rely on this application to avoid obstacles or make safety decisions.



\## Background



VisionX is inspired by an academic assistive-AI concept. The current repository is a minimal laptop-based prototype, not a claim that all features proposed in the original academic project were implemented.



\## Model and Licensing



This project uses the Ultralytics YOLO framework and pretrained model weights. Review the applicable software and model licensing terms before redistribution or commercial use. Review dependency licenses as well.



\## Future Improvements



\- Improve the spoken descriptions and accessibility of the interface.

\- Explore optional live camera input.

\- Evaluate detection quality on a documented test set.

\- Investigate safe and meaningful ways to communicate spatial information.

\- Explore assistive hardware only when resources are available.



