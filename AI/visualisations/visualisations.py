import os
import pymongo
from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for beautiful plots
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Create output directory if it doesn't exist
OUTPUT_DIR = './output'
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"📁 Output directory: {os.path.abspath(OUTPUT_DIR)}")

print("🔌 Connecting to MongoDB...")

# Connect to MongoDB - using your exact connection code
connection_string = os.getenv("MONGO_API_KEY")

if not connection_string:
    raise ValueError("❌ MONGO_API_KEY environment variable not set!")

client = MongoClient(connection_string)
db = client['farmer_assessment_db']
collection_harvest_logs = db['harvest_logs']

print("✅ Connected to MongoDB!")
print("📥 Fetching all harvest data from collection_harvest_logs...")

# Fetch ALL harvest data from MongoDB
harvest_data = list(collection_harvest_logs.find())

print(f"✅ Retrieved {len(harvest_data)} records from MongoDB")

if len(harvest_data) == 0:
    raise ValueError("❌ No data found in collection_harvest_logs! Please check your database.")

# Convert to DataFrame
df = pd.DataFrame(harvest_data)

print(f"\n📊 DataFrame created with {len(df)} rows")
print(f"Columns found: {df.columns.tolist()}")

# Convert date to datetime
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    print(f"\n📅 Date range: {df['date'].min()} to {df['date'].max()}")
else:
    raise ValueError("❌ 'date' column not found in the data!")

print(f"\n✅ Data loaded successfully!")

# Create derived metrics
df['total_hectares'] = (df.get('sunflower_harvested_hectares', 0) + 
                        df.get('beans_harvested_hectares', 0) + 
                        df.get('tomatoes_harvested_hectares', 0) + 
                        df.get('wheat_harvested_hectares', 0))

df['total_harvest_kg'] = (df.get('sunflower_harvested_kg', 0) + 
                          df.get('beans_harvested_kg', 0) + 
                          df.get('tomatoes_harvested_kg', 0) + 
                          df.get('wheat_harvested_kg', 0))

# Productivity metrics
df['sunflower_yield'] = df['sunflower_harvested_kg'] / df['sunflower_harvested_hectares'].replace(0, np.nan)
df['beans_yield'] = df['beans_harvested_kg'] / df['beans_harvested_hectares'].replace(0, np.nan)
df['tomatoes_yield'] = df['tomatoes_harvested_kg'] / df['tomatoes_harvested_hectares'].replace(0, np.nan)
df['wheat_yield'] = df['wheat_harvested_kg'] / df['wheat_harvested_hectares'].replace(0, np.nan)

# Fuel efficiency
df['fuel_per_hectare'] = df['total_fuel_consumed'] / df['total_hectares'].replace(0, np.nan)
df['fuel_per_kg'] = df['total_fuel_consumed'] / df['total_harvest_kg'].replace(0, np.nan)

# Revenue estimation (using oil price as proxy for market prices)
df['revenue_estimate'] = df['total_harvest_kg'] * df['oil_price_per_liter'] * 0.5  # Simplified

# Month and year for grouping
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year
df['year_month'] = df['date'].dt.to_period('M')

print("\nDataFrame created successfully!")
print(f"Shape: {df.shape}")

# ============================================================================
# VISUALIZATION 1: Multi-Panel Harvest Overview Dashboard
# ============================================================================

fig = plt.figure(figsize=(20, 12))
gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)

# 1. Crop Production Over Time (Stacked Area)
ax1 = fig.add_subplot(gs[0, :])
crops = ['sunflower_harvested_kg', 'beans_harvested_kg', 'tomatoes_harvested_kg', 'wheat_harvested_kg']
crop_labels = ['Sunflower', 'Beans', 'Tomatoes', 'Wheat']
colors = ['#FFD700', '#8B4513', '#FF6347', '#F4A460']

for crop, label, color in zip(crops, crop_labels, colors):
    if crop in df.columns:
        ax1.fill_between(df['date'], df[crop], alpha=0.7, label=label, color=color)

ax1.set_xlabel('Date', fontweight='bold')
ax1.set_ylabel('Harvest (kg)', fontweight='bold')
ax1.set_title('🌾 Crop Production Timeline - Stacked View', fontsize=16, fontweight='bold', pad=20)
ax1.legend(loc='upper left', framealpha=0.9)
ax1.grid(True, alpha=0.3)

# 2. Harvest Hectares by Crop (Bar Chart)
ax2 = fig.add_subplot(gs[1, 0])
hectare_cols = ['sunflower_harvested_hectares', 'beans_harvested_hectares', 
                'tomatoes_harvested_hectares', 'wheat_harvested_hectares']
total_hectares = [df[col].sum() for col in hectare_cols if col in df.columns]
bars = ax2.bar(crop_labels, total_hectares, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

# Add value labels on bars
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}',
            ha='center', va='bottom', fontweight='bold')

