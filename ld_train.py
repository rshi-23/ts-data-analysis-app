from setup import *


def get_ld_last_days(df, criteria, max_days, min_reversal_number):
    """
    This function determines the last day (aka the day the animal met the LD train criteria for the first time). The
    function grabs all the rows that meets the minimum required reversal number and then checks if it passes the
    n days out of n+1 days criteria. If it passes the criteria, the function will mark the day that it passed the
    criteria. At the end, the function will grab all the first occurrences of when the animal passed the criteria and
    return it as a new dataframe.

    :param df: A dataframe that represents cleaned LD Train data
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param max_days: A value that represents how many days are allotted to meet the n/n+1 criteria
    :param min_reversal_number: A value that represents the minimum required reversal number for an animal
    :return: df_copy: A dataframe that only contains the rows that the animals met their criteria on. If an animal did
    not reach the criteria, it will not show up.
    """

    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[df_copy['NumberOfReversal'] >= min_reversal_number]

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
        max_days_apart_ctn = difference_list.tolist().count(2)
        one_day_apart_ctn = difference_list.tolist().count(1)
        total_days = sum(difference_list)

        # due to the n/n+1 criteria, there can only be (1) count of a difference of two days and the rest have to be 1s
        if total_days == criteria and max_days_apart_ctn == 1 and one_day_apart_ctn == max_days - 3:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    # only take the first occurrence of the rows that passed the criteria
    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_ld_train_normal(df, criteria, max_days, min_reversal_number):
    """
    This function drops rows for trials after the criteria met date. The resulting dataframe will contain rows with the
    animal's start date to the criteria end date. If an animal never reaches the criteria, then it will display all the
    trials from the start of testing to the end of testing (for LD Train).

    :param df: A dataframe that represents cleaned LD Train data
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param max_days: A value that represents how many days are allotted to meet the n/n+1 criteria
    :param min_reversal_number: A value that represents the minimum required reversal number for an animal
    """

    df_copy = get_ld_last_days(df, criteria, max_days, min_reversal_number)
    # drop rows that have larger day values and same ids (those are probably extra days to retain mouse memory)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def get_ld_train_criteria_day_all(df, criteria, max_days, min_reversal_number):
    """
    This function will call the get_ld_train_normal() and then get all the last days. For animals that passed
    the criteria, their last day is the day they met the criteria. For animals that did not pass the criteria, their
    last day is the last day the test was ran.

:param df: A dataframe that represents cleaned LD Train data
    :param criteria: A value that represents how many days the minimum required reversal number must be met
    :param max_days: A value that represents how many days are allotted to meet the n/n+1 criteria
    :param min_reversal_number: A value that represents the minimum required reversal number for an animal
    """
    get_ld_train_normal(df, criteria, max_days, min_reversal_number)
    df.drop_duplicates(subset='ID', keep='last', inplace=True)


def ld_train_delete_other_difficulties(df):
    """
    This function will delete the other difficulties that aren't used in LD Train. The test type of LD train is
    intermediate, so this will drop hard, easy, and undetermined types from the dataframe. The resulting dataframe
    should only have intermediate type rows.

    :param df: A dataframe that contains cleaned LD train data
    """

    # for ld train, we want only intermediate, delete all others
    df.drop(df.loc[df['Type'] == 'hard'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'easy'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'undetermined'].index, inplace=True)
    df.sort_values(['ID', 'Date'], ascending=[1, 1], inplace=True)
    df['Day'] = df.groupby('ID').cumcount() + 1


def ld_train_criteria_min_rev_check(criteria, min_reversal_number):
    """
    This function checks that the criteria widgets are not empty and have valid inputs.

    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    :returns: The criteria list version of the criteria input string, separated by '/' and the minimum reversal number
    """

    try:
        criteria_list = criteria.get().split('/')
    except ValueError:
        mb.showerror('LD Train Criteria Error',
                     'ld_train_criteria_min_rev_check() error: Criteria might be empty or invalid!')
        print('ld_train_criteria_min_rev_check() error: Criteria might be empty or invalid!')
        return None

    try:
        min_rev = int(min_reversal_number.get())
    except ValueError:
        mb.showerror('LD Train Criteria Error',
                     'ld_train_criteria_min_rev_check() error: Minimum required reversal number might be empty'
                     ' or is not numeric!')
        print('ld_train_criteria_min_rev_check() error: Minimum required reversal number might be empty'
              ' or is not numeric!')
        return None

    return criteria_list, min_rev


