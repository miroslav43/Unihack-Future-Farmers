import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

print("🌾 Generating demo harvest data...")

# Generate synthetic harvest data similar to your MongoDB structure
np.random.seed(42)
dates = pd.date_range(start='2024-01-01', end='2025-11-15', freq='3D')
n_records = len(dates)

df = pd.DataFrame({
    'date': dates,
    'notes': np.random.choice(['Normal', 'Excellent', 'Fair', 'Good'], n_records),
    'sunflower_harvested_hectares': np.random.uniform(0.5, 1.5, n_records),
    'beans_harvested_hectares': np.random.uniform(0.8, 2.0, n_records),
    'tomatoes_harvested_hectares': np.random.uniform(0.3, 1.0, n_records),
    'wheat_harvested_hectares': np.random.uniform(5.0, 12.0, n_records),
    'oil_price_per_liter': 6.0 + np.random.randn(n_records) * 0.8 + np.sin(np.arange(n_records) / 30) * 1.5,
    'total_fuel_consumed': 150 + np.random.randn(n_records) * 40 + np.random.uniform(0, 100, n_records),
    'fuel_cost': None,  # Will calculate
})

# Calculate harvest amounts based on hectares and realistic yields
df['sunflower_harvested_kg'] = df['sunflower_harvested_hectares'] * np.random.uniform(2200, 2800, n_records)
df['beans_harvested_kg'] = df['beans_harvested_hectares'] * np.random.uniform(1800, 2200, n_records)
df['tomatoes_harvested_kg'] = df['tomatoes_harvested_hectares'] * np.random.uniform(30000, 40000, n_records)
df['wheat_harvested_kg'] = df['wheat_harvested_hectares'] * np.random.uniform(3000, 4500, n_records)

# Calculate fuel cost
df['fuel_cost'] = df['total_fuel_consumed'] * np.random.uniform(6, 8, n_records)

# Add some seasonal patterns
month_factors = {1: 0.7, 2: 0.8, 3: 0.9, 4: 1.1, 5: 1.3, 6: 1.4,
                 7: 1.3, 8: 1.2, 9: 1.1, 10: 0.9, 11: 0.8, 12: 0.7}
df['month'] = df['date'].dt.month
df['season_factor'] = df['month'].map(month_factors)
for col in ['sunflower_harvested_kg', 'beans_harvested_kg', 'tomatoes_harvested_kg', 'wheat_harvested_kg']:
    df[col] = df[col] * df['season_factor']

df = df.drop('season_factor', axis=1)

# Create derived metrics
df['total_hectares'] = (df['sunflower_harvested_hectares'] + 
                        df['beans_harvested_hectares'] + 
                        df['tomatoes_harvested_hectares'] + 
                        df['wheat_harvested_hectares'])

df['total_harvest_kg'] = (df['sunflower_harvested_kg'] + 
                          df['beans_harvested_kg'] + 
                          df['tomatoes_harvested_kg'] + 
                          df['wheat_harvested_kg'])

# Productivity metrics
df['sunflower_yield'] = df['sunflower_harvested_kg'] / df['sunflower_harvested_hectares']
df['beans_yield'] = df['beans_harvested_kg'] / df['beans_harvested_hectares']
df['tomatoes_yield'] = df['tomatoes_harvested_kg'] / df['tomatoes_harvested_hectares']
df['wheat_yield'] = df['wheat_harvested_kg'] / df['wheat_harvested_hectares']

# Fuel efficiency
df['fuel_per_hectare'] = df['total_fuel_consumed'] / df['total_hectares']
df['fuel_per_kg'] = df['total_fuel_consumed'] / df['total_harvest_kg']

# Revenue estimation
df['revenue_estimate'] = df['total_harvest_kg'] * df['oil_price_per_liter'] * 0.5

df['year'] = df['date'].dt.year
df['year_month'] = df['date'].dt.to_period('M')

print(f"✅ Generated {len(df)} harvest records from {df['date'].min()} to {df['date'].max()}")

# ============================================================================
# VISUALIZATION 1: Multi-Panel Harvest Overview Dashboard
# ============================================================================

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

crops = ['sunflower_harvested_kg', 'beans_harvested_kg', 'tomatoes_harvested_kg', 'wheat_harvested_kg']
crop_labels = ['Sunflower', 'Beans', 'Tomatoes', 'Wheat']
colors = ['#FFD700', '#8B4513', '#FF6347', '#F4A460']

