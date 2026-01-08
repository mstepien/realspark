import { describe, test, expect, beforeEach, jest } from '@jest/globals';
import { ApiClient } from '../js/modules/api.js';

describe('ApiClient', () => {
    let api;
    const baseUrl = 'http://test-api.com';

    beforeEach(() => {
        api = new ApiClient(baseUrl);
        global.fetch = jest.fn();
    });

    describe('uploadImage', () => {
        test('successfully uploads image', async () => {
            const mockResponse = { task_id: '123' };
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });

            const formData = new FormData();
            const result = await api.uploadImage(formData);

            expect(global.fetch).toHaveBeenCalledWith(`${baseUrl}/upload`, {
                method: 'POST',
                body: formData
            });
            expect(result).toEqual(mockResponse);
        });

        test('throws error on failed upload', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: false,
                statusText: 'Internal Server Error'
            });

            await expect(api.uploadImage(new FormData()))
                .rejects.toThrow('Upload failed: Internal Server Error');
        });
    });

    describe('getProgress', () => {
        test('returns task data on success', async () => {
            const mockResponse = { progress: 50 };
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });

            const result = await api.getProgress('123');

            expect(global.fetch).toHaveBeenCalledWith(`${baseUrl}/progress/123`);
            expect(result).toEqual(mockResponse);
        });

        test('returns null if task not found (404)', async () => {
            global.fetch.mockResolvedValueOnce({ ok: false });

            const result = await api.getProgress('invalid');
            expect(result).toBeNull();
        });

        test('returns null and logs error on fetch failure', async () => {
            const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
            global.fetch.mockRejectedValueOnce(new Error('Network failure'));

            const result = await api.getProgress('123');
            expect(result).toBeNull();
            expect(consoleSpy).toHaveBeenCalled();
            consoleSpy.mockRestore();
        });
    });

    describe('getStats', () => {
        test('returns stats on success', async () => {
            const mockResponse = { total_images: 10 };
            global.fetch.mockResolvedValueOnce({
                ok: true,
                json: () => Promise.resolve(mockResponse)
            });

            const result = await api.getStats();

            expect(global.fetch).toHaveBeenCalledWith(`${baseUrl}/stats`);
            expect(result).toEqual(mockResponse);
        });

        test('throws error on failed fetch', async () => {
            global.fetch.mockResolvedValueOnce({
                ok: false,
                statusText: 'Forbidden'
            });

            await expect(api.getStats()).rejects.toThrow('Failed to fetch stats: Forbidden');
        });
    });
});
