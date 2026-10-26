# VisionX - Assistive AI

VisionX is an assistive AI prototype that uses computer vision to identify objects and provide spoken feedback. It explores how AI can make visual information more accessible to people with visual impairments.

The application runs on a computer and supports image uploads, camera photos, and continuous webcam detection.

## The Problem

People with visual impairments may need additional ways to learn about objects in their surroundings. VisionX explores how computer vision and audio feedback can help communicate some of this information.

## The Solution

VisionX uses a pretrained YOLO model to detect supported objects in images and webcam video. It displays detection results and can communicate detected object information through browser-based speech.

This is an experimental prototype, not a complete assistive navigation system.

## Features

- Upload an image for object detection.
- Capture a photo using the camera.
- Detect supported objects using YOLO.
- View object labels and bounding boxes.
- Review detection confidence scores.
- Process live webcam video.
- Hear spoken descriptions and live detection announcements.
- Run the application locally through Streamlit.

## Screenshots

### Main application

![VisionX home screen](docs/screenshots/VisionXHome.png)

### Object detection

![Object detection](docs/screenshots/ObjectDetection.png)

### Detection results

![Detection results](docs/screenshots/DetectionResults.png)

### Live webcam detection

![Live detection](docs/screenshots/LiveDetection.png)

## Technology Stack

- Python
- Streamlit
- Ultralytics YOLO
- OpenCV
- Pillow
- Streamlit WebRTC
- PyAV
- Browser Speech Synthesis API

## How It Works

1. Start VisionX and open the local web interface.
2. Upload an image, capture a camera photo, or start live webcam detection.
3. The YOLO model processes the image or video frames.
4. View the detected objects and bounding boxes.
5. Use the available speech features to hear information about detected objects.

For live announcements, allow camera access and enable spoken feedback in the application.

## Getting Started

### Requirements

- Python
- A compatible web browser
- A webcam for live detection
- Internet access to install dependencies
- The required YOLO model weights

### Installation

Clone the repository and open its folder in a terminal:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd visionx-assistive-ai
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install the dependencies on Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Make sure the required model file, `yolo11n.pt`, is available in the project root. The model weights are not included in this repository by default.

Start the application:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local URL displayed in the terminal, usually `http://localhost:8501`.

The repository URL above is a placeholder until the GitHub repository is created.

## Sample Images

Two example images are provided for trying image detection:

- `docs/sample-images/StreetScene.png`
- `docs/sample-images/BusyRoad.png`

Detection results depend on the objects present in the image and the model's predictions.

## Limitations and Safety

- Objects can be missed or incorrectly identified.
- Confidence scores do not guarantee that a detection is correct.
- Spoken feedback may not fully describe the scene or spatial relationships.
- The application has not been validated for independent navigation or safety-critical use.
- It does not provide a validated obstacle-distance measurement or route-guidance system.

**Do not rely on VisionX to cross roads, avoid obstacles, or make safety-critical decisions.** It is a prototype for learning and experimentation.

## Future Improvements

- Improve spoken descriptions and accessibility.
- Evaluate detection quality using a documented test set.
- Improve live detection responsiveness.
- Explore clearer ways to communicate spatial information.
- Investigate assistive hardware when suitable resources are available.

These are potential improvements, not features promised by the current implementation.

## Licensing and Attribution

This project uses third-party software and pretrained model weights. Check the relevant licenses and attribution requirements before redistributing the software, model weights, or other assets.

Making a repository public does not automatically grant others permission to reuse all its contents. An appropriate project license can be added after the licensing of the included work has been confirmed.

## Project Status

VisionX is an ongoing assistive AI prototype. This repository documents the current implementation, how to run it, and its known limitations.
