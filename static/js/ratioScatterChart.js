document.addEventListener("DOMContentLoaded", function () {
  ratioScatterChart = new Chart(document.getElementById("ratioScatterChart"), {
    type: "scatter",
    data: {
      datasets: [
        {
          label: "Left Fractions",
          data: [], // This will be populated later
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          pointRadius: 1,
        },
        {
          label: "Right Fractions",
          data: [], // This will be populated later
          borderColor: "rgba(54, 162, 235, 1)",
          backgroundColor: "rgba(54, 162, 235, 0.2)",
          pointRadius: 1,
        },
      ],
    },
    options: {
      scales: {
        x: {
          type: "linear",
          position: "bottom",
        },
      },
      animation: {
        duration: 0, // general animation time
      },
      hover: {
        animationDuration: 0, // duration of animations when hovering an item
      },
    },
  });
});
