import tkinter.filedialog as filedialog
import os
from setuptools import glob
from setup_functions import *


def data_setup():
    # asks for the directory with all the RAW DATA csv files
    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')
    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return

    # passes the folder directory and compiles all the csv files into ONE csv file

    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    original_location = os.getcwd()
    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        # read the first csv file in the folder
        try:
            df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
        except IndexError:
            print('Either the directory is empty or does not contain any .csv files!')
            return
        # append all the other csv files onto the current dataframe
        for file in files[1:len(files)]:
            if not file.startswith('.'):
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
            print(
                'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
                script_location)
            df.to_csv('merged_file.csv', index=True)
        except PermissionError:
            print('You may have the merged_file.csv already open! Please close it!')
            return

        # sort by trial number and runtime
        df = df.sort_values(by=['End Summary - Trials Completed (1)', 'End Summary - Condition (1)'])

        # create a dataframe that holds the duplicates
        df_duplicates = pd.DataFrame()
        duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
        df_duplicates = df_duplicates.append(df.loc[duplicates])
        # sort the duplicates
        df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        try:
            print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
                  script_location)
            df_duplicates.to_csv('dropped_duplicates.csv', index=True)
        except PermissionError:
            print('You may have the dropped_duplicates.csv already open! Please close it!')
            return

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

        # headername_list = get_header_names(raw_data_headers, number_correct_header)
        # print(headername_list)

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
        mean_correct_touch_header = index_range('Trial Analysis - Correct Image Response Latency (', raw_data_headers,
                                                df)
        # the average time to incorrectly touch
        mean_incorrect_header = index_range('Trial Analysis - Incorrect Image Latency (', raw_data_headers, df)
        # the time it takes to reach first reversal
        first_reversal_time_header = index_range('No trials to criterion - Condition (1)', raw_data_headers, df)
        # the time it takes to reach second reversal
        second_reversal_time_header = index_range('No trials to criterion - Condition (2)', raw_data_headers, df)
        # the trials it takes to reach first reversal
        first_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (1)', raw_data_headers,
                                                   df)
        # the trials it takes to reach second reversal
        second_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (2)', raw_data_headers,
                                                    df)

        print('The program is still running... Please wait....')

        col_names = ['Date', 'ID', 'Type', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        df_final = pd.DataFrame(columns=col_names)

        try:
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
            get_fixed_session_time(df_final, df)

            # get the column headers of the trial numbers
            number_correct_column_names = get_header_names(raw_data_headers, number_correct_header)

            # get the percent correctness for first reversal for each row
            df['PercentCorrectTo1stReversal'] = np.nan
            get_percent_correctness_first(df, df_final, number_correct_column_names)
            df_final['PercentCorrectTo1stReversal'] = df['PercentCorrectTo1stReversal']

            # get the percent correctness for second reversal for each row
            df['PercentCorrectTo2ndReversal'] = np.nan
            get_percent_correctness_second(df, df_final, number_correct_column_names)
            df_final['PercentCorrectTo2ndReversal'] = df['PercentCorrectTo2ndReversal']
        except IndexError or KeyError or ValueError:
            print('Either you selected the wrong type of test or headers are not the same on all files!')
            return

        print('The program is almost done running... Please wait....')

        return df_final
    except PermissionError:
        print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')


def data_setup_gts(gts_type):
    # asks for the directory with all the RAW DATA csv files
    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')
    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return
    # passes the folder directory and compiles all the csv files into ONE csv file

    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    original_location = os.getcwd()
    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        # read the first csv file in the folder
        try:
            df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
        except IndexError:
            print('Either the directory is empty or does not contain any .csv files!')
            return
        # append all the other csv files onto the current dataframe
        for file in files[1:len(files)]:
            if not file.startswith('.'):
                df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
                df = df.append(df_csv)

        if gts_type == 'IT':
            df = df.loc[df['Schedule name'] == 'Mouse LD Initial Touch Training v2']
        if gts_type == 'MI':
            df = df.loc[df['Schedule name'] == 'Mouse LD Must Initiate Training v2']
        if gts_type == 'MT':
            df = df.loc[df['Schedule name'] == 'Mouse LD Must Touch Training v2']

        # get rid of the timestamp from the SCHEDULE DATE column
        df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date

        # sort the csv file by date and animal id in ascending order
        df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        # reset the indices of the combined csv file
        df.reset_index(drop=True, inplace=True)

        # creates the merged_file in the same folder as this script, use to help double check deleted duplicates
        try:
            print(
                'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
                script_location)
            df.to_csv('merged_file.csv', index=True)
        except PermissionError:
            print('You may have the merged_file.csv already open! Please close it!')
            return

        # sort by trial number and runtime
        df = df.sort_values(by=['End Summary - Condition (1)'])

        # create a dataframe that holds the duplicates
        df_duplicates = pd.DataFrame()
        duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
        df_duplicates = df_duplicates.append(df.loc[duplicates])

        # sort the duplicates
        df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        try:
            print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
                  script_location)
            df_duplicates.to_csv('dropped_duplicates.csv', index=True)
        except PermissionError:
            print('You may have the dropped_duplicates.csv already open! Please close it!')
            return

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

        # the mm/dd/yyyy of the program
        date_header = index_range('Schedule run date', raw_data_headers, df)
        # the animal id
        animal_id_header = index_range('Animal ID', raw_data_headers, df)
        # session length
        session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
        # corects
        correct_header = index_range('End Summary - Corrects (1)', raw_data_headers, df)
        # blank touches
        blank_touches_header = index_range('End Summary - Blank Touches (1)', raw_data_headers, df)
        # total iti touches
        iti_blank_header = index_range('End Summary - Left ITI touches (1)', raw_data_headers, df) + \
                           index_range('End Summary - Right ITI touches (1)', raw_data_headers, df)
        # the average time to correctly touch
        mean_correct_touch_header = index_range('Correct touch latency (', raw_data_headers,
                                                df)
        mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
        # the average time to collect reward
        mean_reward_header = index_range('Correct Reward Collection (', raw_data_headers, df)

        print('The program is still running... Please wait....')

        col_names = ['Date', 'ID', 'SessionLength', 'Corrects', 'TotalBlankTouches', 'TotalITITouches',
                     'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency']

        df_final = pd.DataFrame(columns=col_names)

        try:
            # get the date for each row
            df_final['Date'] = df.iloc[:, date_header[0]]
            # get the animal id for each row
            df_final['ID'] = df.iloc[:, animal_id_header[0]]
            # get the session time for each row
            df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
            df_final['Corrects'] = df.iloc[:, correct_header[0]]
            df_final['TotalBlankTouches'] = df.iloc[:, blank_touches_header].sum(axis=1)
            # get the iti touches for each row
            df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
            df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
            df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
            df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
        except IndexError or KeyError or ValueError:
            print('Either you selected the wrong type of test or headers are not the same on all files!')
            return
        print('The program is almost done running... Please wait....')

        return df_final

    except PermissionError:
        print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')


