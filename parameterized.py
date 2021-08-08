import functools

from general_touchscreen import *
from ld_train import *
from ld_probe import *
from acquisition_extinction import *

hab_one_parameters = ['RewardIRBeamBrokenCount', 'ScreenIRBeamBrokenCount', 'CrossedRewardToScreen',
                      'CrossedScreenToReward', 'BottomWindowTouches', 'TopWindowTouches', 'TrayEnteredCount']

hab_two_parameters = ['NumberOfTrial', 'RewardIRBeamBrokenCount', 'ScreenIRBeamBrokenCount', 'BottomLeftWindowTouches',
                      'BottomRightWindowTouches', 'TopWindowTouches', 'TrayEnteredCount', 'MeanRewardCollectionLatency']

it_parameters = ['ImagesTouched', 'Corrects', 'BlankTouches', 'TotalITITouches', 'MeanCorrectTouchLatency',
                 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency']

mt_parameters = ['Corrects', 'TotalBlankTouches', 'TotalITITouches', 'MeanCorrectTouchLatency', 'MeanBlankTouchLatency',
                 'MeanRewardCollectionLatency']

pi_parameters = ['NumberOfTrial', 'PercentCorrect', 'TotalITITouches', 'MeanCorrectTouchLatency',
                 'MeanCorrectRightTouchLatency', 'MeanCorrectLeftTouchLatency', 'MeanCorrectLeftRightTouchLatency',
                 'MeanBlankTouchLatency', 'MeanRewardCollectionLatency']

ld_parameters = ['NumberOfTrial', 'PercentCorrect', 'NumberOfReversal', 'TotalITITouches', 'TotalBlankTouches',
                 'MeanRewardCollectionLatency', 'MeanCorrectTouchLatency', 'MeanIncorrectTouchLatency',
                 'SessionLengthTo1stReversalDuration', 'SessionLengthTo2ndReversalDuration',
                 'NumberOfTrialTo1stReversal', 'NumberOfTrialTo2ndReversal', 'PercentCorrectTo1stReversal',
                 'PercentCorrectTo2ndReversal']

acq_parameters = ['Corrects', 'BlankTouches', 'TotalITITouches', 'MeanCorrectTouchLatency', 'MeanBlankTouchLatency',
                  'MeanRewardTouchLatency']

ext_parameters = ['Responses', 'Omissions', 'TotalITITouches', 'MeanResponseTouchLatency', 'MeanBlankTouchLatency',
                  'MeanTrayEntryLatency']

script_location = os.path.dirname(os.path.abspath(__file__))


def block_parsing_ld_probe(df, test_type, total_blocks, parameters_list, writer):
    for para in parameters_list:
        all_blocks = list()
        for block_number in range(1, int(total_blocks) + 1):
            block_data = df.loc[(df['Block'] == block_number) & (df['Type'] == test_type)]
            block_data = block_data[['ID', 'Date', para, 'Type', 'Block']]
            all_blocks.append(block_data)
        merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='ID', how='outer'), all_blocks)
        merged_df.to_excel(writer, sheet_name=test_type + ' ' + para[0:25], index=False, freeze_panes=(1, 1))
    writer.save()


def ld_probe_parameterized(df):
    try:
        writer_easy = pd.ExcelWriter('All Blocks Parameters Easy.xlsx', engine='xlsxwriter')
        print('A file called All Blocks Parameters Easy.xlsx has been created at:', script_location)
        writer_hard = pd.ExcelWriter('All Blocks Parameters Hard.xlsx', engine='xlsxwriter')
        print('A file called All Blocks Parameters Hard.xlsx has been created at:', script_location)
    except PermissionError:
        print(
            'Either All Blocks Parameters Easy or All Blocks Parameters Hard is opened! Please close them!')
        return

    max_blocks = df['Block'].max()

    block_parsing_ld_probe(df, 'easy', max_blocks, ld_parameters, writer_easy)
    block_parsing_ld_probe(df, 'hard', max_blocks, ld_parameters, writer_hard)


def day_parsing_ld_train(df, test_type, max_days, parameters_list, writer):
    for para in parameters_list:
        all_days = list()
        for day in range(1, int(max_days) + 1):
            day_data = df.loc[(df['Day'] == day) & (df['Type'] == test_type)]
            day_data = day_data[['ID', 'Date', 'Day', para, 'Type']]
            all_days.append(day_data)
        merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='ID', how='outer'), all_days)
        merged_df.to_excel(writer, sheet_name='int ' + para[0:25], index=False, freeze_panes=(1, 1))
    writer.save()


def ld_train_parameterized(df):
    try:
        writer_intermediate = pd.ExcelWriter('LD Train All Days Parameters.xlsx', engine='xlsxwriter')
        print('A file called LD Train All Days Parameters.xlsx has been created at:', script_location)
    except PermissionError:
        print(
            'LD Train All Days Parameters.xlsx is opened! Please close them!')
        return

    max_days = df['Day'].max()
    day_parsing_ld_train(df, 'intermediate', max_days, ld_parameters, writer_intermediate)


