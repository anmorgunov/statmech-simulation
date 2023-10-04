import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

class FigureMaker:
    def __init__(self):
        pass

    def _style_figure(self, figure):
        figure.update_layout(legend=dict(yanchor="top", xanchor="left", x=0.91, y=0.99), plot_bgcolor="white", paper_bgcolor="white")

    def _save_figure(self, figure, fname, html=False, jpg=False):
        if html:
            figure.write_html(os.path.join(os.getcwd(), "figures", "html", f"{fname}.html"), include_plotlyjs="cdn")
        if jpg:
            figure.write_image(os.path.join(os.getcwd(), "figures", "jpg", f"{fname}.jpg"), scale=3.0)


    def create_fractions_scatter_plot(self, left_fractions, right_fractions):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=list(range(len(left_fractions))),
                y=left_fractions,
                mode="lines",
                name="Left Fraction",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=list(range(len(right_fractions))),
                y=right_fractions,
                mode="lines",
                name="Right Fraction",
            )
        )
        fig.update_layout(
            title="Fraction of Oxygen Atoms in Left and Right Compartments",
            xaxis_title="Timestep",
            yaxis_title="Fraction",
        )
        self._style_figure(fig)
        self._save_figure(fig, "compartment_fractions", html=True, jpg=True)

