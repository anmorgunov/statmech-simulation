import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from modules.graph import Graph
import constants


class FigureMaker:
    def __init__(self):
        pass

    def create_fractions_scatter_plot(self, left_fractions, right_fractions):
        fig = go.Figure()
        graph = Graph()
        fig.add_trace(
            go.Scatter(
                x=list(range(len(right_fractions))),
                y=right_fractions,
                mode="lines",
                name="Right Fraction",
                line_color="#4361ee",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=list(range(len(left_fractions))),
                y=left_fractions,
                mode="lines",
                name="Left Fraction",
                line_color="#b5179e",
            )
        )
        fig.add_shape(
            go.layout.Shape(
                type="line",
                x0=0,
                x1=len(left_fractions)
                - 1,  # Assuming left_fractions and right_fractions are of the same length
                y0=50,
                y1=50,
                line=dict(color="Grey", width=2, dash="dash"),
            )
        )
        graph.update_parameters(
            dict(
                title="<b>Fractions of Oxygen Atoms in Left and Right Compartments</b>",
                xaxis_title="Timestep",
                yaxis_title="Fraction",
            )
        )
        graph.style_figure(fig)
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="compartment_fractions",
            html=True,
            jpg=True,
            scale=4.0,
        )

    def create_equipartition_scatter_plot(self, element_to_temp):
        fig = go.Figure()
        graph = Graph()
        elemToColor = {"C": "#2b2d42", "O": "#ef233c"}
        for element, temp in element_to_temp.items():
            fig.add_trace(
                go.Scatter(
                    x=list(range(len(temp))),
                    y=temp,
                    mode="lines",
                    name=f"{element} Temperature",
                    line_color=elemToColor[element],
                )
            )
        graph.update_parameters(
            dict(
                title="<b>Equipartition Temperature</b>",
                xaxis_title="Timestep",
                yaxis_title="Temperature (K)",
            )
        )
        graph.style_figure(fig)
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="equipartition_temperature",
            html=True,
            jpg=True,
            scale=4.0,
        )