def general_by_day_parsing(df, max_days, parameters_list, writer, test_name):
    for para in parameters_list:
        all_days = list()
        for day in range(1, int(max_days) + 1):
            day_data = df.loc[(df['Day'] == day)]
            day_data = day_data[['ID', 'Date', 'Day', para]]
            all_days.append(day_data)
        merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='ID', how='outer'), all_days)
        merged_df.to_excel(writer, sheet_name=test_name + para[0:25], index=False, freeze_panes=(1, 1))
    writer.save()


def general_parameterized(df, name, parameter_list, test_name):
    try:
        some_writer = pd.ExcelWriter(name + ' All Days Parameters.xlsx', engine='xlsxwriter')
    except PermissionError:
        print(name, 'All Days Parameters.xlsx', 'is opened! Please close them!')
        return
    max_days = df['Day'].max()
    general_by_day_parsing(df, max_days, parameter_list, some_writer, test_name)


def general_para_button(data_setup_name, file_name, parameter_list):
    df = data_setup(data_setup_name)
    if df is not None:
        general_parameterized(df, file_name, parameter_list, data_setup_name)
        print('A file called', file_name, 'All Days Parameters.xlsx has been created at:', script_location)


def criteria_widget_check(criteria):
    if len(criteria.get()) != 0 and criteria.get().isnumeric():
        criteria_value = int(criteria.get())
    else:
        print('Please enter a numeric criteria n days in a row!')
        return

    return criteria_value


def pi_para_button(min_trials, percent_one, percent_two):
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

    df = data_setup('PI')
    if df is not None:
        get_punish_incorrect_normal(df, minimum_trials, correct_one, correct_two)
        general_parameterized(df, 'Punish Incorrect', pi_parameters, 'PI')


def acq_para_button(criteria, correct_amount, session_length):
    criteria_value = criteria_widget_check(criteria)

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

    df = data_setup('Acq')
    if df is not None:
        get_acquisition_normal(df, criteria_value, correct_trials_num, session_time_sec)
        general_parameterized(df, 'Acquisition', acq_parameters, 'Acq')


def ext_para_button(criteria, omissions_amount):
    if len(criteria.get()) != 0:
        criteria_list = criteria.get().split('/')
    else:
        print('Please enter the criteria in the form of n/n+1 days')
        return

    if len(omissions_amount.get()) != 0 and omissions_amount.get().isnumeric():
        omissions_count = int(omissions_amount.get())
    else:
        print('Please enter a numeric minimum omissions amount!')
        return

    df = data_setup('Ext')
    if df is not None:
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days, omissions_count)
        general_parameterized(df, 'Extinction', ext_parameters, 'Ext')


def ld_train_para_button(criteria, min_reversal_number):
    if len(criteria.get()) != 0:
        criteria_list = criteria.get().split('/')
    else:
        print('Please enter the criteria in the form of n/n+1 days')
        return

    if len(min_reversal_number.get()) != 0 and min_reversal_number.get().isnumeric():
        min_rev = int(min_reversal_number.get())
    else:
        print('Please enter a numeric minimum reversal number!')
        return

    df = data_setup('LD Train')
    if df is not None:
        ld_train_delete_other_difficulties(df)
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_ld_train_normal(df, criteria_value, criteria_max_days, min_rev)
        ld_train_parameterized(df)


def ld_probe_para_button():
    df = data_setup('LD Probe')
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        get_last_day_difficulty(df)
        ld_probe_parameterized(df)


