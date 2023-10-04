document.addEventListener("DOMContentLoaded", function () {
  vyHistogramChart = new Chart(document.getElementById("vyHistogramChart"), {
    type: "bar",
    data: {
      labels: [], // We'll populate this from the server data
      datasets: [
        {
          label: "y-component of velocity",
          data: [], // We'll populate this from the server data
          backgroundColor: "rgba(255, 99, 132, 0.6)",
          borderColor: "rgba(255, 99, 132, 1)",
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
          min: 0,
          max: 30,
          title: {
            display: true,
            text: "Count",
          },
        },
      },
    },
  });
});