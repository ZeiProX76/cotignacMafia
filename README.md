# cotignacMafia

A Python test suite for evaluating video description capabilities using the Qwen3-VL-32B-Thinking model.

## Description

This project tests the Qwen VL (Vision-Language) model's ability to precisely describe and analyze video content. The test script encodes local video files and sends them to the Qwen API for detailed analysis.

## Features

- Video encoding to base64 for API compatibility
- Streaming response output
- Detailed video content analysis
- Product demonstration detection and timestamping
- Visual quality and content potential scoring

## Prerequisites

- Python 3.8+
- DashScope API Key (from Alibaba Cloud Model Studio)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ZeiProX76/cotignacMafia.git
cd cotignacMafia
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your DASHSCOPE_API_KEY
```

## Usage

Run the video description test:
```bash
python test_video_description.py
```

The script will:
1. Load your video file
2. Encode it to base64
3. Send it to the Qwen3-VL model
4. Stream and display the detailed analysis

## Configuration

Edit the `video_path` variable in `test_video_description.py` to point to your video file:
```python
video_path = "/path/to/your/video.mp4"
```

## API Documentation

This project uses the Qwen API in OpenAI-compatible mode:
- Base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Model: `qwen3-vl-32b-thinking`

## License

MIT

## Author

ZeiProX76
