import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from modules.graph import Graph
from typing import Optional


class FigureMaker:
    def __init__(self):
        pass

    def create_fractions_scatter_plot(
        self, left_fractions, right_fractions, init_temp, fname: Optional[str] = None
    ):
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
                title=f"<b>Initial temperature: {init_temp:.2f} K</b>",
                xaxis_title="Timestep",
                yaxis_title="Fraction",
            )
        )
        graph.style_figure(fig)
        prefix = "" if fname is None else fname
        fig.update_layout(
            legend=dict(yanchor="top", y=0.2, xanchor="left", x=0.54, orientation="h")
        )
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="distribution/" + prefix + "_compartment_fractions",
            html=False,
            jpg=True,
            scale=4.0,
        )

    def create_equipartition_scatter_plot(
        self, element_to_temp, init_temp, fname: Optional[str] = None
    ):
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
                title=f"<b>Initial temperature: {init_temp:.2f} K</b>",
                xaxis_title="Timestep",
                yaxis_title="Temperature (K)",
            )
        )
        graph.style_figure(fig)
        prefix = "" if fname is None else fname
        fig.update_layout(
            legend=dict(yanchor="top", y=0.1, xanchor="left", x=0.5, orientation="h")
        )
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="temperature/" + prefix + "_equipartition_temperature",
            html=False,
            jpg=True,
            scale=4.0,
        )

    def create_pval_scatter_plot(
        self,
        pvals_containers,
        angle_distribution,
        angle_bins,
        init_temp: float,
        fname: Optional[str] = None,
    ):
        subtitles = [
            "Chi",
            "Chi Relaxed",
            "Kolmogorov-Smirnov",
            "Distribution at Last Timestep",
        ]
        fig = make_subplots(
            rows=1,
            cols=4,
            subplot_titles=[f"<b>{test}</b>" for test in subtitles],
        )
        graph = Graph()
        colors = ["#F75C03", "#00CC66", "#9d4edd", "#1789FC"]
        xVals = list(range(len(next(iter(pvals_containers)))))
        for i, container in enumerate(pvals_containers):
            fig.add_trace(
                go.Scatter(
                    x=xVals,
                    y=container,
                    mode="lines",
                    # name=f"{subtitles[i]} Temperature",
                    showlegend=False,
                    line_color=colors[i],
                ),
                row=1,
                col=i + 1,
            )
        bins = [bin[0] for bin in angle_bins]
        tick_bins = [f"{bin[0]:.2f}" for bin in angle_bins]
        fig.add_trace(
            go.Bar(
                x=bins,
                y=angle_distribution,
                marker_color=colors[-1],
                showlegend=False,
            ),
            row=1,
            col=4,
        )
        graph.update_parameters(
            dict(
                title=f"<b>Initial temperature: {init_temp:.2f} K</b>",
                xaxis_title="Timestep",
                height=400,
                width=1200,
                t_margin=80
                # yaxis_title="Temperature (K)",
            )
        )
        graph.style_figure(fig)
        prefix = "" if fname is None else fname
        # iterate through every y-axis and fix its scale
        for i in range(1, 4):
            fig.update_yaxes(range=[0, 1], row=1, col=i)
        fig.update_xaxes(
            range=[-3.14, 3.14], tickvals=tick_bins, title="Angle", row=1, col=4
        )
        fig.update_layout(bargap=0.1)
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="uniformity/" + prefix + "_uniformity_confidence",
            html=False,
            jpg=True,
            scale=4.0,
        )

    def create_speed_distribution_plot(
        self,
        left_distribution,
        right_distribution,
        left_bins,
        right_bins,
        left_color,
        right_color,
        left_name,
        right_name,
        temp_dic,
        time,
        fname: Optional[str] = None,
    ):
        fig = go.Figure()
        graph = Graph()
        for bin_tuples, distrib, color in [
            (left_bins, left_distribution, left_color),
            (right_bins, right_distribution, right_color),
        ]:
            bins = [bin[0] for bin in bin_tuples]
            label = left_name if color == left_color else right_name
            fig.add_trace(
                go.Bar(
                    x=bins,
                    y=distrib,
                    marker_color=color,
                    name=f"{label} atoms",
                    opacity=0.6,
                    # showlegend=False,
                )
            )
        title = "Timestep: " + str(time) + " | "
        for element, temp in temp_dic.items():
            title += f"{element} atoms: {temp[-1]:.2f} K | "

        graph.update_parameters(
            dict(
                title=f"<b>{title[:-2]}</b>",
                xaxis_title="Magnitude of velocity",
                # height=400,
                # width=1200,
                # t_margin=80
                # yaxis_title="Temperature (K)",
            )
        )
        graph.style_figure(fig)
        prefix = "" if fname is None else fname
        # iterate through every y-axis and fix its scale
        fig.update_layout(bargap=0.1, barmode="overlay")
        graph.save_figure(
            figure=fig,
            path=os.path.join(os.getcwd(), "figures"),
            fname="speed/" + prefix + "_uniformity_confidence",
            html=False,
            jpg=True,
            scale=4.0,
        )
