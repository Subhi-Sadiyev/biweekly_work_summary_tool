import pandas as pd
from openai import OpenAI
from datetime import datetime, timedelta
from smtp import send_email
from calendars import generate_repeating_dates
import configparser ## for importing credentials
from combined_logs import combine_logs ##custom function
import traceback
import logging


## loading the config file
config = configparser.ConfigParser()
config.read('config.ini')

## loading and combination of work logs
root_directory = config['paths']['root_directory'] 
combine_logs(root_directory)

client = OpenAI(
    organization=config['openai']['organization'],
    project=config['openai']['project'],
    api_key=config['openai']['api_key']
    )

# Read the Excel file
file_path = r"combined_work_logs.xlsx"  ## local directory
excel_data = pd.read_excel(file_path)

# Prepare the data for analysis
excel_data['date'] = pd.to_datetime(excel_data['date'], dayfirst=True)
last_two_weeks = datetime.now() - timedelta(weeks=2)
excel_data = excel_data[excel_data['date'] >= last_two_weeks]
employee_group = excel_data.groupby('User')

# Export the last two weeks' data to Excel for testing
excel_data.to_excel("last_two_weeks_data.xlsx", index=False)
print("Filtered data for the last two weeks has been exported to 'last_two_weeks_data.xlsx'")


# Generate the calendar dates and all repeating dates
calendar_dates, all_dates = generate_repeating_dates()

# Create summaries for all employees
all_summaries = {}


for employee, group in employee_group:
    # Summarize contribution areas and prepare summary content
    projects_worked_on = group['project_or_scope'].nunique()
    project_counts = group['project_or_scope'].value_counts()
    most_focused_project = project_counts.idxmax() if not project_counts.empty else "None"
    total_days_worked = group['date'].nunique()
    work_entries_count = group.shape[0]
    
    # Summarize work notes
    notes_content = "\n".join([str(note) for note in group['notes'].unique() if pd.notna(note)])
    if notes_content:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant for the team manager. Please summarize the following work notes of employee or employees into key contribution areas. Only summarize or rephrase existing information and avoid adding extra details not found in the original notes. If the notes only include a single sentence, make minimal assumptions about what that could mean."},
                {"role": "user", "content": notes_content}
            ],

            temperature=0.0   # Setting temperature to 0 to make the output more deterministic and factual
        )
        summarized_contribution_areas = completion.choices[0].message.content
    else:
        summarized_contribution_areas = "No significant contributions noted."

    # Build summary text
    summary = (
        f"### Work Summary for {employee} (Last Two Weeks)\n\n"
        f"#### Overview\n"
    )

    if projects_worked_on > 0:
        summary += (
            f"In the last two weeks, {employee} has contributed to **{projects_worked_on} project{'s' if projects_worked_on > 1 else ''}**. The primary focus has been on **{most_focused_project}**.\n"
            f"#### Project Breakdown\n"
        )

        for project, count in project_counts.items():
            project_entries = group[group['project_or_scope'] == project]
            project_notes = "\n".join([str(note) for note in project_entries['notes'].unique() if pd.notna(note)])
            if project_notes:
                project_summary = summarized_contribution_areas if project in summarized_contribution_areas else "No significant contributions noted for this project."
            else:
                project_summary = "No significant contributions noted for this project."

            summary += (
                f"1. **{project}**\n"
                f"   - **Entries**: {count}\n"
                f"   - **Summary**: {project_summary}\n\n"
            )

        summary += (
            f"#### Insights and Metrics\n"
            f"- **Total Days Worked**: {total_days_worked} days\n"
            f"- **Total Work Entries**: {work_entries_count} entries\n"
            f"- **Key Contribution Areas**: {summarized_contribution_areas}\n\n"
        )
    else:
        summary += "No projects were worked on during this period.\n\n"

    summary += (
        f"#### Conclusion\n"
        f"{employee} demonstrated {('involvement in ' + ('a project' if projects_worked_on == 1 else 'multiple projects') + ', with particular emphasis on **' + most_focused_project + '**') if projects_worked_on > 0 else 'no significant contributions during the last two weeks.'}"
    )
    all_summaries[employee] = summary
    

# Main flow, trigger
if __name__ == "__main__":
    today = datetime.now().date()

    # Check if today matches any scheduled date
    for start_label, date_list in calendar_dates.items():
        for date, employees in date_list:
            if today == date.date():
                # Select summaries for only the scheduled employees for today
                summaries = [all_summaries[emp] for emp in employees if emp in all_summaries]

                # Email configuration
                subject = "Biweekly Work Summary"
                to_email = config['smtp']['to_email']
                from_email = config['smtp']['from_email']
                cc_email = config['smtp']['cc_email']
                password = config['smtp']['password']
                

                # Concatenate selected summaries into a single email body
                body = "\n\n".join(summaries)

                try:
                    send_email(subject=subject,
                                body=body, 
                                to_email=to_email,
                                cc_email=cc_email, 
                                from_email=from_email,
                                password=password)
                    print("Email sent")
                except Exception as e:
                    logging.error(f"An error occurred while sending the email: {e}")
                    logging.error(traceback.format_exc())