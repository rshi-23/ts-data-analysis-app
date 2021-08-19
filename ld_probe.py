from setup import *


def get_last_day_difficulty(df):
    """
    This function gets the last day of each difficulty for each LD Probe block. Since each block is 4 days by default,
    this function will return every 2nd and 4th day. If there are multiple blocks being passed in, the function will
    accurately assign which block the animal's row belongs to.

    :param df: A dataframe that represents all the cleaned LD Probe data.
    """

    df['Day'] = df.groupby('ID').cumcount() + 1
    df['Day'] = df['Day'].astype(float)
    df['Block'] = np.ceil(df['Day'] / 4)
    df.drop(df.loc[df['Day'] % 2 == 1].index, inplace=True)


def ld_probe_delete_other_difficulties(df):
    """
    This function deletes the other location discrimination difficulties that are not used in LD Probe. Since both LD
    Train and LD Probe run on the same ABET schedule, we separate LD Train and LD Probe by LD difficulty. In LD Probe,
    we want all the easy and hard rows. This function will drop all the intermediate and undetermined rows from the
    working dataframe

    :param df: A dataframe that represents all the cleaned LD Probe data.
    """

    # for ld train, we want only intermediate, delete all others
    df.drop(df.loc[df['Type'] == 'intermediate'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'undetermined'].index, inplace=True)
    df.sort_values(['Date', 'ID'], ascending=[1, 1], inplace=True)
    df['Day'] = df.groupby('ID').cumcount() + 1


def ld_probe_last_day_difficulty():
    """
    This function creates a csv file for the LD Probe test. Each row will be the last day of each difficulty within each
    block. Afterward, the function will ask the user to save the newly created csv file in a directory.
    """

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        get_last_day_difficulty(df)
        save_file_message(df)


def ld_probe_widget_check(widget):
    """
    This function checks the LD Probe select id and select day widgets. It checks if the value given is a valid numeric
    value, otherwise it print an error message and return None.

    :param widget: An entry widget that contains the value of the selected id/day.
    :return: None: If the function doesn't pass the widget check, it will stop and return None.
    """

    try:
        widget_value = int(widget.get())
    except ValueError:
        mb.showerror('LD Probe Error', 'ld_probe_widget_check() error: The selected day/id is invalid or empty!')
        print('ld_probe_widget_check() error: The selected day/id is invalid or empty!')
        return None

    return widget_value


def ld_probe_select_day(enter_day):
    """
    This function creates a csv file for the LD Probe test. Each row will be the selected day for each animal.
    Afterward, the function will ask the user to save the newly created csv file in a directory.

    :param enter_day: An entry widget that contains the value for the selected day.
    :return: None: If the function doesn't pass the widget check, it will stop and return None.
    """

    if ld_probe_widget_check(enter_day) is not None:
        selected_day = ld_probe_widget_check(enter_day)
    else:
        mb.showerror('LD Probe Error', 'ld_probe_select_id() error: The selected day criteria is empty or invalid!')
        print('ld_probe_select_id() error: The selected day criteria is empty or invalid!')
        return None

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def ld_probe_select_id(enter_id):
    """
    This function creates a csv file for the LD Probe test. Each row will be all the rows for the selected animal id.
    Afterward, the function will ask the user to save the newly created csv file in a directory.

    :param enter_id: An entry widget that contains the value for the selected id.
    :return: None: If the function doesn't pass the widget check, it will stop and return None.
    """

    if ld_probe_widget_check(enter_id) is not None:
        selected_id = ld_probe_widget_check(enter_id)
    else:
        mb.showerror('LD Probe Error', 'ld_probe_select_id() error: The selected id criteria is empty or invalid!')
        print('ld_probe_select_id() error: The selected id criteria is empty or invalid!')
        return None

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)


