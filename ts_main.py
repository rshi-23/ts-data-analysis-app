import tkinter as tk

from parameterized import *
import webbrowser


root = tk.Tk()
root.geometry('404x345')
root.title('Raymon Shi Touchscreen Data Analysis App')
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)


def display_frame(frame_page):
    frame_page.tkraise()


main_page_frame = tk.Frame(root)
main_page_frame.grid(row=0, column=0, sticky='nsew')

main_page_frame.columnconfigure(0, weight=1)

general_ts_frame = tk.Frame(root)
general_ts_frame.grid(row=0, column=0, sticky='nsew')
general_ts_frame.columnconfigure(0, weight=1)

ld_train_frame = tk.Frame(root)
ld_train_frame.grid(row=0, column=0, sticky='nsew')

ld_probe_frame = tk.Frame(root)
ld_probe_frame.grid(row=0, column=0, sticky='nsew')

extinction_paradigm_frame = tk.Frame(root)
extinction_paradigm_frame.grid(row=0, column=0, sticky='nsew')

parameterized_frame = tk.Frame(root)
parameterized_frame.grid(row=0, column=0, sticky='nsew')


def main_page_frame_buttons():
    main_general_ts_btn = tk.Button(main_page_frame, text='General Touchscreen',
                                    command=lambda: display_frame(general_ts_frame))
    main_general_ts_btn.grid(row=1, column=0)
    main_ld_train_btn = tk.Button(main_page_frame, text='LD Train',
                                  command=lambda: display_frame(ld_train_frame))
    main_ld_train_btn.grid(row=2, column=0)
    main_ld_probe_btn = tk.Button(main_page_frame, text='LD Probe',
                                  command=lambda: display_frame(ld_probe_frame))
    main_ld_probe_btn.grid(row=3, column=0)
    main_extinction_btn = tk.Button(main_page_frame, text='Extinction Paradigm',
                                    command=lambda: display_frame(extinction_paradigm_frame))
    main_extinction_btn.grid(row=4, column=0)
    main_parameterized_btn = tk.Button(main_page_frame, text='Parameterized', command=lambda: display_frame(parameterized_frame))
    main_parameterized_btn.grid(row=5, column=0)
    main_github_code_btn = tk.Button(main_page_frame, text='Github Code Page', command=lambda: webbrowser.open(
        'https://github.com/raymon-shi/ts-data-analysis-script'))
    main_github_code_btn.grid(row=6, column=0)


def main_menu_buttons(tk, frame):
    main_menu_btn = tk.Button(frame, text='Main Menu', command=lambda: display_frame(main_page_frame), width=30)
    spacer_btn = tk.Label(frame, text='')
    spacer_btn.grid(row=15, column=0)
    main_menu_btn.grid()


make_general_ts_buttons(tk, general_ts_frame)
main_menu_buttons(tk, general_ts_frame)

make_ld_train_buttons(tk, ld_train_frame)
main_menu_buttons(tk, ld_train_frame)

make_ld_probe_buttons(tk, ld_probe_frame)
main_menu_buttons(tk, ld_probe_frame)

make_extinction_buttons(tk, extinction_paradigm_frame)
main_menu_buttons(tk, extinction_paradigm_frame)

make_parameterized_button(tk, parameterized_frame)
main_menu_buttons(tk, parameterized_frame)

display_frame(main_page_frame)

main_page_frame_buttons()

root.mainloop()
