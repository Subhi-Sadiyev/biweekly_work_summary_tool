### generates the dates of biweekly meetings
## dates are used to send summaries on schedule
 
from datetime import datetime, timedelta

def generate_repeating_dates(interval_days=14, duration_days=365):
    """
    Generates a static schedule of repeating biweekly meeting dates with assigned employees.

    Parameters:
        interval_days (int): Interval between each repeating date in days (default is 14).
        duration_days (int): Total duration in days for which dates are generated (default is 365).

    Returns:
        dict: Dictionary with start date labels as keys and tuples of datetime objects and employee lists as values.
        list: Flattened list of all dates generated for easier selection.
    """
    # Static initial dates and employees
    meeting_schedule = {
        datetime(2024, 11, 30): ["employee1", "employee2", "employee3"],
    }

    interval = timedelta(days=interval_days)
    num_cycles = duration_days // interval_days  # Number of cycles to cover the duration

    # Dictionary to store repeating dates with associated employees
    calendar_dates = {}

    # Fill the dictionary with dates and employees
    for start_date, employees in meeting_schedule.items():
        current_date = start_date
        date_list = []
        
        for _ in range(num_cycles):
            date_list.append((current_date, employees))  # Store the date with associated employees
            current_date += interval
        
        calendar_dates[start_date.strftime("%B %d")] = date_list

    # Flatten the dates into a list for easier selection
    all_dates = [date for dates in calendar_dates.values() for date, _ in dates]
    

    return calendar_dates, all_dates