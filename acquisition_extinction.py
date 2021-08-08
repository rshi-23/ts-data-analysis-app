from setup import *


def get_acq_final_days(df, criteria, correct_amount, session_length):
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
        if day_counter == sorted(range(day_counter[0], day_counter[-1] + 1)):
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_acquisition_normal(df, criteria, correct_amount, session_length):
    df_copy = get_acq_final_days(df, criteria, correct_amount, session_length)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def acq_widget_check(criteria, correct_amount, session_length):
    if len(criteria.get()) != 0 and criteria.get().isnumeric():
        criteria_value = int(criteria.get())
    else:
        print('Please enter a numeric criteria of n days in row!')
        return
    if len(correct_amount.get()) != 0 and correct_amount.get().isnumeric():
        correct_trials_num = int(correct_amount.get())
    else:
        print('Please enter a numeric minimum correct trials amount!')
        return

    if len(session_length.get()) != 0 and session_length.get().isnumeric():
        session_time_sec = int(session_length.get())
    else:
        print('Please enter a numeric minimum session length in seconds!')
        return

    return criteria_value, correct_trials_num, session_time_sec


def button_acquisition_all(criteria, correct_amount, session_length):
    criteria_value, correct_trials_num, session_time_sec = acq_widget_check(criteria, correct_amount, session_length)

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        save_file_message(df)


def button_acquisition_first(criteria, correct_amount, session_length):
    criteria_value, correct_trials_num, session_time_sec = acq_widget_check(criteria, correct_amount, session_length)
    df = data_setup('Acq')

    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_acquisition_last(criteria, correct_amount, session_length):
    criteria_value, correct_trials_num, session_time_sec = acq_widget_check(criteria, correct_amount, session_length)
    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_acquisition_select_day(select_day, criteria, correct_amount, session_length):
    if select_day.get() != '' and criteria.get() != '':
        selected_day = int(select_day.get())
    else:
        print('The selected day is empty!')
        return
    criteria_value, correct_trials_num, session_time_sec = acq_widget_check(criteria, correct_amount, session_length)

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def button_acquisition_select_id(select_id, criteria, correct_amount, session_length):
    if select_id.get() != '' and criteria.get() != '':
        selected_id = int(select_id.get())
    else:
        print('Either the criteria is empty or the selected day is empty!')
        return
    criteria_value, correct_trials_num, session_time_sec = acq_widget_check(criteria, correct_amount, session_length)

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)


def get_ext_last_day(df, criteria, max_days, omission_amount):
    df['Day'] = df.groupby('ID').cumcount() + 1
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[(df_copy['Omissions'] >= omission_amount)]

    df_copy.sort_values(['ID', 'Day'], inplace=True)

    df_copy.reset_index(drop=True, inplace=True)

    row_index = 0
    while row_index < df_copy.shape[0] - (criteria - 1):
        rows_to_sum = list()
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
        if day_counter == sorted(range(day_counter[0], day_counter[-1] + 1)):
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        difference_list = np.diff(day_counter)
        max_days_apart_ctn = difference_list.tolist().count(1)
        one_day_apart_ctn = difference_list.tolist().count(2)
        total_days = sum(difference_list)

        if total_days == criteria and one_day_apart_ctn == max_days - 3 and max_days_apart_ctn == 1:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_extinction_all(df, criteria, max_days, omission_amount):
    df_copy = get_ext_last_day(df, criteria, max_days, omission_amount)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def ext_widget_check(criteria, omission_amount):
    if len(criteria.get()) != 0:
        criteria_list = criteria.get().split('/')
    else:
        print('Please enter the criteria as n/n+1 days')
        return

    if len(omission_amount.get()) != 0 and omission_amount.get().isnumeric():
        min_omission = int(omission_amount.get())
    else:
        print('Please enter a numeric minimum omission amount')
        return

    return criteria_list, min_omission


def ext_criteria_list_check(criteria_list):
    try:
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        return criteria_value, criteria_max_days
    except ValueError:
        print('Enter numeric values for the criteria n/n+1 days')
        return


def button_extinction_all(criteria, omission_amount):
    criteria_list, min_omission = ext_widget_check(criteria, omission_amount)

    df = data_setup('Ext')
    if df is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        save_file_message(df)


def button_extinction_first(criteria, omission_amount):
    criteria_list, min_omission = ext_widget_check(criteria, omission_amount)

    df = data_setup('Ext')
    if df is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_extinction_last_day(criteria, omission_amount):
    criteria_list, min_omission = ext_widget_check(criteria, omission_amount)

    df = data_setup('Ext')
    if df is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df.sort_values(['ID', 'Date'], inplace=True)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_extinction_select_day(selected_day, criteria, omission_amount):
    if len(selected_day.get()) and selected_day.get().isnumeric():
        select_day = int(selected_day.get())
    else:
        print('Enter a numeric day for Extinction (Select Day)!')
        return

    criteria_list, min_omission = ext_widget_check(criteria, omission_amount)
    df = data_setup('Ext')
    if df is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['Day'] == select_day]
        save_file_message(df)


def button_extinction_select_id(selected_id, criteria, omission_amount):
    if len(selected_id.get()) and selected_id.get().isnumeric():
        select_id = int(selected_id.get())
    else:
        print('Enter a numeric day for Extinction (Select Day)!')
        return

    criteria_list, min_omission = ext_widget_check(criteria, omission_amount)

    df = data_setup('Ext')
    if df is not None:
        criteria_value, criteria_max_days = ext_criteria_list_check(criteria_list)
        get_extinction_all(df, criteria_value, criteria_max_days, min_omission)
        df = df.loc[df['ID'] == select_id]
        save_file_message(df)


def make_extinction_buttons(tk, root):
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

    ###
    spacer_btn_one = tk.Label(root, text='', width=57, bg='#D6D6D6')
    spacer_btn_one.grid(row=8, columnspan=2)

    ext_criteria_label = tk.Label(root, text='Enter the criteria as n days/n+1 days:')
    ext_criteria_label.grid(row=9, column=0)
    ext_criteria_text = tk.Entry(root, width=30, justify='center')
    ext_criteria_text.grid(row=9, column=1)

    ext_min_omissions_label = tk.Label(root, text='Enter the min omission amount:')
    ext_min_omissions_label.grid(row=10, column=0)
    ext_min_omissions_text = tk.Entry(root, width=30, justify='center')
    ext_min_omissions_text.grid(row=10, column=1)

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