def data_setup_pi():
    # asks for the directory with all the RAW DATA csv files
    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')
    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return

    # passes the folder directory and compiles all the csv files into ONE csv file
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    original_location = os.getcwd()
    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        # read the first csv file in the folder
        try:
            df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
        except IndexError:
            print('Either the directory is empty or does not contain any .csv files!')
            return
        # append all the other csv files onto the current dataframe
        for file in files[1:len(files)]:
            if not file.startswith('.'):
                df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
                df = df.append(df_csv)

        df = df.loc[df['Schedule name'] == 'Mouse LD Punish Incorrect Training v2']

        # get rid of the timestamp from the SCHEDULE DATE column
        df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date

        # sort the csv file by date and animal id in ascending order
        df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        # reset the indices of the combined csv file
        df.reset_index(drop=True, inplace=True)

        # creates the merged_file in the same folder as this script, use to help double check deleted duplicates
        try:
            print(
                'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
                script_location)
            df.to_csv('merged_file.csv', index=True)
        except PermissionError:
            print('You may have the merged_file.csv already open! Please close it!')
            return

        # sort by trial number and runtime
        df = df.sort_values(by=['End Summary - Condition (1)'])

        # create a dataframe that holds the duplicates
        df_duplicates = pd.DataFrame()
        duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
        df_duplicates = df_duplicates.append(df.loc[duplicates])

        # sort the duplicates
        df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        try:
            print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
                  script_location)
            df_duplicates.to_csv('dropped_duplicates.csv', index=True)
        except PermissionError:
            print('You may have the dropped_duplicates.csv already open! Please close it!')
            return

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

        # the mm/dd/yyyy of the program
        date_header = index_range('Schedule run date', raw_data_headers, df)
        # the animal id
        animal_id_header = index_range('Animal ID', raw_data_headers, df)
        # session length
        session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
        # total trials completed
        trial_completed_header = index_range('End Summary - Trials Completed (1)', raw_data_headers, df)
        # percent correct of trials
        percent_correct_headers = index_range('End Summary - % Correct (1)', raw_data_headers, df)
        # total iti touches
        iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + \
                           index_range('End Summary - Right ITI Touches (1)', raw_data_headers, df)
        # the average time to correctly touch
        mean_correct_touch_header = index_range('Correct touch latency (', raw_data_headers,
                                                df)
        mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
        # the average time to collect reward
        mean_reward_header = index_range('Correct Reward Collection (', raw_data_headers, df)

        print('The program is still running... Please wait....')

        col_names = ['Date', 'ID', 'SessionLength', 'TotalTrials', 'PercentCorrect', 'TotalITITouches',
                     'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency']

        df_final = pd.DataFrame(columns=col_names)
        try:
            # get the date for each row
            df_final['Date'] = df.iloc[:, date_header[0]]
            # get the animal id for each row
            df_final['ID'] = df.iloc[:, animal_id_header[0]]
            # get the session time for each row
            df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
            df_final['TotalTrials'] = df.iloc[:, trial_completed_header[0]]
            df_final['PercentCorrect'] = df.iloc[:, percent_correct_headers]
            # get the iti touches for each row
            df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
            df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
            df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
            df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
        except IndexError or KeyError or ValueError:
            print('Either you selected the wrong type of test or headers are not the same on all files!')
            return
        print('The program is almost done running... Please wait....')

        return df_final

    except PermissionError:
        print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')


