import os
import pymongo
from pymongo import MongoClient
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import streamlit as st
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="🌾 Harvest Analytics Dashboard",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Set style for plots
sns.set_style("whitegrid")
sns.set_palette("husl")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<p class="main-header">🌾 Harvest Analytics Dashboard 🚜</p>', unsafe_allow_html=True)

# ============================================================================
# DATA LOADING FUNCTION
# ============================================================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load data from MongoDB"""
    try:
        connection_string = os.getenv("MONGO_API_KEY")
        
        if not connection_string:
            st.error("❌ MONGO_API_KEY environment variable not set!")
            return None
        
        client = MongoClient(connection_string)
        db = client['farmer_assessment_db']
        collection_harvest_logs = db['harvest_logs']
        
        # Fetch data
        harvest_data = list(collection_harvest_logs.find())
        
        if len(harvest_data) == 0:
            st.error("❌ No data found in collection_harvest_logs!")
            return None
        
        # Convert to DataFrame
        df = pd.DataFrame(harvest_data)
        
        # Convert date to datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
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
        
        # Revenue estimation
        df['revenue_estimate'] = df['total_harvest_kg'] * df['oil_price_per_liter'] * 0.5
        
        # Time features
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        df['day_of_week'] = df['date'].dt.day_name()
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# Load data
with st.spinner('📥 Loading data from MongoDB...'):
    df = load_data()

if df is None:
    st.stop()

st.success(f"✅ Loaded {len(df)} records from {df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}")

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

st.sidebar.header("⚙️ Dashboard Controls")

# Date range selection
st.sidebar.subheader("📅 Time Period")
timeframe_option = st.sidebar.radio(
    "Select timeframe:",
    ["Last 7 Days", "Last 2 Weeks", "Last Month", "Last 3 Months", "All Time", "Custom Range"]
)

# Calculate date range
max_date = df['date'].max()
min_date = df['date'].min()

if timeframe_option == "Last 7 Days":
    start_date = max_date - timedelta(days=7)
    end_date = max_date
elif timeframe_option == "Last 2 Weeks":
    start_date = max_date - timedelta(days=14)
    end_date = max_date
elif timeframe_option == "Last Month":
    start_date = max_date - timedelta(days=30)
    end_date = max_date
elif timeframe_option == "Last 3 Months":
    start_date = max_date - timedelta(days=90)
    end_date = max_date
elif timeframe_option == "All Time":
    start_date = min_date
    end_date = max_date
else:  # Custom Range
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input("Start Date", min_date.date())
        start_date = pd.to_datetime(start_date)
    with col2:
        end_date = st.date_input("End Date", max_date.date())
        end_date = pd.to_datetime(end_date)

# Filter dataframe by date
df_filtered = df[(df['date'] >= start_date) & (df['date'] <= end_date)].copy()

st.sidebar.info(f"📊 Showing {len(df_filtered)} records")

# Metric selection
st.sidebar.subheader("📊 Select Analysis")
analysis_type = st.sidebar.selectbox(
    "Choose analysis type:",
    ["Overview Dashboard", "Fuel Analysis", "Yield Analysis", "Harvest Volume", 
     "Economic Analysis", "Crop Comparison", "Time Trends"]
)

# Crop selection
st.sidebar.subheader("🌱 Crop Filter")
all_crops = ["Sunflower", "Beans", "Tomatoes", "Wheat"]
selected_crops = st.sidebar.multiselect(
    "Select crops:",
    all_crops,
    default=all_crops
)

# Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# ============================================================================
# OVERVIEW DASHBOARD
# ============================================================================

