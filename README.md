# Business KPI Dashboard

A desktop GUI app for loading CSV files, selecting key business columns, and generating KPI summaries such as total records, total value, average value, and category breakdowns.

## Features

- load CSV files locally
- choose value, category/stage, and optional date columns
- generate KPI summary stats
- preview loaded data
- export summary to JSON
- export summary to CSV
- clean recruiter-friendly desktop GUI
- branded icon assets and Windows `.exe` build instructions

## Why this project exists

Business teams often have raw CSV exports but no fast local way to turn them into clean metrics. This project provides a lightweight dashboard for generating useful KPI summaries without needing a full BI platform.

## Tech Stack

- Python 3
- Tkinter GUI
- CSV / JSON
- Standard library only

## Project Structure

```bash
business-kpi-dashboard/
├── dashboard.py
├── sample_data.csv
├── run_dashboard.bat
├── launch_dashboard.sh
├── app_icon.svg
├── app_icon.png
├── app_icon.ico
├── build_exe_instructions.md
├── requirements.txt
├── .gitignore
└── README.md
```

## How to Run

### Windows
Double-click:

```bash
run_dashboard.bat
```

### Linux / macOS
```bash
python3 dashboard.py
```

or:

```bash
bash launch_dashboard.sh
```

## Example Workflow

1. Load a CSV file
2. Choose the value column (revenue, sales, amount, etc.)
3. Choose the category/stage column
4. Click **Analyze**
5. Review stats and export a summary report

## Future Improvements

- embedded charts
- date-range filtering
- saved dashboard presets
- PDF export
- more advanced column inference

## License

MIT
