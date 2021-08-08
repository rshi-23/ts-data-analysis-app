# functions
import numpy as np
import pandas as pd


# a function that converts the column index range and returns a list of column header names
def get_header_names(raw_data_headers, header_index_range):
    header_names_list = []
    for index in header_index_range:
        header_names_list.append(raw_data_headers[index])

    return header_names_list


# a function that converts a specific range of the csv into numerics (floats)
def convert_to_int(header_index_range, raw_data_headers, dataframe):
    # replace NaNs and - (no values/blank spaces) with a very large placeholder number
    dataframe.replace(np.nan, '999999999', regex=True, inplace=True)
    dataframe.replace('-', '999999999', regex=True, inplace=True)

    header_names_range = get_header_names(raw_data_headers, header_index_range)

    # turn this header range from strings to ints
    dataframe[header_names_range] = dataframe[header_names_range].apply(pd.to_numeric)

    # replace that very large placeholder number with NaNs again
    dataframe.replace('999999999', np.nan, regex=True, inplace=True)
    dataframe.replace(999999999, np.nan, regex=True, inplace=True)

    return dataframe


# a function that gets the indice range for specific headers
def index_range(keyword, header_list, dataframe):
    index_list = []
    for header in header_list:
        if header.startswith(keyword):
            index_list.append(header_list.index(header))

    return index_list


def get_missing_reversal_trials(df, column_names):
    for index in df.iterrows():
        if np.isnan(index[1]['NumberOfTrialTo1stReversal']):
            # if not reach first reversal, make it the total number of trials
            df.at[index[0], 'NumberOfTrialTo1stReversal'] = df.at[index[0], 'NumberOfTrial']
        if np.isnan(index[1]['NumberOfTrialTo2ndReversal']) and index[1]['NumberOfReversal'] > 0:
            # if not reach second reversal and made more than one reversal, make it the difference
            df.at[index[0], 'NumberOfTrialTo2ndReversal'] = df.at[index[0], 'NumberOfTrial'] - df.at[
                index[0], 'NumberOfTrialTo1stReversal']


def get_fixed_session_time(df, df2):
    for index in df.iterrows():
        if index[1]['NumberOfReversal'] == 0:
            df.at[index[0], 'SessionLengthTo1stReversalDuration'] = df.at[index[0], 'SessionLength']
        elif index[1]['NumberOfReversal'] == 1:
            df.at[index[0], 'SessionLengthTo2ndReversalDuration'] = df.at[index[0], 'SessionLength'] - df.at[
                index[0], 'SessionLengthTo1stReversalDuration']
        else:
            df.at[index[0], 'SessionLengthTo2ndReversalDuration'] = df2.at[index[
                                                                               0], 'No trials to criterion - Condition (2)'] - \
                                                                    df2.at[index[
                                                                               0], 'No trials to criterion - Condition (1)']


# a function that gets the first reversal correctness
def get_percent_correctness_first(df1, df2, column_names):
    for index in df1.iterrows():
        stop_point = df1.at[index[0], 'No trials to criterion - Generic Evaluation (1)']
        # if did not reach first reversal, make the value the correct percentage value
        if np.isnan(stop_point) or index[1]['End Summary - Times Criteria reached (1)'] == 0:
            stop_point = df1.at[index[0], 'End Summary - Trials Completed (1)']
            df1.at[index[0], 'PercentCorrectTo1stReversal'] = df1.at[index[
                                                                         0], 'End Summary - Percentage Correct (1)'] / 100
            int_stop_point = int(stop_point)

            df1.at[index[0], 'PercentCorrectTo1stReversal'] = df1[column_names[0:int_stop_point + 1]].mean(axis=1)[
                index[0]]
            df2.at[index[0], 'NumberOfTrialTo1stReversal'] = int_stop_point + 1
        else:
            int_stop_point = int(stop_point)
            df1.at[index[0], 'PercentCorrectTo1stReversal'] = df1[column_names[0:int_stop_point]].mean(axis=1)[index[0]]


# function that gets the second reversal correctness
def get_percent_correctness_second(df1, df2, column_names):
    for index in df1.iterrows():
        start_point = df1.at[index[0], 'No trials to criterion - Generic Evaluation (1)']
        stop_point = df2.at[index[0], 'NumberOfTrialTo2ndReversal'] + start_point
        if np.isnan(start_point) or np.isnan(stop_point):
            df1.at[index[0], 'PercentCorrectTo2ndReversal'] = np.nan
        elif index[1]['End Summary - Times Criteria reached (1)'] == 1:
            int_start_point = int(start_point)
            list_wo_nans = df1[column_names[int_start_point:]].count(axis=1).tolist()
            df1.at[index[0], 'PercentCorrectTo2ndReversal'] = \
                df1[column_names[int_start_point:]].mean(axis=1)[index[0]]
            df2.at[index[0], 'NumberOfTrialTo2ndReversal'] = list_wo_nans[index[0]]
        else:
            int_start_point = int(start_point)
            int_stop_point = int(stop_point)
            df1.at[index[0], 'PercentCorrectTo2ndReversal'] = \
                df1[column_names[int_start_point:int_stop_point]].mean(axis=1)[index[0]]


# function that gets which ld test was ran between (easy, hard, intermediate and undetermined)
def get_test_type(df1, column_names):
    some_list = df1[column_names].values.tolist()
    for index in df1.iterrows():
        if 8.0 in some_list[index[0]] or 11.0 in some_list[index[0]]:
            df1.at[index[0], 'Type'] = 'intermediate'
        elif 9.0 in some_list[index[0]] or 10.0 in some_list[index[0]]:
            df1.at[index[0], 'Type'] = 'hard'
        elif 7.0 in some_list[index[0]] or 12.0 in some_list[index[0]]:
            df1.at[index[0], 'Type'] = 'easy'
        else:
            df1.at[index[0], 'Type'] = 'undetermined'