# 1. Crop Production Over Time (Stacked Area)
ax1 = fig.add_subplot(gs[0, :])
ax1.fill_between(df['date'], 0, df['sunflower_harvested_kg'], alpha=0.7, label='Sunflower', color=colors[0])
ax1.fill_between(df['date'], df['sunflower_harvested_kg'], 
                 df['sunflower_harvested_kg'] + df['beans_harvested_kg'], 
                 alpha=0.7, label='Beans', color=colors[1])
ax1.fill_between(df['date'], 
                 df['sunflower_harvested_kg'] + df['beans_harvested_kg'],
                 df['sunflower_harvested_kg'] + df['beans_harvested_kg'] + df['tomatoes_harvested_kg'],
                 alpha=0.7, label='Tomatoes', color=colors[2])
ax1.fill_between(df['date'], 
                 df['sunflower_harvested_kg'] + df['beans_harvested_kg'] + df['tomatoes_harvested_kg'],
                 df['total_harvest_kg'],
                 alpha=0.7, label='Wheat', color=colors[3])

ax1.set_xlabel('Date', fontweight='bold', fontsize=12)
ax1.set_ylabel('Harvest (kg)', fontweight='bold', fontsize=12)
ax1.set_title('🌾 Crop Production Timeline - Stacked View', fontsize=16, fontweight='bold', pad=20)
ax1.legend(loc='upper left', framealpha=0.9, fontsize=11)
ax1.grid(True, alpha=0.3)
ax1.set_ylim(bottom=0)

# 2. Harvest Hectares by Crop (Bar Chart)
ax2 = fig.add_subplot(gs[1, 0])
hectare_cols = ['sunflower_harvested_hectares', 'beans_harvested_hectares', 
                'tomatoes_harvested_hectares', 'wheat_harvested_hectares']
total_hectares = [df[col].sum() for col in hectare_cols]
bars = ax2.bar(crop_labels, total_hectares, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.0f}',
            ha='center', va='bottom', fontweight='bold', fontsize=10)

