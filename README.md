# Image Analysis for Art Authentication

This application is aimed to count various statistics in uploaded images to decide the chances of whether the image was AI-generated or human-made. The image the application is focused on is photos of art, specifically paintings on canvas, board, or metal.

## Prerequisites

- Python 3.8+
- pip

## Installation

1.  Clone the repository.
2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Project Structure
```text
.
├── app/                      # Main application package
│   ├── main.py               # FastAPI entry point
│   ├── database.py           # Database management
│   ├── storage.py            # GCS interaction
│   ├── visualization.py      # HOG/Image visualization
│   ├── analysis/             # Analysis sub-package
│   ├── static/               # CSS, JS modules
│   └── templates/            # HTML templates
├── tests/                    # Backend/Frontend tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
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
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

The application will be available at `http://localhost:8080`.

### Backend Tests (Python)

The project uses `pytest` for backend testing. To run the test suite:

```bash
./venv/bin/pytest
```

This will execute all tests located in the `tests/` directory.

### Frontend Tests (JavaScript)

The project uses `Jest` for unit testing the frontend logic (validators, renderers, etc.).

**Prerequisites:**
- **Node.js**: Version 16.0 or higher is required for ES Module support.
- **npm**: Installed with Node.js.

**Setup and Execution:**

0.  **Select Node.js version**:
    ```bash
    nvm use v18.20.8
    ```

1.  **Install dependencies**:
    ```bash
    npm install
    ```

2.  **Run tests**:
    ```bash
    npm test
    ```

3.  **Run with coverage**:
    ```bash
    npm run test:coverage
    ```

## Deploy with Docker

You can easily deploy the application using Docker. This ensures all dependencies are correctly managed and provided.

### Prerequisites
- Docker installed
- Docker Compose (optional but recommended)

### Option 1: Using Docker Compose (Recommended)

This method sets up volumes for persisting the database and model cache.

1.  **Start the application**:
    ```bash
    docker-compose up -d
    ```

2.  **View logs**:
    ```bash
    docker-compose logs -f
    ```

3.  **Stop the application**:
    ```bash
    docker-compose down
    ```

### Option 2: Using Docker directly

1.  **Build the image**:
    ```bash
    docker build -t image-analysis-app .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8080:8080 image-analysis-app
    ```

### Docker Volume Mapping
If running with `docker-compose`, the following volumes are mapped to persist data:
- `data/`: Persists the analysis history (`image_stats.duckdb`). Mounting the directory allows for data locking and temporary files required by DuckDB.
- `tmp/`: Persists generated HOG visualizations.
- `cache/transformers/`: Persists the AI model weights to avoid downloading them on every restart.

### Environment Variables
You can pass environment variables to the container for custom configuration (e.g., in `docker-compose.yml` or using `-e` flag):
- `GCS_BUCKET_NAME`: Set your Google Cloud Storage bucket name.
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account JSON file (ensure the file is also mounted as a volume).

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
- `analysis/fractaldim.py`: Fractal dimensionality.


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
        2. `Histogram Analysis`: Computing RGB color histograms.
        3. `HOG Analysis`: Computing Histogram of Oriented Gradients.
        4. `AI Classifier`: Running the ViT inference.
        5. `Fractal Analysis`: Computing fractal dimensionality.
        6. `Uploading to Storage`: Saving the original image to GCS.
        7. `Saving to Database`: Storing results and metadata in DuckDB.
    *   `current_step`: (string) The step currently executing.
    *   `completed_steps`: (list) List of completed steps.
    *   `partial_results`: (object, optional) Real-time results as they become available:
        *   `histogram_r`, `histogram_g`, `histogram_b`: (arrays) RGB histogram data (256 bins each).
        *   `hog_image_url`: (string) URL to HOG visualization image.
        *   `ai_probability`: (float) AI detection probability (0.0-1.0).
        *   `fd_default`: (float) Fractal dimension value.
    *   `result`: (object, optional) Final result when complete (includes `id`, `url`, and `stats`).
    *   `error`: (string, optional) Error message if failed.

### Get Statistics
**GET** `/stats`
*   Retrieves aggregate statistics of all analyzed images.

### Get Static File
**GET** `/tmp/{filename}`
*   Serves generated files like HOG visualizations.


# TODO:
- Read embedded SynthID digital watermark (Requires Google Cloud Vertex AI SDK; no offline library available) 