def ld_criteria_list_check(criteria_list):
    """
    This function gets to make sure that the criteria for n/n+1 days is valid and that both n and n+1 are numeric.

    :param criteria_list: A list version of the criteria input string, separated by '/'
    :returns: The n days and the n+1 days
    """

    try:
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        return criteria_value, criteria_max_days
    except ValueError:
        mb.showerror('LD Train Criteria Error',
                     'ld_criteria_list_check() error: Criteria is either empty or invalid!')
        print('ld_criteria_list_check() error: Criteria is either empty or invalid!')
        return None


def button_ld_train_all(criteria, min_reversal_number):
    """
    This function creates a csv file for the LD Train test. Each animal will have rows that start from their
    start date to their criteria met date. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    """

    # check that the inputs to the criteria widgets are valid
    if ld_train_criteria_min_rev_check(criteria, min_reversal_number) is not None:
        criteria_list, min_rev = ld_train_criteria_min_rev_check(criteria, min_reversal_number)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_all() error: One of the two criteria is empty or invalid!')
        print('button_ld_train_all() error: One of the two criteria is empty or invalid!')
        return None

    if ld_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ld_criteria_list_check(criteria_list)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_all() error: The n/n+1 days criteria is empty or invalid!')
        print('button_ld_train_all() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        get_ld_train_normal(df, criteria_value, criteria_max_days, min_rev)
        save_file_message(df)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_all() error:  One of the criterias is invalid or you hit the cancel button!!')
        print('button_ld_train_all() error:  One of the criterias is invalid or you hit the cancel button!')
        return None


def button_ld_train_select_day(enter_day, criteria, min_reversal_number):
    """
    This function creates a csv file for the LD Train test. Each row will be the selected day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param enter_day: A widget that contains the value that represents the selected day.
    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    """

    # check that the inputs to the criteria widgets are valid
    try:
        selected_day = int(enter_day.get())
    except ValueError:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_id() error: The select id value is empty or invalid!')
        print('button_ld_train_select_id() error: The select id value is empty or invalid!')
        mb.showerror("ERROR", 'button_ld_train_select_id() error: The select id value is empty or invalid!')
        return None

    # check that the inputs to the criteria widgets are valid
    if ld_train_criteria_min_rev_check(criteria, min_reversal_number) is not None:
        criteria_list, min_rev = ld_train_criteria_min_rev_check(criteria, min_reversal_number)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_day() error: One of the three criteria is empty or invalid!')
        print('button_ld_train_select_day() error: One of the three criteria is empty or invalid!')
        return None

    if ld_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ld_criteria_list_check(criteria_list)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_day() error: The n/n+1 days criteria is empty or invalid!')
        print('button_ld_train_select_day() error: One of the criteria is empty or invalid!')
        return None

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        get_ld_train_normal(df, criteria_value, criteria_max_days, min_rev)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)
    else:
        mb.showerror('LD Train Criteria Error',
                     'ld_train_criteria_min_rev_check() error: Criteria might be empty or invalid!')
        print('button_ld_train_select_day() error: One of the criterias is invalid or you hit the cancel button!')
        return None


def button_ld_train_first_day(criteria, min_reversal_number):
    """
    This function creates a csv file for the LD Train test. Each row will be the first day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    """

    # check that the inputs to the criteria widgets are valid
    if ld_train_criteria_min_rev_check(criteria, min_reversal_number) is not None:
        criteria_list, min_rev = ld_train_criteria_min_rev_check(criteria, min_reversal_number)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_first_day() error: One of the three criteria is empty or invalid!')
        print('button_ld_train_first_day() error: One of the three criteria is empty or invalid!')
        return None

    if ld_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ld_criteria_list_check(criteria_list)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_first_day() error: The n/n+1 days criteria is empty or invalid!')
        print('button_ld_train_first_day() error: The n/n+1 days criteria is empty or invalid!')
        return None

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        get_ld_train_normal(df, criteria_value, criteria_max_days, min_rev)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_first_day() error: One of the criterias is invalid or you hit the cancel button!')
        print('button_ld_train_first_day() error: One of the criterias is invalid or you hit the cancel button!')
        return None


def button_ld_train_last_day(criteria, min_reversal_number):
    """
    This function creates a csv file for the LD Train test. Each row will be the last day the animal ran the
    test. If the animal does not meet the criteria, then their last date will be the last day of the test. At the end,
    the function will ask the user to save the newly created csv file in a directory.

    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    """

    # check that the inputs to the criteria widgets are valid
    if ld_train_criteria_min_rev_check(criteria, min_reversal_number) is not None:
        criteria_list, min_rev = ld_train_criteria_min_rev_check(criteria, min_reversal_number)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_last_day() error: One of the three criteria is empty or invalid!')
        print('button_ld_train_last_day() error: One of the three criteria is empty or invalid!')
        return None

    if ld_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ld_criteria_list_check(criteria_list)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_last_day() error: The n/n+1 days criteria is empty or invalid!')
        print('button_ld_train_last_day() error: The n/n+1 days criteria is empty or invalid!')
        return None

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        df = get_ld_last_days(df, criteria_value, criteria_max_days, min_rev)
        save_file_message(df)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_last_day() error: One of the criterias is invalid or you hit the cancel button!')
        print('button_ld_train_last_day() error: One of the criterias is invalid or you hit the cancel button!')
        return None


