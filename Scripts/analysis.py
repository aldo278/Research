import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
df = pd.read_csv("dataset.csv")

# AI mentions by year
print("AI Mentions by Year:")
print("=" * 30)
ai_by_year = df.groupby('Year')['Ai_mentions'].agg(['sum', 'mean', 'count']).round(2)
ai_by_year.columns = ['Total AI Mentions', 'Average AI Mentions', 'Number of Companies']
print(ai_by_year)
print()

# AI mentions by industry
print("AI Mentions by Industry:")
print("=" * 30)
ai_by_industry = df.groupby('Sector')['Ai_mentions'].agg(['sum', 'mean', 'count']).round(2)
ai_by_industry.columns = ['Total AI Mentions', 'Average AI Mentions', 'Number of Filings']
print(ai_by_industry)
print()

# Filing length by industry
print("Filing Length by Industry:")
print("=" * 30)
length_by_industry = df.groupby('Sector')['Words'].agg(['mean', 'median', 'min', 'max']).round(0)
length_by_industry.columns = ['Average Words', 'Median Words', 'Min Words', 'Max Words']
print(length_by_industry)
print()

# Optional: Create visualizations
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# AI mentions by year
ai_by_year['Total AI Mentions'].plot(kind='bar', ax=axes[0], color='skyblue')
axes[0].set_title('AI Mentions by Year')
axes[0].set_ylabel('Total AI Mentions')
axes[0].tick_params(axis='x', rotation=0)

# AI mentions by industry
ai_by_industry['Average AI Mentions'].plot(kind='bar', ax=axes[1], color='lightcoral')
axes[1].set_title('Average AI Mentions by Industry')
axes[1].set_ylabel('Average AI Mentions')
axes[1].tick_params(axis='x', rotation=45)
axes[1].set_xticklabels(ai_by_industry.index, rotation=45, ha='right')

# Filing length by industry
length_by_industry['Average Words'].plot(kind='bar', ax=axes[2], color='lightgreen')
axes[2].set_title('Average Filing Length by Industry')
axes[2].set_ylabel('Average Words')
axes[2].tick_params(axis='x', rotation=45)
axes[2].set_xticklabels(length_by_industry.index, rotation=45, ha='right')

plt.tight_layout()
plt.savefig('analysis_charts.png', dpi=300, bbox_inches='tight')
print("Charts saved as 'analysis_charts.png'")
