# Image Analysis for Art Authentication

This application is aimed to count various statistics in uploaded images to decide the chances of whether the image was AI-generated or human-made. The image the application is focused on is photos of art, specifically paintings on canvas, board, or metal.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  Clone the repository.
2.  Create a virtual environment (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run the App

You can run the application using `uvicorn` directly or via the provided helper script.

### Using the helper script (Recommended)

This script manages the process for you, stopping any existing instances and starting a new one in the background.

```bash
./restart_app.sh
```

Logs will be written to `server.log`.

### Manual Start

To start the application manually:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

The application will be available at `http://localhost:8080`.

## How to Run Tests

The project uses `pytest` for testing. To run the test suite:

```bash
pytest
```

This will execute all tests located in the `tests/` directory.

## How to Use the App

1.  **Web Interface**:
    *   Open your browser and navigate to `http://localhost:8080`.
    *   Use the upload form to select an image file (supported formats: JPEG, PNG, etc.).
    *   Submit the form to upload the image.
    *   The application will analyze the image and display statistics related to its composition and features.

2.  **API Endpoints**:
    *   `POST /upload`: Upload an image file for analysis.
    *   `GET /stats`: Retrieve aggregate statistics of analyzed images.
