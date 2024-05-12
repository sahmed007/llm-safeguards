from pathlib import Path

import pandas as pd
import faicons as fa


def categorize_education(edu_str):
    if "BS" in edu_str or "Bachelor" in edu_str:
        return "Bachelor's"
    elif "MS" in edu_str or "Master" in edu_str:
        return "Master's"
    elif "PhD" in edu_str:
        return "PhD"
    elif "BE" in edu_str:
        return "BE"
    else:
        return "Other"


app_dir = Path(__file__).parent
applicants = pd.read_csv(app_dir / "applicants.csv")

ICONS = {
    "user": fa.icon_svg("user", "regular"),
    "briefcase": fa.icon_svg("briefcase"),
    "graduation-cap": fa.icon_svg("graduation-cap"),
    "ellipsis": fa.icon_svg("ellipsis"),
}
