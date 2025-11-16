import json
from datetime import datetime
from collections import defaultdict
import re

def parse_temperature(temp_str):
    """Extract numeric temperature value from string like '14°C' or '14°'"""
    if not temp_str or temp_str == '--°C' or temp_str == 'N/A':
        return None
    # Remove degree symbols and 'C'
    cleaned = re.sub(r'[°ÂC]', '', temp_str)
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None

def format_date(day, month, year):
    """Create a standardized date string"""
    return f"{year}-{month:02d}-{day:02d}"

def process_accuweather_data(filepath, month_num, year):
    """Process AccuWeather format data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    weather_dict = {}
    for entry in data['data']:
        day = int(entry['Day of the month'])
        
        # Determine actual month (handle overlap with previous/next month)
        # Days at the start that are higher numbers are from previous month
        # Days at the end that are lower numbers are from next month
        actual_month = month_num
        if month_num == 11 and day == 30:  # Nov 30 at start of November data is actually Oct 30
            continue  # Skip, should be in October data
        elif month_num == 12 and day == 30:  # Dec 30 at start of December data is actually Nov 30
            continue  # Skip, should be in November data
        
        date_key = format_date(day, actual_month, year)
        
        max_temp = parse_temperature(entry['Maximum predicted weather'])
        min_temp = parse_temperature(entry['Minimum predicted weather'])
        description = entry['General weather description']
        
        if max_temp is not None or min_temp is not None:
            weather_dict[date_key] = {
                'source': 'accuweather',
                'max_temp': max_temp,
                'min_temp': min_temp,
                'description': description if description != '-' else None
            }
    
    return weather_dict

def process_weathercom_data(filepath):
    """Process Weather.com format data"""
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    weather_dict = {}
    for entry in data:
        date_str = entry['date']
        # Parse date like "10/26" or "11/1"
        month, day = map(int, date_str.split('/'))
        # Assume 2025 for October onwards
        year = 2025
        
        date_key = format_date(day, month, year)
        
        max_temp = parse_temperature(entry['temp_high'])
        min_temp = parse_temperature(entry['temp_low'])
        weather_desc = entry['weather']
        
        if max_temp is not None or min_temp is not None:
            weather_dict[date_key] = {
                'source': 'weather.com',
                'max_temp': max_temp,
                'min_temp': min_temp,
                'description': weather_desc if weather_desc != 'N/A' else None
            }
    
    return weather_dict

def merge_weather_data(accuweather_data, weathercom_data):
    """Merge data from both sources, calculating means where both exist"""
    all_dates = set(accuweather_data.keys()) | set(weathercom_data.keys())
    merged_data = []
    
    for date_key in sorted(all_dates):
        accu = accuweather_data.get(date_key)
        wcom = weathercom_data.get(date_key)
        
        entry = {'date': date_key}
        
        # Calculate mean temperatures where both sources have data
        if accu and wcom:
            # Both sources available - calculate mean
            max_temps = [t for t in [accu['max_temp'], wcom['max_temp']] if t is not None]
            min_temps = [t for t in [accu['min_temp'], wcom['min_temp']] if t is not None]
            
            entry['max_temp_celsius'] = round(sum(max_temps) / len(max_temps), 1) if max_temps else None
            entry['min_temp_celsius'] = round(sum(min_temps) / len(min_temps), 1) if min_temps else None
            entry['data_sources'] = ['accuweather', 'weather.com']
            
            # Include both descriptions
            descriptions = []
            if accu['description']:
                descriptions.append(f"AccuWeather: {accu['description']}")
            if wcom['description']:
                descriptions.append(f"Weather.com: {wcom['description']}")
            entry['weather_description'] = ' | '.join(descriptions) if descriptions else None
            
        elif accu:
            # Only AccuWeather data
            entry['max_temp_celsius'] = accu['max_temp']
            entry['min_temp_celsius'] = accu['min_temp']
            entry['data_sources'] = ['accuweather']
            entry['weather_description'] = accu['description']
            
        elif wcom:
            # Only Weather.com data
            entry['max_temp_celsius'] = wcom['max_temp']
            entry['min_temp_celsius'] = wcom['min_temp']
            entry['data_sources'] = ['weather.com']
            entry['weather_description'] = wcom['description']
        
        merged_data.append(entry)
    
    return merged_data

def main():
    # Load AccuWeather data
    print("Loading AccuWeather data...")
    october_accu = process_accuweather_data('./accuweather/october_weather_data.json', 10, 2025)
    november_accu = process_accuweather_data('./accuweather/november_weather_data.json', 11, 2025)
    december_accu = process_accuweather_data('./accuweather/december_weather_data.json', 12, 2025)
    
    # Combine all AccuWeather data
    accuweather_data = {**october_accu, **november_accu, **december_accu}
    print(f"  Loaded {len(accuweather_data)} days from AccuWeather")
    
    # Load Weather.com data
    print("Loading Weather.com data...")
    weathercom_data = process_weathercom_data('./weatherdotcom/timisoara_weather.json')
    print(f"  Loaded {len(weathercom_data)} days from Weather.com")
    
    # Merge data
    print("\nMerging data...")
    merged_data = merge_weather_data(accuweather_data, weathercom_data)
    
    # Create final output structure
    output = {
        'location': 'Timisoara, Romania',
        'temperature_unit': 'Celsius',
        'merged_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'total_days': len(merged_data),
        'sources': ['AccuWeather', 'Weather.com'],
        'note': 'When data from both sources is available for the same day, temperatures are averaged',
        'data': merged_data
    }
    
    # Save merged data
    output_path = './merged_weather_timisoara.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nMerged data saved to: {output_path}")
    print(f"Total days in merged dataset: {len(merged_data)}")
    
    # Print some statistics
    both_sources = sum(1 for d in merged_data if len(d.get('data_sources', [])) > 1)
    accu_only = sum(1 for d in merged_data if d.get('data_sources') == ['accuweather'])
    wcom_only = sum(1 for d in merged_data if d.get('data_sources') == ['weather.com'])
    
    print(f"\nData source breakdown:")
    print(f"  Both sources (averaged): {both_sources} days")
    print(f"  AccuWeather only: {accu_only} days")
    print(f"  Weather.com only: {wcom_only} days")

if __name__ == '__main__':
    main()