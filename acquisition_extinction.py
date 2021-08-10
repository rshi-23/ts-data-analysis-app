from setup import *


def get_acq_final_days(df, criteria, correct_amount, session_length):
    """
    This function returns the last days for the Acquisition test. The function grabs all the rows that meet the minimum
    correct trials amount and the maximum session length amount. Then it calculates the first instance when the animal
    meets the n days in a row criteria. Then it will return a dataframe that contains all the first instances of the
    animals that met the criteria of n days in a row with at least the minimum correct amount and finished the test in
    less than or equal to the maximum session length.

    :param df: A dataframe that represents the cleaned Acquisition data.
    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria

    :return: df_copy: A dataframe with all the first instances of the animals that met the criteria.
    """

    df['Day'] = df.groupby('ID').cumcount() + 1
    df_copy = df.copy(deep=True)
    df_copy.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
    df_copy = df_copy.loc[(df_copy['Corrects'] >= correct_amount) & (df_copy['SessionLength'] <= session_length)]
    df_copy.replace(0, 1, inplace=True)

    df_copy.sort_values(['ID', 'Day'], inplace=True)
    df_copy.reset_index(drop=True, inplace=True)

    row_index = 0
    while row_index < df_copy.shape[0] - (criteria - 1):
        rows_to_sum = list()
        # compare x amount of rows in a row
        for sum_numbers in range(criteria):
            rows_to_add = df_copy.loc[row_index + sum_numbers]
            while rows_to_add['ID'] != df_copy.at[row_index, 'ID'] and row_index < df_copy.shape[0] - 1:
                row_index += 1
            rows_to_sum.append(rows_to_add)

        last_row_info = rows_to_sum[-1]

        if len(rows_to_sum) < criteria:
            continue

        if last_row_info['ID'] != rows_to_sum[0]['ID']:
            continue

        day_counter = list()
        for row in rows_to_sum:
            day_counter.append(row['Day'])
        # if the days are consecutive, it passes the criteria
        if day_counter == sorted(range(day_counter[0], day_counter[-1] + 1)):
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    # only take the first occurrence of the rows that passed the criteria
    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_acquisition_normal(df, criteria, correct_amount, session_length):
    """
    This function drops rows for trials after the criteria met date. The resulting dataframe will contain rows with the
    animal's start date to the criteria end date. If an animal never reaches the criteria, then it will display all the
    trials from the start of testing to the end of testing (for Acquisition).

    :param df: A dataframe that represents cleaned Acquisition data
    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    """

    df_copy = get_acq_final_days(df, criteria, correct_amount, session_length)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def acq_widget_check(criteria, correct_amount, session_length):
    """
    This function checks that the criteria widgets are not empty and have valid inputs.

    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    :return: (criteria_value, correct_trials_num, session_time_sec): The values for all the criteria
    """

    try:
        criteria_value = int(criteria.get())
    except ValueError:
        print('acq_widget_check() error: The n days in a row is either empty or invalid!')
        return None

    try:
        correct_trials_num = int(correct_amount.get())
    except ValueError:
        print('acq_widget_check() error: The correct trials is either empty or invalid!')
        return None

    try:
        session_time_sec = int(session_length.get())
    except ValueError:
        print('acq_widget_check() error: The session length is either empty or invalid!')
        return None

    return criteria_value, correct_trials_num, session_time_sec


def button_acquisition_all(criteria, correct_amount, session_length):
    """
    This function creates a csv file for the Acquisition test. Each animal will have rows that start from their
    start date to their criteria met date. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    """

    if acq_widget_check(criteria, correct_amount, session_length) is not None:
        criteria_value, correct_trials_num, session_time_sec = \
            acq_widget_check(criteria, correct_amount, session_length)
    else:
        print('button_acquisition_all() error: One of the three criteria is invalid or empty!')
        return

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        save_file_message(df)


