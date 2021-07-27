import numpy as np
from setup import *


def get_ld_last_days(df, criteria, max_days):
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[df_copy['NumberOfReversal'] > 1]

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
        max_days_apart_ctn = difference_list.tolist().count(2)
        one_day_apart_ctn = difference_list.tolist().count(1)
        total_days = sum(difference_list)

        if total_days == criteria and max_days_apart_ctn == 1 and one_day_apart_ctn == max_days - 3:
            df_copy.at[last_row_info.name, 'Criteria Passed?'] = 'yes'

        row_index += 1

    df_copy.to_csv('why date missing2.csv')

    df_copy = df_copy.loc[df_copy['Criteria Passed?'] == 'yes']
    df_copy['Mice ID'] = df_copy['ID']
    df_copy = df_copy.groupby('Mice ID').first()

    df_copy.to_csv('why date missing.csv')

    return df_copy


def get_ld_train_normal(df, criteria, max_days):
    df_copy = get_ld_last_days(df, criteria, max_days)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def get_ld_train_criteria_day_all(df, criteria, max_days):
    get_ld_train_normal(df, criteria, max_days)
    df.drop_duplicates(subset='ID', keep='last', inplace=True)


def ld_train_delete_other_difficulties(df):
    # for ld train, we want only intermediate, delete all others
    df.drop(df.loc[df['Type'] == 'hard'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'easy'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'undetermined'].index, inplace=True)
    df.sort_values(['ID', 'Date'], ascending=[1, 1], inplace=True)
    df['Day'] = df.groupby('ID').cumcount() + 1


def button_ld_train_all(criteria):
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)

        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])

        get_ld_train_normal(df, criteria_value, criteria_max_days)
        save_file_message(df)


def button_ld_train_select_day(enter_day, criteria):
    print('You have selected the LD Train(Select Day) button!')
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)

        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])

        get_ld_train_normal(df, criteria_value, criteria_max_days)
        selected_day = int(enter_day.get())
        df = df.loc[df['Day'] == selected_day]
        save_file_message(df)


def button_ld_train_first_day(criteria):
    print('You have selected the LD Train(First Day) button!')
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])

        get_ld_train_normal(df, criteria_value, criteria_max_days)
        df = df.loc[df['Day'] == 1]
        save_file_message(df)


def button_ld_train_last_day(criteria):
    print('You have selected the LD Train(Last Day) button!')
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_ld_train_criteria_day_all(df, criteria_value, criteria_max_days)
        save_file_message(df)


def button_ld_train_select_id(enter_id, criteria):
    print('You have selected the LD Train(Select ID) button!')
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])

        get_ld_train_normal(df, criteria_value, criteria_max_days)
        selected_id = int(enter_id.get())
        df = df.loc[df['ID'] == selected_id]
        save_file_message(df)


def make_ld_train_buttons(tk, root):
    criteria_label = tk.Label(root,
                              text='Enter the criteria as n days/n+1 days:')
    criteria_label.grid(row=0, column=0)
    criteria_text = tk.Entry(root, width=30, justify='center')
    criteria_text.grid(row=0, column=1)

    ld_train_button_all = tk.Button(root, text='LD Train (All)', command=lambda: button_ld_train_all(criteria_text),
                                    width=30)
    ld_train_button_all.grid(row=1, column=0)

    enter_day = tk.Entry(root, width=30, justify='center')
    enter_day.grid(row=2, column=1)

    ld_train_button_select_day = tk.Button(root, text='LD Train (Select Day)',
                                           command=lambda: button_ld_train_select_day(enter_day, criteria_text),
                                           width=30)
    ld_train_button_select_day.grid(row=2, column=0)

    ld_train_button_first_day = tk.Button(root, text='LD Train (First Day)',
                                          command=lambda: button_ld_train_first_day(criteria_text), width=30
                                          )
    ld_train_button_first_day.grid(row=3, column=0)

    ld_train_button_last_day = tk.Button(root, text='LD Train (Last Day)',
                                         command=lambda: button_ld_train_last_day(criteria_text), width=30)
    ld_train_button_last_day.grid(row=4, column=0)

    enter_id = tk.Entry(root, width=30, justify='center')
    enter_id.grid(row=5, column=1)

    ld_train_button_select_id = tk.Button(root, text='LD Train (Select Animal ID)',
                                          command=lambda: button_ld_train_select_id(enter_id, criteria_text), width=30)
    ld_train_button_select_id.grid(row=5, column=0)
