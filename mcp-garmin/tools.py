
def list_tools():
    return [
        {"name":"garmin.sync","description":"Runs a full daily sync of all metrics for today.","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":[]}},
        {"name":"garmin.get_stats","description":"Daily stats for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_user_summary","description":"User summary for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_stats_and_body","description":"Stats + body composition","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_steps_data","description":"Steps for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_heart_rates","description":"Heart rate time series for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_resting_heart_rate","description":"Resting HR for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_sleep_data","description":"Sleep for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_all_day_stress","description":"Stress for a given date","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_training_readiness","description":"Training readiness","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_training_status","description":"Training status","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_respiration_data","description":"Respiration","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_spo2_data","description":"SpO2","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_max_metrics","description":"VO2max/Fitness age","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_hrv_data","description":"HRV","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_fitnessage_data","description":"Fitness age metrics","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_stress_data","description":"Stress summary","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_lactate_threshold","description":"Lactate threshold","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_intensity_minutes_data","description":"Intensity minutes","input_schema":{"type":"object","properties":{"date":{"type":"string","format":"date"}},"required":["date"]}},
        {"name":"garmin.get_activities_range","description":"Activities for a date range (defaults to last 7 days if none)","input_schema":{"type":"object","properties":{"start_date":{"type":"string","format":"date"},"end_date":{"type":"string","format":"date"}}}}
    ]