def ld_probe_select_block(block_number):
    """
    This function creates a csv file for the LD Probe test. Each row will be the last days of a specific block. This
    function works better if there are multiple blocks that are being entered. For single blocks, please use the Last
    Day Difficulty All button! Afterward, the function will ask the user to save the newly created csv file in a
    directory.

    :param block_number: An entry widget that contains the value for the block number.
    :return: None: If the function doesn't pass the widget check, it will stop and return None.
    """

    if ld_probe_widget_check(block_number) is not None:
        selected_block = ld_probe_widget_check(block_number)
    else:
        mb.showerror('LD Probe Error', 'ld_probe_select_block() error: The block number criteria is empty or invalid!')
        print('ld_probe_select_block() error: The block number criteria is empty or invalid!')
        return None

    block_day_range_max = 4 * selected_block
    block_day_range_min = block_day_range_max - 3
    block_day_total_range = [*range(block_day_range_min, block_day_range_max + 1, 1)]

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[(df['Day'] == block_day_total_range[1]) | (df['Day'] == block_day_total_range[3])]

        save_file_message(df)


def averaging_process(df):
    """
    This function does inter-difficulty averages. It will calculate the averages for the two easy days and the two hard
    days and return them as separate rows. If the animal reaches a criteria on one day and does not reach the same
    criteria the next day, the average will automatically be the result of the day that it actually reached the
    criteria.

    :param df: A dataframe that contains all the cleaned LD Probe data with only easy and hard rows.
    :return: new_df: A dataframe that contains all the inter-difficulty averages.
    """

    new_df = pd.DataFrame()
    row_index = 0

    while row_index < df.shape[0] - 1:
        rows_to_avg = list()

        # average two rows at a time
        for avg_index in range(2):
            row_to_add = df.loc[avg_index + row_index]
            rows_to_avg.append(row_to_add)

        # check that the ids are same and the days are 1 day apart and then does the averaging
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
    """
    This function creates a csv file for the LD Probe test. Each row will be the inter-difficulty averages for each
    animal. Afterward, the function will ask the user to save the newly created csv file in a directory.
    """

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect',
                     'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        new_df = averaging_process(df)

        new_df = new_df[col_names]
        save_file_message(new_df)


def ld_probe_block_average(block_number):
    """
    This function creates a csv file for the LD Probe test. Each row will be the inter-difficulty averages for each
    animal for a specific block. Afterward, the function will ask the user to save the newly created csv file
    in a directory.

    :param block_number: An entry widget that contains the value of the block number.
    :return: None: If the function doesn't pass the widget check, it will stop and return None.
    """

    if ld_probe_widget_check(block_number) is not None:
        selected_block = ld_probe_widget_check(block_number)
    else:
        mb.showerror('LD Probe Error', 'ld_probe_select_block() error: The block number criteria is empty or invalid!')
        print('ld_probe_select_block() error: The block number criteria is empty or invalid!')
        return None

    block_day_range_max = 4 * selected_block
    block_day_range_min = block_day_range_max - 3
    block_day_total_range = [*range(block_day_range_min, block_day_range_max + 1, 1)]

    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[df['Day'].isin(block_day_total_range)]

        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect',
                     'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        new_df = averaging_process(df)

        new_df = new_df[col_names]
        save_file_message(new_df)


