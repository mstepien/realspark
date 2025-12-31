# Image Analysis for Art Authentication

This application is aimed to count various statistics in uploaded images to decide the chances of whether the image was AI-generated or human-made. The image the application is focused on is photos of art, specifically paintings on canvas, board, or metal.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  Clone the repository.
2.  **Create and Activate a Virtual Environment (Required):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    *Note: Always allow the `venv` environment for development and running the app.*

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the App

You can run the application using `uvicorn` directly or via the provided helper script.

### Using the helper script (Recommended)

This script manages the process for you, stopping any existing instances and starting a new one in the background.

```bash
./app_restart.sh
```

Logs will be written to `server.log`.

### Manual Start

To start the application manually:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

The application will be available at `http://localhost:8080`.

## How to Run Tests

The project uses `pytest` for testing. To run the test suite ensuring the correct environment is used:

```bash
./venv/bin/pytest
```

Or, if you have already activated your virtual environment:

```bash
source venv/bin/activate
pytest
```

This will execute all tests located in the `tests/` directory.

## How to Use the App

1.  **Web Interface**:
    *   Open your browser and navigate to `http://localhost:8080`.
    *   Use the upload form to select an image file (supported formats: JPEG, PNG, etc.).
    *   Submit the form to upload the image.
    *   The application will analyze the image and display statistics related to its composition and features.

## Features

### AI Image Detection (Offline)
The application uses a pre-trained **Vision Transformer (ViT)** model locally for high-accuracy detection of AI-generated content.
- **Model**: `Ateeqq/ai-vs-human-image-detector` (available on Hugging Face).
- **Architecture**: Vision Transformer (ViT).
- **Implementation**: Uses `transformers` and `torch` for offline inference.

It provides a probability score (0.0 to 1.0) where higher values indicate high likelihood of AI generation.

### HOG Feature Visualization
Histogram of Oriented Gradients (HOG) analysis is performed to identify structural patterns in the image, which are then visualized to show the detected features.

### Modular Analysis Package
The analysis logic is organized into a modular package structure:
- `analysis/analysis.py`: Numerical image analysis (HOG, metadata).
- `analysis/aiclassifiers.py`: AI classification logic and model management.


## API Reference

### Upload Image
**POST** `/upload`
*   Starts an asynchronous image analysis task.
*   **Body**: `multipart/form-data` with `file` field.
*   **Response**: `{"task_id": "uuid..."}`

### Check Progress
**GET** `/progress/{task_id}`
*   Returns the status and progress of a task.
*   **Response**: JSON containing:
    *   `status`: (string) Current status message.
    *   `progress`: (int) Progress percentage (0-100).
    *   `steps`: (list) List of total steps:
        1. `Preprocessing`: Basic image loading and metadata extraction.
        2. `HOG Analysis`: Computing Histogram of Oriented Gradients.
        3. `AI Classifier`: Running the ViT inference.
        4. `Fractal Analysis`: Computing fractal dimensionality.
        5. `Uploading to Storage`: Saving the original image to GCS.
        6. `Saving to Database`: Storing results and metadata in DuckDB.
    *   `current_step`: (string) The step currently executing.
    *   `completed_steps`: (list) List of completed steps.
    *   `result`: (object, optional) Final result when complete (includes `stats` and `hog_image_url`).
    *   `error`: (string, optional) Error message if failed.

### Get Statistics
**GET** `/stats`
*   Retrieves aggregate statistics of all analyzed images.

### Get Static File
**GET** `/tmp/{filename}`
*   Serves generated files like HOG visualizations.


# TODO:
- Read embedded SynthID digital watermark (Requires Google Cloud Vertex AI SDK; no offline library available) 
