document.addEventListener("DOMContentLoaded", function () {
  vabsHistogramChart = new Chart(
    document.getElementById("vabsHistogramChart"),
    {
      type: "bar",
      data: {
        labels: [], // We'll populate this from the server data
        datasets: [
          {
            label: "Speed",
            data: [], // We'll populate this from the server data
            backgroundColor: "rgba(72, 202, 228, 0.6)",
            borderColor: "rgba(72, 202, 228, 1)",
            borderWidth: 1,
          },
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
            // max: 0.5,
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