def data_setup_acq():
    # asks for the directory with all the RAW DATA csv files
    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')
    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return

    # passes the folder directory and compiles all the csv files into ONE csv file

    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    original_location = os.getcwd()
    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        # read the first csv file in the folder
        try:
            df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
        except IndexError:
            print('Either the directory is empty or does not contain any .csv files!')
            return
        # append all the other csv files onto the current dataframe
        for file in files[1:len(files)]:
            if not file.startswith('.'):
                df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
                df = df.append(df_csv)

        df = df.loc[df['Schedule name'] == 'Mouse Extinction pt 1 v2']

        # df = df.loc[~(df['End Summary - Corrects (1)'] == 0)]

        # get rid of the timestamp from the SCHEDULE DATE column
        df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date

        # sort the csv file by date and animal id in ascending order
        df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        # reset the indices of the combined csv file
        df.reset_index(drop=True, inplace=True)

        # creates the merged_file in the same folder as this script, use to help double check deleted duplicates
        try:
            print(
                'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
                script_location)
            df.to_csv('merged_file.csv', index=True)
        except PermissionError:
            print('You may have the merged_file.csv already open! Please close it!')
            return

        # sort by trial number and runtime
        df = df.sort_values(by=['End Summary - Corrects (1)', 'End Summary - Condition (1)'])

        # create a dataframe that holds the duplicates
        df_duplicates = pd.DataFrame()
        duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
        df_duplicates = df_duplicates.append(df.loc[duplicates])

        # sort the duplicates
        df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        try:
            print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
                  script_location)
            df_duplicates.to_csv('dropped_duplicates.csv', index=True)
        except PermissionError:
            print('You may have the dropped_duplicates.csv already open! Please close it!')
            return

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

        # the mm/dd/yyyy of the program
        date_header = index_range('Schedule run date', raw_data_headers, df)
        # the animal id
        animal_id_header = index_range('Animal ID', raw_data_headers, df)
        # session length
        session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
        # corrects
        correct_header = index_range('End Summary - Corrects (1)', raw_data_headers, df)
        # blank touches
        blank_touches_header = index_range('End Summary - Blank Touches (1)', raw_data_headers, df)
        # total iti touches
        iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
            'End Summary - Right ITI Touches (1)', raw_data_headers, df) + index_range(
            'End Summary - Centre ITI Touches (1)', raw_data_headers, df)
        correct_touch_latency_header = index_range('Correct touch latency (', raw_data_headers, df)
        blank_touch_latency_header = index_range('Blank Touch Latency (', raw_data_headers, df)
        correct_reward_collect_header = index_range('Correct Reward Collection (', raw_data_headers, df)

        print('The program is still running... Please wait....')

        col_names = ['Date', 'ID', 'SessionLength', 'Corrects', 'BlankTouches', 'TotalITITouches',
                     'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardTouchLatency']

        df_final = pd.DataFrame(columns=col_names)
        try:
            # get the date for each row
            df_final['Date'] = df.iloc[:, date_header[0]]
            # get the animal id for each row
            df_final['ID'] = df.iloc[:, animal_id_header[0]]
            # get the session time for each row
            df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
            df_final['Corrects'] = df.iloc[:, correct_header[0]]
            df_final['BlankTouches'] = df.iloc[:, blank_touches_header[0]]
            # get the iti touches for each row
            df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
            df_final['MeanCorrectTouchLatency'] = df.iloc[:, correct_touch_latency_header].mean(axis=1)
            df_final['MeanBlankTouchLatency'] = df.iloc[:, blank_touch_latency_header].mean(axis=1)
            df_final['MeanRewardTouchLatency'] = df.iloc[:, correct_reward_collect_header].mean(axis=1)
        except IndexError or KeyError or ValueError:
            print('Either you selected the wrong type of test or headers are not the same on all files!')
            return
        print('The program is almost done running... Please wait....')

        return df_final

    except PermissionError:
        print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')