ax2.set_ylabel('Total Hectares', fontweight='bold')
ax2.set_title('📏 Total Hectares Harvested by Crop', fontsize=12, fontweight='bold')
ax2.grid(True, alpha=0.3, axis='y')

# 3. Yield Efficiency (kg per hectare)
ax3 = fig.add_subplot(gs[1, 1])
yield_cols = ['sunflower_yield', 'beans_yield', 'tomatoes_yield', 'wheat_yield']
avg_yields = [df[col].mean() for col in yield_cols if col in df.columns]
bars = ax3.barh(crop_labels, avg_yields, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)

for i, bar in enumerate(bars):
    width = bar.get_width()
    if not np.isnan(width):
        ax3.text(width, bar.get_y() + bar.get_height()/2.,
                f'{width:.0f}',
                ha='left', va='center', fontweight='bold')

ax3.set_xlabel('Yield (kg/hectare)', fontweight='bold')
ax3.set_title('⚡ Average Yield Efficiency', fontsize=12, fontweight='bold')
ax3.grid(True, alpha=0.3, axis='x')

# 4. Fuel Consumption Analysis
ax4 = fig.add_subplot(gs[1, 2])
ax4_twin = ax4.twinx()

line1 = ax4.plot(df['date'], df['total_fuel_consumed'], 
                 color='#FF4500', linewidth=2, marker='o', markersize=4, label='Fuel Consumed (L)')
line2 = ax4_twin.plot(df['date'], df['fuel_cost'], 
                      color='#32CD32', linewidth=2, marker='s', markersize=4, label='Fuel Cost ($)')

ax4.set_xlabel('Date', fontweight='bold')
ax4.set_ylabel('Fuel Consumed (L)', color='#FF4500', fontweight='bold')
ax4_twin.set_ylabel('Fuel Cost ($)', color='#32CD32', fontweight='bold')
ax4.tick_params(axis='y', labelcolor='#FF4500')
ax4_twin.tick_params(axis='y', labelcolor='#32CD32')
ax4.set_title('⛽ Fuel Consumption & Cost Trends', fontsize=12, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Combine legends
lines1, labels1 = ax4.get_legend_handles_labels()
lines2, labels2 = ax4_twin.get_legend_handles_labels()
ax4.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

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
         color='#FFD700', linewidth=3, marker='D', markersize=6)
ax6.fill_between(df['date'], df['oil_price_per_liter'], alpha=0.3, color='#FFD700')
ax6.set_xlabel('Date', fontweight='bold')
ax6.set_ylabel('Price per Liter ($)', fontweight='bold')
ax6.set_title('💰 Oil Price Fluctuation', fontsize=12, fontweight='bold')
ax6.grid(True, alpha=0.3)

plt.suptitle('🚜 COMPREHENSIVE HARVEST ANALYTICS DASHBOARD 🌾', 
             fontsize=20, fontweight='bold', y=0.995)

plt.savefig(f'{OUTPUT_DIR}/harvest_dashboard.png', dpi=300, bbox_inches='tight')
print("\n✅ Dashboard saved: harvest_dashboard.png")

# ============================================================================
# VISUALIZATION 2: Crop Performance Comparison - Violin & Box Plots
# ============================================================================

fig, axes = plt.subplots(2, 2, figsize=(18, 12))

# Prepare data for violin plots
crop_data = []
for crop, label in zip(crops, crop_labels):
    if crop in df.columns:
        temp_df = df[df[crop] > 0][['date', crop]].copy()
        temp_df['crop'] = label
        temp_df['harvest_kg'] = temp_df[crop]
        crop_data.append(temp_df[['date', 'crop', 'harvest_kg']])

crop_df = pd.concat(crop_data, ignore_index=True)

# Violin plot for harvest distribution
sns.violinplot(data=crop_df, x='crop', y='harvest_kg', ax=axes[0, 0], 
               palette=colors, inner='box', linewidth=1.5)
axes[0, 0].set_title('🎻 Harvest Distribution by Crop (Violin Plot)', fontsize=14, fontweight='bold')
axes[0, 0].set_ylabel('Harvest (kg)', fontweight='bold')
axes[0, 0].set_xlabel('Crop', fontweight='bold')
axes[0, 0].grid(True, alpha=0.3, axis='y')

# Yield comparison box plot
yield_data = []
for yield_col, label in zip(yield_cols, crop_labels):
    if yield_col in df.columns:
        temp_df = df[df[yield_col].notna()][['date', yield_col]].copy()
        temp_df['crop'] = label
        temp_df['yield'] = temp_df[yield_col]
        yield_data.append(temp_df[['date', 'crop', 'yield']])

