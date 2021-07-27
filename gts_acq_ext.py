from setup import *


def get_general_ts_it():
    df = data_setup_gts('IT')
    if df is not None:
        save_file_message(df)


def get_general_ts_mi():
    df = data_setup_gts('MI')
    if df is not None:
        save_file_message(df)


def get_general_ts_mt():
    df = data_setup_gts('MT')
    if df is not None:
        save_file_message(df)


def get_punish_incorrect():
    df = data_setup_pi()
    if df is not None:
        save_file_message(df)


def make_general_ts_buttons(tk, root):
    general_ts_button = tk.Button(root, text='General TS (IT)', command=get_general_ts_it, width=30)
    general_ts_button.grid(row=0, column=0)
    general_ts_button = tk.Button(root, text='General TS (MI)', command=get_general_ts_mi, width=30)
    general_ts_button.grid(row=1, column=0)
    general_ts_button = tk.Button(root, text='General TS (MT)', command=get_general_ts_mt, width=30)
    general_ts_button.grid(row=2, column=0)
    punish_incorrect_button = tk.Button(root, text='General TS (PI)', command=get_punish_incorrect, width=30)
    punish_incorrect_button.grid(row=3, column=0)


def get_acq_final_days(df, criteria):
    df['Day'] = df.groupby('ID').cumcount() + 1
    df_copy = df.copy(deep=True)
    df_copy.sort_values(['ID', 'Day'], ascending=[1, 1], inplace=True)
    df_copy = df_copy.loc[(df_copy['Corrects'] == 30) & (df_copy['SessionLength'] <= 900)]
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


def get_acquisition_normal(df, criteria):
    df_copy = get_acq_final_days(df, criteria)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def button_acquisition_all(criteria):
    df = data_setup_acq()
    if df is not None:
        criteria_value = int(criteria.get())
        get_acquisition_normal(df, criteria_value)
        save_file_message(df)


def button_acquisition_first(criteria):
    df = data_setup_acq()
    if df is not None:
        criteria_value = int(criteria.get())
        get_acquisition_normal(df, criteria_value)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_acquisition_last(criteria):
    df = data_setup_acq()
    if df is not None:
        criteria_value = int(criteria.get())
        get_acquisition_normal(df, criteria_value)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_acquisition_select(select_day, criteria):
    if select_day.get() != '' and criteria.get() != '':
        selected = int(select_day.get())
        criteria_value = int(criteria.get())
    else:
        print('Either the criteria is empty or the selected day is empty!')
        return
    df = data_setup_acq()
    if df is not None:
        get_acquisition_normal(df, criteria_value)
        df = df.loc[df['Day'] == selected]
        save_file_message(df)


def get_ext_last_day(df, criteria, max_days):
    df['Day'] = df.groupby('ID').cumcount() + 1
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[(df_copy['Omissions'] >= 24)]

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

    df_copy.to_csv('third2.csv')

    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    return df_copy


def get_extinction_all(df, criteria, max_days):
    df_copy = get_ext_last_day(df, criteria, max_days)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def button_extinction_all(criteria):
    if criteria.get() == '':
        print('The criteria is empty! Please update it!')
        return

    df = data_setup_ext()

    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        save_file_message(df)


def button_extinction_first(criteria):
    if criteria.get() == '':
        print('The criteria is empty! Please update it!')
        return
    df = data_setup_ext()
    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_extinction_last_day(criteria):
    if criteria.get() == '':
        print('The criteria is empty! Please update it!')
        return
    df = data_setup_ext()
    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        df.sort_values(['ID', 'Date'], inplace=True)
        df.drop_duplicates(subset='ID', keep='last', inplace=True)
        save_file_message(df)


def button_extinction_select_day(selected_day, criteria):
    if criteria.get() == '':
        print('The criteria is empty! Please update it!')
        return
    df = data_setup_ext()
    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        select_day = int(selected_day.get())
        df = df.loc[df['Day'] == select_day]
        save_file_message(df)


def button_extinction_select_id(selected_id, criteria):
    if selected_id.get() != '' and criteria.get() != '':
        selected = int(selected_id.get())
        criteria_value = int(criteria.get())
    else:
        print('Either the criteria is empty or the selected day is empty!')
        return

    df = data_setup_ext()
    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        select_id = int(selected_id.get())
        df = df.loc[df['ID'] == select_id]
        save_file_message(df)


def make_extinction_buttons(tk, root):
    acq_criteria_label = tk.Label(root, text='Enter the criteria as n days in a row:')
    acq_criteria_label.grid(row=0, column=0)
    acq_criteria_text = tk.Entry(root, width=30, justify='center')
    acq_criteria_text.grid(row=0, column=1)

    acquisition_button = tk.Button(root, text='Acquisition (All)',
                                   command=lambda: button_acquisition_all(acq_criteria_text), width=30)
    acquisition_button.grid(row=1, column=0)
    acquisition_first_button = tk.Button(root, text='Acquisition (First Day)',
                                         command=lambda: button_acquisition_first(acq_criteria_text), width=30)
    acquisition_first_button.grid(row=2, column=0)
    acquisition_last_button = tk.Button(root, text='Acquisition (Last Day)',
                                        command=lambda: button_acquisition_last(acq_criteria_text), width=30)
    acquisition_last_button.grid(row=3, column=0)

    select_acq_day_text = tk.Entry(root, width=30, justify='center')
    select_acq_day_text.grid(row=4, column=1)

    acquisition_select_button = tk.Button(root, text='Acquisition (Select Day)',
                                          command=lambda: button_acquisition_select(select_acq_day_text,
                                                                                    acq_criteria_text), width=30)
    acquisition_select_button.grid(row=4, column=0)

    ###
    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=5, column=0)

    ext_criteria_label = tk.Label(root, text='Enter the criteria as n days/n+1 days:')
    ext_criteria_label.grid(row=6, column=0)
    ext_criteria_text = tk.Entry(root, width=30, justify='center')
    ext_criteria_text.grid(row=6, column=1)

    extinction_all_button = tk.Button(root, text='Extinction (All)',
                                      command=lambda: button_extinction_all(ext_criteria_text), width=30)
    extinction_all_button.grid(row=7, column=0)
    extinction_first_button = tk.Button(root, text='Extinction (First Day)',
                                        command=lambda: button_extinction_first(ext_criteria_text), width=30)
    extinction_first_button.grid(row=8, column=0)
    extinction_last_button = tk.Button(root, text='Extinction (Last Day)',
                                       command=lambda: button_extinction_last_day(ext_criteria_text), width=30)
    extinction_last_button.grid(row=9, column=0)
    extinction_select_text = tk.Entry(root, width=30, justify='center')
    extinction_select_text.grid(row=10, column=1)
    extinction_select_day_button = tk.Button(root, text='Extinction (Select Day)',
                                             command=lambda: button_extinction_select_day(extinction_select_text,
                                                                                          ext_criteria_text),
                                             width=30)
    extinction_select_day_button.grid(row=10, column=0)
    extinction_select_id_text = tk.Entry(root, width=30, justify='center')
    extinction_select_id_text.grid(row=11, column=1)
    extinction_select_id_button = tk.Button(root, text='Extinction (Select ID)',
                                            command=lambda: button_extinction_select_id(extinction_select_id_text,
                                                                                        ext_criteria_text),
                                            width=30)
    extinction_select_id_button.grid(row=11, column=0)
