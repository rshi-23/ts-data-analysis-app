import numpy as np
import pandas as pd

from setup import *
import math


def get_last_day_difficulty(df):
    df['Day'] = df.groupby('ID').cumcount() + 1
    df['Day'] = df['Day'].astype(float)
    df['Block'] = np.ceil(df['Day'] / 4)
    # delete all odd day occurrences, assume last day of each difficulty is always an even day
    df.drop(df.loc[df['Day'] % 2 == 1].index, inplace=True)


def ld_probe_delete_other_difficulties(df):
    # for ld train, we want only intermediate, delete all others
    df.drop(df.loc[df['Type'] == 'intermediate'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'undetermined'].index, inplace=True)
    df.sort_values(['Date', 'ID'], ascending=[1, 1], inplace=True)
    df['Day'] = df.groupby('ID').cumcount() + 1


def ld_probe_last_day_difficulty():
    print('You have selected the LD Probe(Last Day Difficulty) button!')
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        get_last_day_difficulty(df)
        save_file_message(df)


def ld_probe_select_day(enter_day):
    print('You have selected the LD Probe(Select Day) button!')
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        selected_day = int(enter_day.get())
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def ld_probe_select_id(enter_id):
    print('You have selected the LD Probe(Select ID) button!')
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        selected_id = int(enter_id.get())
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)


def ld_probe_select_block(block_number):
    print('You have selected the LD Probe(Select Block) button!')

    block_day_range_max = 4 * int(block_number.get())
    block_day_range_min = block_day_range_max - 3
    block_day_total_range = [*range(block_day_range_min, block_day_range_max + 1, 1)]

    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[(df['Day'] == block_day_total_range[1]) | (df['Day'] == block_day_total_range[3])]

        save_file_message(df)


def averaging_process(df):
    new_df = pd.DataFrame()
    row_index = 0

    while row_index < df.shape[0] - 1:
        rows_to_avg = list()

        for avg_index in range(2):
            row_to_add = df.loc[avg_index + row_index]
            rows_to_avg.append(row_to_add)

        if rows_to_avg[0]['Day'] + 1 == rows_to_avg[1]['Day'] and rows_to_avg[0]['ID'] == rows_to_avg[1]['ID']:
            temp_row = (rows_to_avg[0][3:18] + rows_to_avg[1][3:18]) / 2
            temp_row['Date'] = rows_to_avg[1]['Date']
            temp_row['Day'] = rows_to_avg[1]['Day']
            temp_row['Type'] = rows_to_avg[1]['Type']
            temp_row['ID'] = rows_to_avg[1]['ID']
            if np.isnan(temp_row['SessionLengthTo2ndReversalDuration']) and not np.isnan(
                    rows_to_avg[0]['SessionLengthTo2ndReversalDuration']):
                temp_row['SessionLengthTo2ndReversalDuration'] = rows_to_avg[0]['SessionLengthTo2ndReversalDuration']
            if np.isnan(temp_row['SessionLengthTo2ndReversalDuration']) and not np.isnan(
                    rows_to_avg[1]['SessionLengthTo2ndReversalDuration']):
                temp_row['SessionLengthTo2ndReversalDuration'] = rows_to_avg[1]['SessionLengthTo2ndReversalDuration']
            if np.isnan(temp_row['NumberOfTrialTo2ndReversal']) and not np.isnan(
                    rows_to_avg[0]['NumberOfTrialTo2ndReversal']):
                temp_row['NumberOfTrialTo2ndReversal'] = rows_to_avg[0]['NumberOfTrialTo2ndReversal']
            if np.isnan(temp_row['NumberOfTrialTo2ndReversal']) and not np.isnan(
                    rows_to_avg[1]['NumberOfTrialTo2ndReversal']):
                temp_row['NumberOfTrialTo2ndReversal'] = rows_to_avg[1]['NumberOfTrialTo2ndReversal']
            if np.isnan(temp_row['PercentCorrectTo2ndReversal']) and not np.isnan(
                    rows_to_avg[0]['PercentCorrectTo2ndReversal']):
                temp_row['PercentCorrectTo2ndReversal'] = rows_to_avg[0]['PercentCorrectTo2ndReversal']
            if np.isnan(temp_row['PercentCorrectTo2ndReversal']) and not np.isnan(
                    rows_to_avg[1]['PercentCorrectTo2ndReversal']):
                temp_row['PercentCorrectTo2ndReversal'] = rows_to_avg[1]['PercentCorrectTo2ndReversal']
            new_df = new_df.append(temp_row, ignore_index=True)
            row_index += 2
        else:
            row_index += 1

    return new_df


