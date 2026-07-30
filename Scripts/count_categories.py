import pandas as pd
from pathlib import Path

# Get the script directory and locate the CSV file
script_dir = Path(__file__).parent
csv_path = script_dir.parent / "annotation_dataset_completed.csv"
output_path = script_dir.parent / "count_categories_output.txt"

# Read the CSV
df = pd.read_csv(csv_path)

# Calculate risk_category distribution (excluding empty values)
risk_category_counts = df["risk_category"].value_counts().sort_index()

# Calculate disclosure_quality distribution (excluding empty values)
disclosure_quality_counts = df["disclosure_quality"].value_counts().sort_index()

# Format output
output_lines = []
output_lines.append("=" * 60)
output_lines.append("RISK CATEGORY DISTRIBUTION")
output_lines.append("=" * 60)
output_lines.append(f"Total annotated passages: {risk_category_counts.sum()}")
output_lines.append("")
for category, count in risk_category_counts.items():
    pct = (count / risk_category_counts.sum()) * 100
    output_lines.append(f"{category:30s} {count:5d} ({pct:5.1f}%)")

output_lines.append("")
output_lines.append("=" * 60)
output_lines.append("DISCLOSURE QUALITY DISTRIBUTION")
output_lines.append("=" * 60)
output_lines.append(f"Total annotated passages: {disclosure_quality_counts.sum()}")
output_lines.append("")
for quality, count in disclosure_quality_counts.items():
    pct = (count / disclosure_quality_counts.sum()) * 100
    output_lines.append(f"{str(quality):30s} {count:5d} ({pct:5.1f}%)")

# Write to output file
with open(output_path, "w", encoding="utf-8") as f:
    f.write("\n".join(output_lines))

print(f"Output saved to: {output_path}")
