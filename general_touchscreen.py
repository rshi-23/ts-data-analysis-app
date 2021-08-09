from setup import *


def get_general_ts_all(test_type):
    """
    A generic function used to get all the rows of a specific general touchscreen test. After the csv is generated, it
     will ask for the user to save the file in a directory. Used for Habituation 1 and 2, Initial Touch, Must Touch,
     and Must Initiate.

    :param test_type: A string that represents one of the general touchscreen test types.
    """

    df = data_setup(test_type)
    if df is not None:
        save_file_message(df)


def get_general_ts_first_day(test_type):
    """
    A generic function used to get all the first days of a specific general touchscreen test. After the csv is
    generated, it will ask for the user to save the file in a directory. Used for Habituation 1 and 2, Initial Touch,
    Must Touch, and Must Initiate.

    :param test_type: A string that represents one of the general touchscreen test types.
    """

    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def get_general_ts_last_day(test_type):
    """
    A generic function used to get all the last days of a specific general touchscreen test. After the csv is
    generated, it will ask for the user to save the file in a directory. Used for Habituation 1 and 2, Initial Touch,
    Must Touch, and Must Initiate.

    :param test_type: A string that represents one of the general touchscreen test types.
    """

    df = data_setup(test_type)
    if df is not None:
        df = df.drop_duplicates(subset='ID', keep='last')
        save_file_message(df)


def check_enter_day(enter_day):
    """
    This function checks to make sure that the selected day value is valid.

    :param enter_day: An Entry widget that contains the numerical value of the day
    :return: The numerical value of the day in the Entry widget
    :except ValueError: If the value is empty or the value is not numeric, this function will stop and return.
    """

    try:
        selected_day = int(enter_day.get())
        return selected_day
    except ValueError:
        print('check_enter_day() error: Either the value is empty or the value is not numeric!')
        return


def check_enter_id(enter_id):
    """
    This function checks to make sure that the selected id value is valid.

    :param enter_id: An Entry widget that contains the numerical value of the id
    :return: The numerical value of the id in the Entry widget
    :except ValueError: If the value is empty or the value is not numeric, this function will stop and return.
    """

    try:
        selected_id = int(enter_id.get())
        return selected_id
    except ValueError:
        print('check_enter_id() error: Either the value is empty or the value is not numeric!')
        return


def get_general_ts_select_day(test_type, enter_day):
    """
    A generic function used to get all rows on a selected days of a specific general touchscreen test. After the csv is
    generated, it will ask for the user to save the file in a directory. Used for Habituation 1 and 2, Initial Touch,
    Must Touch, and Must Initiate.

    :param test_type: A string that represents one of the general touchscreen test types.
    :param enter_day: An Entry widget that contains the selected day value
    """

    # check that the inputs to the criteria widgets are valid
    selected_day = check_enter_day(enter_day)
    if selected_day is None:
        print('get_general_ts_select_day() error: Either the day value is empty or the value is not numeric!')
        return

    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def get_general_ts_select_id(test_type, enter_id):
    """
    A generic function used to get all rows on a selected id of a specific general touchscreen test. After the csv is
    generated, it will ask for the user to save the file in a directory. Used for Habituation 1 and 2, Initial Touch,
    Must Touch, and Must Initiate.

    :param test_type: A string that represents one of the general touchscreen test types.
    :param enter_id: An Entry widget that contains the selected id value
    """

    # check that the inputs to the criteria widgets are valid
    selected_id = check_enter_id(enter_id)
    if selected_id is None:
        print('get_general_ts_select_id() error: Either the id value is empty or the value is not numeric!')
        return

    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == selected_id]
        save_file_message(df)