def data_setup_ext():
    # asks for the directory with all the RAW DATA csv files
    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')
    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return

    # passes the folder directory and compiles all the csv files into ONE csv file

    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    original_location = os.getcwd()
    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        # read the first csv file in the folder
        try:
            df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
        except IndexError:
            print('Either the directory is empty or does not contain any .csv files!')
            return
        # append all the other csv files onto the current dataframe
        for file in files[1:len(files)]:
            if not file.startswith('.'):
                df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
                df = df.append(df_csv)

        df = df.loc[df['Schedule name'] == 'Mouse Extinction pt 2 v2']

        # df = df.loc[~(df['End Summary - Corrects (1)'] == 0)]

        # get rid of the timestamp from the SCHEDULE DATE column
        df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date

        # sort the csv file by date and animal id in ascending order
        df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        # reset the indices of the combined csv file
        df.reset_index(drop=True, inplace=True)

        # creates the merged_file in the same folder as this script, use to help double check deleted duplicates
        try:
            print(
                'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
                script_location)
            df.to_csv('merged_file.csv', index=True)
        except PermissionError:
            print('You may have the merged_file.csv already open! Please close it!')
            return

        # sort by trial number and runtime
        df = df.sort_values(by=['End Summary - Responses (1)', 'End Summary - Condition (1)'])

        # create a dataframe that holds the duplicates
        df_duplicates = pd.DataFrame()
        duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
        df_duplicates = df_duplicates.append(df.loc[duplicates])

        # sort the duplicates
        df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

        try:
            print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
                  script_location)
            df_duplicates.to_csv('dropped_duplicates.csv', index=True)
        except PermissionError:
            print('You may have the dropped_duplicates.csv already open! Please close it!')
            return

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
        all_numeric_values = [*range(7, len(raw_data_headers), 1)]

        convert_to_int(all_numeric_values, raw_data_headers, df)

        # the mm/dd/yyyy of the program
        date_header = index_range('Schedule run date', raw_data_headers, df)
        # the animal id
        animal_id_header = index_range('Animal ID', raw_data_headers, df)
        # session length
        session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
        # corrects
        # total trials completed
        responses_header = index_range('End Summary - Responses (1)', raw_data_headers, df)
        # percent correct of trials
        omissions_header = index_range('End Summary - Omissions (1)', raw_data_headers, df)
        # total iti touches

        # the average time to correctly touch
        mean_response_touch_header = index_range('Response touch latency ', raw_data_headers,
                                                 df)
        mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
        # the average time to collect reward
        mean_tray_entry_latency = index_range('Tray Entry Latency (', raw_data_headers, df)
        # total iti touches
        iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
            'End Summary - Right ITI Touches (1)', raw_data_headers, df) + index_range(
            'End Summary - Centre ITI Touches (1)', raw_data_headers, df)

        print('The program is still running... Please wait....')

        col_names = ['Date', 'ID', 'SessionLength', 'Responses', 'Omissions', 'TotalITITouches',
                     'MeanResponseTouchLatency', 'MeanBlankTouchLatency', 'MeanTrayEntryLatency']

        df_final = pd.DataFrame(columns=col_names)
        try:
            # get the date for each row
            df_final['Date'] = df.iloc[:, date_header[0]]
            # get the animal id for each row
            df_final['ID'] = df.iloc[:, animal_id_header[0]]
            # get the session time for each row
            df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
            df_final['Responses'] = df.iloc[:, responses_header[0]]
            df_final['Omissions'] = df.iloc[:, omissions_header[0]]
            # get the iti touches for each row
            df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
            df_final['MeanResponseTouchLatency'] = df.iloc[:, mean_response_touch_header].mean(axis=1)
            df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
            df_final['MeanTrayEntryLatency'] = df.iloc[:, mean_tray_entry_latency].mean(axis=1)
        except IndexError or KeyError or ValueError:
            print('Either you selected the wrong type of test or headers are not the same on all files!')
            return

        print('The program is almost done running... Please wait....')

        return df_final

    except PermissionError:
        print('You may have closed the window asking for a directory! Or there are no .csv files in this directory!')


def save_file_message(df):
    try:
        print('A window has opened asking for you to save your newly created csv file. Please look for it!')
        save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
        df.to_csv(save_file_path, index=False)
        print('A .csv file has been created. Please look at it in the saved directory!')
        print('\n')
    except FileNotFoundError:
        print('You closed the window before saving! Please run the program again!')
        print('\n')
