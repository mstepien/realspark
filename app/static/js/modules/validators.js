/**
 * Data validation utilities for API responses
 */
export class DataValidator {
    /**
     * Validates task data structure from /progress endpoint
     * @param {Object} taskData - Task data from API
     * @returns {Object} { valid: boolean, errors: string[] }
     */
    static validateTaskData(taskData) {
        if (!taskData) {
            return { valid: false, errors: ['No task data provided'] };
        }

        const errors = [];

        // Validate progress
        if (typeof taskData.progress !== 'number') {
            errors.push('Invalid progress: must be a number');
        } else if (taskData.progress < 0 || taskData.progress > 100) {
            errors.push('Invalid progress: must be between 0 and 100');
        }

        // Validate steps
        if (!Array.isArray(taskData.steps)) {
            errors.push('Invalid steps: must be an array');
        }

        // Validate status
        if (typeof taskData.status !== 'string') {
            errors.push('Invalid status: must be a string');
        }

        return { valid: errors.length === 0, errors };
    }

    /**
     * Validates partial results structure
     * @param {Object} partialResults - Partial results from task data
     * @returns {Object} { valid: boolean, errors: string[] }
     */
    static validatePartialResults(partialResults) {
        // Null/undefined is valid (no partial results yet)
        if (!partialResults) {
            return { valid: true, errors: [] };
        }

        const errors = [];

        // Validate histogram data if present
        if (partialResults.histogram_r !== undefined) {
            if (!Array.isArray(partialResults.histogram_r)) {
                errors.push('histogram_r must be an array');
            } else if (partialResults.histogram_r.length !== 256) {
                errors.push('histogram_r must have exactly 256 bins');
            }
        }

        if (partialResults.histogram_g !== undefined) {
            if (!Array.isArray(partialResults.histogram_g)) {
                errors.push('histogram_g must be an array');
            } else if (partialResults.histogram_g.length !== 256) {
                errors.push('histogram_g must have exactly 256 bins');
            }
        }

        if (partialResults.histogram_b !== undefined) {
            if (!Array.isArray(partialResults.histogram_b)) {
                errors.push('histogram_b must be an array');
            } else if (partialResults.histogram_b.length !== 256) {
                errors.push('histogram_b must have exactly 256 bins');
            }
        }

        // Validate AI probability if present
        if (partialResults.ai_probability !== undefined) {
            const prob = partialResults.ai_probability;
            if (typeof prob !== 'number') {
                errors.push('ai_probability must be a number');
            } else if (isNaN(prob) || !isFinite(prob)) {
                errors.push('ai_probability must be a finite number');
            } else if (prob < 0 || prob > 1) {
                errors.push('ai_probability must be between 0 and 1');
            }
        }

        // Validate fractal dimension if present
        if (partialResults.fd_default !== undefined) {
            const fd = partialResults.fd_default;
            if (typeof fd !== 'number') {
                errors.push('fd_default must be a number');
            } else if (isNaN(fd) || !isFinite(fd)) {
                errors.push('fd_default must be a finite number');
            }
        }

        return { valid: errors.length === 0, errors };
    }
}