def button_acquisition_first(criteria, correct_amount, session_length):
    """
    This function creates a csv file for the Acquisition test. Each row will be the first day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    """

    if acq_widget_check(criteria, correct_amount, session_length) is not None:
        criteria_value, correct_trials_num, session_time_sec = \
            acq_widget_check(criteria, correct_amount, session_length)
    else:
        print('button_acquisition_first() error: One of the three criteria is invalid or empty!')
        return

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_acquisition_last(criteria, correct_amount, session_length):
    """
    This function creates a csv file for the Acquisition test. Each row will be the last day the animal ran the
    test. If the animal does not meet the criteria, then their last date will be the last day of the test. At the end,
    the function will ask the user to save the newly created csv file in a directory.

    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    """

    if acq_widget_check(criteria, correct_amount, session_length) is not None:
        criteria_value, correct_trials_num, session_time_sec = \
            acq_widget_check(criteria, correct_amount, session_length)
    else:
        print('button_acquisition_last() error: One of the three criteria is invalid or empty!')
        return

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_acquisition_select_day(select_day, criteria, correct_amount, session_length):
    """
    This function creates a csv file for the Acquisition test. Each row will be the selected day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param select_day: An entry widget that contains the value of the selected day
    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    :return:
    """

    if acq_widget_check(criteria, correct_amount, session_length) is not None:
        criteria_value, correct_trials_num, session_time_sec = \
            acq_widget_check(criteria, correct_amount, session_length)
    else:
        print('button_acquisition_select_day() error: One of the three criteria is invalid or empty!')
        return

    try:
        selected_day = int(select_day)
    except ValueError:
        print('button_acquisition_select_day() error: The selected day is empty or invalid!')
        return

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def button_acquisition_select_id(select_id, criteria, correct_amount, session_length):
    """
    This function creates a csv file for the Acquisition test. Each row will be all the trials from start date to
    criteria date for a selected animal id. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param select_id: An entry widget that contains the value of the selected id
    :param criteria: The n days in the row that the animal needs to complete with the other criteria
    :param correct_amount: The minimum required correct trials amount that animal needs to achieve
    :param session_length: The maximum session length given to the animal to achieve the other criteria
    """

    if acq_widget_check(criteria, correct_amount, session_length) is not None:
        criteria_value, correct_trials_num, session_time_sec = \
            acq_widget_check(criteria, correct_amount, session_length)
    else:
        print('button_acquisition_select_id() error: One of the three criteria is invalid or empty!')
        return

    try:
        selected_id = int(select_id)
    except ValueError:
        print('button_acquisition_select_id() error: The selected id is empty or invalid!')
        return

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)


