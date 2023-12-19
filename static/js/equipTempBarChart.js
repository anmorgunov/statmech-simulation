document.addEventListener("DOMContentLoaded", function () {
  equipTempBarChart = new Chart(document.getElementById("equipTempBarChart"), {
    type: "bar",
    data: {
      labels: ["Label A", "Label B"],
      datasets: [
        {
          label: "Equipartition Temperature",
          data: [0, 0], // Initial data
          backgroundColor: ["rgba(251, 176, 45, 0.6)", "rgba(251, 176, 45, 0.6)"],
          borderColor: ["rgba(251, 176, 45, 1.0)", "rgba(251, 176, 45, 1.0)"],
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
