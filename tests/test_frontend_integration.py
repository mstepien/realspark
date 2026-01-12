"""
Frontend Integration Tests

These tests use Playwright to verify the frontend behavior of the image analysis
application, including step display, parallel execution handling, and results rendering.
"""
import pytest
from playwright.sync_api import Page, expect
from PIL import Image
import io
import re
from app.main import app
import time


@pytest.fixture
def test_image_bytes():
    """
    Create a test image as bytes.
    """
    img = Image.new('RGB', (100, 100), color='blue')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def test_upload_displays_all_steps(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client):
    """
    Test that all execution steps are displayed after clicking Upload & Analyze.
    """
    # Navigate to the application
    page.goto(live_server)
    
    # Verify page loaded
    expect(page.locator("h1")).to_contain_text("Is that image created by AI?")
    
    # Verify step list is initially hidden
    step_list = page.locator("#stepList")
    expect(step_list).not_to_be_visible()
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Click upload button
    page.locator('button[type="submit"]').click()
    
    # Wait for step list to become visible
    expect(step_list).to_be_visible(timeout=5000)
    
    # Verify all 7 steps are displayed
    expected_steps = [
        "Preprocessing",
        "Metadata Analysis",
        "Histogram Analysis",
        "HOG Analysis",
        "AI Classifier",
        "Fractal Analysis",
        "Uploading to Storage",
        "Saving to Database"
    ]
    
    step_items = page.locator(".step-item")
    expect(step_items).to_have_count(len(expected_steps))
    
    # Verify each step is present
    for step_name in expected_steps:
        step_element = page.locator(f".step-item:has-text('{step_name}')")
        expect(step_element).to_be_visible()


