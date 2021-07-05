import numpy as np
from setup import *


def get_ld_train_final_days(df):
    df_copy = df.copy(deep=True)
    df_copy = df_copy.loc[df_copy['NumberOfReversal'] >= 2]

    df_copy['Counter'] = df_copy.groupby('ID').cumcount() + 1
    df_copy['Difference in Date'] = df_copy['Day'].diff(1)

    df_copy.drop(df_copy.loc[df_copy['Counter'] == 1].index, inplace=True)
    df_copy.drop(df_copy.loc[df_copy['Difference in Date'] == np.nan].index, inplace=True)
    df_copy.drop(df_copy.loc[abs(df_copy['Difference in Date']) > 2].index, inplace=True)
    df_copy.drop_duplicates(subset='ID', keep='first', inplace=True)

    return df_copy


def get_ld_train_normal(df):
    df_copy = get_ld_train_final_days(df)
    for index in df_copy.iterrows():
        df.drop(df.loc[(df['ID'] == index[1]['ID']) & (df['Day'] > index[1]['Day'])].index, inplace=True)


def get_ld_train_criteria_day_all(df):
    get_ld_train_normal(df)
    df.drop_duplicates(subset='ID', keep='last', inplace=True)


def ld_train_delete_other_difficulties(df):
    # for ld train, we want only intermediate, delete all others
    df.drop(df.loc[df['Type'] == 'hard'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'easy'].index, inplace=True)
    df.drop(df.loc[df['Type'] == 'undetermined'].index, inplace=True)
    df.sort_values(['ID', 'Date'], ascending=[1, 1], inplace=True)
    df['Day'] = df.groupby('ID').cumcount() + 1


def button_ld_train_all():
    print('You have selected the LD Train(All) button!')
    df = data_setup()
    ld_train_delete_other_difficulties(df)
    get_ld_train_normal(df)
    save_file_message(df)


def button_ld_train_select_day(enter_day):
    print('You have selected the LD Train(Select Day) button!')
    df = data_setup()
    ld_train_delete_other_difficulties(df)
    get_ld_train_normal(df)
    selected_day = int(enter_day.get())
    df = df.loc[df['Day'] == selected_day]
    save_file_message(df)


def button_ld_train_first_day():
    print('You have selected the LD Train(First Day) button!')
    df = data_setup()
    ld_train_delete_other_difficulties(df)
    get_ld_train_normal(df)
    df = df.loc[df['Day'] == 1]
    save_file_message(df)


def button_ld_train_last_day():
    print('You have selected the LD Train(Last Day) button!')
    df = data_setup()
    ld_train_delete_other_difficulties(df)
    get_ld_train_criteria_day_all(df)
    save_file_message(df)


def button_ld_train_select_id(enter_id):
    print('You have selected the LD Train(Select ID) button!')
    df = data_setup()
    ld_train_delete_other_difficulties(df)
    get_ld_train_normal(df)
    selected_id = int(enter_id.get())
    df = df.loc[df['ID'] == selected_id]
    save_file_message(df)


def make_ld_train_buttons(tk, root):
    ld_train_button_all = tk.Button(root, text='LD Train (All)', command=button_ld_train_all, width=30)
    ld_train_button_all.grid(row=0, column=0)

    enter_day = tk.Entry(root, width=10)
    enter_day.grid(row=1, column=1)

    ld_train_button_select_day = tk.Button(root, text='LD Train (Select Day)',
                                           command=lambda: button_ld_train_select_day(enter_day), width=30)
    ld_train_button_select_day.grid(row=1, column=0)

    ld_train_button_first_day = tk.Button(root, text='LD Train (First Day)', command=button_ld_train_first_day,
                                          width=30)
    ld_train_button_first_day.grid(row=2, column=0)

    ld_train_button_last_day = tk.Button(root, text='LD Train (Last Day)', command=button_ld_train_last_day, width=30)
    ld_train_button_last_day.grid(row=3, column=0)

    enter_id = tk.Entry(root, width=10)
    enter_id.grid(row=4, column=1)

    ld_train_button_select_id = tk.Button(root, text='LD Train (Select Animal ID)',
                                          command=lambda: button_ld_train_select_id(enter_id), width=30)
    ld_train_button_select_id.grid(row=4, column=0)