def ld_probe_last_day_avg():
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        new_df = averaging_process(df)

        new_df = new_df[col_names]
        save_file_message(new_df)


def ld_probe_block_average(block_number):
    print('You have selected the LD Probe(Select Block Average) button!')

    block_day_range_max = 4 * int(block_number.get())
    block_day_range_min = block_day_range_max - 3
    block_day_total_range = [*range(block_day_range_min, block_day_range_max + 1, 1)]

    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[df['Day'].isin(block_day_total_range)]

        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        new_df = averaging_process(df)

        new_df = new_df[col_names]
        save_file_message(new_df)


def ld_probe_id_average(animal_id):
    print('You have selected the LD Probe(Select ID Avg) button!')
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        selected_id = int(animal_id.get())
        df = df.loc[df['ID'] == selected_id]

        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect', 'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        new_df = averaging_process(df)
        new_df = new_df[col_names]
        save_file_message(new_df)


def make_ld_probe_buttons(tk, root):
    ld_probe_button_last_day_all = tk.Button(root, text='LD Probe (Last Day Difficulty All)',
                                             command=ld_probe_last_day_difficulty, width=30)
    ld_probe_button_last_day_all.grid(row=0, column=0)

    ld_probe_enter_day = tk.Entry(root, width=30, justify='center')
    ld_probe_enter_day.grid(row=1, column=1)

    ld_probe_button_select_day = tk.Button(root, text='LD Probe (Select Day)',
                                           command=lambda: ld_probe_select_day(ld_probe_enter_day), width=30)
    ld_probe_button_select_day.grid(row=1, column=0)

    ld_probe_enter_id = tk.Entry(root, width=30, justify='center')
    ld_probe_enter_id.grid(row=2, column=1)

    ld_probe_button_select_id = tk.Button(root, text='LD Probe (Select ID)',
                                          command=lambda: ld_probe_select_id(ld_probe_enter_id), width=30)
    ld_probe_button_select_id.grid(row=2, column=0)

    ld_probe_block_number = tk.Entry(root, width=30, justify='center')
    ld_probe_block_number.grid(row=3, column=1)

    ld_probe_button_select_block = tk.Button(root, text='LD Probe (Select Block)',
                                             command=lambda: ld_probe_select_block(
                                                 ld_probe_block_number), width=30)
    ld_probe_button_select_block.grid(row=3, column=0)

    ld_probe_button_last_day_avg = tk.Button(root, text='LD Probe (Last Day All Avg)', command=ld_probe_last_day_avg,
                                             width=30
                                             )
    ld_probe_button_last_day_avg.grid(row=4, column=0)

    ld_probe_button_block_avg_text = tk.Entry(root, width=30, justify='center')
    ld_probe_button_block_avg_text.grid(row=5, column=1)

    ld_probe_button_block_avg = tk.Button(root, text='LD Probe (Block Avg)',
                                          command=lambda: ld_probe_block_average(ld_probe_button_block_avg_text),
                                          width=30)
    ld_probe_button_block_avg.grid(row=5, column=0)

    ld_probe_button_id_avg_text = tk.Entry(root, width=30, justify='center')
    ld_probe_button_id_avg_text.grid(row=6, column=1)

    ld_probe_button_id_avg = tk.Button(root, text='LD Probe (ID Avg)',
                                       command=lambda: ld_probe_id_average(ld_probe_button_id_avg_text), width=30)
    ld_probe_button_id_avg.grid(row=6, column=0)
