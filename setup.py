import tkinter.filedialog as filedialog
import os
from setuptools import glob
import warnings
from setup_functions import *

warnings.simplefilter(action='ignore', category=FutureWarning)
pd.options.mode.chained_assignment = 'raise'


def specific_schedule_name(df, schedule_name):
    """
    This function returns a new df with specific animal schedule type, removes the timestamp from the schedule date, and
    sorts the df by run date and ID in ascending order
    :param df: The dataframe that represents the raw ABET file
    :param schedule_name: The name of the test the mouse ran, found under the schedule name in raw data
    :return: A dataframe that only contains rows for animals that performed the specific schedule name, sorted in
    ascending order by run date and ID
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    try:
        df = df.loc[df['Schedule name'] == schedule_name]
        # get rid of the timestamp from the SCHEDULE DATE column
        df['Schedule run date'] = pd.to_datetime(df['Schedule run date']).dt.date
        # sort the csv file by date and animal id in ascending order
        df = df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1])
        # reset the indices of the combined csv file
        df = df.reset_index(drop=True)
        return df
    except (IndexError, KeyError, ValueError):
        print('specific_schedule_name() error: either you have selected the wrong type of test',
              'or the headers are not the same for all files!')
        return


def create_merge_file(df, script_location):
    """
    This function creates a csv file called 'merged_file.csv'. This file appends all the raw files together and puts
    them on a single csv file. Useful for testing or just looking at all the data in one file.
    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located and used to store this file there as well
    :except PermissionError: If the merged_file.csv' is already open, it will not update and this function will return
    and stop.
    :except AttributeError: If you run this on non-raw data files,this function will return and stop.
    """

    try:
        df.to_csv('merged_file.csv', index=False)
        print(
            'A file called "merged_file.csv" has been created in the same directory as the script! The location is:',
            script_location)
    except PermissionError:
        print('create_merge_file() error: You may have the "merged_file.csv" already open! Please close it!')
        return
    except AttributeError:
        print('create_merge_file() error: These are not the correct raw data files!')
        return


def create_dropped_duplicates_file(df, script_location):
    """
    This function creates a csv file called 'dropped_duplicates.csv'. This file shows all the rows that were treated as
    duplicates and removed from the working dataframe. Useful for testing and making sure the correct
    duplicates/unwanted were removed from the working dataframe.
    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located and used to store this file there as well
    :except PermissionError: If the 'dropped_duplicates.csv' is already open, it will not update and this function will
    return and stop.
    :except AttributeError: If you run this on non-raw data files,this function will return and stop.
    """

    try:
        df.to_csv('dropped_duplicates.csv', index=False)
        print('A file called "dropped_duplicates.csv" has been created in the same directory! The location is:',
              script_location)
    except PermissionError:
        print('create_dropped_duplicates_file() error: You may have the "merged_file.csv" already open!',
              'Please close it!')
        return
    except AttributeError:
        print('create_dropped_duplicates_file() error: These are not the correct raw data files!')
        return


def remove_duplicates(df, script_location):
    """
    This function actually drops the duplicate rows from the working dataframe.
    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located and used to store this file there as well
    :return: A version of the raw ABET file dataframe with the duplicates removed
    """

    # create a dataframe that holds the duplicates
    df_duplicates = pd.DataFrame()
    duplicates = df.duplicated(subset=['Schedule run date', 'Animal ID'], keep='last')
    df_duplicates = df_duplicates.append(df.loc[duplicates])
    df_duplicates.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1], inplace=True)

    create_dropped_duplicates_file(df_duplicates, script_location)

    # actually drop the duplicates from the working df
    df = df.drop_duplicates(subset=['Schedule run date', 'Animal ID'], keep='last')
    df = df.sort_values(['Schedule run date', 'Animal ID'], ascending=[1, 1])
    df = df.reset_index(drop=True)

    return df


def habituation_one(df, script_location):
    """
    This function is used to specifically get cleaned data for the Habituation 1 test. The resulting dataframe will have
    the following headers: 'Date', 'ID', 'SessionLength', 'RewardIRBeamBrokenCount', 'ScreenIRBeamBrokenCount',
    'CrossedRewardToScreen', 'CrossedScreenToReward', 'BottomWindowTouches', 'TopWindowTouches', 'TrayEnteredCount',
    'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Habituation 1 data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by time and remove duplicates
    df = df.sort_values(by=['End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    reward_ir_beam = index_range('End Summary - Reward IR Beam broken (1)', raw_data_headers, df)
    screen_ir_beam = index_range('End Summary - Screen IR Beam broken (1)', raw_data_headers, df)
    reward_to_screen = index_range('End Summary - Crossed reward to screen (1)', raw_data_headers, df)
    screen_to_reward = index_range('End Summary - Crossed Screen to reward (1)', raw_data_headers, df)
    bottom_window_touches = index_range('End Summary - Touches to bottom screen windows (1)', raw_data_headers, df)
    top_window_touches = index_range('End Summary - Touches to top screen windows (1)', raw_data_headers, df)
    tray_entered_count = index_range('End Summary - Tray Entered - Cnt (1)', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'RewardIRBeamBrokenCount', 'ScreenIRBeamBrokenCount',
                 'CrossedRewardToScreen',
                 'CrossedScreenToReward', 'BottomWindowTouches', 'TopWindowTouches', 'TrayEnteredCount', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['RewardIRBeamBrokenCount'] = df.iloc[:, reward_ir_beam[0]]
        df_final['ScreenIRBeamBrokenCount'] = df.iloc[:, screen_ir_beam[0]]
        df_final['CrossedRewardToScreen'] = df.iloc[:, reward_to_screen[0]]
        df_final['CrossedScreenToReward'] = df.iloc[:, screen_to_reward[0]]
        df_final['BottomWindowTouches'] = df.iloc[:, bottom_window_touches[0]]
        df_final['TopWindowTouches'] = df.iloc[:, top_window_touches[0]]
        df_final['TrayEnteredCount'] = df.iloc[:, tray_entered_count[0]]
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print('habituation_one() error: either you selected the wrong type of test '
              'or headers are not the same on all files!')
        return
    print('The program is almost done running... Please wait....')

    return df_final


def habituation_two(df, script_location):
    """
    This function is used to specifically get cleaned data for the Habituation 2 test. The resulting dataframe will have
    the following headers: 'Date', 'ID', 'SessionLength', 'NumberOfTrial', 'RewardIRBeamBrokenCount',
    'ScreenIRBeamBrokenCount', 'BottomLeftWindowTouches', 'BottomRightWindowTouches', 'TopWindowTouches',
    'TrayEnteredCount', 'MeanRewardCollectionLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Habituation 2 data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by time and remove duplicates
    df = df.sort_values(by=['End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    total_trials = index_range('End Summary - Trial Completed (1)', raw_data_headers, df)
    reward_ir_beam = index_range('End Summary - Reward IR Breaks - Reward Beam Cnt (1)', raw_data_headers, df)
    screen_ir_beam = index_range('End Summary - Screen IR Breaks - Screen IR Cnt (1)', raw_data_headers, df)
    bottom_left_window_touches = index_range('End Summary -  Bottom Left Touches - Bottom Left Cnt (1)',
                                             raw_data_headers, df)
    bottom_right_window_touches = index_range('End Summary - Bottom Right Touches - Bottom Right Cnt (1)',
                                              raw_data_headers, df)
    top_window_touches = index_range('End Summary -  Top Touches - Top Cnt (1)', raw_data_headers, df)
    tray_entered_count = index_range('End Summary - Tray Entered - Cnt (1)', raw_data_headers, df)
    mean_reward_collection_latency = index_range('Reward Collection Latency (', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'NumberOfTrial', 'RewardIRBeamBrokenCount', 'ScreenIRBeamBrokenCount',
                 'BottomLeftWindowTouches',
                 'BottomRightWindowTouches', 'TopWindowTouches', 'TrayEnteredCount', 'MeanRewardCollectionLatency',
                 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['NumberOfTrial'] = df.iloc[:, total_trials[0]]
        df_final['RewardIRBeamBrokenCount'] = df.iloc[:, reward_ir_beam[0]]
        df_final['ScreenIRBeamBrokenCount'] = df.iloc[:, screen_ir_beam[0]]
        df_final['BottomLeftWindowTouches'] = df.iloc[:, bottom_left_window_touches[0]]
        df_final['BottomRightWindowTouches'] = df.iloc[:, bottom_right_window_touches[0]]
        df_final['TopWindowTouches'] = df.iloc[:, top_window_touches[0]]
        df_final['TrayEnteredCount'] = df.iloc[:, tray_entered_count[0]]
        df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_collection_latency].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print(
            'habituation_two() error: Either you selected the wrong type of test '
            'or headers are not the same on all files!')
        return
    print('The program is almost done running... Please wait....')

    return df_final


def initial_touch(df, script_location):
    """
    This function is used to specifically get cleaned data for the Initial Touch test. The resulting dataframe will have
    the following headers: 'Date', 'ID', 'SessionLength', 'ImagesTouched', 'Corrects', 'BlankTouches','TotalITITouches',
    'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by time and remove duplicates
    df = df.sort_values(by=['End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    images_touched = index_range('End Summary - No. images (1)', raw_data_headers, df)
    correct_touches = index_range('End Summary - Corrects (1)', raw_data_headers, df)
    blank_touches = index_range('End Summary - Blank Touches (1)', raw_data_headers, df)
    total_iti_touches = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI Touches (1)', raw_data_headers, df)
    mean_correct_touch_latency = index_range('Correct touch latency (', raw_data_headers, df)
    mean_blank_touch_latency = index_range('Blank Touch Latency (', raw_data_headers, df)
    mean_reward_collection_latency = index_range('Correct Reward Collection (', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'ImagesTouched', 'Corrects', 'BlankTouches',
                 'TotalITITouches', 'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency',
                 'Day']

    df_final = pd.DataFrame(columns=col_names)

    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['ImagesTouched'] = df.iloc[:, images_touched[0]]
        df_final['Corrects'] = df.iloc[:, correct_touches[0]]
        df_final['BlankTouches'] = df.iloc[:, blank_touches[0]]
        df_final['TotalITITouches'] = df.iloc[:, total_iti_touches].sum(axis=1)
        df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_latency].mean(axis=1)
        df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_latency].mean(axis=1)
        df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_collection_latency].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print(
            'initial_touch() error: Either you selected the wrong type of test '
            'or headers are not the same on all files!')
        return
    print('The program is almost done running... Please wait....')

    return df_final


def must_touch_initiate(df, script_location):
    """
    This function is used to specifically get cleaned data for the Must Touch/Must Initiate test. The resulting
    dataframe will have the following headers: 'Date', 'ID', 'SessionLength', 'Corrects', 'TotalBlankTouches',
    'TotalITITouches', 'MeanCorrectTouchLatency', 'MeanCorrectRightTouchLatency', 'MeanCorrectLeftTouchLatency',
    'MeanCorrectLeftRightTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by corrects and time, remove duplicates
    df = df.sort_values(by=['End Summary - Corrects (1)', 'End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    correct_header = index_range('End Summary - Corrects (1)', raw_data_headers, df)
    blank_touches_header = index_range('End Summary - Blank Touches (1)', raw_data_headers, df)
    iti_blank_header = index_range('End Summary - Left ITI touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI touches (1)', raw_data_headers, df)
    mean_correct_touch_header = index_range('Correct touch latency (', raw_data_headers,
                                            df)
    mean_correct_left_touch = index_range('Correct Left touch latency (', raw_data_headers, df)
    mean_correct_right_touch = index_range('Correct Right touch latency (', raw_data_headers, df)
    mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
    mean_reward_header = index_range('Correct Reward Collection (', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'Corrects', 'TotalBlankTouches', 'TotalITITouches',
                 'MeanCorrectTouchLatency', 'MeanCorrectRightTouchLatency', 'MeanCorrectLeftTouchLatency',
                 'MeanCorrectLeftRightTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['Corrects'] = df.iloc[:, correct_header[0]]
        df_final['TotalBlankTouches'] = df.iloc[:, blank_touches_header[0]]
        df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
        df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
        df_final['MeanCorrectRightTouchLatency'] = df.iloc[:, mean_correct_right_touch].mean(axis=1)
        df_final['MeanCorrectLeftTouchLatency'] = df.iloc[:, mean_correct_left_touch].mean(axis=1)
        df_final['MeanCorrectLeftRightTouchLatency'] = df_final[
            ['MeanCorrectLeftTouchLatency', 'MeanCorrectRightTouchLatency']].mean(axis=1)
        df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
        df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print(
            'must_touch_initiate() error: Either you selected the wrong type of test '
            'or headers are not the same on all files!')
        return
    print('The program is almost done running... Please wait....')

    return df_final


def punish_incorrect(df, script_location):
    """
    This function is used to specifically get cleaned data for the Punish Incorrect test. The resulting dataframe will
    have the following headers: 'Date', 'ID', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'TotalITITouches',
    'MeanCorrectTouchLatency', 'MeanCorrectRightTouchLatency', 'MeanCorrectLeftTouchLatency',
    'MeanCorrectLeftRightTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by trials, time and remove duplicates
    df = df.sort_values(by=['End Summary - Trials Completed (1)', 'End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    trial_completed_header = index_range('End Summary - Trials Completed (1)', raw_data_headers, df)
    percent_correct_headers = index_range('End Summary - % Correct (1)', raw_data_headers, df)
    iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI Touches (1)', raw_data_headers, df)
    mean_correct_touch_header = index_range('Correct touch latency (', raw_data_headers, df)
    mean_correct_left_touch = index_range('Correct Left touch latency (', raw_data_headers, df)
    mean_correct_right_touch = index_range('Correct Right touch latency (', raw_data_headers, df)
    mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
    mean_reward_header = index_range('Correct Reward Collection (', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'TotalITITouches',
                 'MeanCorrectTouchLatency', 'MeanCorrectRightTouchLatency', 'MeanCorrectLeftTouchLatency',
                 'MeanCorrectLeftRightTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['NumberOfTrial'] = df.iloc[:, trial_completed_header[0]]
        df_final['PercentCorrect'] = df.iloc[:, percent_correct_headers[0]]
        df_final['TotalITITouches'] = df.iloc[:, iti_blank_header[0]]
        df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
        df_final['MeanCorrectRightTouchLatency'] = df.iloc[:, mean_correct_right_touch].mean(axis=1)
        df_final['MeanCorrectLeftTouchLatency'] = df.iloc[:, mean_correct_left_touch].mean(axis=1)
        df_final['MeanCorrectLeftRightTouchLatency'] = df_final[
            ['MeanCorrectLeftTouchLatency', 'MeanCorrectRightTouchLatency']].mean(axis=1)
        df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
        df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print(
            'punish_incorrect() error: Either you selected the wrong type of test '
            'or headers are not the same on all files!')
        return

    print('The program is almost done running... Please wait....')
    return df_final


def ld(df, script_location):
    """
    This function is used to specifically get cleaned data for the LD Train/LD Probe test. The resulting
    dataframe will have the following headers: 'Date', 'ID', 'Type', 'SessionLength', 'NumberOfTrial', 'PercentCorrect',
    'NumberOfReversal', 'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency',
    'MeanCorrectTouchLatency', 'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
    'SessionLengthTo2ndReversalDuration', 'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal',
    'PercentCorrectTo1stReversal', 'PercentCorrectTo2ndReversal', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """
    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by trials, time and remove duplicates
    df = df.sort_values(by=['End Summary - Trials Completed (1)', 'End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    number_correct_header = index_range('Trial Analysis - No. Correct (', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    correct_position_header = index_range('Trial Analysis - Correct Position (', raw_data_headers, df)
    session_length_header = index_range('End Summary - Session Time (1)', raw_data_headers, df)
    trials_completed_header = index_range('End Summary - Trials Completed (1)', raw_data_headers, df)
    percent_correct_header = index_range('End Summary - Percentage Correct (1)', raw_data_headers, df)
    reversal_number_header = index_range('End Summary - Times Criteria reached (1)', raw_data_headers, df)
    iti_blank_header = index_range('End Summary - Left ITI touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI touches (1)', raw_data_headers, df)
    blank_header = index_range('End Summary - Left Blank Touches - Generic Counter (1)', raw_data_headers, df) + \
                   index_range('End Summary - Right Blank Touches - Generic Counter (1)', raw_data_headers, df) + \
                   index_range('End Summary - Top row touches - Generic Counter (1)', raw_data_headers, df)
    mean_reward_header = index_range('Trial Analysis - Reward Collection Latency (', raw_data_headers, df)
    mean_correct_touch_header = index_range('Trial Analysis - Correct Image Response Latency (', raw_data_headers,
                                            df)
    mean_incorrect_header = index_range('Trial Analysis - Incorrect Image Latency (', raw_data_headers, df)
    first_reversal_time_header = index_range('No trials to criterion - Condition (1)', raw_data_headers, df)
    second_reversal_time_header = index_range('No trials to criterion - Condition (2)', raw_data_headers, df)
    first_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (1)', raw_data_headers,
                                               df)
    second_reversal_trials_header = index_range('No trials to criterion - Generic Evaluation (2)', raw_data_headers,
                                                df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'Type', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                 'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                 'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                 'SessionLengthTo2ndReversalDuration', 'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal',
                 'PercentCorrectTo1stReversal', 'PercentCorrectTo2ndReversal', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]

        df['Type'] = ''
        correct_position_names = get_header_names(raw_data_headers, correct_position_header)
        get_test_type(df, correct_position_names)
        df_final['Type'] = df['Type']

        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['NumberOfTrial'] = df.iloc[:, trials_completed_header[0]]
        df_final['PercentCorrect'] = df.iloc[:, percent_correct_header]
        df_final['NumberOfReversal'] = df.iloc[:, reversal_number_header[0]]
        df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
        df_final['TotalBlankTouches'] = df.iloc[:, blank_header].sum(axis=1)
        df_final['MeanRewardCollectionLatency'] = df.iloc[:, mean_reward_header].mean(axis=1)
        df_final['MeanCorrectTouchLatency'] = df.iloc[:, mean_correct_touch_header].mean(axis=1)
        df_final['MeanIncorrectTouchLatency'] = df.iloc[:, mean_incorrect_header].mean(axis=1)
        df_final['SessionLengthTo1stReversalDuration'] = df.iloc[:, first_reversal_time_header[0]]
        df_final['SessionLengthTo2ndReversalDuration'] = df.iloc[:, second_reversal_time_header[0]]
        df_final['NumberOfTrialTo1stReversal'] = df.iloc[:, first_reversal_trials_header[0]]
        df_final['NumberOfTrialTo2ndReversal'] = df.iloc[:, second_reversal_trials_header[0]]

        get_missing_reversal_trials(df_final, col_names)
        get_fixed_session_time(df_final, df)

        number_correct_column_names = get_header_names(raw_data_headers, number_correct_header)

        df['PercentCorrectTo1stReversal'] = np.nan
        get_percent_correctness_first(df, df_final, number_correct_column_names)
        df_final['PercentCorrectTo1stReversal'] = df['PercentCorrectTo1stReversal']

        df['PercentCorrectTo2ndReversal'] = np.nan
        get_percent_correctness_second(df, df_final, number_correct_column_names)
        df_final['PercentCorrectTo2ndReversal'] = df['PercentCorrectTo2ndReversal']

        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print('ld() error: Either you selected the wrong type of test or headers are not the same on all files!')
        return

    print('The program is almost done running... Please wait....')

    return df_final


def acquisition(df, script_location):
    """
    This function is used to specifically get cleaned data for the Acquisition test. The resulting dataframe will have
    the following headers: 'Date', 'ID', 'SessionLength', 'Corrects', 'BlankTouches', 'TotalITITouches',
    'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardTouchLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by corrects and time, remove duplicates
    df = df.sort_values(by=['End Summary - Corrects (1)', 'End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    # all the headers in the raw data file
    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    correct_header = index_range('End Summary - Corrects (1)', raw_data_headers, df)
    blank_touches_header = index_range('End Summary - Blank Touches (1)', raw_data_headers, df)
    iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Centre ITI Touches (1)', raw_data_headers, df)
    correct_touch_latency_header = index_range('Correct touch latency (', raw_data_headers, df)
    blank_touch_latency_header = index_range('Blank Touch Latency (', raw_data_headers, df)
    correct_reward_collect_header = index_range('Correct Reward Collection (', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'Corrects', 'BlankTouches', 'TotalITITouches',
                 'MeanCorrectTouchLatency', 'MeanBlankTouchLatency', 'MeanRewardTouchLatency', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['Corrects'] = df.iloc[:, correct_header[0]]
        df_final['BlankTouches'] = df.iloc[:, blank_touches_header[0]]
        df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
        df_final['MeanCorrectTouchLatency'] = df.iloc[:, correct_touch_latency_header].mean(axis=1)
        df_final['MeanBlankTouchLatency'] = df.iloc[:, blank_touch_latency_header].mean(axis=1)
        df_final['MeanRewardTouchLatency'] = df.iloc[:, correct_reward_collect_header].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print('Acq() error: Either you selected the wrong type of test or headers are not the same on all files!')
        return
    print('The program is almost done running... Please wait....')

    return df_final


def extinction(df, script_location):
    """
    This function is used to specifically get cleaned data for the Extinction test. The resulting dataframe will have
    the following headers: 'Date', 'ID', 'SessionLength', 'Responses', 'Omissions', 'TotalITITouches',
    'MeanResponseTouchLatency', 'MeanBlankTouchLatency', 'MeanTrayEntryLatency', 'Day'

    :param df: The dataframe that represents the raw ABET file
    :param script_location: The location where the script is located.
    :return: A dataframe with all the Initial Touch data and proper headers.
    :except (IndexError, KeyError, ValueError): Running this function on the wrong test will cause an error! If you're
    running the function on the correct files, then maybe the headers for all the files are not identical!
    """

    create_merge_file(df, script_location)
    print('The program is running... Please wait....')

    # sort by responses and time, remove duplicates
    df = df.sort_values(by=['End Summary - Responses (1)', 'End Summary - Condition (1)'])
    df = remove_duplicates(df, script_location)

    raw_data_headers = df.columns.values.tolist()

    # basically want to replace '-' with NaN values in this specific range
    all_numeric_values = [*range(13, len(raw_data_headers), 1)]
    df = convert_to_int(all_numeric_values, raw_data_headers, df)

    # get the column indices for specific parameters
    date_header = index_range('Schedule run date', raw_data_headers, df)
    animal_id_header = index_range('Animal ID', raw_data_headers, df)
    session_length_header = index_range('End Summary - Condition (1)', raw_data_headers, df)
    responses_header = index_range('End Summary - Responses (1)', raw_data_headers, df)
    omissions_header = index_range('End Summary - Omissions (1)', raw_data_headers, df)
    mean_response_touch_header = index_range('Response touch latency ', raw_data_headers,
                                             df)
    mean_blank_touch_header = index_range('Blank Touch Latency (', raw_data_headers, df)
    mean_tray_entry_latency = index_range('Tray Entry Latency (', raw_data_headers, df)
    iti_blank_header = index_range('End Summary - Left ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Right ITI Touches (1)', raw_data_headers, df) + index_range(
        'End Summary - Centre ITI Touches (1)', raw_data_headers, df)

    print('The program is still running... Please wait....')

    col_names = ['Date', 'ID', 'SessionLength', 'Responses', 'Omissions', 'TotalITITouches',
                 'MeanResponseTouchLatency', 'MeanBlankTouchLatency', 'MeanTrayEntryLatency', 'Day']

    df_final = pd.DataFrame(columns=col_names)

    # extract the necessary data from raw data
    try:
        df_final['Date'] = df.iloc[:, date_header[0]]
        df_final['ID'] = df.iloc[:, animal_id_header[0]]
        df_final['SessionLength'] = df.iloc[:, session_length_header[0]]
        df_final['Responses'] = df.iloc[:, responses_header[0]]
        df_final['Omissions'] = df.iloc[:, omissions_header[0]]
        df_final['TotalITITouches'] = df.iloc[:, iti_blank_header].sum(axis=1)
        df_final['MeanResponseTouchLatency'] = df.iloc[:, mean_response_touch_header].mean(axis=1)
        df_final['MeanBlankTouchLatency'] = df.iloc[:, mean_blank_touch_header].mean(axis=1)
        df_final['MeanTrayEntryLatency'] = df.iloc[:, mean_tray_entry_latency].mean(axis=1)
        df_final['Day'] = df_final.groupby('ID').cumcount() + 1

        df_final = df_final.sort_values(by=['ID', 'Date'])
    except (IndexError, KeyError, ValueError):
        print('Either you selected the wrong type of test or headers are not the same on all files!')
        return

    print('The program is almost done running... Please wait....')

    return df_final


def data_setup(test_type):
    """
    This functions prompts the user for the location of the raw data. It will read the raw data files and create a
    dataframe. Depending on the test type, the function will clean the data and return the appropriate cleaned dataframe,
    which will then be made into a csv to be saved.

    :param test_type: The type of test that the animal ran, listed under schedule type
    :return: A cleaned dataframe with the proper parameters based on the test type.
    :except IndexError: If there are no csv files in the directory, then the function will stop and print the error
    :except (IndexError, ValueError, KeyError, AttributeError):  Running this function on the wrong test will cause an
    error! If you're running the function on the correct files, then maybe the headers for all the files are not
    identical!
    """

    print('Please open the directory that has all the raw data csv files')
    file_path = filedialog.askdirectory(title='Open the directory with csv files')

    if len(file_path) == 0:
        print('The cancel button was clicked! Please try again!')
        return

    # passes the folder directory and compiles all the csv files into ONE csv file
    pattern = os.path.join(file_path, '*.csv')
    files = glob.glob(pattern)

    script_location = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_location)

    try:
        df = pd.read_csv(files[0], encoding='utf-8', delimiter=',', error_bad_lines=False)
    except IndexError:
        print('data_setup() error: Either the directory is empty or does not contain any .csv files!')
        return
    # append all the other csv files onto the current dataframe
    for file in files[1:len(files)]:
        if not file.startswith('.'):
            df_csv = pd.read_csv(file, index_col=False, encoding='utf-8', delimiter=',')
            df = df.append(df_csv)

    if test_type == 'Hab1':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Habituation 1')
            df_hab_one = habituation_one(df_specific, script_location)
            return df_hab_one
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with Hab 1 in setup.py!')
            return

    if test_type == 'Hab2':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Habituation 2')
            df_hab_two = habituation_two(df_specific, script_location)
            return df_hab_two
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with Hab 2 in setup.py!')
            return

    if test_type == 'IT':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Initial Touch Training v2')
            df_initial_touch = initial_touch(df_specific, script_location)
            return df_initial_touch
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with IT in setup.py!')
            return

    if test_type == 'MT':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Must Touch Training v2')
            df_must_touch = must_touch_initiate(df_specific, script_location)
            return df_must_touch
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with MT in setup.py!')
            return

    if test_type == 'MI':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Must Initiate Training v2')
            df_must_initiate = must_touch_initiate(df_specific, script_location)
            return df_must_initiate
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with MI in setup.py!')
            return

    if test_type == 'PI':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD Punish Incorrect Training v2')
            df_punish_incorrect = punish_incorrect(df_specific, script_location)
            return df_punish_incorrect
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with PI in setup.py!')
            return

    if test_type == 'LD Train' or test_type == 'LD Probe':
        try:
            df_specific = specific_schedule_name(df, 'Mouse LD 1 choice reversal v3')
            df_ld = ld(df_specific, script_location)
            return df_ld
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with LD Train/LD Probe in setup.py!')
            return

    if test_type == 'Acq':
        try:
            df_specific = specific_schedule_name(df, 'Mouse Extinction pt 1 v2')
            df_acq = acquisition(df_specific, script_location)
            return df_acq
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with Acq in setup.py!')
            return

    if test_type == 'Ext':
        try:
            df_specific = specific_schedule_name(df, 'Mouse Extinction pt 2 v2')
            df_ext = extinction(df_specific, script_location)
            return df_ext
        except (IndexError, ValueError, KeyError, AttributeError):
            print('data_setup() error: There is an issue with Ext in setup.py!')
            return


def save_file_message(df):
    """
    This functions prompts the user to save the cleaned dataframe as a csv file. The default save type is .csv and
    cannot be changed!
    :param df: The cleaned dataframe ready to be converted into csv file.
    :except FileNotFoundError: This will occur when you close the save window before saving!
    """
    try:
        print('A window has opened asking for you to save your newly created csv file. Please look for it!')
        save_file_path = filedialog.asksaveasfilename(defaultextension='.csv', title='Save the file')
        df.to_csv(save_file_path, index=False)
        print('A .csv file has been created. Please look at it in the saved directory!')
        print('\n')
    except FileNotFoundError:
        print('save_file_message() error: You closed the window before saving! Please run the program again!')
        print('\n')
        return
