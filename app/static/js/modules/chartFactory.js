/**
 * Chart.js factory utilities
 */
export class ChartFactory {
    /**
     * Creates a histogram chart
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Object} histogramData - { histogram_r, histogram_g, histogram_b }
     * @returns {Chart} Chart.js instance
     * @throws {Error} If data is invalid
     */
    static createHistogramChart(ctx, histogramData) {
        const { histogram_r, histogram_g, histogram_b } = histogramData;

        // Validate data
        if (!histogram_r || !histogram_g || !histogram_b) {
            throw new Error('Missing histogram data channels');
        }

        if (!Array.isArray(histogram_r) || !Array.isArray(histogram_g) || !Array.isArray(histogram_b)) {
            throw new Error('Histogram data must be arrays');
        }

        if (histogram_r.length !== 256 || histogram_g.length !== 256 || histogram_b.length !== 256) {
            throw new Error('Histogram data must have exactly 256 bins per channel');
        }

        // Create x-axis labels (0-255)
        const labels = Array.from({ length: 256 }, (_, i) => i);

        return new Chart(ctx, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Red',
                        data: histogram_r,
                        borderColor: 'rgba(255, 99, 132, 0.8)',
                        backgroundColor: 'rgba(255, 99, 132, 0.1)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: true
                    },
                    {
                        label: 'Green',
                        data: histogram_g,
                        borderColor: 'rgba(75, 192, 192, 0.8)',
                        backgroundColor: 'rgba(75, 192, 192, 0.1)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: true
                    },
                    {
                        label: 'Blue',
                        data: histogram_b,
                        borderColor: 'rgba(54, 162, 235, 0.8)',
                        backgroundColor: 'rgba(54, 162, 235, 0.1)',
                        borderWidth: 1,
                        pointRadius: 0,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Pixel Intensity (0-255)'
                        },
                        ticks: {
                            maxTicksLimit: 10
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Frequency'
                        },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    /**
     * Creates aggregate statistics bar chart
     * @param {CanvasRenderingContext2D} ctx - Canvas context
     * @param {Object} statsData - Statistics data from API
     * @returns {Chart} Chart.js instance
     */
    static createStatsChart(ctx, statsData) {
        const { avg_width, avg_height, avg_color, total_images } = statsData;

        return new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Avg Width', 'Avg Height', 'Avg Red', 'Avg Green', 'Avg Blue'],
                datasets: [{
                    label: `Aggregate Statistics (Total Images: ${total_images})`,
                    data: [avg_width, avg_height, avg_color[0], avg_color[1], avg_color[2]],
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(54, 162, 235, 0.2)',
                        'rgba(255, 99, 132, 0.2)',
                        'rgba(75, 192, 192, 0.2)',
                        'rgba(153, 102, 255, 0.2)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 99, 132, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}
