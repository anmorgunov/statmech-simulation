document.addEventListener("DOMContentLoaded", function () {
  vangleHistogramChart = new Chart(
    document.getElementById("vangleHistogramChart"),
    {
      type: "bar",
      data: {
        labels: [], // We'll populate this from the server data
        datasets: [
          {
            label: "Frequency",
            data: [], // We'll populate this from the server data
            backgroundColor: "rgba(0, 204, 102, 0.6)",
            borderColor: "rgba(0, 204, 102, 1.0)",
            // backgroundColor: "rgba(255, 77, 109, 0.6)",
            // borderColor: "rgba(255, 77, 109, 1)",
            borderWidth: 1,
          },
        ],
      },
      options: {
        scales: {
          x: {
            title: {
              display: true,
              text: "Angle Range",
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
