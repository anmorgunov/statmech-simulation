document.addEventListener("DOMContentLoaded", function () {
  ratioBarChart = new Chart(document.getElementById("ratioBarChart"), {
    type: "bar",
    data: {
      labels: ["Left", "Right"],
      datasets: [
        {
          label: "O fraction",
          data: [0, 0], // Initial data
          backgroundColor: ["rgba(60, 9, 108, 0.6)", "rgba(60, 9, 108, 0.6)"],
          borderColor: ["rgba(60, 9, 108, 1)", "rgba(60, 9, 108, 1)"],
          borderWidth: 1,
        },
      ],
    },
    options: {
      scales: {
        y: {
          beginAtZero: true,
          min: 0,
          max: 100,
          ticks: {
            stepSize: 10, // Optional: This will ensure ticks at intervals of 10
          },
        },
      },
    },
  });

});
