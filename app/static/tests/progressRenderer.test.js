import { describe, test, expect, beforeEach } from '@jest/globals';
import { ProgressRenderer } from '../js/modules/progressRenderer.js';

describe('ProgressRenderer', () => {
    describe('renderStepList', () => {
        test('returns empty array for null steps', () => {
            expect(ProgressRenderer.renderStepList(null, 'current', [])).toEqual([]);
        });

        test('returns empty array for undefined steps', () => {
            expect(ProgressRenderer.renderStepList(undefined, 'current', [])).toEqual([]);
        });

        test('returns empty array for non-array steps', () => {
            expect(ProgressRenderer.renderStepList('not array', 'current', [])).toEqual([]);
        });

        test('renders steps with correct status', () => {
            const steps = ['Step 1', 'Step 2', 'Step 3'];
            const result = ProgressRenderer.renderStepList(steps, 'Step 2', ['Step 1']);

            expect(result).toHaveLength(3);
            expect(result[0].status).toBe('done');
            expect(result[1].status).toBe('active');
            expect(result[2].status).toBe('pending');
        });

        test('renders steps with correct icons', () => {
            const steps = ['Step 1', 'Step 2', 'Step 3'];
            const result = ProgressRenderer.renderStepList(steps, 'Step 2', ['Step 1']);

            expect(result[0].icon).toBe('✓');
            expect(result[1].icon).toBe('➤');
            expect(result[2].icon).toBe('•');
        });

        test('marks current step as bold', () => {
            const steps = ['Step 1', 'Step 2'];
            const result = ProgressRenderer.renderStepList(steps, 'Step 2', []);

            expect(result[0].isBold).toBe(false);
            expect(result[1].isBold).toBe(true);
        });

        test('handles empty completed steps array', () => {
            const steps = ['Step 1'];
            const result = ProgressRenderer.renderStepList(steps, 'Step 1', []);

            expect(result[0].status).toBe('active');
        });

        test('handles undefined completed steps', () => {
            const steps = ['Step 1'];
            const result = ProgressRenderer.renderStepList(steps, 'Step 1');

            expect(result[0].status).toBe('active');
        });
    });

    describe('getStepStatus', () => {
        test('returns done for completed step', () => {
            expect(ProgressRenderer.getStepStatus('Step 1', 'Step 2', ['Step 1'])).toBe('done');
        });

        test('returns active for current step', () => {
            expect(ProgressRenderer.getStepStatus('Step 2', 'Step 2', ['Step 1'])).toBe('active');
        });

        test('returns pending for future step', () => {
            expect(ProgressRenderer.getStepStatus('Step 3', 'Step 2', ['Step 1'])).toBe('pending');
        });

        test('handles undefined completed steps', () => {
            expect(ProgressRenderer.getStepStatus('Step 1', 'Step 2')).toBe('pending');
        });
    });

    describe('getStepIcon', () => {
        test('returns checkmark for completed step', () => {
            expect(ProgressRenderer.getStepIcon('Step 1', 'Step 2', ['Step 1'])).toBe('✓');
        });

        test('returns arrow for current step', () => {
            expect(ProgressRenderer.getStepIcon('Step 2', 'Step 2', ['Step 1'])).toBe('➤');
        });

        test('returns dot for pending step', () => {
            expect(ProgressRenderer.getStepIcon('Step 3', 'Step 2', ['Step 1'])).toBe('•');
        });
    });

    describe('updateProgressBar', () => {
        let mockElement;

        beforeEach(() => {
            mockElement = {
                style: {},
                textContent: ''
            };
        });

        test('updates element with valid percent', () => {
            ProgressRenderer.updateProgressBar(mockElement, 50);

            expect(mockElement.style.width).toBe('50%');
            expect(mockElement.textContent).toBe('50%');
        });

        test('clamps negative percent to 0', () => {
            ProgressRenderer.updateProgressBar(mockElement, -10);

            expect(mockElement.style.width).toBe('0%');
            expect(mockElement.textContent).toBe('0%');
        });

        test('clamps percent over 100', () => {
            ProgressRenderer.updateProgressBar(mockElement, 150);

            expect(mockElement.style.width).toBe('100%');
            expect(mockElement.textContent).toBe('100%');
        });

        test('handles null percent', () => {
            ProgressRenderer.updateProgressBar(mockElement, null);

            expect(mockElement.style.width).toBe('0%');
        });

        test('handles undefined percent', () => {
            ProgressRenderer.updateProgressBar(mockElement, undefined);

            expect(mockElement.style.width).toBe('0%');
        });

        test('handles null element gracefully', () => {
            // Should not throw
            expect(() => {
                ProgressRenderer.updateProgressBar(null, 50);
            }).not.toThrow();
        });
    });
});