if yield_data:
    yield_df = pd.concat(yield_data, ignore_index=True)
    sns.boxplot(data=yield_df, x='crop', y='yield', ax=axes[0, 1], 
                palette=colors, linewidth=2)
    axes[0, 1].set_title('📦 Yield Efficiency Distribution (Box Plot)', fontsize=14, fontweight='bold')
    axes[0, 1].set_ylabel('Yield (kg/hectare)', fontweight='bold')
    axes[0, 1].set_xlabel('Crop', fontweight='bold')
    axes[0, 1].grid(True, alpha=0.3, axis='y')

# Swarm plot for recent harvests
recent_df = crop_df[crop_df['date'] >= crop_df['date'].max() - pd.Timedelta(days=90)]
if len(recent_df) > 0:
    sns.swarmplot(data=recent_df, x='crop', y='harvest_kg', ax=axes[1, 0], 
                  palette=colors, size=8, edgecolor='black', linewidth=1)
    axes[1, 0].set_title('🐝 Recent 90-Day Harvest Points (Swarm Plot)', fontsize=14, fontweight='bold')
    axes[1, 0].set_ylabel('Harvest (kg)', fontweight='bold')
    axes[1, 0].set_xlabel('Crop', fontweight='bold')
    axes[1, 0].grid(True, alpha=0.3, axis='y')

# Cumulative harvest over time
axes[1, 1].plot(df['date'], df['sunflower_harvested_kg'].cumsum(), 
                label='Sunflower', linewidth=3, marker='o', color=colors[0])
axes[1, 1].plot(df['date'], df['beans_harvested_kg'].cumsum(), 
                label='Beans', linewidth=3, marker='s', color=colors[1])
axes[1, 1].plot(df['date'], df['tomatoes_harvested_kg'].cumsum(), 
                label='Tomatoes', linewidth=3, marker='^', color=colors[2])
axes[1, 1].plot(df['date'], df['wheat_harvested_kg'].cumsum(), 
                label='Wheat', linewidth=3, marker='D', color=colors[3])