if analysis_type == "Overview Dashboard":
    st.header("📊 Quick Overview")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Harvest",
            f"{df_filtered['total_harvest_kg'].sum():,.0f} kg",
            f"{df_filtered['total_harvest_kg'].sum() - df['total_harvest_kg'].mean() * len(df_filtered):.0f} kg vs avg"
        )
    
    with col2:
        st.metric(
            "Total Fuel Used",
            f"{df_filtered['total_fuel_consumed'].sum():,.1f} L",
            f"${df_filtered['fuel_cost'].sum():,.2f} spent"
        )
    
    with col3:
        st.metric(
            "Avg Yield",
            f"{(df_filtered['total_harvest_kg'].sum() / df_filtered['total_hectares'].sum()):.0f} kg/ha",
            f"{df_filtered['total_hectares'].sum():.1f} ha total"
        )
    
    with col4:
        st.metric(
            "Est. Revenue",
            f"${df_filtered['revenue_estimate'].sum():,.0f}",
            f"${df_filtered['oil_price_per_liter'].mean():.2f}/L avg price"
        )
    
    st.markdown("---")
    
    # Two columns for charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌾 Harvest by Crop")
        crop_mapping = {
            'Sunflower': 'sunflower_harvested_kg',
            'Beans': 'beans_harvested_kg',
            'Tomatoes': 'tomatoes_harvested_kg',
            'Wheat': 'wheat_harvested_kg'
        }
        
        harvest_by_crop = []
        for crop in selected_crops:
            if crop_mapping[crop] in df_filtered.columns:
                harvest_by_crop.append({
                    'Crop': crop,
                    'Harvest (kg)': df_filtered[crop_mapping[crop]].sum()
                })
        
        if harvest_by_crop:
            harvest_df = pd.DataFrame(harvest_by_crop)
            fig, ax = plt.subplots(figsize=(8, 6))
            colors = ['#FFD700', '#8B4513', '#FF6347', '#F4A460']
            bars = ax.barh(harvest_df['Crop'], harvest_df['Harvest (kg)'], 
                          color=colors[:len(harvest_df)], edgecolor='black', linewidth=1.5)
            
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2., 
                       f'{width:,.0f}',
                       ha='left', va='center', fontweight='bold', fontsize=10)
            
            ax.set_xlabel('Harvest (kg)', fontweight='bold')
            ax.set_title('Total Harvest by Crop', fontweight='bold', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
            st.pyplot(fig)
            plt.close()
    
    with col2:
        st.subheader("📈 Daily Harvest Trend")
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(df_filtered['date'], df_filtered['total_harvest_kg'], 
               marker='o', linewidth=2, markersize=6, color='#2E7D32')
        ax.fill_between(df_filtered['date'], df_filtered['total_harvest_kg'], 
                       alpha=0.3, color='#2E7D32')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Harvest (kg)', fontweight='bold')
        ax.set_title('Daily Harvest Volume', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()
    
    # Bottom row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⛽ Fuel Consumption Over Time")
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(df_filtered['date'], df_filtered['total_fuel_consumed'], 
               marker='s', linewidth=2, markersize=6, color='#FF4500', label='Fuel (L)')
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Fuel (L)', fontweight='bold', color='#FF4500')
        ax.tick_params(axis='y', labelcolor='#FF4500')
        
        ax2 = ax.twinx()
        ax2.plot(df_filtered['date'], df_filtered['fuel_cost'], 
                marker='D', linewidth=2, markersize=6, color='#32CD32', label='Cost ($)')
        ax2.set_ylabel('Cost ($)', fontweight='bold', color='#32CD32')
        ax2.tick_params(axis='y', labelcolor='#32CD32')
        
        ax.set_title('Fuel Consumption & Cost', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("💰 Oil Price Trend")
        fig, ax = plt.subplots(figsize=(8, 6))
        
        ax.plot(df_filtered['date'], df_filtered['oil_price_per_liter'], 
               marker='D', linewidth=3, markersize=8, color='#FFD700')
        ax.fill_between(df_filtered['date'], df_filtered['oil_price_per_liter'], 
                       alpha=0.3, color='#FFD700')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Price per Liter ($)', fontweight='bold')
        ax.set_title('Oil Price Fluctuation', fontweight='bold', fontsize=12)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()

# ============================================================================
# FUEL ANALYSIS
# ============================================================================

elif analysis_type == "Fuel Analysis":
    st.header("⛽ Fuel Consumption Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Fuel", f"{df_filtered['total_fuel_consumed'].sum():,.1f} L")
    
    with col2:
        st.metric("Total Cost", f"${df_filtered['fuel_cost'].sum():,.2f}")
    
    with col3:
        avg_per_ha = df_filtered['fuel_per_hectare'].mean()
        st.metric("Avg per Hectare", f"{avg_per_ha:.2f} L/ha" if not np.isnan(avg_per_ha) else "N/A")
    
    with col4:
        avg_per_kg = df_filtered['fuel_per_kg'].mean()
        st.metric("Avg per kg", f"{avg_per_kg:.3f} L/kg" if not np.isnan(avg_per_kg) else "N/A")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Daily Fuel Consumption")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(df_filtered['date'], df_filtered['total_fuel_consumed'], 
              color='#FF4500', alpha=0.7, edgecolor='black', linewidth=1)
        
        # Add moving average
        if len(df_filtered) >= 3:
            ma = df_filtered['total_fuel_consumed'].rolling(window=3).mean()
            ax.plot(df_filtered['date'], ma, color='red', linewidth=3, 
                   label='3-Day Moving Avg', marker='o')
            ax.legend()
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Fuel (L)', fontweight='bold')
        ax.set_title('Daily Fuel Consumption', fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("💵 Fuel Cost Breakdown")
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(df_filtered['date'], df_filtered['fuel_cost'], 
              color='#32CD32', alpha=0.7, edgecolor='black', linewidth=1)
        
        ax.axhline(df_filtered['fuel_cost'].mean(), color='red', 
                  linestyle='--', linewidth=2, label=f'Mean: ${df_filtered["fuel_cost"].mean():.2f}')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Cost ($)', fontweight='bold')
        ax.set_title('Daily Fuel Cost', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()
    
    # Efficiency analysis
    st.subheader("⚙️ Fuel Efficiency Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        scatter = ax.scatter(df_filtered['total_hectares'], 
                           df_filtered['total_fuel_consumed'],
                           c=df_filtered['total_harvest_kg'], 
                           s=200, alpha=0.6, cmap='viridis', 
                           edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Total Hectares', fontweight='bold')
        ax.set_ylabel('Fuel Consumed (L)', fontweight='bold')
        ax.set_title('Fuel vs Hectares (colored by harvest)', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Harvest (kg)', fontweight='bold')
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        if 'fuel_per_kg' in df_filtered.columns:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            fuel_per_kg_clean = df_filtered['fuel_per_kg'].dropna()
            if len(fuel_per_kg_clean) > 0:
                ax.hist(fuel_per_kg_clean, bins=15, color='#FF6347', 
                       alpha=0.7, edgecolor='black', linewidth=1.5)
                ax.axvline(fuel_per_kg_clean.mean(), color='red', 
                          linestyle='--', linewidth=3, 
                          label=f'Mean: {fuel_per_kg_clean.mean():.3f} L/kg')
                
                ax.set_xlabel('Fuel per kg (L/kg)', fontweight='bold')
                ax.set_ylabel('Frequency', fontweight='bold')
                ax.set_title('Fuel Efficiency Distribution', fontweight='bold')
                ax.legend()
                ax.grid(True, alpha=0.3, axis='y')
                
                st.pyplot(fig)
                plt.close()

# ============================================================================
# YIELD ANALYSIS
# ============================================================================

elif analysis_type == "Yield Analysis":
    st.header("⚡ Yield Performance Analysis")
    
    crop_mapping = {
        'Sunflower': ('sunflower_yield', 'sunflower_harvested_hectares', 'sunflower_harvested_kg'),
        'Beans': ('beans_yield', 'beans_harvested_hectares', 'beans_harvested_kg'),
        'Tomatoes': ('tomatoes_yield', 'tomatoes_harvested_hectares', 'tomatoes_harvested_kg'),
        'Wheat': ('wheat_yield', 'wheat_harvested_hectares', 'wheat_harvested_kg')
    }
    
    # Summary metrics
    cols = st.columns(len(selected_crops))
    for idx, crop in enumerate(selected_crops):
        yield_col, ha_col, kg_col = crop_mapping[crop]
        if yield_col in df_filtered.columns:
            avg_yield = df_filtered[yield_col].mean()
            with cols[idx]:
                st.metric(
                    f"{crop}",
                    f"{avg_yield:.0f} kg/ha" if not np.isnan(avg_yield) else "N/A",
                    f"{df_filtered[kg_col].sum():,.0f} kg total"
                )
    
    st.markdown("---")
    
    # Yield comparison
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Average Yield by Crop")
        
        yield_data = []
        colors = {'Sunflower': '#FFD700', 'Beans': '#8B4513', 
                 'Tomatoes': '#FF6347', 'Wheat': '#F4A460'}
        
        for crop in selected_crops:
            yield_col = crop_mapping[crop][0]
            if yield_col in df_filtered.columns:
                avg_yield = df_filtered[yield_col].mean()
                if not np.isnan(avg_yield):
                    yield_data.append({'Crop': crop, 'Yield (kg/ha)': avg_yield})
        
        if yield_data:
            yield_df = pd.DataFrame(yield_data)
            fig, ax = plt.subplots(figsize=(10, 6))
            
            bar_colors = [colors[crop] for crop in yield_df['Crop']]
            bars = ax.bar(yield_df['Crop'], yield_df['Yield (kg/ha)'], 
                         color=bar_colors, alpha=0.8, edgecolor='black', linewidth=2)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.0f}',
                       ha='center', va='bottom', fontweight='bold', fontsize=11)
            
            ax.set_ylabel('Yield (kg/hectare)', fontweight='bold')
            ax.set_title('Average Yield Efficiency', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
            plt.close()
    
    with col2:
        st.subheader("📈 Yield Trends Over Time")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for crop in selected_crops:
            yield_col = crop_mapping[crop][0]
            if yield_col in df_filtered.columns:
                crop_data = df_filtered[df_filtered[yield_col].notna()]
                if len(crop_data) > 0:
                    ax.plot(crop_data['date'], crop_data[yield_col], 
                           marker='o', linewidth=2, markersize=6, 
                           label=crop, color=colors[crop])
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Yield (kg/ha)', fontweight='bold')
        ax.set_title('Yield Performance Over Time', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
    
    # Detailed yield distributions
    st.subheader("📦 Yield Distribution Analysis")
    
    fig, axes = plt.subplots(1, len(selected_crops), figsize=(5*len(selected_crops), 6))
    if len(selected_crops) == 1:
        axes = [axes]
    
    for idx, crop in enumerate(selected_crops):
        yield_col = crop_mapping[crop][0]
        if yield_col in df_filtered.columns:
            yield_data = df_filtered[df_filtered[yield_col].notna()][yield_col]
            
            if len(yield_data) > 0:
                axes[idx].hist(yield_data, bins=10, color=colors[crop], 
                             alpha=0.7, edgecolor='black', linewidth=1.5)
                axes[idx].axvline(yield_data.mean(), color='red', 
                                linestyle='--', linewidth=2, 
                                label=f'Mean: {yield_data.mean():.0f}')
                axes[idx].set_xlabel('Yield (kg/ha)', fontweight='bold')
                axes[idx].set_ylabel('Frequency', fontweight='bold')
                axes[idx].set_title(f'{crop} Yield Distribution', fontweight='bold')
                axes[idx].legend()
                axes[idx].grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()

# ============================================================================
# HARVEST VOLUME
# ============================================================================

elif analysis_type == "Harvest Volume":
    st.header("🌾 Harvest Volume Analysis")
    
    # Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Harvest", f"{df_filtered['total_harvest_kg'].sum():,.0f} kg")
    
    with col2:
        st.metric("Average Daily", f"{df_filtered['total_harvest_kg'].mean():,.0f} kg")
    
    with col3:
        st.metric("Total Area", f"{df_filtered['total_hectares'].sum():.1f} ha")
    
    st.markdown("---")
    
    # Harvest over time
    st.subheader("📈 Harvest Timeline")
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Stacked area chart
        crops_kg = ['sunflower_harvested_kg', 'beans_harvested_kg', 
                   'tomatoes_harvested_kg', 'wheat_harvested_kg']
        crop_labels = ['Sunflower', 'Beans', 'Tomatoes', 'Wheat']
        colors = ['#FFD700', '#8B4513', '#FF6347', '#F4A460']
        
        for crop_kg, label, color in zip(crops_kg, crop_labels, colors):
            if label in selected_crops and crop_kg in df_filtered.columns:
                ax.fill_between(df_filtered['date'], df_filtered[crop_kg], 
                              alpha=0.7, label=label, color=color)
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Harvest (kg)', fontweight='bold')
        ax.set_title('Stacked Harvest Volume', fontweight='bold')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Cumulative harvest
        for crop_kg, label, color in zip(crops_kg, crop_labels, colors):
            if label in selected_crops and crop_kg in df_filtered.columns:
                cumsum = df_filtered[crop_kg].cumsum()
                ax.plot(df_filtered['date'], cumsum, 
                       linewidth=3, marker='o', label=label, color=color)
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Cumulative Harvest (kg)', fontweight='bold')
        ax.set_title('Cumulative Harvest Growth', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
    
    # Harvest by crop pie chart
    st.subheader("🥧 Harvest Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        harvest_by_crop = []
        for crop, crop_kg in zip(crop_labels, crops_kg):
            if crop in selected_crops and crop_kg in df_filtered.columns:
                total = df_filtered[crop_kg].sum()
                if total > 0:
                    harvest_by_crop.append({'Crop': crop, 'Harvest': total})
        
        if harvest_by_crop:
            harvest_df = pd.DataFrame(harvest_by_crop)
            
            fig, ax = plt.subplots(figsize=(8, 8))
            
            crop_colors = [colors[crop_labels.index(crop)] for crop in harvest_df['Crop']]
            wedges, texts, autotexts = ax.pie(harvest_df['Harvest'], 
                                               labels=harvest_df['Crop'],
                                               autopct='%1.1f%%',
                                               colors=crop_colors,
                                               startangle=90,
                                               textprops={'fontsize': 12, 'fontweight': 'bold'})
            
            ax.set_title('Harvest Distribution by Crop', fontweight='bold', fontsize=14)
            
            st.pyplot(fig)
            plt.close()
    
    with col2:
        # Daily harvest bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.bar(df_filtered['date'], df_filtered['total_harvest_kg'], 
              color='#2E7D32', alpha=0.7, edgecolor='black', linewidth=1)
        ax.axhline(df_filtered['total_harvest_kg'].mean(), 
                  color='red', linestyle='--', linewidth=2,
                  label=f'Mean: {df_filtered["total_harvest_kg"].mean():.0f} kg')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Harvest (kg)', fontweight='bold')
        ax.set_title('Daily Total Harvest', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()

# ============================================================================
# ECONOMIC ANALYSIS
# ============================================================================

elif analysis_type == "Economic Analysis":
    st.header("💰 Economic Performance Analysis")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Est. Revenue", f"${df_filtered['revenue_estimate'].sum():,.0f}")
    
    with col2:
        st.metric("Fuel Cost", f"${df_filtered['fuel_cost'].sum():,.2f}")
    
    with col3:
        profit = df_filtered['revenue_estimate'].sum() - df_filtered['fuel_cost'].sum()
        st.metric("Est. Profit", f"${profit:,.0f}")
    
    with col4:
        roi = (profit / df_filtered['fuel_cost'].sum() * 100) if df_filtered['fuel_cost'].sum() > 0 else 0
        st.metric("ROI", f"{roi:.1f}%")
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💵 Revenue vs Cost")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.scatter(df_filtered['fuel_cost'], df_filtered['revenue_estimate'], 
                  s=150, alpha=0.6, c=range(len(df_filtered)), cmap='coolwarm',
                  edgecolor='black', linewidth=1.5)
        
        # Break-even line
        max_val = max(df_filtered['fuel_cost'].max(), df_filtered['revenue_estimate'].max())
        ax.plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='Break-even')
        
        ax.set_xlabel('Fuel Cost ($)', fontweight='bold')
        ax.set_ylabel('Revenue Estimate ($)', fontweight='bold')
        ax.set_title('Cost vs Revenue Analysis', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        st.subheader("📊 Daily Economics")
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(df_filtered))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], df_filtered['revenue_estimate'], 
              width, label='Revenue', color='#32CD32', alpha=0.7, edgecolor='black')
        ax.bar([i + width/2 for i in x], df_filtered['fuel_cost'], 
              width, label='Cost', color='#FF4500', alpha=0.7, edgecolor='black')
        
        ax.set_xlabel('Date Index', fontweight='bold')
        ax.set_ylabel('Amount ($)', fontweight='bold')
        ax.set_title('Revenue vs Cost Comparison', fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        st.pyplot(fig)
        plt.close()
    
    # Profit timeline
    st.subheader("📈 Profit Timeline")
    
    df_filtered['profit'] = df_filtered['revenue_estimate'] - df_filtered['fuel_cost']
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    colors_profit = ['#32CD32' if x >= 0 else '#FF4500' for x in df_filtered['profit']]
    ax.bar(df_filtered['date'], df_filtered['profit'], 
          color=colors_profit, alpha=0.7, edgecolor='black', linewidth=1)
    
    ax.axhline(0, color='black', linewidth=2)
    ax.axhline(df_filtered['profit'].mean(), color='blue', 
              linestyle='--', linewidth=2, label=f'Mean: ${df_filtered["profit"].mean():.2f}')
    
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Profit ($)', fontweight='bold')
    ax.set_title('Daily Profit/Loss', fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    plt.xticks(rotation=45)
    
    st.pyplot(fig)
    plt.close()
    
    # Cumulative profit
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        cumulative_profit = df_filtered['profit'].cumsum()
        ax.plot(df_filtered['date'], cumulative_profit, 
               linewidth=3, marker='o', color='#2E7D32')
        ax.fill_between(df_filtered['date'], cumulative_profit, 
                       alpha=0.3, color='#2E7D32')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Cumulative Profit ($)', fontweight='bold')
        ax.set_title('Cumulative Profit Over Time', fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
    
    with col2:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        ax.plot(df_filtered['date'], df_filtered['oil_price_per_liter'], 
               linewidth=3, marker='D', markersize=8, color='#FFD700')
        ax.fill_between(df_filtered['date'], df_filtered['oil_price_per_liter'], 
                       alpha=0.3, color='#FFD700')
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Price per Liter ($)', fontweight='bold')
        ax.set_title('Oil Price Trend', fontweight='bold')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()

# ============================================================================
# CROP COMPARISON
# ============================================================================

elif analysis_type == "Crop Comparison":
    st.header("🌱 Detailed Crop Comparison")
    
    if len(selected_crops) < 2:
        st.warning("⚠️ Please select at least 2 crops for comparison")
    else:
        crop_mapping = {
            'Sunflower': ('sunflower_harvested_kg', 'sunflower_harvested_hectares', 'sunflower_yield'),
            'Beans': ('beans_harvested_kg', 'beans_harvested_hectares', 'beans_yield'),
            'Tomatoes': ('tomatoes_harvested_kg', 'tomatoes_harvested_hectares', 'tomatoes_yield'),
            'Wheat': ('wheat_harvested_kg', 'wheat_harvested_hectares', 'wheat_yield')
        }
        
        colors = {'Sunflower': '#FFD700', 'Beans': '#8B4513', 
                 'Tomatoes': '#FF6347', 'Wheat': '#F4A460'}
        
        # Side-by-side comparison
        st.subheader("📊 Performance Metrics Comparison")
        
        comparison_data = []
        for crop in selected_crops:
            kg_col, ha_col, yield_col = crop_mapping[crop]
            
            if kg_col in df_filtered.columns:
                comparison_data.append({
                    'Crop': crop,
                    'Total Harvest (kg)': df_filtered[kg_col].sum(),
                    'Total Hectares': df_filtered[ha_col].sum(),
                    'Avg Yield (kg/ha)': df_filtered[yield_col].mean()
                })
        
        if comparison_data:
            comp_df = pd.DataFrame(comparison_data)
            st.dataframe(comp_df.style.format({
                'Total Harvest (kg)': '{:,.0f}',
                'Total Hectares': '{:.2f}',
                'Avg Yield (kg/ha)': '{:.0f}'
            }), use_container_width=True)
        
        st.markdown("---")
        
        # Visual comparisons
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌾 Total Harvest Comparison")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            harvest_data = [df_filtered[crop_mapping[crop][0]].sum() 
                          for crop in selected_crops 
                          if crop_mapping[crop][0] in df_filtered.columns]
            crop_colors = [colors[crop] for crop in selected_crops]
            
            bars = ax.bar(selected_crops, harvest_data, 
                         color=crop_colors, alpha=0.8, edgecolor='black', linewidth=2)
            
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}',
                       ha='center', va='bottom', fontweight='bold')
            
            ax.set_ylabel('Total Harvest (kg)', fontweight='bold')
            ax.set_title('Total Harvest by Crop', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
            plt.close()
        
        with col2:
            st.subheader("⚡ Yield Efficiency Comparison")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            yield_data = [df_filtered[crop_mapping[crop][2]].mean() 
                         for crop in selected_crops 
                         if crop_mapping[crop][2] in df_filtered.columns]
            
            bars = ax.barh(selected_crops, yield_data, 
                          color=crop_colors, alpha=0.8, edgecolor='black', linewidth=2)
            
            for i, bar in enumerate(bars):
                width = bar.get_width()
                if not np.isnan(width):
                    ax.text(width, bar.get_y() + bar.get_height()/2.,
                           f'{width:.0f}',
                           ha='left', va='center', fontweight='bold')
            
            ax.set_xlabel('Avg Yield (kg/ha)', fontweight='bold')
            ax.set_title('Average Yield Efficiency', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='x')
            
            st.pyplot(fig)
            plt.close()
        
        # Harvest trends comparison
        st.subheader("📈 Harvest Trends Comparison")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for crop in selected_crops:
            kg_col = crop_mapping[crop][0]
            if kg_col in df_filtered.columns:
                ax.plot(df_filtered['date'], df_filtered[kg_col], 
                       linewidth=2.5, marker='o', markersize=6, 
                       label=crop, color=colors[crop])
        
        ax.set_xlabel('Date', fontweight='bold')
        ax.set_ylabel('Harvest (kg)', fontweight='bold')
        ax.set_title('Harvest Trends Over Time', fontweight='bold', fontsize=14)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        st.pyplot(fig)
        plt.close()
        
        # Distribution comparison (violin plots)
        st.subheader("🎻 Harvest Distribution Comparison")
        
        # Prepare data for violin plot
        crop_data = []
        for crop in selected_crops:
            kg_col = crop_mapping[crop][0]
            if kg_col in df_filtered.columns:
                temp_df = df_filtered[df_filtered[kg_col] > 0][[kg_col]].copy()
                temp_df['Crop'] = crop
                temp_df['Harvest'] = temp_df[kg_col]
                crop_data.append(temp_df[['Crop', 'Harvest']])
        
        if crop_data:
            violin_df = pd.concat(crop_data, ignore_index=True)
            
            fig, ax = plt.subplots(figsize=(14, 6))
            
            parts = ax.violinplot([violin_df[violin_df['Crop'] == crop]['Harvest'].values 
                                  for crop in selected_crops],
                                 positions=range(len(selected_crops)),
                                 showmeans=True, showmedians=True)
            
            # Color the violins
            for i, pc in enumerate(parts['bodies']):
                pc.set_facecolor(crop_colors[i])
                pc.set_alpha(0.7)
            
            ax.set_xticks(range(len(selected_crops)))
            ax.set_xticklabels(selected_crops)
            ax.set_ylabel('Harvest (kg)', fontweight='bold')
            ax.set_title('Harvest Distribution by Crop', fontweight='bold', fontsize=14)
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
            plt.close()

# ============================================================================
# TIME TRENDS
# ============================================================================

elif analysis_type == "Time Trends":
    st.header("⏰ Time Series & Seasonal Analysis")
    
    # Rolling statistics
    st.subheader("📊 Rolling Statistics")
    
    window = st.slider("Select rolling window (days):", 3, 10, 5)
    
    df_filtered['harvest_rolling_mean'] = df_filtered['total_harvest_kg'].rolling(window=window).mean()
    df_filtered['harvest_rolling_std'] = df_filtered['total_harvest_kg'].rolling(window=window).std()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df_filtered['date'], df_filtered['total_harvest_kg'], 
           alpha=0.4, linewidth=1, color='gray', label='Daily Harvest')
    ax.plot(df_filtered['date'], df_filtered['harvest_rolling_mean'], 
           linewidth=3, color='#2E8B57', label=f'{window}-Day Moving Average')
    ax.fill_between(df_filtered['date'],
                   df_filtered['harvest_rolling_mean'] - df_filtered['harvest_rolling_std'],
                   df_filtered['harvest_rolling_mean'] + df_filtered['harvest_rolling_std'],
                   alpha=0.2, color='#2E8B57', label='±1 Std Dev')
    
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Harvest (kg)', fontweight='bold')
    ax.set_title('Harvest with Rolling Statistics', fontweight='bold', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    st.pyplot(fig)
    plt.close()
    
    # Seasonal pattern
    st.subheader("🗓️ Seasonal Pattern")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'month' in df_filtered.columns and len(df_filtered) > 0:
            monthly_avg = df_filtered.groupby('month')['total_harvest_kg'].mean()
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.bar(monthly_avg.index, monthly_avg.values, 
                  color='#4169E1', alpha=0.7, edgecolor='black', linewidth=1.5)
            ax.set_xticks(monthly_avg.index)
            ax.set_xticklabels([months[i-1] for i in monthly_avg.index])
            ax.set_ylabel('Average Harvest (kg)', fontweight='bold')
            ax.set_title('Average Harvest by Month', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            
            st.pyplot(fig)
            plt.close()
    
    with col2:
        if 'day_of_week' in df_filtered.columns and len(df_filtered) > 0:
            daily_avg = df_filtered.groupby('day_of_week')['total_harvest_kg'].mean()
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            daily_avg = daily_avg.reindex([day for day in day_order if day in daily_avg.index])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            ax.bar(daily_avg.index, daily_avg.values, 
                  color='#FF8C00', alpha=0.7, edgecolor='black', linewidth=1.5)
            ax.set_ylabel('Average Harvest (kg)', fontweight='bold')
            ax.set_title('Average Harvest by Day of Week', fontweight='bold')
            ax.grid(True, alpha=0.3, axis='y')
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
            plt.close()
    
    # Year-over-year comparison
    if 'year' in df_filtered.columns and df_filtered['year'].nunique() > 1:
        st.subheader("📅 Year-over-Year Comparison")
        
        fig, ax = plt.subplots(figsize=(14, 6))
        
        for year in df_filtered['year'].unique():
            year_data = df_filtered[df_filtered['year'] == year].groupby('month')['total_harvest_kg'].sum()
            ax.plot(year_data.index, year_data.values, 
                   marker='o', linewidth=2.5, label=f'Year {int(year)}', markersize=8)
        
        ax.set_xlabel('Month', fontweight='bold')
        ax.set_ylabel('Total Harvest (kg)', fontweight='bold')
        ax.set_title('Year-over-Year Harvest Comparison', fontweight='bold', fontsize=14)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)
        plt.close()
    
    # Productivity trend
    st.subheader("📈 Productivity Trend")
    
    df_filtered['productivity'] = df_filtered['total_harvest_kg'] / df_filtered['total_hectares'].replace(0, np.nan)
    df_filtered['productivity_ma'] = df_filtered['productivity'].rolling(window=3, min_periods=1).mean()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    
    ax.plot(df_filtered['date'], df_filtered['productivity'], 
           alpha=0.3, color='gray', label='Daily Productivity')
    ax.plot(df_filtered['date'], df_filtered['productivity_ma'], 
           linewidth=3, color='#FF1493', label='3-Day Moving Average')
    ax.fill_between(df_filtered['date'], df_filtered['productivity_ma'], 
                   alpha=0.3, color='#FF1493')
    
    ax.set_xlabel('Date', fontweight='bold')
    ax.set_ylabel('Productivity (kg/hectare)', fontweight='bold')
    ax.set_title('Productivity Trend Analysis', fontweight='bold', fontsize=14)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    
    st.pyplot(fig)
    plt.close()

# ============================================================================
# FOOTER & DATA EXPORT
# ============================================================================

st.markdown("---")

st.subheader("📥 Export Options")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Download Filtered Data (CSV)"):
        csv = df_filtered.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"harvest_data_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 View Summary Statistics"):
        st.subheader("Summary Statistics")
        
        summary = {
            'Total Harvest (kg)': df_filtered['total_harvest_kg'].sum(),
            'Total Hectares': df_filtered['total_hectares'].sum(),
            'Total Fuel (L)': df_filtered['total_fuel_consumed'].sum(),
            'Total Fuel Cost ($)': df_filtered['fuel_cost'].sum(),
            'Est. Revenue ($)': df_filtered['revenue_estimate'].sum(),
            'Avg Yield (kg/ha)': df_filtered['total_harvest_kg'].sum() / df_filtered['total_hectares'].sum() if df_filtered['total_hectares'].sum() > 0 else 0,
            'Avg Fuel/ha (L)': df_filtered['fuel_per_hectare'].mean(),
            'Avg Oil Price ($/L)': df_filtered['oil_price_per_liter'].mean()
        }
        
        for key, value in summary.items():
            st.metric(key, f"{value:,.2f}")

with col3:
    st.info(f"📊 Currently showing:\n\n{len(df_filtered)} records\n\nFrom {start_date.strftime('%Y-%m-%d')}\n\nTo {end_date.strftime('%Y-%m-%d')}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
        <p>🌾 <b>Harvest Analytics Dashboard</b> | Built with Streamlit & Python</p>
        <p>📊 Real-time data from MongoDB | 🔄 Auto-refresh every 5 minutes</p>
    </div>
""", unsafe_allow_html=True)

# streamlit run harvest_dashboard.py