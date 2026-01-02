/**
 * Results rendering utilities for partial results display
 */
export class ResultsRenderer {
    /**
     * Renders AI score data
     * @param {number} aiProbability - AI probability (0-1)
     * @returns {Object|null} { percent, className, description } or null
     */
    static renderAIScore(aiProbability) {
        if (aiProbability === undefined || aiProbability === null) {
            return null;
        }

        // Handle invalid numbers
        if (typeof aiProbability !== 'number' || isNaN(aiProbability)) {
            console.warn('Invalid AI probability:', aiProbability);
            return null;
        }

        const percent = (aiProbability * 100).toFixed(1);
        let className, description;

        if (aiProbability < 0.3) {
            className = 'ai-score-safe';
            description = 'Likely Human-Created / Authentic Art';
        } else if (aiProbability < 0.7) {
            className = 'ai-score-warning';
            description = 'Uncertain / Mixed Indicators';
        } else {
            className = 'ai-score-danger';
            description = 'High Likelihood of AI Generation';
        }

        return { percent, className, description };
    }

    /**
     * Determines if histogram should be rendered
     * @param {Object} partialResults - Partial results object
     * @param {boolean} alreadyRendered - Whether histogram was already rendered
     * @returns {boolean} True if should render
     */
    static shouldRenderHistogram(partialResults, alreadyRendered) {
        if (alreadyRendered) return false;
        if (!partialResults) return false;

        return !!(
            partialResults.histogram_r &&
            partialResults.histogram_g &&
            partialResults.histogram_b &&
            Array.isArray(partialResults.histogram_r) &&
            Array.isArray(partialResults.histogram_g) &&
            Array.isArray(partialResults.histogram_b)
        );
    }

    /**
     * Formats fractal dimension for display
     * @param {number} fdValue - Fractal dimension value
     * @param {number} decimals - Number of decimal places (default: 4)
     * @returns {string|null} Formatted string or null
     */
    static formatFractalDimension(fdValue, decimals = 4) {
        if (fdValue === undefined || fdValue === null) {
            return null;
        }

        if (typeof fdValue !== 'number' || isNaN(fdValue)) {
            console.warn('Invalid fractal dimension:', fdValue);
            return null;
        }

        return fdValue.toFixed(decimals);
    }

    /**
     * Checks if HOG image URL should be updated
     * @param {string} currentSrc - Current image src
     * @param {string} newUrl - New URL from partial results
     * @returns {boolean} True if should update
     */
    static shouldUpdateHOGImage(currentSrc, newUrl) {
        if (!newUrl) return false;
        if (!currentSrc) return true;
        return !currentSrc.endsWith(newUrl);
    }
}
