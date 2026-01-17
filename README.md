# RealSpark. AI Art Detector & Analyzer

This application is aimed to count various statistics in uploaded images to decide the chances of whether the image was AI-generated or human-made. The image the application is focused on is photos of art, specifically paintings on canvas, board, or metal.

## Features

### AI Image Detection (Offline)
The application uses a pre-trained **Vision Transformer (ViT)** model locally for high-accuracy detection of AI-generated content.
- **Model**: `Ateeqq/ai-vs-human-image-detector` (available on Hugging Face).
- **Architecture**: Vision Transformer (ViT).
- **Implementation**: Uses `transformers` and `torch` for offline inference.

It provides a probability score (0.0 to 1.0) where higher values indicate high likelihood of AI generation.

### HOG Feature Visualization
Histogram of Oriented Gradients (HOG) analysis is performed to identify structural patterns in the image, which are then visualized to show the detected features.

### Art Medium Analysis (DINOv2 + CLIP)
The application performs a multi-stage analysis to identify the artistic medium and verify its physical consistency.
- **Physical Texture Analysis (DINOv2)**: 
    - The image is tiled into overlapping 224x224 patches.
    - **DINOv2** (`facebook/dinov2-base`) generates high-dimensional embeddings for each patch.
    - **Vector Search & Clustering**: Patches are compared using cosine similarity. Repeatable textures (e.g., "scratchiness" of a dry brush or specific impasto strokes) cluster together.
    - **Consistency Scoring**: Measures texture uniformity. Low consistency suggests complex physical brushwork, while high consistency often points to digital media or uniform washes.
- **High-Level Labeling (CLIP)**:
    - **CLIP** (`openai/clip-vit-base-patch32`) provides zero-shot classification for the entire image against labels like *Watercolor, Oil, Acrylic, Digital painting*, etc.
- **Cross-Verification**: The local texture findings from DINOv2 are contrasted with global CLIP labels to provide a nuanced description of the medium and its authenticity.

### AI Insight Summary (LLM)
A specialized "synthesizer" step that processes all previous technical findings into a single, professional conclusion for an appraiser.
- **Model**: `google/flan-t5-small`.
- **Architecture**: Instruction-tuned Text-to-Text Transfer Transformer (T5).
- **Function**: It translates metrics like "85% AI probability" and "DINOv2 consistency scores" into a human-readable insight.

## How to Use

1.  **Web Interface**:
    *   Open your browser and navigate to `http://localhost:8080`.
    *   Use the upload form to select an image file (supported formats: JPEG, PNG, etc.).
    *   Submit the form to upload the image.
    *   The application will analyze the image and display statistics related to its composition and features.

## Prerequisites

- **Python**: 3.10.x, 3.11.x, or 3.12.x
- **pip**: Python package manager
- **Node.js**: v16+ (Required for API generation and Frontend tests)
- **npm**: Node package manager

## Installation

1.  Clone the repository.
2.  **Create a virtual environment (optional but recommended):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install the required dependencies:
    ```bash
    # For production:
    pip install -r requirements.txt

    # For development (tests, linting, api-gen):
    pip install -r requirements-dev.txt
    ```

## Development Workflow

The preferred development workflow is using **VS Code Dev Containers**. This project uses a **multi-stage Dockerfile** to provide a perfectly configured environment.

- **Automated Setup**: Installs Python 3.12, Node.js v18 (for API generation), and all development tools.
- **Isolated Environment**: Bypasses local dependency conflicts (especially with PyTorch/Transformers on Intel Macs).
- **Integrated Tools**: Pre-configures extensions and services (Formatter: `ruff`, Linter: `PyLance`).

**How to start:**
1. Open the project folder in VS Code.
2. Click **"Reopen in Container"** when prompted (or via the Command Palette).
3. The environment will automatically build using the `development` target, installing both production and development requirements.