def get_ext_last_day(df, criteria, max_days, omission_amount):
    """
    This function determines the last day (aka the day the animal met the Extinction criteria for the first time). The
    function grabs all the rows that meets the minimum required reversal number and then checks if it passes the
    n days out of n+1 days criteria. If it passes the criteria, the function will mark the day that it passed the
    criteria. At the end, the function will grab all the first occurrences of when the animal passed the criteria and
    return it as a new dataframe.

    :param df: A dataframe that represents cleaned Extinction data
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param max_days: A value that represents how many days are allotted to meet the n/n+1 criteria
    :param omission_amount: A value that represents the minimum required omissions for an animal
    :return: df_copy: A dataframe that only contains the rows that the animals met their criteria on. If an animal did
    not reach the criteria, it will not show up.
    """

    df['Day'] = df.groupby('ID').cumcount() + 1
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[(df_copy['Omissions'] >= omission_amount)]

    df_copy.sort_values(['ID', 'Day'], inplace=True)

    df_copy.reset_index(drop=True, inplace=True)

    row_index = 0
    while row_index < df_copy.shape[0] - (criteria - 1):
        rows_to_sum = list()
        # compare rows with the same ID
        for sum_numbers in range(criteria):
            row_to_add = df_copy.loc[row_index + sum_numbers]
            while row_to_add['ID'] != df_copy.at[row_index, 'ID'] and row_index < df_copy.shape[0] - 1:
                row_index += 1
            rows_to_sum.append(row_to_add)

        last_row_info = rows_to_sum[-1]
        if len(rows_to_sum) < criteria:
            continue
        if last_row_info['ID'] != rows_to_sum[0]['ID']:
            continue

        day_counter = list()
        for row in rows_to_sum:
            day_counter.append(row['Day'])
        # if the days are consecutive, it passes the criteria
        if day_counter == sorted(range(day_counter[0], day_counter[-1] + 1)):
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        difference_list = np.diff(day_counter)
        max_days_apart_ctn = difference_list.tolist().count(1)
        one_day_apart_ctn = difference_list.tolist().count(2)
        total_days = sum(difference_list)

        # due to the n/n+1 criteria, there can only be (1) count of a difference of two days and the rest have to be 1s
        if total_days == criteria and one_day_apart_ctn == max_days - 3 and max_days_apart_ctn == 1:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    # only take the first occurrence of the rows that passed the criteria
    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_extinction_all(df, criteria, max_days, omission_amount):
    """
    This function drops rows for trials after the criteria met date. The resulting dataframe will contain rows with the
    animal's start date to the criteria end date. If an animal never reaches the criteria, then it will display all the
    trials from the start of testing to the end of testing (for Extinction).

    :param df: A dataframe that represents cleaned Extinction data
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param max_days: A value that represents how many days are allotted to meet the n/n+1 criteria
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    df_copy = get_ext_last_day(df, criteria, max_days, omission_amount)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def ext_widget_check(criteria, omission_amount):
    """
    This function checks that the criteria widgets are not empty and have valid inputs.

    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    :return: (criteria_list, min_omission): The n and n+1 of the criteria and the minimum required omission amount
    """

    if len(criteria.get()) != 0:
        criteria_list = criteria.get().split('/')
    else:
        print('ext_widget_check() error: The criteria days are empty or invalid!')
        return None

    try:
        min_omission = int(omission_amount.get())
    except ValueError:
        print('ext_widget_check() error: The omissions is empty or invalid!')
        return None

    return criteria_list, min_omission


def ext_criteria_list_check(criteria_list):
    """
    This function gets to make sure that the criteria for n/n+1 days is valid and that both n and n+1 are numeric.

    :param criteria_list: A list version of the criteria input string, separated by '/'
    :returns: (criteria_value, criteria_max_days): The n days and the n+1 days
    """

    try:
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        return criteria_value, criteria_max_days
    except ValueError:
        print('ext_criteria_list_check() error: The criteria days are empty or invalid!')
        return None


def button_extinction_all(criteria, omission_amount):
    """
    This function creates a csv file for the Extinction test. Each animal will have rows that start from their
    start date to their criteria met date. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    if ext_widget_check(criteria, omission_amount) is not None:
        criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    else:
        print('button_extinction_all() error: One of the criteria is empty or invalid!')
        return None

    if ext_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
    else:
        print('button_extinction_all() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('Ext')
    if df is not None:
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        save_file_message(df)


def button_extinction_first(criteria, omission_amount):
    """
    This function creates a csv file for the Extinction test. Each row will be the first day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    if ext_widget_check(criteria, omission_amount) is not None:
        criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    else:
        print('button_extinction_first() error: One of the criteria is empty or invalid!')
        return None

    if ext_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
    else:
        print('button_extinction_first() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('Ext')
    if df is not None:
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_extinction_last_day(criteria, omission_amount):
    """
    This function creates a csv file for the Extinction test. Each row will be the last day the animal ran the
    test. If the animal does not meet the criteria, then their last date will be the last day of the test. At the end,
    the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    if ext_widget_check(criteria, omission_amount) is not None:
        criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    else:
        print('button_extinction_last_day() error: One of the criteria is empty or invalid!')
        return None

    if ext_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
    else:
        print('button_extinction_last_day() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('Ext')
    if df is not None:
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df.sort_values(['ID', 'Date'], inplace=True)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_extinction_select_day(selected_day, criteria, omission_amount):
    """
    This function creates a csv file for the Extinction test. Each row will be the selected day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param selected_day: A widget that contains the value that represents the selected day.
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    try:
        select_day = int(selected_day.get())
    except ValueError:
        print('button_extinction_select_day() error: The selected day is empty or invalid!')
        return

    if ext_widget_check(criteria, omission_amount) is not None:
        criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    else:
        print('button_extinction_select_day() error: One of the criteria is empty or invalid!')
        return None

    if ext_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
    else:
        print('button_extinction_select_day() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('Ext')
    if df is not None:
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['Day'] == select_day]
        save_file_message(df)


def button_extinction_select_id(selected_id, criteria, omission_amount):
    """
    This function creates a csv file for the Extinction test. Each row will be all the trials from start date to
    criteria date for a selected animal id. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param selected_id: A widget that contains the value that represents the selected id
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param omission_amount: A value that represents the minimum required omissions for an animal
    """

    try:
        select_id = int(selected_id.get())
    except ValueError:
        print('button_extinction_select_id() error: The selected id is empty or invalid!')
        return

    if ext_widget_check(criteria, omission_amount) is not None:
        criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    else:
        print('button_extinction_select_id() error: One of the criteria is empty or invalid!')
        return None

    if ext_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
    else:
        print('button_extinction_select_id() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('Ext')
    if df is not None:
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['ID'] == select_id]
        save_file_message(df)


def make_extinction_buttons(tk, root):
    """
    This function creates all the extinction buttons found on the Extinction Paradigm sub-menu.

    :param tk: The TKinter library
    :param root: A specific frame where all the buttons will live on.
    :return:
    """

    # makes acquisition criteria widgets
    acq_criteria_label = tk.Label(root, text='Enter the criteria as n days in a row:')
    acq_criteria_label.grid(row=0, column=0)
    acq_criteria_text = tk.Entry(root, width=30, justify='center')
    acq_criteria_text.grid(row=0, column=1)

    acq_min_correct_label = tk.Label(root, text='Enter the min correct trials amount:')
    acq_min_correct_label.grid(row=1, column=0)
    acq_min_correct_text = tk.Entry(root, width=30, justify='center')
    acq_min_correct_text.grid(row=1, column=1)

    acq_min_session_length_label = tk.Label(root, text='Enter the max session length req:')
    acq_min_session_length_label.grid(row=2, column=0)
    acq_min_session_length_text = tk.Entry(root, width=30, justify='center')
    acq_min_session_length_text.grid(row=2, column=1)

    # makes acquisition buttons all
    acquisition_button = tk.Button(root, text='Acquisition (All)',
                                   command=lambda: button_acquisition_all(acq_criteria_text, acq_min_correct_text,
                                                                          acq_min_session_length_text), width=30)
    acquisition_button.grid(row=3, column=0)
    acquisition_first_button = tk.Button(root, text='Acquisition (First Day)',
                                         command=lambda: button_acquisition_first(acq_criteria_text,
                                                                                  acq_min_correct_text,
                                                                                  acq_min_session_length_text),
                                         width=30)
    acquisition_first_button.grid(row=4, column=0)
    acquisition_last_button = tk.Button(root, text='Acquisition (Last Day)',
                                        command=lambda: button_acquisition_last(acq_criteria_text, acq_min_correct_text,
                                                                                acq_min_session_length_text), width=30)
    acquisition_last_button.grid(row=5, column=0)

    select_acq_day_text = tk.Entry(root, width=30, justify='center')
    select_acq_day_text.grid(row=6, column=1)

    acquisition_select_button = tk.Button(root, text='Acquisition (Select Day)',
                                          command=lambda: button_acquisition_select_day(select_acq_day_text,
                                                                                        acq_criteria_text,
                                                                                        acq_min_correct_text,
                                                                                        acq_min_session_length_text),
                                          width=30)
    acquisition_select_button.grid(row=6, column=0)

    acquisition_select_id_text = tk.Entry(root, width=30, justify='center')
    acquisition_select_id_text.grid(row=7, column=1)
    acquisition_select_id_btn = tk.Button(root, text='Acquisition (Select ID)',
                                          command=lambda: button_acquisition_select_id(acquisition_select_id_text,
                                                                                       acq_criteria_text,
                                                                                       acq_min_correct_text,
                                                                                       acq_min_session_length_text),
                                          width=30)
    acquisition_select_id_btn.grid(row=7, column=0)

    # visual spacer between acq and ext
    spacer_btn_one = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_one.grid(row=8, columnspan=2)

    # makes extinction criteria widgets
    ext_criteria_label = tk.Label(root, text='Enter the criteria as n days/n+1 days:')
    ext_criteria_label.grid(row=9, column=0)
    ext_criteria_text = tk.Entry(root, width=30, justify='center')
    ext_criteria_text.grid(row=9, column=1)

    ext_min_omissions_label = tk.Label(root, text='Enter the min omission amount:')
    ext_min_omissions_label.grid(row=10, column=0)
    ext_min_omissions_text = tk.Entry(root, width=30, justify='center')
    ext_min_omissions_text.grid(row=10, column=1)

    # makes extinction buttons all
    extinction_all_button = tk.Button(root, text='Extinction (All)',
                                      command=lambda: button_extinction_all(ext_criteria_text, ext_min_omissions_text),
                                      width=30)
    extinction_all_button.grid(row=11, column=0)
    extinction_first_button = tk.Button(root, text='Extinction (First Day)',
                                        command=lambda: button_extinction_first(ext_criteria_text,
                                                                                ext_min_omissions_text), width=30)
    extinction_first_button.grid(row=12, column=0)
    extinction_last_button = tk.Button(root, text='Extinction (Last Day)',
                                       command=lambda: button_extinction_last_day(ext_criteria_text,
                                                                                  ext_min_omissions_text), width=30)
    extinction_last_button.grid(row=13, column=0)
    extinction_select_text = tk.Entry(root, width=30, justify='center')
    extinction_select_text.grid(row=14, column=1)
    extinction_select_day_button = tk.Button(root, text='Extinction (Select Day)',
                                             command=lambda: button_extinction_select_day(extinction_select_text,
                                                                                          ext_criteria_text,
                                                                                          ext_min_omissions_text),
                                             width=30)
    extinction_select_day_button.grid(row=14, column=0)
    extinction_select_id_text = tk.Entry(root, width=30, justify='center')
    extinction_select_id_text.grid(row=15, column=1)
    extinction_select_id_button = tk.Button(root, text='Extinction (Select ID)',
                                            command=lambda: button_extinction_select_id(extinction_select_id_text,
                                                                                        ext_criteria_text,
                                                                                        ext_min_omissions_text),
                                            width=30)
    extinction_select_id_button.grid(row=15, column=0)
