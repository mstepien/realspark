/**
 * Progress rendering utilities (pure functions)
 */
export class ProgressRenderer {
    /**
     * Updates progress bar element
     * @param {HTMLElement} progressElement - Progress bar element
     * @param {number} percent - Progress percentage (0-100)
     */
    static updateProgressBar(progressElement, percent) {
        if (!progressElement) {
            console.warn('Progress element not found');
            return;
        }

        // Clamp percent to valid range
        const safePercent = Math.max(0, Math.min(100, percent || 0));
        progressElement.style.width = `${safePercent}%`;
        progressElement.textContent = `${safePercent}%`;
    }

    /**
     * Renders step list data structure (pure function)
     * @param {string[]} steps - Array of step names
     * @param {string} currentStep - Currently executing step
     * @param {string[]} completedSteps - Array of completed step names
     * @returns {Array} Array of step objects with status and icon
     */
    static renderStepList(steps, currentStep, completedSteps = []) {
        if (!Array.isArray(steps)) {
            return [];
        }

        return steps.map(step => ({
            name: step,
            status: this.getStepStatus(step, currentStep, completedSteps),
            icon: this.getStepIcon(step, currentStep, completedSteps),
            isBold: currentStep === step
        }));
    }

    /**
     * Determines step status
     * @param {string} step - Step name
     * @param {string} current - Current step
     * @param {string[]} completed - Completed steps
     * @returns {string} 'done' | 'active' | 'pending'
     */
    static getStepStatus(step, current, completed = []) {
        if (completed.includes(step)) return 'done';
        if (current === step) return 'active';
        return 'pending';
    }

    /**
     * Gets icon for step status
     * @param {string} step - Step name
     * @param {string} current - Current step
     * @param {string[]} completed - Completed steps
     * @returns {string} Icon character
     */
    static getStepIcon(step, current, completed = []) {
        if (completed.includes(step)) return '✓';
        if (current === step) return '➤';
        return '•';
    }
}