def punish_incorrect_last_days(df, min_trial_req, criteria_one, criteria_two):
    """
    This function determines the last day (aka the first time the animal has met the PI criteria) for all animals. The
    function grabs all rows that have at least the minimum trials completed requirement and checks if the animal on the
    first day has at least criteria_one percent correctness and on the second day has at least criteria_two percent
    correctness. If it passes the criteria, the function will mark the day that it passed the criteria. At the end, the
    function will grab all the first occurrences of when the animal passed the criteria and return it as a new
    dataframe.

    :param df: A dataframe that represents cleaned Punish Incorrect data
    :param min_trial_req: A value that represents the minimum required trials to pass the criteria (int)
    :param criteria_one: A value that represents the minimum percent correctness for the first day (int)
    :param criteria_two: A value that represents the minimum precent correctness for the second day (int)
    :return: A dataframe that only contains the rows that the animals met their criteria on. If an animal did not reach
    the criteria, it will not show up.
    """

    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[df_copy['NumberOfTrial'] >= min_trial_req]
    df_copy.sort_values(['ID', 'Day'], inplace=True)
    df_copy.reset_index(drop=True, inplace=True)

    row_index = 0

    while row_index < df_copy.shape[0] - 1:
        rows_to_check = list()
        # compare two rows at a time with the same ID
        for row in range(2):
            row_to_add = df_copy.loc[row_index + row]
            while row_to_add['ID'] != df_copy.at[row_index, 'ID'] and row_index < df_copy.shape[0] - 1:
                row_index += 1
            rows_to_check.append(row_to_add)

        last_row_info = rows_to_check[-1]
        if len(rows_to_check) < 2:
            continue
        if last_row_info['ID'] != rows_to_check[0]['ID']:
            continue

        # checks the correctness matches the requirement and that both days are only 1 day apart
        if rows_to_check[0]['PercentCorrect'] >= criteria_one and rows_to_check[1]['PercentCorrect'] >= criteria_two \
                and abs(rows_to_check[0]['Day'] - rows_to_check[1]['Day']) == 1:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    # only take the first occurrence of the rows that passed the criteria
    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_punish_incorrect_normal(df, min_trials, percent_one, percent_two):
    """
    This function drops rows for trials after the criteria met date. The resulting dataframe will contain rows with the
    animal's start date to the criteria end date. If an animal never reaches the criteria, then it will display all the
    trials from the start of testing to the end of testing (for punish incorrect).

    :param df: A dataframe that represents cleaned Punish Incorrect data
    :param min_trials: A value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: A value that represents the minimum percent correctness for the first day (int)
    :param percent_two: A value that represents the minimum precent correctness for the second day (int)
    """

    df_copy = punish_incorrect_last_days(df, min_trials, percent_one, percent_two)
    # drop rows that have larger day values and same ids (those are probably extra days to retain mouse memory)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def get_punish_incorrect_criteria_days(df, min_trials, percent_one, percent_two):
    """
    This function will call the get_punish_incorrect_normal() and then get all the last days. For animals that passed
    the criteria, their last day is the day they met the criteria. For animals that did not pass the criteria, their
    last day is the last day the test was ran.

    :param df: A dataframe that represents cleaned Punish Incorrect data
    :param min_trials: A value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: A value that represents the minimum percent correctness for the first day (int)
    :param percent_two: A value that represents the minimum percent correctness for the second day (int)
    """

    get_punish_incorrect_normal(df, min_trials, percent_one, percent_two)
    df.drop_duplicates(subset='ID', keep='last', inplace=True)


def pi_widget_check(min_trials, percent_one, percent_two):
    """
    This function checks all the criteria widgets to make sure that they are filled in and have valid numeric values.
    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    :return: Returns the value for the minimum required trials, the minimum required percent correctness for the first
    day, and the minimum required percent correctness for the second day.
    :except ValueError: If any of the criteria entries are empty or invalid, the function will print an error message
    and stop.
    """
    try:
        minimum_trials = int(min_trials.get())
    except ValueError:
        print('pi_widget_check() error: Either the trial value is empty of the value is not numeric!')
        return

    try:
        correct_one = int(percent_one.get())
    except ValueError:
        print('pi_widget_check() error: Either the percent correctness 1 is empty of the value is not numeric!')
        return

    try:
        correct_two = int(percent_two.get())
    except ValueError:
        print('pi_widget_check() error: Either the percent correctness 2 is empty of the value is not numeric!')
        return

    return minimum_trials, correct_one, correct_two