def test_parallel_steps_show_running_state(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that parallel steps show running indicators during execution.
    """
    control.reset()
    # Set a longer delay for some steps to ensure we catch them running
    control.delays["metadata"] = 1.0
    control.delays["ai"] = 1.0
    
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for parallel analysis phase
    # We should see multiple steps with running indicators (↻)
    parallel_steps = [
        "Metadata Analysis",
        "Histogram Analysis",
        "HOG Analysis",
        "AI Classifier",
        "Fractal Analysis",
        "Uploading to Storage"
    ]
    
    # Check that we see at least one running indicator during parallel phase
    # This is timing-dependent, so we check within a reasonable window
    running_icon_seen = False
    for _ in range(20):  # Check for 2 seconds
        running_icons = page.locator('.step-icon.running')
        if running_icons.count() > 0:
            running_icon_seen = True
            break
        time.sleep(0.1)
    
    assert running_icon_seen, "Should see running indicators during parallel execution"


def test_partial_results_display_progressively(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that partial results appear progressively as analysis completes.
    """
    control.reset()
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for and verify HOG visualization appears
    hog_container = page.locator("#hogContainer")
    expect(hog_container).to_be_visible(timeout=10000)
    
    hog_image = page.locator("#hogImage")
    expect(hog_image).to_have_attribute("src", re.compile(r".+"))
    
    # Wait for and verify AI Detection card appears
    ai_card = page.locator("#aiResultCard")
    expect(ai_card).to_be_visible(timeout=10000)
    
    ai_score = page.locator("#aiScoreDisplay")
    expect(ai_score).not_to_be_empty()
    
    # Wait for and verify Fractal Dimension card appears
    fractal_card = page.locator("#fractalResultCard")
    expect(fractal_card).to_be_visible(timeout=10000)
    
    fd_display = page.locator("#fdDefaultDisplay")
    expect(fd_display).not_to_have_text("-")
    
    # Wait for and verify Histogram card appears
    histogram_card = page.locator("#histogramCard")
    expect(histogram_card).to_be_visible(timeout=10000)
    
    # Wait for and verify Metadata card appears
    metadata_card = page.locator("#metadataResultCard")
    expect(metadata_card).to_be_visible(timeout=10000)
    
    metadata_desc = page.locator("#metadataDescription")
    expect(metadata_desc).not_to_be_empty()


def test_final_results_display(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that all final results are displayed correctly after completion.
    """
    control.reset()
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for completion
    upload_result = page.locator("#uploadResult")
    expect(upload_result).to_contain_text("Success!", timeout=15000)
    
    # Verify all result cards are visible
    expect(page.locator("#aiResultCard")).to_be_visible()
    expect(page.locator("#fractalResultCard")).to_be_visible()
    expect(page.locator("#histogramCard")).to_be_visible()
    expect(page.locator("#hogContainer")).to_be_visible()
    expect(page.locator("#metadataResultCard")).to_be_visible()
    expect(page.locator("#debugContainer")).to_be_visible()
    
    # Verify all steps show completion checkmarks
    completed_icons = page.locator('.step-icon.done')
    expect(completed_icons).to_have_count(8)
    
    # Verify AI probability is displayed
    ai_score = page.locator("#aiScoreDisplay")
    expect(ai_score).to_contain_text("% AI Probability")
    
    # Verify Fractal dimension is displayed
    fd_display = page.locator("#fdDefaultDisplay")
    expect(fd_display).not_to_have_text("-")
    expect(fd_display).not_to_have_text("Timed Out")
    
    # Verify debug output is present
    debug_output = page.locator("#debugOutput")
    expect(debug_output).not_to_be_empty()


def test_step_progression_sequence(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client):
    """
    Test that steps progress in the correct sequence with proper status indicators.
    """
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for step list to appear
    step_list = page.locator("#stepList")
    expect(step_list).to_be_visible(timeout=5000)
    
    # Track step status changes
    preprocessing_step = page.locator('.step-item:has-text("Preprocessing")')
    
    # Initially, preprocessing should be running or completed quickly
    # (Due to mocking, it completes very fast)
    
    # Wait for parallel analysis phase
    status_text = page.locator("#statusText")
    
    # We should eventually see completion
    expect(status_text).to_contain_text("Success:", timeout=15000)
    
    # Verify progress bar reached 100%
    progress_bar = page.locator("#progressBar")
    expect(progress_bar).to_have_text("100%")


def test_ui_elements_visibility_flow(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client):
    """
    Test the complete visibility flow of UI elements from upload to completion.
    """
    page.goto(live_server)
    
    # Initial state: result cards should be hidden
    expect(page.locator("#aiResultCard")).not_to_be_visible()
    expect(page.locator("#fractalResultCard")).not_to_be_visible()
    expect(page.locator("#histogramCard")).not_to_be_visible()
    expect(page.locator("#hogContainer")).not_to_be_visible()
    expect(page.locator("#metadataResultCard")).not_to_be_visible()
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Progress container should become visible
    progress_container = page.locator("#progressContainer")
    expect(progress_container).to_be_visible(timeout=5000)
    
    # Step list should become visible
    expect(page.locator("#stepList")).to_be_visible()
    
    # Result cards should progressively become visible
    expect(page.locator("#aiResultCard")).to_be_visible(timeout=10000)
    expect(page.locator("#fractalResultCard")).to_be_visible(timeout=10000)
    expect(page.locator("#histogramCard")).to_be_visible(timeout=10000)
    expect(page.locator("#hogContainer")).to_be_visible(timeout=10000)
    expect(page.locator("#metadataResultCard")).to_be_visible(timeout=10000)
    
    # Wait for completion
    expect(page.locator("#uploadResult")).to_contain_text("Success!", timeout=15000)
    
    # Debug container should be visible at the end
    expect(page.locator("#debugContainer")).to_be_visible()


def test_timeout_handling_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that timeout states are correctly displayed in the UI.

    This test mocks a step to timeout and verifies the UI shows the timeout icon.
    """
    control.reset()
    # Mock one of the analysis functions to timeout
    # STEP_TIMEOUT is patched to 2 in conftest.py
    control.delays["fractal"] = 4
    
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Verify status text shows timeout count
    status_text = page.locator("#statusText")
    expect(status_text).to_contain_text("Timed Out: 1", timeout=10000)
    expect(status_text).to_contain_text("(Timeout: 10s)")

    # Verify timeout icon appears for Fractal Analysis step
    fractal_step = page.locator('.step-item:has-text("Fractal Analysis")')
    timeout_icon = fractal_step.locator('.step-icon.timed-out')
    expect(timeout_icon).to_be_visible()
    
    # Verify timeout icon is a clock emoji
    expect(timeout_icon).to_have_text('🕒')
    
    # Verify Fractal card shows "Timed Out"
    fd_display = page.locator("#fdDefaultDisplay")
    expect(fd_display).to_have_text("Timed Out")


def test_multiple_timeouts_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that multiple timeout states are correctly displayed in the UI.
    """
    control.reset()
    # Mock multiple functions to timeout
    control.delays["fractal"] = 4
    control.delays["ai"] = 4
    
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for completion
    expect(page.locator("#uploadResult")).to_contain_text("Success!", timeout=20000)
    
    # Verify both timeout icons appear
    timeout_icons = page.locator('.step-icon.timed-out')
    expect(timeout_icons).to_have_count(2)
    
    # Verify status shows 2 timeouts
    status_text = page.locator("#statusText")
    expect(status_text).to_contain_text("Timed Out: 2")
    
    # Verify AI card shows "Timed Out"
    ai_score = page.locator("#aiScoreDisplay")
    expect(ai_score).to_have_text("Timed Out")
    
    # Verify Fractal card shows "Timed Out"
    fd_display = page.locator("#fdDefaultDisplay")
    expect(fd_display).to_have_text("Timed Out")


def test_error_handling_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that error states are correctly displayed in the UI.
    """
    control.reset()
    # Mock preprocessing to raise an error
    control.errors["prepare"] = ValueError("Simulated preprocessing error")
    
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    page.locator('button[type="submit"]').click()
    
    # Wait for error to appear
    upload_result = page.locator("#uploadResult")
    expect(upload_result).to_contain_text("Error:", timeout=10000)
    expect(upload_result).to_contain_text("Simulated preprocessing error")
    
    # Verify progress container is hidden after error
    progress_container = page.locator("#progressContainer")
    expect(progress_container).not_to_be_visible()


def test_invalid_file_upload_error(page: Page, live_server: str):
    """
    Test that uploading an invalid file type shows an appropriate error.
    """
    page.goto(live_server)
    
    # Try to upload a text file instead of an image
    text_content = b"This is not an image"
    
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.txt",
        "mimeType": "text/plain",
        "buffer": text_content
    })
    
    page.locator('button[type="submit"]').click()
    
    # The backend should reject this with a 400 error
    # The frontend should display an error message
    upload_result = page.locator("#uploadResult")
    expect(upload_result).to_contain_text("Error:", timeout=5000)