ax2.set_ylabel('Total Hectares', fontweight='bold')
ax2.set_title('📏 Total Hectares Harvested by Crop', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 3. Yield Efficiency (kg per hectare)
ax3 = fig.add_subplot(gs[1, 1])
yield_cols = ['sunflower_yield', 'beans_yield', 'tomatoes_yield', 'wheat_yield']
avg_yields = [df[col].mean() for col in yield_cols]
bars = ax3.barh(crop_labels, avg_yields, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

for i, bar in enumerate(bars):
    width = bar.get_width()
    ax3.text(width, bar.get_y() + bar.get_height()/2.,
            f' {width:.0f}',
            ha='left', va='center', fontweight='bold', fontsize=10)

ax3.set_xlabel('Yield (kg/hectare)', fontweight='bold')
ax3.set_title('⚡ Average Yield Efficiency', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# 4. Fuel Consumption Analysis
ax4 = fig.add_subplot(gs[1, 2])
ax4_twin = ax4.twinx()

line1 = ax4.plot(df['date'], df['total_fuel_consumed'], 
                 color='#FF4500', linewidth=2, marker='o', markersize=3, label='Fuel Consumed (L)', alpha=0.7)
line2 = ax4_twin.plot(df['date'], df['fuel_cost'], 
                      color='#32CD32', linewidth=2, marker='s', markersize=3, label='Fuel Cost ($)', alpha=0.7)

ax4.set_xlabel('Date', fontweight='bold')
ax4.set_ylabel('Fuel Consumed (L)', color='#FF4500', fontweight='bold')
ax4_twin.set_ylabel('Fuel Cost ($)', color='#32CD32', fontweight='bold')
ax4.tick_params(axis='y', labelcolor='#FF4500')
ax4_twin.tick_params(axis='y', labelcolor='#32CD32')
ax4.set_title('⛽ Fuel Consumption & Cost Trends', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=9)

# 5. Monthly Harvest Heatmap
ax5 = fig.add_subplot(gs[2, :2])
monthly_harvest = df.groupby(['year', 'month'])['total_harvest_kg'].sum().reset_index()
pivot_harvest = monthly_harvest.pivot(index='year', columns='month', values='total_harvest_kg')

sns.heatmap(pivot_harvest, annot=True, fmt='.0f', cmap='YlOrRd', 
            cbar_kws={'label': 'Total Harvest (kg)'}, ax=ax5, linewidths=0.5)
ax5.set_xlabel('Month', fontweight='bold')
ax5.set_ylabel('Year', fontweight='bold')
ax5.set_title('🔥 Monthly Harvest Intensity Heatmap', fontsize=12, fontweight='bold')

# 6. Oil Price Trend
ax6 = fig.add_subplot(gs[2, 2])
ax6.plot(df['date'], df['oil_price_per_liter'], 
         color='#FFD700', linewidth=3, marker='D', markersize=4, alpha=0.8)
ax6.fill_between(df['date'], df['oil_price_per_liter'], alpha=0.3, color='#FFD700')
ax6.set_xlabel('Date', fontweight='bold')
ax6.set_ylabel('Price per Liter ($)', fontweight='bold')
ax6.set_title('💰 Oil Price Fluctuation', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)

plt.suptitle('🚜 COMPREHENSIVE HARVEST ANALYTICS DASHBOARD 🌾', 
             fontsize=20, fontweight='bold', y=0.995)

plt.savefig('./harvest_dashboard_demo.png', dpi=300, bbox_inches='tight')
print("\n✅ Dashboard saved!")
plt.close()

# ============================================================================
# VISUALIZATION 2: Crop Performance Comparison
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Prepare data for violin plots
crop_data = []
for crop, label in zip(crops, crop_labels):
    temp_df = df[df[crop] > 0][['date', crop]].copy()
    temp_df['crop'] = label
    temp_df['harvest_kg'] = temp_df[crop]
    crop_data.append(temp_df[['date', 'crop', 'harvest_kg']])

crop_df = pd.concat(crop_data, ignore_index=True)

# Violin plot
sns.violinplot(data=crop_df, x='crop', y='harvest_kg', ax=axes[0, 0], 
               palette=colors, inner='box', linewidth=1.5)
axes[0, 0].set_title('🎻 Harvest Distribution by Crop (Violin Plot)', fontsize=14, fontweight='bold')
axes[0, 0].set_ylabel('Harvest (kg)', fontweight='bold')
axes[0, 0].set_xlabel('Crop', fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Yield box plot
yield_data = []
for yield_col, label in zip(yield_cols, crop_labels):
    temp_df = df[df[yield_col].notna()][['date', yield_col]].copy()
    temp_df['crop'] = label
    temp_df['yield'] = temp_df[yield_col]
    yield_data.append(temp_df[['date', 'crop', 'yield']])

yield_df = pd.concat(yield_data, ignore_index=True)
sns.boxplot(data=yield_df, x='crop', y='yield', ax=axes[0, 1], 
            palette=colors, linewidth=2)
axes[0, 1].set_title('📦 Yield Efficiency Distribution (Box Plot)', fontsize=14, fontweight='bold')
axes[0, 1].set_ylabel('Yield (kg/hectare)', fontweight='bold')
axes[0, 1].set_xlabel('Crop', fontweight='bold')
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Swarm plot for recent harvests
recent_df = crop_df[crop_df['date'] >= crop_df['date'].max() - pd.Timedelta(days=90)]
sns.swarmplot(data=recent_df, x='crop', y='harvest_kg', ax=axes[1, 0], 
              palette=colors, size=6, edgecolor='black', linewidth=0.5, alpha=0.7)
axes[1, 0].set_title('🐝 Recent 90-Day Harvest Points (Swarm Plot)', fontsize=14, fontweight='bold')
axes[1, 0].set_ylabel('Harvest (kg)', fontweight='bold')
axes[1, 0].set_xlabel('Crop', fontweight='bold')
axes[1, 0].grid(True, alpha=0.3, axis='y')

# Cumulative harvest
axes[1, 1].plot(df['date'], df['sunflower_harvested_kg'].cumsum(), 
                label='Sunflower', linewidth=3, marker='o', markersize=2, color=colors[0])
axes[1, 1].plot(df['date'], df['beans_harvested_kg'].cumsum(), 
                label='Beans', linewidth=3, marker='s', markersize=2, color=colors[1])
axes[1, 1].plot(df['date'], df['tomatoes_harvested_kg'].cumsum(), 
                label='Tomatoes', linewidth=3, marker='^', markersize=2, color=colors[2])
axes[1, 1].plot(df['date'], df['wheat_harvested_kg'].cumsum(), 
                label='Wheat', linewidth=3, marker='D', markersize=2, color=colors[3])
axes[1, 1].set_title('📈 Cumulative Harvest Growth', fontsize=14, fontweight='bold')
axes[1, 1].set_ylabel('Cumulative Harvest (kg)', fontweight='bold')
axes[1, 1].set_xlabel('Date', fontweight='bold')
axes[1, 1].legend(framealpha=0.9)
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle('🌱 CROP PERFORMANCE DEEP DIVE 🌱', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('./crop_performance_demo.png', dpi=300, bbox_inches='tight')
print("✅ Crop performance analysis saved!")
plt.close()

# ============================================================================
# VISUALIZATION 3: Economic & Efficiency Analysis
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Fuel efficiency scatter
scatter = axes[0, 0].scatter(df['total_hectares'], df['total_fuel_consumed'], 
                             c=df['total_harvest_kg'], s=200, alpha=0.6, 
                             cmap='viridis', edgecolor='black', linewidth=1.5)
axes[0, 0].set_xlabel('Total Hectares Harvested', fontweight='bold')
axes[0, 0].set_ylabel('Fuel Consumed (L)', fontweight='bold')
axes[0, 0].set_title('⚙️ Fuel Efficiency Analysis', fontsize=14, fontweight='bold')
axes[0, 0].grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=axes[0, 0])
cbar.set_label('Total Harvest (kg)', fontweight='bold')

# Fuel per kg distribution
axes[0, 1].hist(df['fuel_per_kg'].dropna(), bins=30, color='#FF6347', 
                alpha=0.7, edgecolor='black', linewidth=1.5)
axes[0, 1].axvline(df['fuel_per_kg'].mean(), color='red', 
                   linestyle='--', linewidth=3, label=f'Mean: {df["fuel_per_kg"].mean():.3f}')
axes[0, 1].set_xlabel('Fuel Consumption per kg', fontweight='bold')
axes[0, 1].set_ylabel('Frequency', fontweight='bold')
axes[0, 1].set_title('📊 Fuel Efficiency Distribution', fontsize=14, fontweight='bold')
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3, axis='y')

# Revenue vs Cost
axes[1, 0].scatter(df['fuel_cost'], df['revenue_estimate'], 
                   s=150, alpha=0.6, c=range(len(df)), cmap='coolwarm', 
                   edgecolor='black', linewidth=1.5)
axes[1, 0].plot([df['fuel_cost'].min(), df['fuel_cost'].max()], 
                [df['fuel_cost'].min(), df['fuel_cost'].max()], 
                'r--', linewidth=2, label='Break-even Line')
axes[1, 0].set_xlabel('Fuel Cost ($)', fontweight='bold')
axes[1, 0].set_ylabel('Revenue Estimate ($)', fontweight='bold')
axes[1, 0].set_title('💵 Cost vs Revenue Analysis', fontsize=14, fontweight='bold')
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

# Productivity trend
df['productivity'] = df['total_harvest_kg'] / df['total_hectares']
df['productivity_ma'] = df['productivity'].rolling(window=5, min_periods=1).mean()

axes[1, 1].plot(df['date'], df['productivity'], 
                alpha=0.3, color='gray', label='Daily Productivity', linewidth=1)
axes[1, 1].plot(df['date'], df['productivity_ma'], 
                linewidth=3, color='#FF1493', label='5-Day Moving Average')
axes[1, 1].fill_between(df['date'], df['productivity_ma'], alpha=0.3, color='#FF1493')
axes[1, 1].set_xlabel('Date', fontweight='bold')
axes[1, 1].set_ylabel('Productivity (kg/hectare)', fontweight='bold')
axes[1, 1].set_title('📈 Productivity Trend Analysis', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle('💰 ECONOMIC & EFFICIENCY METRICS 💰', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('./economic_analysis_demo.png', dpi=300, bbox_inches='tight')
print("✅ Economic analysis saved!")
plt.close()

# ============================================================================
# VISUALIZATION 4: Correlation Matrix
# ============================================================================

fig, ax = plt.subplots(1, 1, figsize=(14, 10))

numeric_cols = ['sunflower_harvested_kg', 'beans_harvested_kg', 'tomatoes_harvested_kg', 
                'wheat_harvested_kg', 'total_fuel_consumed', 'fuel_cost', 
                'oil_price_per_liter', 'total_hectares', 'total_harvest_kg']
corr_df = df[numeric_cols].corr()

mask = np.triu(np.ones_like(corr_df, dtype=bool), k=1)
sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=2, cbar_kws={"shrink": 0.8}, ax=ax,
            vmin=-1, vmax=1, mask=mask, annot_kws={'size': 10})
ax.set_title('🔗 Feature Correlation Matrix', fontsize=18, fontweight='bold', pad=20)

plt.tight_layout()
plt.savefig('./correlation_demo.png', dpi=300, bbox_inches='tight')
print("✅ Correlation analysis saved!")
plt.close()

# ============================================================================
# VISUALIZATION 5: Time Series Analysis
# ============================================================================

fig, axes = plt.subplots(3, 1, figsize=(18, 14))

# Rolling statistics
window = 7
df['harvest_rolling_mean'] = df['total_harvest_kg'].rolling(window=window).mean()
df['harvest_rolling_std'] = df['total_harvest_kg'].rolling(window=window).std()

axes[0].plot(df['date'], df['total_harvest_kg'], 
             label='Daily Harvest', alpha=0.4, linewidth=1, color='gray')
axes[0].plot(df['date'], df['harvest_rolling_mean'], 
             label=f'{window}-Day Moving Average', linewidth=3, color='#2E8B57')
axes[0].fill_between(df['date'], 
                     df['harvest_rolling_mean'] - df['harvest_rolling_std'],
                     df['harvest_rolling_mean'] + df['harvest_rolling_std'],
                     alpha=0.2, color='#2E8B57', label='±1 Std Dev')
axes[0].set_ylabel('Harvest (kg)', fontweight='bold')
axes[0].set_title('📊 Total Harvest with Rolling Statistics', fontsize=14, fontweight='bold')
axes[0].legend(loc='best')
axes[0].grid(True, alpha=0.3)

# Seasonal pattern
monthly_avg = df.groupby('month')['total_harvest_kg'].mean()
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
axes[1].bar(monthly_avg.index, monthly_avg.values, 
            color='#4169E1', alpha=0.7, edgecolor='black', linewidth=1.5)
axes[1].set_xticks(range(1, 13))
axes[1].set_xticklabels([months[i-1] for i in monthly_avg.index])
axes[1].set_ylabel('Average Harvest (kg)', fontweight='bold')
axes[1].set_title('🗓️ Seasonal Harvest Pattern', fontsize=14, fontweight='bold')
axes[1].grid(True, alpha=0.3, axis='y')

# Year-over-year
for year in df['year'].unique():
    year_data = df[df['year'] == year].groupby('month')['total_harvest_kg'].sum()
    axes[2].plot(year_data.index, year_data.values, 
                 marker='o', linewidth=3, label=f'Year {year}', markersize=8)
axes[2].set_xlabel('Month', fontweight='bold')
axes[2].set_ylabel('Total Harvest (kg)', fontweight='bold')
axes[2].set_title('📅 Year-over-Year Comparison', fontsize=14, fontweight='bold')
axes[2].legend(fontsize=11)
axes[2].grid(True, alpha=0.3)

plt.suptitle('⏰ TIME SERIES ANALYSIS & SEASONAL PATTERNS ⏰', 
             fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig('./time_series_demo.png', dpi=300, bbox_inches='tight')
print("✅ Time series analysis saved!")
plt.close()

# Summary
print("\n" + "="*80)
print("📊 HARVEST ANALYTICS SUMMARY (DEMO DATA)")
print("="*80)

print(f"\n🌾 TOTAL PRODUCTION:")
for crop, label in zip(crops, crop_labels):
    print(f"  {label:12s}: {df[crop].sum():>15,.0f} kg")

print(f"\n📏 TOTAL AREA HARVESTED:")
for hectare_col, label in zip(['sunflower_harvested_hectares', 'beans_harvested_hectares', 
                                'tomatoes_harvested_hectares', 'wheat_harvested_hectares'], 
                               crop_labels):
    print(f"  {label:12s}: {df[hectare_col].sum():>15,.2f} hectares")

print(f"\n⚡ AVERAGE YIELDS (kg/hectare):")
for yield_col, label in zip(yield_cols, crop_labels):
    print(f"  {label:12s}: {df[yield_col].mean():>15,.0f} kg/ha")

print(f"\n⛽ FUEL STATISTICS:")
print(f"  Total Fuel Used    : {df['total_fuel_consumed'].sum():>15,.2f} liters")
print(f"  Total Fuel Cost    : ${df['fuel_cost'].sum():>15,.2f}")
print(f"  Avg Fuel/Hectare   : {df['fuel_per_hectare'].mean():>15,.2f} L/ha")
print(f"  Avg Fuel/kg        : {df['fuel_per_kg'].mean():>15,.3f} L/kg")

print(f"\n💰 ECONOMIC METRICS:")
print(f"  Avg Oil Price      : ${df['oil_price_per_liter'].mean():>15,.2f}/L")
print(f"  Total Est. Revenue : ${df['revenue_estimate'].sum():>15,.2f}")

print("\n" + "="*80)
print("✅ ALL 5 DEMO VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*80)
print("\n📁 Generated files:")
print("  1. harvest_dashboard_demo.png - Comprehensive overview")
print("  2. crop_performance_demo.png - Detailed crop metrics")
print("  3. economic_analysis_demo.png - Cost and revenue insights")
print("  4. correlation_demo.png - Relationship patterns")
print("  5. time_series_demo.png - Temporal trends")
print("\n🎉 Demo complete! These visualizations show what your real data will look like!")