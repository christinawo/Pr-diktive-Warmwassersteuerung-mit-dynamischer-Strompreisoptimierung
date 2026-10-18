import pandas as pd
from pathlib import Path

def export_results(results, days_count):
    df = pd.DataFrame(results, columns=[
            "Profile",
            "Boiler (L)",
            "Volatility",
            "Strategy",
            "Cost (€)",
            "Comfort (%)",
            "Energy (kWh)",
            "CO2 (kg)",
            "Runtime (s)"
        ])

    # Calculate savings compared to Predictive Strategy
    predictive = df[df["Strategy"] == "Predictive Strategy"]

    savings_rows = []

    for _, pred in predictive.iterrows():
        baselines = df[
            (df["Profile"] == pred["Profile"]) &
            (df["Boiler (L)"] == pred["Boiler (L)"]) &
            (df["Volatility"] == pred["Volatility"]) &
            (df["Strategy"] != "Predictive Strategy")
        ]

        for _, baseline in baselines.iterrows():
            savings = baseline["Cost (€)"] - pred["Cost (€)"]

            savings_rows.append({
                "Profile": pred["Profile"],
                "Boiler (L)": pred["Boiler (L)"],
                "Volatility": pred["Volatility"],
                "Baseline": baseline["Strategy"],
                "Baseline Cost (€)": baseline["Cost (€)"],
                "Predictive Cost (€)": pred["Cost (€)"],
                "Savings (€)": savings,
                "Savings (%)": (
                    savings / baseline["Cost (€)"] * 100
                    if baseline["Cost (€)"] != 0 else None
                )
            })

    savings_df = pd.DataFrame(savings_rows)

    # Create output folder
    output_dir = Path("evaluation/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"simulation_results_{days_count}_days.xlsx"

    # Export all tables to Excel
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Simulation Results", index=False)
        savings_df.to_excel(writer, sheet_name="Savings Comparison", index=False)

        # Format worksheets
        for sheet in writer.sheets.values():
            sheet.freeze_panes = "A2"
            sheet.auto_filter.ref = sheet.dimensions

            for column in sheet.columns:
                max_length = max(
                    len(str(cell.value)) if cell.value is not None else 0
                    for cell in column
                )
                sheet.column_dimensions[column[0].column_letter].width = min(max_length + 3, 45)

            for row in sheet.iter_rows(min_row=2):
                for cell in row:
                    if isinstance(cell.value, float):
                        cell.number_format = "0.00"