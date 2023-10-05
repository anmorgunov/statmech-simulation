document.addEventListener("DOMContentLoaded", function () {
  mbdistTempBarChart = new Chart(document.getElementById("mbdistTempBarChart"), {
    type: "bar",
    data: {
      labels: ["Carbon", "Oxygen"],
      datasets: [
        {
          label: "Maxwell-Boltzmann Temperature",
          data: [0, 0], // Initial data
          backgroundColor: ["rgba(0, 119, 182, 0.6)", "rgba(0, 119, 182, 0.6)"],
          borderColor: ["rgba(0, 119, 182, 1.0)", "rgba(0, 119, 182, 1.0)"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          // min: 250,
          // max: 350,
          ticks: {
            stepSize: 10, // Optional: This will ensure ticks at intervals of 10
          },
        },
      },
    },
  });

});
