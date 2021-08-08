from setup import *


def get_general_ts_all(test_type):
    df = data_setup(test_type)
    if df is not None:
        save_file_message(df)


def get_general_ts_first_day(test_type):
    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def get_general_ts_last_day(test_type):
    df = data_setup(test_type)
    if df is not None:
        df = df.drop_duplicates(subset='ID', keep='last')
        save_file_message(df)


def get_general_ts_select_day(test_type, enter_day):
    if len(enter_day.get()) != 0 and enter_day.get().isnumeric:
        selected_day = int(enter_day.get())
    else:
        print('Enter a numeric trial day!')
        return
    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def get_general_ts_select_id(test_type, enter_id):
    if len(enter_id.get()) != 0 and enter_id.get().isnumeric:
        selected_id = int(enter_id.get())
    else:
        print('Enter a numeric trial day!')
        return
    df = data_setup(test_type)
    if df is not None:
        df = df.loc[df['Day'] == selected_id]
        save_file_message(df)


def punish_incorrect_last_days(df, min_trial_req, criteria_one, criteria_two):
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[df_copy['NumberOfTrial'] >= min_trial_req]
    df_copy.sort_values(['ID', 'Day'], inplace=True)
    df_copy.reset_index(drop=True, inplace=True)

    row_index = 0
    while row_index < df_copy.shape[0] - 1:
        rows_to_check = list()
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

        if rows_to_check[0]['PercentCorrect'] >= criteria_one and rows_to_check[1]['PercentCorrect'] >= criteria_two \
                and abs(rows_to_check[0]['Day'] - rows_to_check[1]['Day']) == 1:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_punish_incorrect_normal(df, min_trials, percent_one, percent_two):
    df_copy = punish_incorrect_last_days(df, min_trials, percent_one, percent_two)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def get_punish_incorrect_criteria_days(df, min_trials, percent_one, percent_two):
    get_punish_incorrect_normal(df, min_trials, percent_one, percent_two)
    df.drop_duplicates(subset='ID', keep='last', inplace=True)


def pi_widget_check(min_trials, percent_one, percent_two):
    if len(min_trials.get()) != 0 and min_trials.get().isnumeric():
        minimum_trials = int(min_trials.get())
    else:
        print('Enter a numeric minimum req trials')
        return
    if len(percent_one.get()) != 0 and percent_one.get().isnumeric():
        correct_one = int(percent_one.get())
    else:
        print('Enter a numeric minimum first percent correct')
        return
    if len(percent_two.get()) != 0 and percent_two.get().isnumeric():
        correct_two = int(percent_two.get())
    else:
        print('Enter a numeric minimum second percent correct')
        return

    return minimum_trials, correct_one, correct_two


def pi_all_button(min_trials, percent_one, percent_two):
    minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        save_file_message(df)


def pi_first_button(min_trials, percent_one, percent_two):
    minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def pi_last_button(min_trials, percent_one, percent_two):
    minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_criteria_days(df, minimum_trials, correct_one, correct_two)
        save_file_message(df)


def pi_select_day_button(min_trials, percent_one, percent_two, enter_day):
    minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)

    if len(enter_day.get()) != 0 and enter_day.get().isnumeric():
        selected_day = int(enter_day.get())
    else:
        print('Enter a numeric trial day!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def pi_select_id_button(min_trials, percent_one, percent_two, enter_id):
    minimum_trials, correct_one, correct_two = pi_widget_check(min_trials, percent_one, percent_two)
    if len(enter_id.get()) != 0 and enter_id.get().isnumeric():
        selected_id = int(enter_id.get())
    else:
        print('Enter a numeric trial day!')
        return

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        df = df.loc[df['Day'] == selected_id]
        save_file_message(df)


def make_general_ts_buttons(tk, root):
    hab_one_btn = tk.Button(root, text='Habituation 1', command=lambda: get_general_ts_all('Hab1'), width=30)
    hab_one_btn.grid(row=0, column=0)
    hab_two_btn = tk.Button(root, text='Habituation 2', command=lambda: get_general_ts_all('Hab2'), width=30)
    hab_two_btn.grid(row=1, column=0)

    spacer_btn = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn.grid(row=2, columnspan=2)

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

    spacer_btn_two = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_two.grid(row=8, columnspan=2)

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

    spacer_btn_three = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_three.grid(row=14, columnspan=2)

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

    spacer_btn_four = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_four.grid(row=20, columnspan=2)

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
