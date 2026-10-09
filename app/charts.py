import plotly.graph_objects as go
from plotly.subplots import make_subplots

POPULATION_LABELS = {
    "b_cell": "B cells",
    "cd4_t_cell": "CD4 T cells",
    "cd8_t_cell": "CD8 T cells",
    "monocyte": "Monocytes",
    "nk_cell": "NK cells",
}

POPULATION_COLORS = {
    "b_cell": "#4d8fbf",
    "cd4_t_cell": "#8a69b8",
    "cd8_t_cell": "#bd6477",
    "monocyte": "#c28a4c",
    "nk_cell": "#4d946c",
}

RESPONSE_COLORS = {
    "yes": "#d8d4cc",
    "no": "#59656c",
}


def sample_composition_chart(composition):
    chart_data = composition.copy()
    chart_data["label"] = chart_data["population"].map(
        POPULATION_LABELS
    )
    figure = go.Figure()

    for _, row in chart_data.iterrows():
        figure.add_trace(
            go.Bar(
                x=[row["percentage"]],
                y=[row["label"]],
                orientation="h",
                marker_color=POPULATION_COLORS[row["population"]],
                text=f'{row["percentage"]:.1f}%',
                textposition="outside",
                hovertemplate=(
                    f"<b>{row['label']}</b><br>"
                    f"Count: {row['count']:,}<br>"
                    f"Frequency: {row['percentage']:.2f}%"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )

    figure.update_layout(
        height=390,
        margin=dict(l=0, r=70, t=25, b=25),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#a5afb5",
            size=14,
        ),
        xaxis=dict(
            title="Relative frequency (%)",
            range=[
                0,
                max(40, chart_data["percentage"].max() + 5),
            ],
            showgrid=True,
            gridcolor="#20282d",
            zeroline=False,
        ),
        yaxis=dict(
            title=None,
            autorange="reversed",
            showgrid=False,
        ),
        bargap=0.42,
    )

    return figure


def response_boxplots(cohort, day=0):
    populations = list(POPULATION_LABELS)
    data = cohort[cohort["day"] == day]
    figure = make_subplots(
        rows=1,
        cols=5,
        shared_yaxes=True,
        subplot_titles=[
            POPULATION_LABELS[population]
            for population in populations
        ],
        horizontal_spacing=0.035,
    )

    for column, population in enumerate(populations, start=1):
        population_data = data[
            data["population"] == population
        ]

        for response in ("yes", "no"):
            group = population_data[
                population_data["response"] == response
            ]

            figure.add_trace(
                go.Box(
                    y=group["percentage"],
                    name=(
                        "Responder"
                        if response == "yes"
                        else "Nonresponder"
                    ),
                    marker_color=RESPONSE_COLORS[response],
                    line_color=RESPONSE_COLORS[response],
                    boxpoints=False,
                    showlegend=column == 1,
                    legendgroup=response,
                    hovertemplate=(
                        "%{y:.2f}%"
                        "<extra></extra>"
                    ),
                ),
                row=1,
                col=column,
            )

    figure.update_yaxes(
        title_text="Relative frequency (%)",
        gridcolor="#20282d",
        zeroline=False,
        row=1,
        col=1,
    )

    for column in range(2, 6):
        figure.update_yaxes(
            gridcolor="#20282d",
            zeroline=False,
            row=1,
            col=column,
        )

    figure.update_layout(
        height=440,
        margin=dict(l=0, r=0, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#a5afb5",
            size=12,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="right",
            x=1,
        ),
    )

    return figure


def longitudinal_change_chart(cohort):
    changes = (
        cohort
        .pivot(
            index=["subject_id", "response", "population"],
            columns="day",
            values="percentage",
        )
        .reset_index()
    )

    changes["Day 7"] = changes[7] - changes[0]
    changes["Day 14"] = changes[14] - changes[0]
    populations = list(POPULATION_LABELS)
    figure = make_subplots(
        rows=1,
        cols=5,
        shared_yaxes=True,
        subplot_titles=[
            POPULATION_LABELS[population]
            for population in populations
        ],
        horizontal_spacing=0.035,
    )

    for column, population in enumerate(populations, start=1):
        population_data = changes[
            changes["population"] == population
        ]

        for response in ("yes", "no"):
            group = population_data[
                population_data["response"] == response
            ]
            label = (
                "Responder"
                if response == "yes"
                else "Nonresponder"
            )
            figure.add_trace(
                go.Scatter(
                    x=["Day 7", "Day 14"],
                    y=[
                        group["Day 7"].mean(),
                        group["Day 14"].mean(),
                    ],
                    mode="lines+markers",
                    name=label,
                    legendgroup=response,
                    showlegend=column == 1,
                    line=dict(
                        color=RESPONSE_COLORS[response],
                        width=2,
                    ),
                    marker=dict(
                        color=RESPONSE_COLORS[response],
                        size=7,
                    ),
                    hovertemplate=(
                        f"<b>{label}</b><br>"
                        "%{x}<br>"
                        "Mean change: %{y:+.2f} pp"
                        "<extra></extra>"
                    ),
                ),
                row=1,
                col=column,
            )

    figure.add_hline(
        y=0,
        line_width=1,
        line_dash="dot",
        line_color="#465057",
    )
    figure.update_yaxes(
        title_text="Change from baseline (pp)",
        gridcolor="#20282d",
        zeroline=False,
        row=1,
        col=1,
    )

    for column in range(2, 6):
        figure.update_yaxes(
            gridcolor="#20282d",
            zeroline=False,
            row=1,
            col=column,
        )

    figure.update_layout(
        height=390,
        margin=dict(l=0, r=0, t=55, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#a5afb5",
            size=12,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.12,
            xanchor="right",
            x=1,
        ),
    )

    return figure


def cohort_breakdown_chart(breakdown):
    labels = {
        "project": "Project",
        "response": "Response",
        "sex": "Sex",
    }
    category_labels = {
        "yes": "Responder",
        "no": "Nonresponder",
        "M": "Male",
        "F": "Female",
    }

    figure = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[
            "Project",
            "Response",
            "Sex",
        ],
        horizontal_spacing=0.12,
    )

    for column, breakdown_type in enumerate(
        ("project", "response", "sex"),
        start=1,
    ):
        data = breakdown[
            breakdown["breakdown"] == breakdown_type
        ].copy()

        data["label"] = data["category"].map(
            category_labels
        ).fillna(data["category"])

        figure.add_trace(
            go.Bar(
                x=data["count"],
                y=data["label"],
                orientation="h",
                text=data["count"],
                textposition="outside",
                cliponaxis=False,
                hovertemplate=(
                    "%{y}<br>"
                    "%{x:,}"
                    "<extra></extra>"
                ),
                marker=dict(
                    color="#7f8b92",
                ),
                showlegend=False,
            ),
            row=1,
            col=column,
        )

    figure.update_xaxes(
        visible=False,
        range=[0, 430],
    )

    figure.update_yaxes(
        title=None,
        tickfont=dict(color="#a5afb5"),
    )
    figure.update_layout(
        height=250,
        margin=dict(l=0, r=25, t=50, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="Inter, sans-serif",
            color="#a5afb5",
            size=12,
        ),
        bargap=0.4,
    )

    return figure