axes[1, 1].set_title('📈 Cumulative Harvest Growth', fontsize=14, fontweight='bold')
axes[1, 1].set_ylabel('Cumulative Harvest (kg)', fontweight='bold')
axes[1, 1].set_xlabel('Date', fontweight='bold')
axes[1, 1].legend(framealpha=0.9)
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle('🌱 CROP PERFORMANCE DEEP DIVE 🌱', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/crop_performance_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Crop performance analysis saved: crop_performance_analysis.png")

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

# Cost per kg analysis
if 'fuel_per_kg' in df.columns:
    axes[0, 1].hist(df['fuel_per_kg'].dropna(), bins=20, color='#FF6347', 
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

# Productivity over time (3-day moving average)
df['productivity'] = df['total_harvest_kg'] / df['total_hectares'].replace(0, np.nan)
df['productivity_ma'] = df['productivity'].rolling(window=3, min_periods=1).mean()

axes[1, 1].plot(df['date'], df['productivity'], 
                alpha=0.3, color='gray', label='Daily Productivity')
axes[1, 1].plot(df['date'], df['productivity_ma'], 
                linewidth=3, color='#FF1493', label='3-Day Moving Average')
axes[1, 1].fill_between(df['date'], df['productivity_ma'], alpha=0.3, color='#FF1493')
axes[1, 1].set_xlabel('Date', fontweight='bold')
axes[1, 1].set_ylabel('Productivity (kg/hectare)', fontweight='bold')
axes[1, 1].set_title('📈 Productivity Trend Analysis', fontsize=14, fontweight='bold')
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle('💰 ECONOMIC & EFFICIENCY METRICS 💰', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/economic_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Economic analysis saved: economic_analysis.png")

# ============================================================================
# VISUALIZATION 4: Correlation & Relationship Matrix
# ============================================================================

fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Correlation heatmap
numeric_cols = ['sunflower_harvested_kg', 'beans_harvested_kg', 'tomatoes_harvested_kg', 
                'wheat_harvested_kg', 'total_fuel_consumed', 'fuel_cost', 
                'oil_price_per_liter', 'total_hectares', 'total_harvest_kg']
corr_df = df[numeric_cols].corr()

sns.heatmap(corr_df, annot=True, fmt='.2f', cmap='coolwarm', center=0,
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=axes[0],
            vmin=-1, vmax=1)
axes[0].set_title('🔗 Feature Correlation Matrix', fontsize=16, fontweight='bold', pad=20)

# Pairplot style scatter matrix for key variables
from pandas.plotting import scatter_matrix

key_vars = df[['total_harvest_kg', 'total_fuel_consumed', 'total_hectares', 'fuel_cost']]
pd.plotting.scatter_matrix(key_vars, ax=axes[1], alpha=0.6, figsize=(10, 10), 
                          diagonal='kde', color='#1f77b4', s=100)
axes[1].set_title('🎯 Key Metrics Scatter Matrix', fontsize=16, fontweight='bold')

plt.suptitle('🔬 CORRELATION & RELATIONSHIP ANALYSIS 🔬', fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/correlation_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Correlation analysis saved: correlation_analysis.png")

# ============================================================================
# VISUALIZATION 5: Time Series Decomposition & Trends
# ============================================================================

fig, axes = plt.subplots(3, 1, figsize=(18, 14))

# Rolling statistics for total harvest
window = 5
df['harvest_rolling_mean'] = df['total_harvest_kg'].rolling(window=window).mean()
df['harvest_rolling_std'] = df['total_harvest_kg'].rolling(window=window).std()

axes[0].plot(df['date'], df['total_harvest_kg'], 
             label='Daily Harvest', alpha=0.5, linewidth=1, color='gray')
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
if 'month' in df.columns:
    monthly_avg = df.groupby('month')['total_harvest_kg'].mean()
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    axes[1].bar(monthly_avg.index, monthly_avg.values, 
                color='#4169E1', alpha=0.7, edgecolor='black', linewidth=1.5)
    axes[1].set_xticks(monthly_avg.index)
    axes[1].set_xticklabels([months[i-1] for i in monthly_avg.index])
    axes[1].set_ylabel('Average Harvest (kg)', fontweight='bold')
    axes[1].set_title('🗓️ Seasonal Harvest Pattern', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')

# Year-over-year comparison
if 'year' in df.columns and df['year'].nunique() > 1:
    for year in df['year'].unique():
        year_data = df[df['year'] == year].groupby('month')['total_harvest_kg'].sum()
        axes[2].plot(year_data.index, year_data.values, 
                     marker='o', linewidth=2, label=f'Year {year}', markersize=8)
    axes[2].set_xlabel('Month', fontweight='bold')
    axes[2].set_ylabel('Total Harvest (kg)', fontweight='bold')
    axes[2].set_title('📅 Year-over-Year Comparison', fontsize=14, fontweight='bold')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

plt.suptitle('⏰ TIME SERIES ANALYSIS & SEASONAL PATTERNS ⏰', 
             fontsize=18, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/time_series_analysis.png', dpi=300, bbox_inches='tight')
print("✅ Time series analysis saved: time_series_analysis.png")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n" + "="*80)
print("📊 HARVEST ANALYTICS SUMMARY")
print("="*80)

print(f"\n🌾 TOTAL PRODUCTION:")
for crop, label in zip(crops, crop_labels):
    if crop in df.columns:
        print(f"  {label:12s}: {df[crop].sum():>10,.0f} kg")

print(f"\n📏 TOTAL AREA HARVESTED:")
for hectare_col, label in zip(['sunflower_harvested_hectares', 'beans_harvested_hectares', 
                                'tomatoes_harvested_hectares', 'wheat_harvested_hectares'], 
                               crop_labels):
    if hectare_col in df.columns:
        print(f"  {label:12s}: {df[hectare_col].sum():>10,.2f} hectares")

print(f"\n⚡ AVERAGE YIELDS (kg/hectare):")
for yield_col, label in zip(yield_cols, crop_labels):
    if yield_col in df.columns:
        avg = df[yield_col].mean()
        if not np.isnan(avg):
            print(f"  {label:12s}: {avg:>10,.0f} kg/ha")

print(f"\n⛽ FUEL STATISTICS:")
print(f"  Total Fuel Used    : {df['total_fuel_consumed'].sum():>10,.2f} liters")
print(f"  Total Fuel Cost    : ${df['fuel_cost'].sum():>10,.2f}")
print(f"  Avg Fuel/Hectare   : {df['fuel_per_hectare'].mean():>10,.2f} L/ha")
print(f"  Avg Fuel/kg        : {df['fuel_per_kg'].mean():>10,.3f} L/kg")

print(f"\n💰 ECONOMIC METRICS:")
print(f"  Avg Oil Price      : ${df['oil_price_per_liter'].mean():>10,.2f}/L")
print(f"  Total Est. Revenue : ${df['revenue_estimate'].sum():>10,.2f}")

print("\n" + "="*80)
print("✅ ALL VISUALIZATIONS GENERATED SUCCESSFULLY!")
print("="*80)
print("\nGenerated files:")
print("  1. harvest_dashboard.png - Comprehensive overview")
print("  2. crop_performance_analysis.png - Detailed crop metrics")
print("  3. economic_analysis.png - Cost and revenue insights")
print("  4. correlation_analysis.png - Relationship patterns")
print("  5. time_series_analysis.png - Temporal trends")
print("\n🎉 Analysis complete! Check the outputs folder for your visualizations.")