def make_parameterized_button(tk, root):
    hab_one_para_btn = tk.Button(root, text='Habituation 1 Parameterized',
                                 command=lambda: general_para_button('Hab1', 'Habituation 1', hab_one_parameters),
                                 width=30)
    hab_one_para_btn.grid(row=0, column=0)
    hab_two_para_btn = tk.Button(root, text='Habituation 2 Parameterized',
                                 command=lambda: general_para_button('Hab2', 'Habituation 2', hab_two_parameters),
                                 width=30)
    hab_two_para_btn.grid(row=1, column=0)
    it_para_btn = tk.Button(root, text='Initial Touch Parameterized',
                            command=lambda: general_para_button('IT', 'Initial Touch', it_parameters),
                            width=30)
    it_para_btn.grid(row=2, column=0)
    mt_para_btn = tk.Button(root, text='Must Touch Parameterized',
                            command=lambda: general_para_button('MT', 'Must Touch', mt_parameters),
                            width=30)
    mt_para_btn.grid(row=3, column=0)
    mi_para_btn = tk.Button(root, text='Must Initiate Parameterized',
                            command=lambda: general_para_button('MI', 'Must Initiate', mt_parameters),
                            width=30)
    mi_para_btn.grid(row=4, column=0)

    spacer_btw_ts_pi = tk.Label(root, text='', bg='#D6D6D6', width=57)
    spacer_btw_ts_pi.grid(row=5, columnspan=2)

    pi_para_min_trials_labels = tk.Label(root, text='Enter the min req trial amount:')
    pi_para_min_trials_labels.grid(row=6, column=0)
    pi_para_min_trials_text = tk.Entry(root, width=30, justify='center')
    pi_para_min_trials_text.grid(row=6, column=1)

    pi_para_correct_one_label = tk.Label(root, text='Enter the min % correct for first day:')
    pi_para_correct_one_label.grid(row=7, column=0)
    pi_para_correct_one_text = tk.Entry(root, width=30, justify='center')
    pi_para_correct_one_text.grid(row=7, column=1)

    pi_para_correct_two_label = tk.Label(root, text='Enter the min % correct for second day:')
    pi_para_correct_two_label.grid(row=8, column=0)
    pi_para_correct_two_text = tk.Entry(root, width=30, justify='center')
    pi_para_correct_two_text.grid(row=8, column=1)

    pi_para_btn = tk.Button(root, text='Punish Incorrect Parameterized',
                            command=lambda: pi_para_button(pi_para_min_trials_text, pi_para_correct_one_text,
                                                           pi_para_correct_two_text), width=30)
    pi_para_btn.grid(row=9, column=0)

    spacer_btw_pi_ld = tk.Label(root, text='', bg='#D6D6D6', width=57)
    spacer_btw_pi_ld.grid(row=10, columnspan=2)

    ld_train_criteria_label = tk.Label(root, text='Enter criteria as n days/n+1 days: ')
    ld_train_criteria_label.grid(row=11, column=0)
    ld_train_criteria_text = tk.Entry(root, width=30, justify='center')
    ld_train_criteria_text.grid(row=11, column=1)

    ld_train_min_rev_num_label = tk.Label(root, text='Enter the min reversal number: ')
    ld_train_min_rev_num_label.grid(row=12, column=0)
    ld_train_min_rev_num_text = tk.Entry(root, width=30, justify='center')
    ld_train_min_rev_num_text.grid(row=12, column=1)

    ld_train_para_btn = tk.Button(root, text='LD Train Parameterized',
                                  command=lambda: ld_train_para_button(ld_train_criteria_text,
                                                                       ld_train_min_rev_num_text), width=30)
    ld_train_para_btn.grid(row=13, column=0)

    ld_probe_para_btn = tk.Button(root, text='LD Probe Parameterized', command=ld_probe_para_button, width=30)
    ld_probe_para_btn.grid(row=14, column=0)

    spacer_btw_ld_acq = tk.Label(root, text='', bg='#D6D6D6', width=57)
    spacer_btw_ld_acq.grid(row=15, columnspan=2)

    acq_para_label = tk.Label(root, text='Enter criteria as n days in a row: ')
    acq_para_label.grid(row=16, column=0)
    acq_para_text = tk.Entry(root, width=30, justify='center')
    acq_para_text.grid(row=16, column=1)

    acq_para_corrects_label = tk.Label(root, text='Enter the min corrects amount:')
    acq_para_corrects_label.grid(row=17, column=0)
    acq_para_corrects_text = tk.Entry(root, width=30, justify='center')
    acq_para_corrects_text.grid(row=17, column=1)

    acq_para_session_len_label = tk.Label(root, text='Enter the min session length time:')
    acq_para_session_len_label.grid(row=18, column=0)
    acq_para_session_len_text = tk.Entry(root, width=30, justify='center')
    acq_para_session_len_text.grid(row=18, column=1)

    acq_para_btn = tk.Button(root, text='Acquisition Parameterized',
                             command=lambda: acq_para_button(acq_para_text, acq_para_corrects_text,
                                                             acq_para_session_len_text),
                             width=30)
    acq_para_btn.grid(row=19, column=0)

    spacer_btw_acq_ext = tk.Label(root, text='', bg='#D6D6D6', width=57)
    spacer_btw_acq_ext.grid(row=20, columnspan=2)

    ext_para_label = tk.Label(root, text='Enter criteria as n days/n+1 days:')
    ext_para_label.grid(row=21, column=0)
    ext_para_text = tk.Entry(root, width=30)
    ext_para_text.grid(row=21, column=1)

    ext_para_omissions_label = tk.Label(root, text='Enter the min omissions req:')
    ext_para_omissions_label.grid(row=22, column=0)
    ext_para_omissions_text = tk.Entry(root, width=30, justify='center')
    ext_para_omissions_text.grid(row=22, column=1)

    ext_para_btn = tk.Button(root, text='Extinction Parameterized',
                             command=lambda: ext_para_button(ext_para_text, ext_para_omissions_text),
                             width=30)
    ext_para_btn.grid(row=23, column=0)
