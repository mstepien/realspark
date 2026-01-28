import { describe, test, expect } from '@jest/globals';
import { ResultsRenderer } from '../js/modules/resultsRenderer.js';

describe('ResultsRenderer', () => {
    describe('renderAIScore', () => {
        test('classifies low probability as safe', () => {
            const result = ResultsRenderer.renderAIScore(0.2);

            expect(result).not.toBeNull();
            expect(result.className).toBe('ai-score-safe');
            expect(result.description).toContain('Human-Created');
            expect(result.percent).toBe('20.0');
        });

        test('classifies medium probability as warning', () => {
            const result = ResultsRenderer.renderAIScore(0.5);

            expect(result.className).toBe('ai-score-warning');
            expect(result.description).toContain('Uncertain');
        });

        test('classifies high probability as danger', () => {
            const result = ResultsRenderer.renderAIScore(0.8);

            expect(result.className).toBe('ai-score-danger');
            expect(result.description).toContain('AI Generation');
        });

        test('handles boundary values correctly', () => {
            expect(ResultsRenderer.renderAIScore(0.3).className).toBe('ai-score-warning');
            expect(ResultsRenderer.renderAIScore(0.29).className).toBe('ai-score-safe');
            expect(ResultsRenderer.renderAIScore(0.7).className).toBe('ai-score-danger');
            expect(ResultsRenderer.renderAIScore(0.69).className).toBe('ai-score-warning');
        });

        test('handles null probability', () => {
            expect(ResultsRenderer.renderAIScore(null)).toBeNull();
        });

        test('handles undefined probability', () => {
            expect(ResultsRenderer.renderAIScore(undefined)).toBeNull();
        });

        test('handles NaN probability', () => {
            expect(ResultsRenderer.renderAIScore(NaN)).toBeNull();
        });

        test('formats percentage correctly', () => {
            expect(ResultsRenderer.renderAIScore(0.123).percent).toBe('12.3');
            expect(ResultsRenderer.renderAIScore(0.999).percent).toBe('99.9');
            expect(ResultsRenderer.renderAIScore(0).percent).toBe('0.0');
            expect(ResultsRenderer.renderAIScore(1).percent).toBe('100.0');
        });
    });

    describe('shouldRenderHistogram', () => {
        test('returns false if already rendered', () => {
            const data = {
                histogram_r: [1, 2, 3],
                histogram_g: [1, 2, 3],
                histogram_b: [1, 2, 3]
            };

            expect(ResultsRenderer.shouldRenderHistogram(data, true)).toBe(false);
        });

        test('returns false if partial results null', () => {
            expect(ResultsRenderer.shouldRenderHistogram(null, false)).toBe(false);
        });

        test('returns false if data incomplete', () => {
            const data1 = { histogram_r: [1] };
            const data2 = { histogram_r: [1], histogram_g: [1] };

            expect(ResultsRenderer.shouldRenderHistogram(data1, false)).toBe(false);
            expect(ResultsRenderer.shouldRenderHistogram(data2, false)).toBe(false);
        });

        test('returns false if data not arrays', () => {
            const data = {
                histogram_r: 'not array',
                histogram_g: [1],
                histogram_b: [1]
            };

            expect(ResultsRenderer.shouldRenderHistogram(data, false)).toBe(false);
        });

        test('returns true if data complete and not rendered', () => {
            const data = {
                histogram_r: [1, 2, 3],
                histogram_g: [4, 5, 6],
                histogram_b: [7, 8, 9]
            };

            expect(ResultsRenderer.shouldRenderHistogram(data, false)).toBe(true);
        });
    });

    describe('formatFractalDimension', () => {
        test('formats with default 4 decimals', () => {
            expect(ResultsRenderer.formatFractalDimension(2.123456)).toBe('2.1235');
        });

        test('formats with custom decimals', () => {
            expect(ResultsRenderer.formatFractalDimension(2.123456, 2)).toBe('2.12');
            expect(ResultsRenderer.formatFractalDimension(2.123456, 6)).toBe('2.123456');
        });

        test('handles null/undefined', () => {
            expect(ResultsRenderer.formatFractalDimension(null)).toBeNull();
            expect(ResultsRenderer.formatFractalDimension(undefined)).toBeNull();
        });

        test('handles NaN', () => {
            expect(ResultsRenderer.formatFractalDimension(NaN)).toBeNull();
        });

        test('handles invalid type', () => {
            expect(ResultsRenderer.formatFractalDimension('not a number')).toBeNull();
        });
    });
});
