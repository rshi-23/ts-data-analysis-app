import tkinter as tk
from tkinter import filedialog
import glob
from ts_data_analysis_functions import *

root = tk.Tk()
# gets rid of tk window
root.withdraw()
root.attributes("-topmost", True)

# asks for the directory with all the RAW DATA csv files
print('Please open the directory that has all the raw data csv files')
file_path = filedialog.askdirectory()

# passes the folder directory and compiles all the csv files into ONE csv file
pattern = file_path + '\\*'
files = glob.glob(pattern)

try:
    # read the first csv file in the folder
    df = pd.read_csv(files[0], encoding='utf-8', delimiter=',')
    # append all the other csv files onto the current dataframe
    for file in files[1:len(files)]:
        df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
        df = df.append(df_csv)

    # get rid of the timestamp from the SCHEDULE DATE column
    df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date

    # sort the csv file by date and animal id in ascending order
    df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

    # reset the indices of the combined csv file
    df.reset_index(drop=True, inplace=True)

    # creates the merged_file in the same folder as this script, use to help double check deleted duplicates
    try:
        print('A file called "merged_file.csv" has been created in the same directory as the script!')
        df.to_csv('merged_file.csv', index=True)
    except PermissionError:
        print('You may have the merged_file.csv already open! Please close it!')

    # sort by trial number and runtime
    df = df.sort_values(by=['End Summary - Trials Completed (1)', 'End Summary - Condition (1)'])

    # create a dataframe that holds the duplicates
    df_duplicates = pd.DataFrame()
    duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
    df_duplicates = df_duplicates.append(df.loc[duplicates])
    # sort the duplicates
    df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

    try:
        print('A file called "dropped_duplicates.csv" has been created in the same directory!')
        df_duplicates.to_csv('dropped_duplicates.csv', index=True)
    except PermissionError:
        print('You may have the dropped_duplicates.csv already open! Please close it!')

    # actually drop the duplicates from the current dataframe and sort the values again
    df = df.drop_duplicates(subset=['Schedule run date', 'Animal ID'],
                            keep='last')
    df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

    # reset the index again
    df.reset_index(drop=True, inplace=True)

    print('The program is running... Please wait....')

    # all the headers in the raw data file
    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    convert_to_int(all_numeric_values, raw_data_headers, df)

    # the next few lines are all indice ranges for specific column headers

    # the mm/dd/yyyy of the program
    date_header = index_range('Schedule run date', raw_data_headers, df)
    # the correct trials
    number_correct_header = index_range('Trial Analysis - No. Correct (', raw_data_headers, df)
    # the animal id
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    # LD test type: 7&11 = easy, 8&11 = intermediate, 9&10 = hard
    correct_position_header = index_range('Trial Analysis - Correct Position (', raw_data_headers, df)
    # the duration of the test
    session_length_header = index_range('End Summary - Session Time (1)', raw_data_headers, df)
    # the number of completed trials during the test
    trials_completed_header = index_range('End Summary - Trials Completed (1)', raw_data_headers, df)
    # the percentage correct of the test
    percent_correct_header = index_range('End Summary - Percentage Correct (1)', raw_data_headers, df)
    # the amount of reversals reached
    reversal_number_header = index_range('End Summary - Times Criteria reached (1)', raw_data_headers, df)
    # the total amount of ITI blank touches
    iti_blank_header = index_range('End Summary - Left ITI touches (1)', raw_data_headers, df) + \
                       index_range('End Summary - Right ITI touches (1)', raw_data_headers, df)
    # the total amount of blank touches
    blank_header = index_range('End Summary - Left Blank Touches - Generic Counter (1)', raw_data_headers, df) + \
                   index_range('End Summary - Right Blank Touches - Generic Counter (1)', raw_data_headers, df) + \
                   index_range('End Summary - Top row touches - Generic Counter (1)', raw_data_headers, df)
    # the average time to collect reward
    mean_reward_header = index_range('Trial Analysis - Reward Collection Latency (', raw_data_headers, df)
    # the average time to correctly touch
    mean_correct_touch_header = index_range('Trial Analysis - Correct Image Response Latency (', raw_data_headers, df)
    # the average time to incorrectly touch
    mean_incorrect_header = index_range('Trial Analysis - Incorrect Image Latency (', raw_data_headers, df)
    # the time it takes to reach first reversal
    first_reversal_time_header = index_range('No trials to criterion - Condition (1)', raw_data_headers, df)
    # the time it takes to reach second reversal
    second_reversal_time_header = index_range('No trials to criterion - Condition (2)', raw_data_headers, df)
    # the trials it takes to reach first reversal
    first_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (1)', raw_data_headers, df)
    # the trials it takes to reach second reversal
    second_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (2)', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'Type', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                 'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                 'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                 'SessionLengthTo2ndReversalDuration',
                 'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                 'PercentCorrectTo2ndReversal']

    df_final = pd.DataFrame(columns=col_names)

    # get the date for each row
    df_final['Date'] = df.iloc[:, date_header[0]]
    # get the animal id for each row
    df_final['ID'] = df.iloc[:, animal_id_header[0]]

    # get the test type for each row
    df['Type'] = ''
    correct_position_names = get_header_names(raw_data_headers, correct_position_header)
    get_test_type(df, correct_position_names)
    df_final['Type'] = df['Type']

    # get the session time for each row
    df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
    # get the number of trials for each row
    df_final['NumberOfTrial'] = df.iloc[:, trials_completed_header[0]]
    # get the percent correctness for each row
    df_final['PercentCorrect'] = df.iloc[:, percent_correct_header]
    # get the number of reversals for each row
    df_final['NumberOfReversal'] = df.iloc[:, reversal_number_header[0]]
    # get the iti touches for each row
    df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
    # get the blank touches for each row
    df_final['TotalBlankTouches'] = df.iloc[:, blank_header].sum(axis=1)
    # get the avg reward collection time for each row
    df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
    # get the avg correct touch time for each row
    df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
    # get the avg incorrect touch time for each row
    df_final['MeanIncorrectTouchLatency'] = df.iloc[:, mean_incorrect_header].mean(axis=1)
    # get the session time to first reversal for each row
    df_final['SessionLengthTo1stReversalDuration'] = df.iloc[:, first_reversal_time_header[0]]
    # get the session time to second reversal for each row
    df_final['SessionLengthTo2ndReversalDuration'] = df.iloc[:, second_reversal_time_header[0]]
    # get the number of trials for first reversal for each row
    df_final['NumberOfTrialTo1stReversal'] = df.iloc[:, first_reversal_trials_header[0]]
    # get the number of trials for second reversal for each row
    df_final['NumberOfTrialTo2ndReversal'] = df.iloc[:, second_reversal_trials_header[0]]

    # fix the reversal number trials
    get_missing_reversal_trials(df_final, col_names)
    # fixed the session time to be duration for each
    get_fixed_session_time(df_final)

    # get the column headers of the trial numbers
    number_correct_column_names = get_header_names(raw_data_headers, number_correct_header)

    # get the percent correctness for first reversal for each row
    df['PercentCorrectTo1stReversal'] = np.nan
    get_percent_correctness_first(df, number_correct_column_names)
    df_final['PercentCorrectTo1stReversal'] = df['PercentCorrectTo1stReversal']

    # get the percent correctness for second reversal for each row
    df['PercentCorrectTo2ndReversal'] = np.nan
    get_percent_correctness_second(df, df_final, number_correct_column_names)
    df_final['PercentCorrectTo2ndReversal'] = df['PercentCorrectTo2ndReversal']

    print('The program is almost done running... Please wait....')

    program_type = input('Please enter if you want LD Train (1) or LD Probe (2): ')
    if program_type == '1':
        # for ld train, we want only intermediate, delete all others
        df_final.drop(df_final.loc[df_final['Type'] == 'hard'].index, inplace=True)
        df_final.drop(df_final.loc[df_final['Type'] == 'easy'].index, inplace=True)
        df_final.drop(df_final.loc[df_final['Type'] == 'undetermined'].index, inplace=True)
        try:
            print('A window has opened asking for you to save your newly created csv file. Please look for it!')
            save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
            df_final.to_csv(save_file_path, index=False)
            print('A .csv file has been created. Please look at it in the saved directory!')
        except FileNotFoundError:
            print('You closed the window before saving! Please run the program again!')
        print('The program has ended!')
    elif program_type == '2':
        # for ld probe, we only want columns that are 'easy' or 'hard', delete all other test rows
        df_final.drop(df_final.loc[df_final['Type'] == 'intermediate'].index, inplace=True)
        df_final.drop(df_final.loc[df_final['Type'] == 'undetermined'].index, inplace=True)
        get_last_day_difficulty(df_final)
        try:
            print('A window has opened asking for you to save your newly created csv file. Please look for it!')
            save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
            df_final.to_csv(save_file_path, index=False)
            print('A .csv file has been created. Please look at it in the saved directory!')
        except FileNotFoundError:
            print('You closed the window before saving! Please run the program again!')
        print('The program has ended!')
    else:
        raise ValueError('You input an invalid value! Please input 1 for LD Train or 2 for LD Probe!')
except PermissionError:
    print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')
