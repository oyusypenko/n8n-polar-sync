# n8n Python Code Node
import json
from datetime import datetime

# Get data from the previous node (array with data)
input_data = _input.all()[0]['json']

# Check data structure - can be array or object with nights
if isinstance(input_data, list):
    # If it's an array, take the first element
    if input_data and 'nights' in input_data[0]:
        sleep_data = input_data[0]['nights'][0]
    else:
        sleep_data = input_data[0]  # Direct array with sleep data
elif isinstance(input_data, dict) and 'nights' in input_data:
    # If it's an object with nights
    sleep_data = input_data['nights'][0]
else:
    # If it's a direct object with sleep data
    sleep_data = input_data

# Norms for comparison
NORMAL_RANGES = {
    'deep_sleep': (15, 20),
    'rem_sleep': (20, 25),  
    'light_sleep': (50, 65),
    'continuity': (4.0, 5.0),
    'sleep_efficiency': (85, 95)
}

def evaluate_range(value, normal_range):
    min_val, max_val = normal_range
    if value < min_val:
        return "low"
    elif value > max_val:
        return "high" 
    else:
        return "normal"

def format_minutes_to_hours_minutes(minutes):
    """Convert minutes to 'X hours Y minutes' format"""
    if minutes < 0:
        return f"-{format_minutes_to_hours_minutes(-minutes)}"
    
    hours = int(minutes // 60)
    remaining_minutes = int(minutes % 60)
    
    if hours == 0:
        return f"{remaining_minutes}m"
    elif remaining_minutes == 0:
        return f"{hours}h"
    else:
        return f"{hours}h {remaining_minutes}m"

# Basic calculations (all in seconds, convert to minutes)
light_sleep_sec = sleep_data.get('light_sleep', 0)
deep_sleep_sec = sleep_data.get('deep_sleep', 0)
rem_sleep_sec = sleep_data.get('rem_sleep', 0)
unrecognized_sec = sleep_data.get('unrecognized_sleep_stage', 0)

# Convert to minutes for all calculations
light_sleep_min = light_sleep_sec / 60
deep_sleep_min = deep_sleep_sec / 60
rem_sleep_min = rem_sleep_sec / 60
unrecognized_min = unrecognized_sec / 60

total_sleep_time_sec = light_sleep_sec + deep_sleep_sec + rem_sleep_sec
total_sleep_time_min = total_sleep_time_sec / 60

# Time
start_time = sleep_data.get('sleep_start_time', '')
end_time = sleep_data.get('sleep_end_time', '')

try:
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
    time_in_bed_sec = (end_dt - start_dt).total_seconds()
    time_in_bed_min = time_in_bed_sec / 60
except:
    time_in_bed_sec = total_sleep_time_sec + sleep_data.get('total_interruption_duration', 0)
    time_in_bed_min = time_in_bed_sec / 60

# Sleep efficiency
sleep_efficiency = (total_sleep_time_min / time_in_bed_min * 100) if time_in_bed_min > 0 else 0

# Sleep phases
if total_sleep_time_min > 0:
    light_pct = (light_sleep_min / total_sleep_time_min) * 100
    deep_pct = (deep_sleep_min / total_sleep_time_min) * 100
    rem_pct = (rem_sleep_min / total_sleep_time_min) * 100
    unrecognized_pct = (unrecognized_min / total_sleep_time_min) * 100 if unrecognized_min > 0 else 0
else:
    light_pct = deep_pct = rem_pct = unrecognized_pct = 0

# Evaluations
deep_status = evaluate_range(deep_pct, NORMAL_RANGES['deep_sleep'])
rem_status = evaluate_range(rem_pct, NORMAL_RANGES['rem_sleep'])
light_status = evaluate_range(light_pct, NORMAL_RANGES['light_sleep'])
continuity_status = evaluate_range(sleep_data.get('continuity', 0), NORMAL_RANGES['continuity'])

# Sleep quality
interruptions_min = sleep_data.get('total_interruption_duration', 0) // 60
short_interruptions_min = sleep_data.get('short_interruption_duration', 0) // 60
long_interruptions_min = sleep_data.get('long_interruption_duration', 0) // 60

# Hypnogram
hypnogram = sleep_data.get('hypnogram', {})
wake_episodes = sum(1 for value in hypnogram.values() if value == 0) if hypnogram else 0

# Basic metrics (all in minutes)
sleep_goal_sec = sleep_data.get('sleep_goal', 28800)  # Default 8 hours in seconds
sleep_goal_min = sleep_goal_sec / 60
sleep_deficit_min = max(0, sleep_goal_min - total_sleep_time_min)  # Only positive deficit
sleep_surplus_min = max(0, total_sleep_time_min - sleep_goal_min)  # Extra sleep

# Science-based recommendations using Polar data and modern research
recommendations = []

# 1. Sleep duration recommendations (based on scientific data)
if sleep_deficit_min > 30:
    recommendations.append(f"🕐 Increase sleep time by {format_minutes_to_hours_minutes(sleep_deficit_min)} for optimal recovery")
elif total_sleep_time_min < 360:  # less than 6 hours
    recommendations.append("🕐 Critically low sleep - aim for 7-9 hours for adults")
elif sleep_data.get('group_duration_score', 100) < 80:  # softer threshold
    recommendations.append("🕐 Sleep duration consistency is more important than perfect amount")

# 2. Continuity recommendations (based on Polar documentation)
continuity_val = sleep_data.get('continuity', 0)
continuity_class = sleep_data.get('continuity_class', 0)

# Using official Polar descriptions
if continuity_class == 1 or continuity_val < 2.0:
    recommendations.append("😴 Fragmented sleep: check mattress, pillow and room temperature (16-19°C)")
elif continuity_class == 2 or continuity_val < 3.0:
    recommendations.append("😴 Fairly fragmented sleep: limit noise and light, avoid caffeine after 2 PM")
elif continuity_class == 3 or continuity_val < 4.0:
    recommendations.append("😴 Moderate continuity: create consistent bedtime ritual")

# 3. Sleep phase recommendations (based on validated Polar data)
regeneration_score = sleep_data.get('group_regeneration_score', 100)

# Deep sleep recommendations (Polar: optimal ~17% for maximum score)
if deep_status == "low" or deep_pct < 13:
    recommendations.append("🛌 Low deep sleep: maintain regular sleep schedule, avoid alcohol 3 hours before bed")
    if total_sleep_time_min > 0:
        recommendations.append("🛌 For deep sleep: go to bed before midnight when main recovery occurs")

# REM sleep recommendations (Polar: optimal ~25% for maximum score)
if rem_status == "low" or rem_pct < 18:
    recommendations.append("🧠 Low REM sleep: manage stress, avoid intense workouts before bed")
    recommendations.append("🧠 REM sleep is crucial for memory: maintain stable wake time")

# 4. Sleep efficiency (scientifically validated 85% threshold)
if sleep_efficiency < 85:
    recommendations.append("⚡ Low sleep efficiency: only go to bed when feeling sleepy")
    recommendations.append("⚡ 20-minute rule: if not asleep in 20 min - get up and do quiet activity")

# 5. Sleep interruption recommendations (based on Polar documentation)
long_interruptions_min = sleep_data.get('long_interruption_duration', 0) / 60
short_interruptions_min = sleep_data.get('short_interruption_duration', 0) / 60

# Polar: long awakenings ≥90 seconds, average ~15 minutes per night
if long_interruptions_min > 20:  # above average + margin
    recommendations.append("🚫 Frequent long awakenings: consult doctor to rule out sleep apnea")
elif long_interruptions_min > 15:
    recommendations.append("🚫 Long awakenings: check bed comfort and eliminate external disturbances")

# 6. Sleep charge (personal Polar metric)
sleep_charge = sleep_data.get('sleep_charge', 3)
if sleep_charge <= 2:
    recommendations.append("📈 Sleep quality below usual: analyze recent lifestyle changes")
    if continuity_val < 3.0:
        recommendations.append("📈 Consider relaxation techniques before bed (meditation, breathing exercises)")
elif sleep_charge >= 4:
    recommendations.append("✨ Excellent sleep quality! Continue current habits")

# 7. Heart rate analysis (based on HRV during sleep research)
heart_rate_samples = sleep_data.get('heart_rate_samples', {})
if heart_rate_samples:
    hr_values = list(heart_rate_samples.values())
    if hr_values:
        avg_hr = sum(hr_values) / len(hr_values)
        # More individualized approach instead of fixed 70 threshold
        # Consider age and fitness level
        estimated_resting_hr = 60 + (max(0, 30 - 20) * 0.5)  # approximate formula
        
        if avg_hr > estimated_resting_hr * 1.3:  # 30% above estimated
            recommendations.append("❤️ Elevated sleep heart rate: check room temperature, stress levels")
            recommendations.append("❤️ Consider stress reduction techniques and medical consultation")

# 8. Sleep cycle recommendations (scientific data: 4-5 cycles per night)
sleep_cycles = sleep_data.get('sleep_cycles', 0)
if sleep_cycles < 3 and total_sleep_time_min > 300:  # if slept more than 5 hours but few cycles
    recommendations.append("🔄 Few sleep cycles: possible fragmentation, check sleep conditions")
elif sleep_cycles > 6:
    recommendations.append("🔄 Many short cycles: possible frequent micro-awakenings")

# 9. Special recommendations based on patterns
total_interruption_min = sleep_data.get('total_interruption_duration', 0) / 60
if total_interruption_min > total_sleep_time_min * 0.15:  # more than 15% time in awakenings
    recommendations.append("⚠️ Significant sleep fragmentation: consider specialist consultation")

# 10. Positive reinforcements (important for motivation)
if sleep_efficiency >= 90 and continuity_val >= 4.0:
    recommendations.append("🌟 Excellent sleep architecture - your habits are working perfectly!")

if deep_pct >= 15 and rem_pct >= 20:
    recommendations.append("🌟 Optimal sleep phase ratio for recovery")

# Time formatting
try:
    start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    start_time_str = start_dt.strftime('%H:%M')
    end_time_str = datetime.fromisoformat(end_time.replace('Z', '+00:00')).strftime('%H:%M')
    date_str = start_dt.strftime('%d/%m/%Y')
except:
    start_time_str = "N/A"
    end_time_str = "N/A"
    date_str = sleep_data.get('date', 'N/A')

# Prepare sleep balance text
if sleep_deficit_min > 0:
    sleep_balance_text = f"Deficit: {format_minutes_to_hours_minutes(sleep_deficit_min)}"
elif sleep_surplus_min > 0:
    sleep_balance_text = f"Surplus: {format_minutes_to_hours_minutes(sleep_surplus_min)}"
else:
    sleep_balance_text = "Goal achieved!"

# Report generation
report = f"""
  SLEEP ANALYSIS - {date_str}                     

🕐 SLEEP TIME:
   Bedtime: {start_time_str} | Wake time: {end_time_str}
   Time in bed: {format_minutes_to_hours_minutes(time_in_bed_min)}
   Actual sleep: {format_minutes_to_hours_minutes(total_sleep_time_min)}
   Sleep goal: {format_minutes_to_hours_minutes(sleep_goal_min)}
   {sleep_balance_text}
   Efficiency: {sleep_efficiency:.1f}%

🧠 SLEEP PHASES:
   • Light:  {format_minutes_to_hours_minutes(light_sleep_min)}  ({light_pct:.1f}%) (Normal: 44-65%)
   • Deep: {format_minutes_to_hours_minutes(deep_sleep_min)} ({deep_pct:.1f}%) (Normal: 17-20%)
   • REM:     {format_minutes_to_hours_minutes(rem_sleep_min)} ({rem_pct:.1f}%) (Normal: 20-25%)
   • Unrecognized: {format_minutes_to_hours_minutes(unrecognized_min)} ({unrecognized_pct:.1f}%) (Normal: 0-10%)

📊 SLEEP QUALITY:
   Overall score: {sleep_data.get('sleep_score', 0)}/100
   Continuity: {sleep_data.get('continuity', 0):.1f}/5.0 [{continuity_status}]
   Sleep cycles: {sleep_data.get('sleep_cycles', 0)}
   Sleep charge: {sleep_data.get('sleep_charge', 0)}/5 (vs usual level)

⚠️  AWAKENINGS:
   • Wake episodes: {wake_episodes}

💡 RECOMMENDATIONS:"""

for i, rec in enumerate(recommendations, 1):
    report += f"\n   {i}. {rec}"

if not recommendations:
    report += "\n   ✅ Excellent sleep quality! Keep it up."

date_iso = end_dt.strftime('%Y-%m-%d')  # ISO format for return
# Return array of dictionaries for n8n
return [{
    'json': {
        'message': report,
        'date': date_iso
    }
}]