def button_ld_train_select_id(enter_id, criteria, min_reversal_number):
    """
    This function creates a csv file for the LD Train test. Each row will be all the trials from start date to
    criteria date for a selected animal id. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param enter_id: A widget that contains the value that represents the selected id.
    :param criteria: A widget that contains a string that represents the duration of the criteria as n days/n+1 days
    :param min_reversal_number: An entry widget that contains a value that represents the the minimum required reversal
    number for an animal
    """

    # check that the inputs to the criteria widgets are valid
    try:
        selected_id = int(enter_id.get())
    except ValueError:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_id() error: The select id value is empty or invalid!')
        print('button_ld_train_select_id() error: The select id value is empty or invalid!')
        return None

    # check that the inputs to the criteria widgets are valid
    if ld_train_criteria_min_rev_check(criteria, min_reversal_number) is not None:
        criteria_list, min_rev = ld_train_criteria_min_rev_check(criteria, min_reversal_number)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_id() error: One of the three criteria is empty or invalid!')
        print('button_ld_train_select_id() error: One of the three criteria is empty or invalid!')
        return None

    if ld_criteria_list_check(criteria_list) is not None:
        criteria_value, criteria_max_days = ld_criteria_list_check(criteria_list)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_id() error: The n/n+1 days criteria is empty or invalid!')
        print('button_ld_train_select_id() error: The n/n+1 days criteria is empty or invalid!')
        return None

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        get_ld_train_normal(df, criteria_value, criteria_max_days, min_rev)
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)
    else:
        mb.showerror('LD Train Criteria Error',
                     'button_ld_train_select_id() error: One of the criterias is invalid or you hit the cancel button!')
        print('button_ld_train_select_id() error: One of the criterias is invalid or you hit the cancel button!')
        return None


def make_ld_train_buttons(tk, root):
    """
    This function creates all the location discrimination train buttons found on the LD Train sub-menu.

    :param tk: The TKinter library
    :param root: A specific frame where all the buttons will live on.
    """

    # creates all the ld train criteria widgets
    criteria_label = tk.Label(root,
                              text='Enter the criteria as n days/n+1 days:')
    criteria_label.grid(row=0, column=0)
    criteria_text = tk.Entry(root, width=30, justify='center')
    criteria_text.grid(row=0, column=1)

    min_reversal_num_label = tk.Label(root, text='Enter the min reversal number req:')
    min_reversal_num_label.grid(row=1, column=0)
    min_reversal_num_text = tk.Entry(root, width=30, justify='center')
    min_reversal_num_text.grid(row=1, column=1)

    # creates all the ld train buttons
    ld_train_button_all = tk.Button(root, text='LD Train (All)',
                                    command=lambda: button_ld_train_all(criteria_text, min_reversal_num_text),
                                    width=30)
    ld_train_button_all.grid(row=2, column=0)

    enter_day = tk.Entry(root, width=30, justify='center')
    enter_day.grid(row=3, column=1)

    ld_train_button_select_day = tk.Button(root, text='LD Train (Select Day)',
                                           command=lambda: button_ld_train_select_day(enter_day, criteria_text,
                                                                                      min_reversal_num_text),
                                           width=30)
    ld_train_button_select_day.grid(row=3, column=0)

    ld_train_button_first_day = tk.Button(root, text='LD Train (First Day)',
                                          command=lambda: button_ld_train_first_day(criteria_text,
                                                                                    min_reversal_num_text), width=30
                                          )
    ld_train_button_first_day.grid(row=4, column=0)

    ld_train_button_last_day = tk.Button(root, text='LD Train (Last Day)',
                                         command=lambda: button_ld_train_last_day(criteria_text, min_reversal_num_text),
                                         width=30)
    ld_train_button_last_day.grid(row=5, column=0)

    enter_id = tk.Entry(root, width=30, justify='center')
    enter_id.grid(row=6, column=1)

    ld_train_button_select_id = tk.Button(root, text='LD Train (Select Animal ID)',
                                          command=lambda: button_ld_train_select_id(enter_id, criteria_text,
                                                                                    min_reversal_num_text), width=30)
    ld_train_button_select_id.grid(row=6, column=0)