def pi_all_button(min_trials, percent_one, percent_two):
    """
    This function creates a csv file for the Punish Incorrect test. Each animal will have rows that start from their
    start date to their criteria met date. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    """

    # check that the inputs to the criteria widgets are valid
    if pi_widget_check(min_trials, percent_one, percent_two) is not None:
        minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    else:
        print('pi_all_button() error: One of the three criteria is either empty or non-numeric!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        save_file_message(df)


def pi_first_button(min_trials, percent_one, percent_two):
    """
    This function creates a csv file for the Punish Incorrect test. Each row will be the first day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    """

    # check that the inputs to the criteria widgets are valid
    if pi_widget_check(min_trials, percent_one, percent_two) is not None:
        minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    else:
        print('pi_first_button() error: One of the three criteria is either empty or non-numeric!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def pi_last_button(min_trials, percent_one, percent_two):
    """
    This function creates a csv file for the Punish Incorrect test. Each row will be the last day the animal ran the
    test. If the animal does not meet the criteria, then their last date will be the last day of the test. At the end,
    the function will ask the user to save the newly created csv file in a directory.

    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    """

    # check that the inputs to the criteria widgets are valid
    if pi_widget_check(min_trials, percent_one, percent_two) is not None:
        minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    else:
        print('pi_last_button() error: One of the three criteria is either empty or non-numeric!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_criteria_days(df, minimum_trials, correct_one, correct_two)
        save_file_message(df)


def pi_select_day_button(min_trials, percent_one, percent_two, enter_day):
    """
    This function creates a csv file for the Punish Incorrect test. Each row will be the selected day the animal ran the
    test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    """

    # check that the inputs to the criteria widgets are valid
    if pi_widget_check(min_trials, percent_one, percent_two) is not None:
        minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    else:
        print('pi_select_day_button() error: One of the three criteria is either empty or non-numeric!')
        return

    # check that the inputs to the criteria widgets are valid
    selected_day = check_enter_day(enter_day)
    if selected_day is None:
        print('pi_select_day_button() error: Either the day value is empty or the value is not numeric!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def pi_select_id_button(min_trials, percent_one, percent_two, enter_id):
    """
    This function creates a csv file for the Punish Incorrect test. Each row will be all the trials from start date to
    criteria date for a selected animal id. If the animal does not meet the criteria, then their last date will be the
    last day of the test. At the end, the function will ask the user to save the newly created csv file in a directory.

    :param min_trials: An entry with the value that represents the minimum required trials to pass the criteria (int)
    :param percent_one: An entry with the value that represents the minimum percent correctness for the first day (int)
    :param percent_two: An entry with the value that represents the minimum percent correctness for the second day (int)
    """

    # check that the inputs to the criteria widgets are valid
    if pi_widget_check(min_trials, percent_one, percent_two) is not None:
        minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    else:
        print('pi_select_id_button() error: One of the three criteria is either empty or non-numeric!')
        return

    # check that the inputs to the criteria widgets are valid
    selected_id = check_enter_id(enter_id)
    if selected_id is None:
        print('pi_select_id_button() error: Either the id value is empty or the value is not numeric!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == selected_id]
        save_file_message(df)


def make_general_ts_buttons(tk, root):
    """
    This function creates all the general touchscreen buttons found on the General Touchscreen sub-menu.

    :param tk: The TKinter library
    :param root: A specific frame where all the buttons will live on.
    """

    # creates hab 1 and hab 2 buttons
    hab_one_btn = tk.Button(root, text='Habituation 1', command=lambda: get_general_ts_all('Hab1'), width=30)
    hab_one_btn.grid(row=0, column=0)
    hab_two_btn = tk.Button(root, text='Habituation 2', command=lambda: get_general_ts_all('Hab2'), width=30)
    hab_two_btn.grid(row=1, column=0)

    # visual spacer between hab and it
    spacer_btn = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn.grid(row=2, columnspan=2)

    # creates all it buttons
    it_btn = tk.Button(root, text='Initial Touch (All)', command=lambda: get_general_ts_all('IT'), width=30)
    it_btn.grid(row=3, column=0)
    it_first_btn = tk.Button(root, text='Initial Touch (First Day)', command=lambda: get_general_ts_first_day('IT'),
                             width=30)
    it_first_btn.grid(row=4, column=0)
    it_last_btn = tk.Button(root, text='Initial Touch (Last Day)', command=lambda: get_general_ts_last_day('IT'),
                            width=30)
    it_last_btn.grid(row=5, column=0)
    it_sel_day_text = tk.Entry(root, width=30, justify='center')
    it_sel_day_text.grid(row=6, column=1)
    it_sel_day_btn = tk.Button(root, text='Initial Touch (Select Day)',
                               command=lambda: get_general_ts_select_day('IT', it_sel_day_text), width=30)
    it_sel_day_btn.grid(row=6, column=0)
    it_sel_id_text = tk.Entry(root, width=30, justify='center')
    it_sel_id_text.grid(row=7, column=1)
    it_sel_id_btn = tk.Button(root, text='Initial Touch (Select ID)',
                              command=lambda: get_general_ts_select_id('IT', it_sel_id_text), width=30)
    it_sel_id_btn.grid(row=7, column=0)

    # visual spacer between it and mi
    spacer_btn_two = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_two.grid(row=8, columnspan=2)

    # creates all the mi buttons
    mi_btn = tk.Button(root, text='Must Initiate (All)', command=lambda: get_general_ts_all('MI'), width=30)
    mi_btn.grid(row=9, column=0)
    mi_first_btn = tk.Button(root, text='Must Initiate (First Day)', command=lambda: get_general_ts_first_day('MI'),
                             width=30)
    mi_first_btn.grid(row=10, column=0)
    mi_last_btn = tk.Button(root, text='Must Initiate (Last Day)', command=lambda: get_general_ts_last_day('MI'),
                            width=30)
    mi_last_btn.grid(row=11, column=0)
    mi_sel_day_text = tk.Entry(root, width=30, justify='center')
    mi_sel_day_text.grid(row=12, column=1)
    mi_sel_day_btn = tk.Button(root, text='Must Initiate(Select Day)',
                               command=lambda: get_general_ts_select_day('MI', it_sel_day_text), width=30)
    mi_sel_day_btn.grid(row=12, column=0)
    mi_sel_id_text = tk.Entry(root, width=30, justify='center')
    mi_sel_id_text.grid(row=13, column=1)
    mi_sel_id_btn = tk.Button(root, text='Must Initiate (Select ID)',
                              command=lambda: get_general_ts_select_id('MI', it_sel_id_text), width=30)
    mi_sel_id_btn.grid(row=13, column=0)

    # visual spacer between mi and mt
    spacer_btn_three = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_three.grid(row=14, columnspan=2)

    # creates all the mt buttons
    mt_btn = tk.Button(root, text='Must Touch (All)', command=lambda: get_general_ts_all('MT'), width=30)
    mt_btn.grid(row=15, column=0)
    mt_first_btn = tk.Button(root, text='Must Touch (First Day)', command=lambda: get_general_ts_first_day('MT'),
                             width=30)
    mt_first_btn.grid(row=16, column=0)
    mt_last_btn = tk.Button(root, text='Must Touch (Last Day)', command=lambda: get_general_ts_last_day('MT'),
                            width=30)
    mt_last_btn.grid(row=17, column=0)
    mt_sel_day_text = tk.Entry(root, width=30, justify='center')
    mt_sel_day_text.grid(row=18, column=1)
    mt_sel_day_btn = tk.Button(root, text='Must Touch (Select Day)',
                               command=lambda: get_general_ts_select_day('MT', it_sel_day_text), width=30)
    mt_sel_day_btn.grid(row=18, column=0)
    mt_sel_id_text = tk.Entry(root, width=30, justify='center')
    mt_sel_id_text.grid(row=19, column=1)
    mt_sel_id_btn = tk.Button(root, text='Must Touch (Select ID)',
                              command=lambda: get_general_ts_select_id('MT', it_sel_id_text), width=30)
    mt_sel_id_btn.grid(row=19, column=0)

    # visual spacer between mt and pi
    spacer_btn_four = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_four.grid(row=20, columnspan=2)

    # creates all the pi criteria widgets
    pi_min_trial_label = tk.Label(root, text='Enter the min req trial amount:')
    pi_min_trial_label.grid(row=21, column=0)
    pi_min_trial_text = tk.Entry(root, width=30, justify='center')
    pi_min_trial_text.grid(row=21, column=1)
    pi_correct_one_label = tk.Label(root, text='Enter the min % correct for first day:')
    pi_correct_one_label.grid(row=22, column=0)
    pi_correct_one_text = tk.Entry(root, width=30, justify='center')
    pi_correct_one_text.grid(row=22, column=1)
    pi_correct_two_label = tk.Label(root, text='Enter the min % correct for second day:')
    pi_correct_two_label.grid(row=23, column=0)
    pi_correct_two_text = tk.Entry(root, width=30, justify='center')
    pi_correct_two_text.grid(row=23, column=1)

    # creates all the pi buttons
    pi_btn = tk.Button(root, text='Punish Incorrect (All)',
                       command=lambda: pi_all_button(pi_min_trial_text, pi_correct_one_text, pi_correct_two_text),
                       width=30)
    pi_btn.grid(row=24, column=0)
    pi_first_btn = tk.Button(root, text='Punish Incorrect (First Day)',
                             command=lambda: pi_first_button(pi_min_trial_text, pi_correct_one_text,
                                                             pi_correct_two_text),
                             width=30)
    pi_first_btn.grid(row=25, column=0)
    pi_last_btn = tk.Button(root, text='Punish Incorrect (Last Day)',
                            command=lambda: pi_last_button(pi_min_trial_text, pi_correct_one_text, pi_correct_two_text),
                            width=30)
    pi_last_btn.grid(row=26, column=0)
    pi_sel_day_text = tk.Entry(root, width=30, justify='center')
    pi_sel_day_text.grid(row=27, column=1)
    pi_sel_day_btn = tk.Button(root, text='Punish Incorrect (Select Day)',
                               command=lambda: pi_select_day_button(pi_min_trial_text, pi_correct_one_text,
                                                                    pi_correct_two_text, pi_sel_day_text), width=30)
    pi_sel_day_btn.grid(row=27, column=0)
    pi_sel_id_text = tk.Entry(root, width=30, justify='center')
    pi_sel_id_text.grid(row=28, column=1)
    pi_sel_id_btn = tk.Button(root, text='Punish Incorrect (Select ID)',
                              command=lambda: pi_select_id_button(pi_min_trial_text, pi_correct_one_text,
                                                                  pi_correct_two_text, pi_sel_id_text), width=30)
    pi_sel_id_btn.grid(row=28, column=0)
