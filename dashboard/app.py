import pandas as pd
import seaborn as sns

# Load data and compute static values
from shared import app_dir, applicants, experience_rng, load_data_to_sqlite, ICONS

from shiny import reactive, render
from shiny.express import input, ui


con = load_data_to_sqlite("applicants.db", "applicants", app_dir / "applicants.csv")

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
        "education_level",
        "Education Level",
        applicants.education_level.unique().tolist(),
        selected=applicants.education_level.unique().tolist(),
        inline=True,
    )
    ui.input_action_button("reset", "Reset filters", class_="btn-tertiary rounded-3")

with ui.navset_tab(id="tab"):
    # Overview Tab
    with ui.nav_panel("Overview"):
        # Analytics Overview Cards
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

        # Education Plot
        with ui.layout_columns(col_widths=12):
            with ui.card(full_screen=True):
                with ui.card_header(
                    class_="d-flex justify-content-between align-items-center"
                ):
                    "Experience vs Education"
                    with ui.popover(title="Add a color variable", placement="top"):
                        ICONS["ellipsis"]
                        ui.input_radio_buttons(
                            "scatter_color",
                            None,
                            ["none", "education", "company"],
                            inline=True,
                        )

                @render.plot(alt="Number of candidates per education level.")
                def histplot():
                    ax = sns.histplot(data=applicants_data(), x="education_level")
                    ax.set_title("Candidate by Degree Level")
                    ax.set_xlabel("Degree Level")
                    ax.set_ylabel("Number of Candidates")
                    return ax

    # Applicants Explorer Tab
    with ui.nav_panel("Applicants Explorer"):
        with ui.layout_columns(col_widths=12):
            with ui.card(full_screen=True):
                ui.card_header("Applicant data")

                @render.data_frame
                def table():
                    return render.DataGrid(applicants_data())

    # AI Query Tab
    with ui.nav_panel("AI Query"):
        # AI Query Input
        with ui.layout_columns(col_widths=12):
            with ui.card():
                ui.card_header("AI Query Assistant")
                ui.input_text_area(
                    "textarea",
                    "Ask a question...",
                    "How many candidates do I have for this role?",
                    width="100%",
                    rows=4,
                )
                with ui.layout_columns(fill=False):
                    ui.input_action_button(
                        "meta", "Show metadata", class_="btn-secondary rounded-3"
                    )
                    ui.input_action_button(
                        "submit", "Submit", class_="btn-success rounded-3"
                    )

        # AI Query Output
        with ui.layout_columns(col_widths=12):
            with ui.card():
                ui.card_header("AI Query Results")

                @render.data_frame
                @reactive.event(input.submit)
                def query_result():
                    qry = input.textarea().replace("\n", " ")
                    df = pd.read_sql_query(qry, con)
                    return df

                @render.data_frame
                @reactive.event(input.meta)
                def show_metadata():
                    qry = "PRAGMA table_info(applicants);"
                    df = pd.read_sql_query(qry, con)
                    return df


ui.include_css(app_dir / "styles.css")

# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------


@reactive.calc
def applicants_data():
    exp = input.years_of_experience()
    idx1 = applicants.years_of_experience.between(exp[0], exp[1])
    idx2 = applicants.education_level.isin(input.education_level())
    return applicants[idx1 & idx2]


@reactive.effect
@reactive.event(input.reset)
def _():
    ui.update_slider("years_of_experience", value=experience_rng)
    ui.update_checkbox_group(
        "education", selected=applicants.education.unique().tolist()
    )
