from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).with_name("student_learning.csv")
OUTPUT_IMAGE = Path(__file__).with_name("learning_summary.svg")
OUTPUT_REPORT = Path(__file__).with_name("analysis_report.txt")


def svg_scatter(points, x_col, y_col, title, x_label, x_suffix=""):
    """Create a compact, dependency-free SVG scatterplot."""
    width, height = 540, 310
    left, top, plot_w, plot_h = 70, 48, 430, 190
    x_values = points[x_col].tolist()
    y_values = points[y_col].tolist()
    x_min, x_max = min(x_values), max(x_values)
    y_min, y_max = 40, 100

    def px(value):
        return left + (value - x_min) / (x_max - x_min) * plot_w

    def py(value):
        return top + plot_h - (value - y_min) / (y_max - y_min) * plot_h

    grid = []
    for score in (40, 55, 70, 85, 100):
        y = py(score)
        grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" stroke="#dce4ed"/>')
        grid.append(f'<text x="{left - 10}" y="{y + 5:.1f}" text-anchor="end" font-size="12">{score}</text>')
    dots = "".join(
        f'<circle cx="{px(x):.1f}" cy="{py(y):.1f}" r="5" fill="#327fd6" opacity="0.82"/>'
        for x, y in zip(x_values, y_values)
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="white"/>
  <text x="{left}" y="25" font-family="Arial" font-size="16" font-weight="700" fill="#10233d">{title}</text>
  {''.join(grid)}
  <line x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}" stroke="#5b6b82"/>
  <line x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}" stroke="#5b6b82"/>
  {dots}
  <text x="{left + plot_w / 2}" y="{top + plot_h + 42}" text-anchor="middle" font-size="12" fill="#5b6b82">{x_label}{x_suffix}</text>
  <text x="15" y="{top + plot_h / 2}" text-anchor="middle" font-size="12" fill="#5b6b82" transform="rotate(-90 15 {top + plot_h / 2})">Final Score</text>
</svg>'''


def main():
    df = pd.read_csv(DATA_FILE)
    duplicate_count = int(df.duplicated().sum())
    missing_count = int(df.isna().sum().sum())
    invalid_scores = int(((df["final_score"] < 0) | (df["final_score"] > 100)).sum())

    correlation_hours = df["study_hours"].corr(df["final_score"])
    correlation_attendance = df["attendance_rate"].corr(df["final_score"])

    left_chart = svg_scatter(
        df, "study_hours", "final_score", "Study Hours vs Final Score", "Weekly Study Hours"
    )
    attendance = df.assign(attendance_percent=df["attendance_rate"] * 100)
    right_chart = svg_scatter(
        attendance, "attendance_percent", "final_score", "Attendance vs Final Score", "Attendance Rate", " (%)"
    )
    OUTPUT_IMAGE.write_text(
        f'''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="360" viewBox="0 0 1100 360">
<text x="30" y="28" font-family="Arial" font-size="20" font-weight="700" fill="#10233d">Student Learning Data: Exploratory Analysis</text>
<g transform="translate(0,35)">{left_chart}</g>
<g transform="translate(550,35)">{right_chart}</g>
</svg>''',
        encoding="utf-8",
    )

    report = f"""Student Learning Data Report
============================
Rows: {len(df)}
Missing values: {missing_count}
Duplicate rows: {duplicate_count}
Invalid final scores: {invalid_scores}

Correlation (study hours, final score): {correlation_hours:.2f}
Correlation (attendance rate, final score): {correlation_attendance:.2f}

Interpretation:
The sample shows positive associations between both study hours and attendance
with final score. These are correlations within this small dataset; they do not
demonstrate that either factor alone causes a higher score.
"""
    OUTPUT_REPORT.write_text(report, encoding="utf-8")
    print(report)
    print(f"Saved chart: {OUTPUT_IMAGE.name}")


if __name__ == "__main__":
    main()
