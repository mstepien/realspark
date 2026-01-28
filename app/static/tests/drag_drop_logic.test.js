import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import fs from 'fs';
import path from 'path';

// Helper to extract the app function from index.html
function getAppFunction() {
    const htmlPath = path.resolve(process.cwd(), 'app/templates/index.html');
    const html = fs.readFileSync(htmlPath, 'utf8');
    const startMarker = 'function app() {';
    const startIndex = html.indexOf(startMarker);
    const endMarker = 'return {'; // Look for the return object start

    // This is a bit brittle, but avoids complex parsing
    // We basically want to extract the logic inside function app()
    // A better way is to extract until the matching closing brace, 
    // but for a test we can just extract the whole thing and eval it.

    const scriptStart = html.indexOf('<script>', html.indexOf('<!-- Metadata Card (Moved) -->'));
    const scriptEnd = html.lastIndexOf('</script>');
    const scriptContent = html.substring(scriptStart + 8, scriptEnd);

    return scriptContent;
}

describe('Drag and Drop Logic', () => {
    let appScope;

    beforeEach(() => {
        // Mock globals
        global.fetch = jest.fn();
        global.URL = {
            createObjectURL: jest.fn(() => 'blob:mock-url'),
            revokeObjectURL: jest.fn()
        };
        global.localStorage = {
            getItem: jest.fn(),
            setItem: jest.fn()
        };
        global.Chart = jest.fn().mockImplementation(() => ({
            destroy: jest.fn(),
            update: jest.fn(),
            data: { datasets: [{ data: [] }] },
            options: { scales: { x: { ticks: {}, grid: {} }, y: { ticks: {}, grid: {} } }, plugins: { legend: { labels: {} } } }
        }));
        global.Chart.defaults = { color: '', borderColor: '' };
        global.getComputedStyle = jest.fn(() => ({
            getPropertyValue: jest.fn(() => '#000')
        }));
        global.document = {
            documentElement: {}
        };

        // Extract and eval the app function
        const script = getAppFunction();
        // We wrap it to return the app object
        const factory = new Function(script + '; return app();');
        appScope = factory();
    });

    test('isDragging is initially false', () => {
        expect(appScope.isDragging).toBe(false);
    });

    test('handleDrop sets isDragging to false and processes the file', () => {
        const mockFile = new File([''], 'test.png', { type: 'image/png' });
        const mockEvent = {
            dataTransfer: {
                files: [mockFile]
            }
        };

        // Spy on processFile (it's internal to the return object)
        const processFileSpy = jest.spyOn(appScope, 'processFile');
        const startUploadSpy = jest.spyOn(appScope, 'startUpload').mockImplementation(() => { });

        appScope.handleDrop(mockEvent);

        expect(appScope.isDragging).toBe(false);
        expect(processFileSpy).toHaveBeenCalledWith(mockFile);
        expect(appScope.previewUrl).toBe('blob:mock-url');
        expect(startUploadSpy).toHaveBeenCalled();
    });

    test('processFile handles null file gracefully', () => {
        const startUploadSpy = jest.spyOn(appScope, 'startUpload');
        appScope.processFile(null);
        expect(startUploadSpy).not.toHaveBeenCalled();
    });

    test('isDragging can be toggled', () => {
        appScope.isDragging = true;
        expect(appScope.isDragging).toBe(true);
        appScope.isDragging = false;
        expect(appScope.isDragging).toBe(false);
    });
});
