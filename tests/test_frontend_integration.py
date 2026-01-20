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
    expect(page.locator("h1")).to_contain_text("RealSpark")
    
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
    
    # Wait for step list to become visible
    expect(step_list).to_be_visible(timeout=5000)
    
    # Verify all 10 steps are displayed
    expected_steps = [
        "Preprocessing",
        "Metadata Analysis",
        "Histogram Analysis",
        "HOG Analysis",
        "AI Classifier",
        "Fractal Dimension",
        "Art Medium Analysis",
        "Uploading to Storage",
        "Saving to Database",
        "AI Insight Summary"
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
    
    # Upload an image triggers automatically
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # We should see multiple steps with running indicators (bi-spin)
    running_icon_seen = False
    for _ in range(20):  # Check for 2 seconds
        running_icons = page.locator('.bi-spin')
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
    
    # Wait for and verify HOG visualization appears
    hog_container = page.locator("#hogContainer")
    expect(hog_container).to_be_visible(timeout=10000)
    
    # Wait for and verify AI Detection card appears
    ai_card = page.locator("#aiResultCard")
    expect(ai_card).to_be_visible(timeout=10000)
    expect(ai_card).to_contain_text("%")

    # Verify Summary card
    summary_card = page.locator("#summaryCard")
    expect(summary_card).to_be_visible(timeout=15000)
    expect(summary_card).to_contain_text("Summary")

    # Wait for and verify Art Medium card appears
    medium_card = page.locator("#artMediumResultCard")
    expect(medium_card).to_be_visible(timeout=15000)


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
    
    # Wait for completion
    upload_result = page.locator("#uploadResult")
    expect(upload_result).to_contain_text("Success!", timeout=15000)
    
    # Verify all result cards are visible
    expect(page.locator("#aiResultCard")).to_be_visible()
    expect(page.locator("#fractalResultCard")).to_be_visible()
    expect(page.locator("#artMediumResultCard")).to_be_visible()
    
    # Verify all steps show completion checkmarks (1 preprocessing + 6 cluster + 1 Storage + 1 DB + 1 Summary = 10)
    # Note: "Parallel Analysis & Upload" is a internal step state, but exactly 10 step items show checkmarks.
    completed_icons = page.locator('.bi-check-circle-fill')
    expect(completed_icons).to_have_count(10)


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
    
    # Wait for step list to appear
    step_list = page.locator("#stepList")
    expect(step_list).to_be_visible(timeout=5000)
    
    # Wait for completion
    status_text = page.locator("#statusText")
    expect(status_text).to_contain_text("Complete", timeout=15000)

    # Verify progress bar reached 100%
    progress_bar = page.locator("#progressBar")
    expect(progress_bar).to_have_attribute("aria-valuenow", "100")


def test_ui_elements_visibility_flow(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client):
    """
    Test the complete visibility flow of UI elements from upload to completion.
    """
    page.goto(live_server)
    
    # Upload an image
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Step list should become visible
    expect(page.locator("#stepList")).to_be_visible(timeout=5000)
    
    # Result cards should progressively become visible
    expect(page.locator("#aiResultCard")).to_be_visible(timeout=10000)
    
    # Wait for completion
    expect(page.locator("#uploadResult")).to_contain_text("Success!", timeout=15000)


def test_timeout_handling_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that timeout states are correctly displayed in the UI.
    """
    control.reset()
    control.delays["fractal"] = 4
    
    page.goto(live_server)
    
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Verify timeout icon appears for Fractal Dimension step
    fractal_step = page.locator('.step-item:has-text("Fractal Dimension")')
    timeout_icon = fractal_step.locator('.bi-exclamation-triangle-fill')
    expect(timeout_icon).to_be_visible(timeout=10000)
    
    # Verify Fractal card shows "Timed Out"
    expect(page.locator("#fractalResultCard")).to_contain_text("Timed Out")


def test_multiple_timeouts_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that multiple timeout states are correctly displayed in the UI.
    """
    control.reset()
    control.delays["fractal"] = 4
    control.delays["ai"] = 4
    
    page.goto(live_server)
    
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Wait for completion
    expect(page.locator("#uploadResult")).to_contain_text("Success!", timeout=20000)
    
    # Verify both timeout icons appear
    timeout_icons = page.locator('.bi-exclamation-triangle-fill')
    expect(timeout_icons).to_have_count(2)


def test_error_handling_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that error states are correctly displayed in the UI.
    """
    control.reset()
    msg = "Simulated preprocessing error"
    control.errors["prepare"] = ValueError(msg)
    
    page.goto(live_server)
    
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Wait for error to appear
    upload_result = page.locator("#uploadResult")
    # Use regular expression to be flexible with "Error: " prefix
    expect(upload_result).to_contain_text(re.compile(r".*Simulated preprocessing error"), timeout=10000)


def test_invalid_file_upload_error(page: Page, live_server: str):
    """
    Test that uploading an invalid file type shows an appropriate error.
    """
    page.goto(live_server)
    
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files({
        "name": "test.txt",
        "mimeType": "text/plain",
        "buffer": b"This is not an image"
    })
    
    upload_result = page.locator("#uploadResult")
    expect(upload_result).to_contain_text("Error", timeout=10000)


def test_task_abandonment_in_ui(page: Page, live_server: str, test_image_bytes: bytes, mock_db_connection, mock_storage_client, control):
    """
    Test that starting a new upload while one is in progress works correctly (cancels the previous one).
    """
    control.reset()
    # Ensure a delay so we have time to trigger the second upload
    control.delays["metadata"] = 2.0
    
    page.goto(live_server)
    
    file_input = page.locator('input[type="file"]')
    
    # 1. Start first upload
    file_input.set_input_files({
        "name": "first.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # Wait for it to start (step list starts appearing)
    expect(page.locator("#stepList")).to_be_visible(timeout=5000)
    
    # 2. Immediately start second upload
    file_input.set_input_files({
        "name": "second.png",
        "mimeType": "image/png",
        "buffer": test_image_bytes
    })
    
    # 3. Verify the new upload completes successfully
    # The UI resets when a new file is dropped, so it should just start the new pipeline.
    expect(page.locator("#uploadResult")).to_contain_text("Success!", timeout=15000)
