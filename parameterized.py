import functools
from ld_probe import *
from ld_train import *
from gts_acq_ext import *

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


def block_parsing_ld_probe(df, type, total_blocks, parameters_list, writer):
    for para in parameters_list:
        all_blocks = list()
        for block_number in range(1, int(total_blocks) + 1):
            block_data = df.loc[(df['Block'] == block_number) & (df['Type'] == type)]
            block_data = block_data[['ID', 'Date', para, 'Type', 'Block']]
            all_blocks.append(block_data)
        merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='ID', how='outer'), all_blocks)
        merged_df.to_excel(writer, sheet_name=type + ' ' + para[0:25], index=False, freeze_panes=(1, 1))
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


def day_parsing_ld_train(df, type, max_days, parameters_list, writer):
    for para in parameters_list:
        all_days = list()
        for day in range(1, int(max_days) + 1):
            day_data = df.loc[(df['Day'] == day) & (df['Type'] == type)]
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


def acq_ext_parsing(df, max_days, parameters_list, writer):
    for para in parameters_list:
        all_days = list()
        for day in range(1, int(max_days) + 1):
            day_data = df.loc[(df['Day'] == day)]
            day_data = day_data[['ID', 'Date', 'Day', para]]
            all_days.append(day_data)
        merged_df = functools.reduce(lambda left, right: pd.merge(left, right, on='ID', how='outer'), all_days)
        merged_df.to_excel(writer, sheet_name='acq ' + para[0:25], index=False, freeze_panes=(1, 1))
    writer.save()


def acq_para_parameterized(df):
    try:
        writer_acq = pd.ExcelWriter('Acquisition All Days Parameters.xlsx', engine='xlsxwriter')
        print('A file called Acquisition All Days Parameters.xlsx has been created at:', script_location)
    except PermissionError:
        print(
            'Acquisition All Days Parameters.xlsx is opened! Please close them!')
        return

    max_days = df['Day'].max()
    acq_ext_parsing(df, max_days, acq_parameters, writer_acq)


def ext_para_parameterized(df):
    try:
        writer_ext = pd.ExcelWriter('Extinction All Days Parameters.xlsx', engine='xlsxwriter')
        print('A file called Extinction All Days Parameters.xlsx has been created at:', script_location)
    except PermissionError:
        print(
            'Extinction All Days Parameters.xlsx is opened! Please close them!')
        return

    max_days = df['Day'].max()
    acq_ext_parsing(df, max_days, acq_parameters, writer_ext)


def acq_para_button(criteria):
    if criteria == '':
        print('The criteria is empty! Please fill in the criteria!')
        return
    df = data_setup_acq()
    if df is not None:
        criteria_value = int(criteria.get())
        get_acquisition_normal(df, criteria_value)
        acq_para_parameterized(df)


def ext_para_button(criteria):
    if criteria == '':
        print('The criteria is empty! Please fill in the criteria!')
        return
    df = data_setup_ext()
    if df is not None:
        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])
        get_extinction_all(df, criteria_value, criteria_max_days)
        ext_para_parameterized(df)


def ld_train_para_button(criteria):
    df = data_setup()
    if df is not None:
        ld_train_delete_other_difficulties(df)

        criteria_list = criteria.get().split('/')
        criteria_value = int(criteria_list[0])
        criteria_max_days = int(criteria_list[1])

        get_ld_train_normal(df, criteria_value, criteria_max_days)
        ld_train_parameterized(df)


def ld_probe_para_button():
    df = data_setup()
    if df is not None:
        ld_probe_delete_other_difficulties(df)
        get_last_day_difficulty(df)
        ld_probe_parameterized(df)


def make_parameterized_button(tk, root):
    ld_train_criteria_label = tk.Label(root, text='Enter the LD Train Criteria as n days/n+1 days: ')
    ld_train_criteria_label.grid(row=0, column=0)
    ld_train_criteria_text = tk.Entry(root, width=30)
    ld_train_criteria_text.grid(row=0, column=1)

    ld_train_para_btn = tk.Button(root, text='LD Train Parameterized',
                                  command=lambda: ld_train_para_button(ld_train_criteria_text), width=30)
    ld_train_para_btn.grid(row=1, column=0)

    ld_probe_para_btn = tk.Button(root, text='LD Probe Parameterized', command=ld_probe_para_button, width=30)
    ld_probe_para_btn.grid(row=2, column=0)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=3, column=0)

    acq_para_label = tk.Label(root, text='Enter Acquisition criteria as n days in a row: ')
    acq_para_label.grid(row=4, column=0)
    acq_para_text = tk.Entry(root, width=30)
    acq_para_text.grid(row=4, column=1)
    acq_para_btn = tk.Button(root, text='Acquisition Parameterized', command=lambda: acq_para_button(acq_para_text),
                             width=30)
    acq_para_btn.grid(row=5, column=0)

    spacer_btn = tk.Label(root, text='')
    spacer_btn.grid(row=6, column=0)

    ext_para_label = tk.Label(root, text='Enter Extinction criteria as n days/n+1 days: ')
    ext_para_label.grid(row=7, column=0)
    ext_para_text = tk.Entry(root, width=30)
    ext_para_text.grid(row=7, column=1)
    ext_para_btn = tk.Button(root, text='Extinction Parameterized', command=lambda: ext_para_button(ext_para_text),
                             width=30)
    ext_para_btn.grid(row=8, column=0)
