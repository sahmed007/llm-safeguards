import faicons as fa
import plotly.express as px

# Load data and compute static values
from shared import app_dir, applicants
from shinywidgets import render_plotly

from shiny import reactive, render
from shiny.express import input, ui

experience_rng = (
    min(applicants.years_of_experience),
    max(applicants.years_of_experience),
)

# Add page title and sidebar
ui.page_opts(title="Applicant Data", fillable=True)

with ui.sidebar(open="desktop"):
    ui.input_slider(
        "years_of_experience",
        "Years of Experience",
        min=experience_rng[0],
        max=experience_rng[1],
        value=experience_rng,
    )
    ui.input_checkbox_group(
        "education",
        "Education Level",
        applicants.education.unique().tolist(),
        selected=applicants.education.unique().tolist(),
        inline=True,
    )
    ui.input_action_button("reset", "Reset filter")

# Add main content
ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "briefcase": fa.icon_svg("briefcase"),
    "graduation-cap": fa.icon_svg("graduation-cap"),
    "ellipsis": fa.icon_svg("ellipsis"),
}

with ui.layout_columns(fill=False):
    with ui.value_box(showcase=ICONS["user"]):
        "Total applicants"

        @render.express
        def total_applicants():
            applicants_data().shape[0]

    with ui.value_box(showcase=ICONS["briefcase"]):
        "Average experience"

        @render.express
        def average_experience():
            d = applicants_data()
            if d.shape[0] > 0:
                avg_exp = d.years_of_experience.mean()
                f"{avg_exp:.1f} years"

    with ui.value_box(showcase=ICONS["graduation-cap"]):
        "Most common education level"

        @render.express
        def common_education():
            d = applicants_data()
            if d.shape[0] > 0:
                common_edu = d.education.mode()[0]
                common_edu


with ui.layout_columns(col_widths=12):
    with ui.card(full_screen=True):
        ui.card_header("Applicant data")

        @render.data_frame
        def table():
            return render.DataGrid(applicants_data())

    with ui.card(full_screen=True):
        with ui.card_header(class_="d-flex justify-content-between align-items-center"):
            "Experience vs Education"
            with ui.popover(title="Add a color variable", placement="top"):
                ICONS["ellipsis"]
                ui.input_radio_buttons(
                    "scatter_color",
                    None,
                    ["none", "education", "company"],
                    inline=True,
                )

        @render_plotly
        def boxplot():
            color = input.scatter_color()
            return px.box(
                applicants_data(),
                x="years_of_experience",
                y="education",
                color=None if color == "none" else color,
            )


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def applicants_data():
    exp = input.years_of_experience()
    idx1 = applicants.years_of_experience.between(exp[0], exp[1])
    idx2 = applicants.education.isin(input.education())
    return applicants[idx1 & idx2]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("years_of_experience", value=experience_rng)
    ui.update_checkbox_group(
        "education", selected=applicants.education.unique().tolist()
    )
