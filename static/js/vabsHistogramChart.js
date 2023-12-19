document.addEventListener("DOMContentLoaded", function () {
  vabsHistogramChart = new Chart(
    document.getElementById("vabsHistogramChart"),
    {
      type: "bar",
      data: {
        labels: [], // We'll populate this from the server data
        datasets: [
          {
            label: "Frequency 1",
            data: [], // Populate with data for the first dataset
            backgroundColor: "rgba(72, 202, 228, 0.6)", // Color for the first dataset
            borderColor: "rgba(72, 202, 228, 1)",
            borderWidth: 1,
            // categoryPercentage: 1.0,
            // barPercentage: 1.0
          },
          {
            label: "Frequency 2",
            data: [], // Populate with data for the second dataset
            backgroundColor: "rgba(255, 99, 132, 0.6)", // Different color for the second dataset
            borderColor: "rgba(255, 99, 132, 1)",
            borderWidth: 1,
            // categoryPercentage: 1.0,
            // barPercentage: 1.0
          }
        ],
      },
      options: {
        scales: {
          x: {
            title: {
              display: true,
              text: "Velocity Range",
            },
            ticks: {
              display: false,
            },
          },
          y: {
            beginAtZero: true,
            // min: 0,
            // max: 1.0,
            title: {
              display: true,
              text: "Count",
            },
          },
        },
      },
    }
  );
});
