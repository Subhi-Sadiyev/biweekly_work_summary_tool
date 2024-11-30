### source table generator for all the logs combined
## needed for passing into GPT4o-mini through API
## should be triggered before main
import os
import pandas as pd
import configparser

## loading the config file
config = configparser.ConfigParser()
config.read('config.ini')


def combine_logs(root_directory, output_file='combined_work_logs.xlsx'):
    combined_data = []

    # Loop through each subfolder and file
    for subdir, _, files in os.walk(root_directory):
        for file in files:
            if file.endswith('.xlsx') or file.endswith('.xls'):
                file_path = os.path.join(subdir, file)
                user_name = os.path.basename(subdir)  # if sub-folder name represents the user

                xls = pd.ExcelFile(file_path)

                # Iterate through each sheet (each month)
                for sheet_name in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name=sheet_name)

                    # Add metadata columns for user and month
                    df['User'] = user_name
                    df['Month'] = sheet_name


                    # Convert the 'date' column to a consistent datetime format (DD.MM.YYYY)
                    if 'date' in df.columns:
                        df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce').dt.strftime('%d.%m.%Y')

                    combined_data.append(df[['User', 'Month', 'project_or_scope', 'time', 'notes', 'date']])

    # Concatenate all dataframes into a single DataFrame
    final_df = pd.concat(combined_data, ignore_index=True)

    # Save the combined data to a new Excel file
    final_df.to_excel(output_file, index=False)
    print("Data has been successfully combined and saved.")

if __name__ == "__main__":
    root_directory = config['paths']['root_directory'] ## update in config if working from another computer
    combine_logs(root_directory)