def ld_probe_id_average(animal_id, difficulty_type):
    """
    This function creates a csv file for the LD Probe test. It will return a row with the average performance of all the
    test for a selected animal. Afterward, the function will ask the user to save the newly created csv file in a
    directory.

    :param animal_id: An entry widget that contains the value of the selected id.
    :param difficulty_type: A string that determines which determines which difficulty to average.
    """
    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        selected_id = int(animal_id.get())
        df = df.loc[(df['ID'] == selected_id) & (df['Type'] == difficulty_type)]

        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['Date', 'ID', 'Type', 'Day', 'SessionLength', 'NumberOfTrial', 'PercentCorrect',
                     'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        avg_col = ['SessionLength', 'NumberOfTrial', 'PercentCorrect',
                   'NumberOfReversal',
                   'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                   'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                   'SessionLengthTo2ndReversalDuration',
                   'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                   'PercentCorrectTo2ndReversal']

        new_df = df.copy(deep=True)
        new_df = new_df[col_names]

        for col in avg_col:
            new_df['Avg' + col] = df[col].mean(axis=0)
            new_df.drop(col, axis=1, inplace=True)

        new_df.drop_duplicates(subset='ID', keep='last', inplace=True)

        save_file_message(new_df)


def ld_probe_type_average(difficulty_type):
    """
    This function creates a csv file for the LD Probe test. The resulting csv file will have the average performance
    for all animals based on difficulty type. Afterward, the function will ask the user to save the newly created csv
    file in a directory.

    :param difficulty_type: A string that determines which determines which difficulty to average.
    """
    print('You have selected the LD Probe(Select ID Avg) button!')
    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        df = df.loc[(df['Type'] == difficulty_type)]

        df.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
        df.reset_index(drop=True, inplace=True)

        col_names = ['ID', 'SessionLength', 'NumberOfTrial', 'PercentCorrect',
                     'NumberOfReversal',
                     'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                     'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                     'SessionLengthTo2ndReversalDuration',
                     'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                     'PercentCorrectTo2ndReversal']

        avg_col = ['SessionLength', 'NumberOfTrial', 'PercentCorrect',
                   'NumberOfReversal',
                   'TotalITITouches', 'TotalBlankTouches', 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency',
                   'MeanIncorrectTouchLatency', 'SessionLengthTo1stReversalDuration',
                   'SessionLengthTo2ndReversalDuration',
                   'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                   'PercentCorrectTo2ndReversal']

        new_df = pd.DataFrame(columns=col_names)
        df.reset_index(drop=True, inplace=True)
        for col in avg_col:
            new_df[col] = df.groupby('ID')[col].mean()

        new_df['ID'] = df['ID'].unique()

        save_file_message(new_df)


def make_ld_probe_buttons(tk, root):
    """
    This function creates all the location discrimination probe buttons found on the LD Probe sub-menu.

    :param tk: The TKinter library
    :param root: A specific frame where all the buttons will live on.
    """

    # creates all ld probe buttons
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

    spacer_btn = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn.grid(row=4, columnspan=2)

    ld_probe_button_last_day_avg = tk.Button(root, text='LD Probe (Last Day All Avg)', command=ld_probe_last_day_avg,
                                             width=30
                                             )
    ld_probe_button_last_day_avg.grid(row=5, column=0)

    ld_probe_button_block_avg_text = tk.Entry(root, width=30, justify='center')
    ld_probe_button_block_avg_text.grid(row=6, column=1)
    ld_probe_button_block_avg = tk.Button(root, text='LD Probe (Block Avg)',
                                          command=lambda: ld_probe_block_average(ld_probe_button_block_avg_text),
                                          width=30)
    ld_probe_button_block_avg.grid(row=6, column=0)

    ld_probe_button_id_avg_text = tk.Entry(root, width=30, justify='center')
    ld_probe_button_id_avg_text.grid(row=7, column=1)
    ld_probe_button_id_avg = tk.Button(root, text='LD Probe (ID Avg Easy)',
                                       command=lambda: ld_probe_id_average(ld_probe_button_id_avg_text, 'easy'),
                                       width=30)
    ld_probe_button_id_avg.grid(row=7, column=0)

    ld_probe_button_id_avg_text_two = tk.Entry(root, width=30, justify='center')
    ld_probe_button_id_avg_text_two.grid(row=8, column=1)
    ld_probe_button_id_avg_two = tk.Button(root, text='LD Probe (ID Avg Hard)',
                                           command=lambda: ld_probe_id_average(ld_probe_button_id_avg_text, 'hard'),
                                           width=30)
    ld_probe_button_id_avg_two.grid(row=8, column=0)

    ld_probe_button_avg_easy = tk.Button(root, text='LD Probe (Avg Easy)',
                                         command=lambda: ld_probe_type_average('easy'),
                                         width=30)
    ld_probe_button_avg_easy.grid(row=9, column=0)
    ld_probe_button_avg_hard = tk.Button(root, text='LD Probe (Avg Hard)',
                                         command=lambda: ld_probe_type_average('hard'),
                                         width=30)
    ld_probe_button_avg_hard.grid(row=10, column=0)