The application will be available at [http://localhost:8080](http://localhost:8080).

### Automatic Reload & Manual Restart

When developing within the Dev Container, you have two options to ensure your Python code changes are reflected:

1.  **Automatic Reload (Recommended)**: The `Dockerfile` is configured with the `--reload`. Any save to a `.py` file will trigger an automatic restart of the Uvicorn server. Speficically use `--reload-dir app` flag to exclude observing frequent changes of `.py` in /cache directory.
    *   *Note: If you have just updated your local files and your container was already running, you may need to **"Rebuild Container"** to apply the new `Dockerfile` configuration.*
2.  **Manual Restart script**: If you don't want to rebuild the container, you can manually trigger a restart with auto-reload enabled by running:
    ```bash
    bash app_restart.sh
    ```
    This is useful if the auto-detection fails or if you've made changes to the environment.

## Project Structure
```text
.
├── app/                      # Main application package
│   ├── main.py               # FastAPI entry point
│   ├── models.py             # Generated Pydantic models [GENERATED]
│   ├── database.py           # Database management (DuckDB)
│   ├── storage.py            # GCS interaction
│   ├── visualization.py      # HOG/Image visualization
│   ├── analysis/             # Analysis sub-package
│   │   ├── analysis.py       # Numerical image analysis
│   │   ├── aiclassifiers.py  # AI classification logic (ViT)
│   │   ├── fractaldim.py     # Fractal dimension computation
│   │   ├── histogram.py      # Color histogram computation
│   │   ├── artmedium/        # Art Medium classification (DINOv2, CLIP)
│   │   └── summarizer.py     # AI Insight generation (Flan-T5)
│   ├── static/               # Frontend assets
│   │   └── js/client/        # Generated JS Client SDK [GENERATED]
│   └── templates/            # Jinja2 HTML templates
├── tests/                    # Test suite
│   └── ...
├── data/                     # Local data storage (DuckDB files)
├── tmp/                      # Temporary file storage
├── cache/                    # Local cache (AI model weights)
├── openapi.yaml              # OpenAPI specification
├── generate-api.sh           # API code generation script
├── pytest.ini                # Pytest configuration
├── package.json              # Node.js dependencies/scripts
├── Dockerfile                # Docker image definition
├── docker-compose.yml        # Docker composition
├── requirements.txt          # Production dependencies
├── requirements-dev.txt      # Development & Test dependencies
└── ...
```

## Testing

### Backend Tests (Python)

The project uses `pytest` for backend testing. To run the test suite:

On local environment:
```bash
./venv/bin/pytest
```

On docker environment:
```bash
pytest
```

This will execute all tests located in the `tests/` directory.

### Frontend Tests (JavaScript)

The project uses `Jest` for unit testing the frontend logic (validators, renderers, etc.).

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

### Frontend Integration Tests (Playwright)

The project uses **Playwright** for browser-based integration testing of the complete upload and analysis workflow.

**Prerequisites:**
- **Python 3.10-3.12** (Python 3.13+ has compatibility issues with numpy<2.0).
- Python virtual environment activated
- Playwright browsers installed

**Setup (One-time):**

1.  **Ensure you're using the correct Python version**:
    ```bash
    python3 --version  # Should show 3.10.x, 3.11.x, or 3.12.x
    ```

2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Install Playwright browsers**:
    ```bash
    playwright install chromium
    ```

**Running Frontend Integration Tests:**

1.  **Run all frontend integration tests** (headless mode):
    ```bash
    pytest tests/test_frontend_integration.py -v
    ```

2.  **Run with visible browser** (for debugging):
    ```bash
    pytest tests/test_frontend_integration.py -v --headed
    ```

3.  **Run a specific test**:
    ```bash
    pytest tests/test_frontend_integration.py::test_upload_displays_all_steps -v
    ```

4.  **Run all tests** (backend + frontend):
    ```bash
    pytest -v
    ```

**What the Frontend Integration Tests Cover:**
- ✅ All execution steps are displayed after upload
- ✅ Parallel step execution indicators (running state)
- ✅ Progressive display of partial results (HOG, AI, Fractal, Histogram)
- ✅ Final results display with all cards visible
- ✅ Step progression sequence and status indicators
- ✅ UI element visibility flow
- ✅ Timeout handling
- ✅ Multiple timeouts displayed correctly
- ✅ Error handling and error messages
- ✅ Invalid file upload rejection


## API Code Generation

The project utilizes an **OpenAPI-driven development** workflow. The central source of truth for the API is `openapi.yaml`. 

### When to run generation
You **must** run the generation script whenever you modify the API definition in `openapi.yaml`. This is essential because:
- **Backend (Python)**: The Pydantic models in `app/models.py` are automatically updated to match the latest schema. These models are used throughout `app/main.py`.
- **Frontend (JavaScript)**: The UI uses standard `fetch()` calls and **Alpine.js** for reactivity. This ensures a lightweight, build-free frontend while maintaining alignment with the backend through manual implementation of the shared API contract.

### How to run generation
The easiest way is to use the provided `npm` script:

**Recommended Method (npm):**
```bash
npm run generate-api
```

**Alternative (Bash):**
```bash
bash generate-api.sh
```

### Underlying Tools
- **Python Models**: Generated using `datamodel-code-generator` (installed automatically in `venv`). It parses `openapi.yaml` and produces `app/models.py`.


## Deploy with Docker

The project uses a **multi-stage build** process to ensure a secure and lean production environment.

### Multi-Stage Dockerfile Targets
- **`base`**: Common runtime environment.
- **`development`**: Includes full build toolchain (git, curl, wget, Node.js, build-essential) and development dependencies for testing and API generation.
- **`production`**: Minimal image containing only the application code and production dependencies for maximum security and performance.

### Option 1: Using Docker Compose (Recommended)
This method handles volume mapping for database persistence and model caching.

**To start for local development (includes dev tools):**
```bash
docker compose up -d --build
```
*Note: The `docker-compose.yml` is configured to use the `development` target by default, which includes all tools for API generation and testing.*

**To view logs:**
```bash
docker compose logs -f
```

**To stop:**
```bash
docker compose down -v
```

### Option 2: Building for Production (Lean)
To build a lean image without development tools:
```bash
docker build --target production -t art-analysis-prod .
```

### Docker Volume Mapping
If running with `docker compose`, the following volumes are mapped to persist data:
- `data/`: Persists the analysis history (`image_stats.duckdb`). Mounting the directory allows for data locking and temporary files required by DuckDB.
- `tmp/`: Persists generated HOG visualizations.
- `cache/transformers/`: Persists the AI model weights to avoid downloading them on every restart.

### Environment Variables
You can pass environment variables to the container for custom configuration (e.g., in `docker-compose.yml` or using `-e` flag):
- `GCS_BUCKET_NAME`: Set your Google Cloud Storage bucket name.
- `GOOGLE_APPLICATION_CREDENTIALS`: Path to your service account JSON file (ensure the file is also mounted as a volume).

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
        2. `Metadata Analysis`: Examining EXIF and software tags for AI signatures.
        3. `Histogram Analysis`: Computing RGB color histograms.
        4. `HOG Analysis`: Computing Histogram of Oriented Gradients for structural patterns.
        5. `AI Classifier`: Running ViT inference for AI-vs-human detection.
        6. `Fractal Dimension`: Computing fractal dimensionality.
        7. `Art Medium Analysis`: DINOv2 patch analysis and CLIP classification.
        8. `Uploading to Storage`: Saving the original image to GCS.
        9. `Saving to Database`: Storing results and metadata in DuckDB.
        10. `AI Insight Summary`: Generates the final human-readable conclusion.
    *   `current_step`: (string) The step currently executing.
    *   `completed_steps`: (list) List of completed steps.
    *   `partial_results`: (object, optional) Real-time results as they become available:
        *   `histogram_r`, `histogram_g`, `histogram_b`: (arrays) RGB histogram data (256 bins each).
        *   `hog_image_url`: (string) URL to HOG visualization image.
        *   `ai_probability`: (float) AI detection probability (0.0-1.0).
        *   `fd_default`: (float) Fractal dimension value.
        *   `summary`: (string) The generated AI Insight text.
    *   `result`: (object, optional) Final result when complete (includes `id`, `url`, and `stats`).
    *   `error`: (string, optional) Error message if failed.

### Get Statistics
**GET** `/stats`
*   Retrieves aggregate statistics of all analyzed images.

### Get Static File
**GET** `/tmp/{filename}`
*   Serves generated files like HOG visualizations.


## Security

This project prioritizes security and environment integrity through the following measures:

### Restricted Interfaces
The application is configured to listen on `127.0.0.1` (localhost) when running natively. When running via Docker, it is exposed only to the local machine via the published port on `127.0.0.1:8080`. This ensures the application is not accessible from your local network or public internet unless explicitly configured.

### Dependency & Vulnerability Management
Due to the use of specific AI/ML frameworks (PyTorch 2.2+, Transformers), the project uses multi-stage builds to mitigate risks:
- **Environment Isolation**: Production images exclude all high-risk development tools (git, curl, build-essential, etc.).
- **Known Vulnerabilities**: Some local Intel-Mac versions of libraries may have CVEs; Docker provides a modern Linux environment where the latest non-vulnerable versions can be run regardless of your host OS.

### Trusted Model Loading
The application only downloads and loads pre-trained weights from verified official repositories (OpenAI, Facebook/Meta) on Hugging Face.

### User Permissions
Docker containers run as a non-root user (`vscode`) to prevent privilege escalation within the container environment.

## Licensing
- **Application Code**: Licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
- **AI Models**: All pre-trained models used in this project are released under the **Apache 2.0 License**:
    - AI Classifier: `Ateeqq/ai-vs-human-image-detector`
    - Texture Analysis: `facebook/dinov2-base`
    - Labeling: `openai/clip-vit-base-patch32`
    - Summarizer: `google/flan-t5-small`