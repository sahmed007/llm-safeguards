from pathlib import Path

import pandas as pd

app_dir = Path(__file__).parent
applicants = pd.read_csv(app_dir / "applicants.csv")
