import { describe, test, expect } from '@jest/globals';
import { DataValidator } from '../js/modules/validators.js';

describe('DataValidator', () => {
    describe('validateTaskData', () => {
        test('accepts valid task data', () => {
            const validData = {
                progress: 50,
                steps: ['Step 1', 'Step 2'],
                status: 'Processing...'
            };

            const result = DataValidator.validateTaskData(validData);
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });

        test('rejects null/undefined data', () => {
            expect(DataValidator.validateTaskData(null).valid).toBe(false);
            expect(DataValidator.validateTaskData(undefined).valid).toBe(false);
        });

        test('rejects invalid progress type', () => {
            const data = { progress: '50', steps: [], status: 'test' };
            const result = DataValidator.validateTaskData(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('Invalid progress: must be a number');
        });

        test('rejects out-of-range progress', () => {
            const data1 = { progress: -10, steps: [], status: 'test' };
            const data2 = { progress: 150, steps: [], status: 'test' };

            expect(DataValidator.validateTaskData(data1).valid).toBe(false);
            expect(DataValidator.validateTaskData(data2).valid).toBe(false);
        });

        test('rejects invalid steps type', () => {
            const data = { progress: 50, steps: 'not an array', status: 'test' };
            const result = DataValidator.validateTaskData(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('Invalid steps: must be an array');
        });

        test('rejects invalid status type', () => {
            const data = { progress: 50, steps: [], status: 123 };
            const result = DataValidator.validateTaskData(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('Invalid status: must be a string');
        });
    });

    describe('validatePartialResults', () => {
        test('accepts null/undefined (no partial results yet)', () => {
            expect(DataValidator.validatePartialResults(null).valid).toBe(true);
            expect(DataValidator.validatePartialResults(undefined).valid).toBe(true);
        });

        test('accepts valid histogram data', () => {
            const data = {
                histogram_r: new Array(256).fill(0),
                histogram_g: new Array(256).fill(0),
                histogram_b: new Array(256).fill(0)
            };

            const result = DataValidator.validatePartialResults(data);
            expect(result.valid).toBe(true);
            expect(result.errors).toHaveLength(0);
        });

        test('rejects histogram with wrong length', () => {
            const data = {
                histogram_r: new Array(100).fill(0)
            };

            const result = DataValidator.validatePartialResults(data);
            expect(result.valid).toBe(false);
            expect(result.errors).toContain('histogram_r must have exactly 256 bins');
        });

        test('rejects non-array histogram', () => {
            const data = {
                histogram_r: 'not an array'
            };

            const result = DataValidator.validatePartialResults(data);
            expect(result.valid).toBe(false);
            expect(result.errors).toContain('histogram_r must be an array');
        });

        test('accepts valid AI probability', () => {
            const data = { ai_probability: 0.75 };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(true);
        });

        test('rejects out-of-range AI probability', () => {
            const data1 = { ai_probability: -0.1 };
            const data2 = { ai_probability: 1.5 };

            expect(DataValidator.validatePartialResults(data1).valid).toBe(false);
            expect(DataValidator.validatePartialResults(data2).valid).toBe(false);
        });

        test('rejects NaN AI probability', () => {
            const data = { ai_probability: NaN };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('ai_probability must be a finite number');
        });

        test('rejects Infinity AI probability', () => {
            const data = { ai_probability: Infinity };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(false);
        });

        test('accepts valid fractal dimension', () => {
            const data = { fd_default: 2.5 };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(true);
        });

        test('rejects invalid fractal dimension type', () => {
            const data = { fd_default: 'not a number' };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('fd_default must be a number');
        });

        test('accepts valid HOG image URL', () => {
            const data = { hog_image_url: '/tmp/hog_123.png' };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(true);
        });

        test('rejects invalid HOG image URL type', () => {
            const data = { hog_image_url: 123 };
            const result = DataValidator.validatePartialResults(data);

            expect(result.valid).toBe(false);
            expect(result.errors).toContain('hog_image_url must be a string');
        });
    });
});
