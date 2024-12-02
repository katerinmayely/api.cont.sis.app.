from datetime import timedelta

def convert_minutes_to_time(minutes):
    
    minutes_in_year = 525600  # 60 * 24 * 365
    minutes_in_month = 43200  # 60 * 24 * 30
    minutes_in_day = 1440   
    minutes_in_hour = 60 
    
    # Calcular los años, meses, días y minutos equivalentes
    years = minutes // minutes_in_year

    months = minutes // minutes_in_month
    
    days = minutes // minutes_in_day
    
    hours = minutes // minutes_in_hour
    
    return years, months, days, hours