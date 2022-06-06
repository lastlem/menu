import time
from tkinter import *
from tkinter import filedialog as fd
from tkinter import messagebox as mb
from tkinter.ttk import Combobox
from typing import Callable

file = None
text_copy = ''
check_buttons = []
logs = []


def create_file(text: Text) -> None:
    global file
    if text.get(1.0, END) == '\n':
        return

    answer = mb.askyesnocancel('Save file', 'Do you want to save changes in the file?')
    if answer:
        save_file(text)
    text.delete(1.0, END)


def check_saves(text):
    if file:
        with open(file.name) as f:
            first_text = f.read()
            second_text = text.get(1.0, END).strip()
            return first_text != second_text
    return True


def open_file(text: Text) -> None:
    global file

    if check_saves(text):
        answer = mb.askyesnocancel('Save file', 'Do you want to save this as file?')
        if answer:
            save_as_file(text)

    file = fd.askopenfile()
    if not file:
        return
    text.delete(1.0, END)
    text.insert(1.0, file.read())


def save_file(text: Text) -> None:
    global file
    if not file:
        save_as_file(text)
        return
    with open(file.name, 'w') as f:
        f.write(text.get(1.0, END).strip())


def save_as_file(text: Text) -> None:
    global file
    file = fd.asksaveasfile()
    if not file:
        return
    file.write(text.get(1.0, END).strip())


def print_file(text: Text) -> None:
    print(text.get(1.0, END).strip())


def back_text(text: Text) -> None:
    text['state'] = 'normal'
    text.delete(1.0, END)
    new_text = logs.pop().strip()
    text.insert(1.0, new_text)


def cut_text(text: Text) -> None:
    global text_copy
    if not text.tag_ranges('sel'):
        return

    text_copy = text.get(SEL_FIRST, SEL_LAST)
    text.delete(SEL_FIRST, SEL_LAST)


def copy_text(text: Text) -> None:
    global text_copy
    if not text.tag_ranges('sel'):
        return

    text_copy = text.get(SEL_FIRST, SEL_LAST)


def paste_text(text: Text) -> None:
    if not text_copy:
        return

    text.insert(INSERT, text_copy)
    text['state'] = 'disable'


def delete_text(text: Text) -> None:
    if not text.tag_ranges('sel'):
        return

    text.delete(SEL_FIRST, SEL_LAST)
    text['state'] = 'disable'


def copy_all_text(text: Text) -> None:
    text.tag_add(SEL, 1.0, END)


def add_date(text: Text) -> None:
    time_now = time.strftime('%H:%M %d.%m.%y')
    text.insert(INSERT, time_now)


def make_combobox(frame: Frame, text_label: str, values: tuple) -> Combobox:
    frame_type = Frame(frame)
    frame_type.pack(side=LEFT, fill=BOTH, expand=1, pady=10, padx=10)
    Label(frame_type, text=text_label).pack()
    font_type = Combobox(frame_type, values=values, width=32)
    font_type.pack()
    return font_type


def change_font(text: Text) -> None:
    with open('app_menu_fonts.txt') as fonts_file:
        fonts = tuple(fonts_file.read().strip().split(', '))

    font_root = Toplevel()
    font_root.resizable(False, False)

    main_frame = Frame(font_root)
    main_frame.pack(fill=BOTH)

    font_type = make_combobox(main_frame, 'Font type:', fonts)
    font_size = make_combobox(main_frame, 'Font size:', tuple(range(1, 56, 2)))

    command = lambda: confirm_changes(text, font_root, font_size, font_type)
    Button(font_root, text='Confirm', command=command).pack(fill=BOTH)

    font_root.mainloop()


def confirm_changes(text: Text, font_root: Toplevel, font_size: Entry, font_type: Entry) -> None:
    if check_inputs(font_size):
        text.config(font=(font_type.get(), font_size.get()))
    else:
        mb.showinfo('Incorrect Input', 'Size should be an integer')

    font_root.destroy()


def check_inputs(font_size: Entry) -> bool:
    return False if not font_size.get().isdigit() else True


def change_wrap(text: Text) -> None:
    wrap = check_buttons[0]
    text.config(wrap=WORD) if wrap.get() else text.config(wrap=CHAR)


def get_status(event: EventType, label: Label) -> None:
    line, char = event.widget.index(INSERT).split('.')
    text = f'Line: {line}, Char: {int(char) + 1}'
    label['text'] = text


def show_status_line(label: Label) -> None:
    show_status = check_buttons[1]
    label.pack(side=BOTTOM) if show_status.get() else label.pack_forget()


def connect_text_and_combination(text: str, combination: str) -> str:
    return f'{text.ljust(20)}{combination.rjust(20)}'


def exit_programme() -> None:
    quit()


def combination_normalization(combination: str) -> str:
    combination = combination.capitalize().replace('Ctrl', 'Control').replace('+', '-')
    return combination.title().replace('Control-Shift', 'Control-Shift-Key') if 'shift' in combination else combination


def bind_key_combinations(text: Text, combination: str, func: Callable):
    combination = combination_normalization(combination)
    if combination and func == make_window:
        text.bind(f'<{combination}>', lambda event: func())
    elif combination:
        text.bind(f'<{combination}>', lambda event: func(text))


def russian_combination_control(event: EventType):
    keycode_funcs = [(78, create_file),
                     (79, open_file),
                     (83, save_file),
                     (80, print_file),
                     (90, back_text),
                     (88, cut_text),
                     (67, copy_text),
                     (86, paste_text),
                     (65, copy_all_text),
                     ]
    for keycode, func in keycode_funcs:
        if event.keycode == keycode:
            func(event.widget)


def russian_combination_control_shift(event: EventType):
    if event.keycode == 78:
        make_window()
    elif event.keycode == 83:
        save_as_file(event.widget)


def add_log(event: EventType) -> None:
    text = event.widget.get(1.0, END)
    logs.append(text)
    if len(logs) > 1 and logs[-2] == logs[-1]:
        logs.pop()


def return_state(event: EventType) -> None:
    event.widget['state'] = 'normal'


def popup(event: EventType, menu: Menu):
    menu.post(event.x_root, event.y_root)


def make_popup_menu(text: Text):
    menu = Menu(tearoff=0)
    menu_subcommands = [('Cut', cut_text),
                        ('Copy', copy_text),
                        ('Paste', paste_text)
                        ]
    for subcommand_name, func in menu_subcommands:
        menu.add_command(label=subcommand_name, command=lambda e=func: e(text))
    return menu


def make_menu(subcommand_type: str, text: str, menu: Menu, func: Callable, widget: Text | Label) -> None:
    if subcommand_type == 'separator':
        menu.add_separator()
    elif subcommand_type == 'button':
        menu.add_command(label=text, command=lambda el=widget: func(el), activebackground='Red')
    elif subcommand_type == 'checkbutton':
        checkbutton = BooleanVar()
        check_buttons.append(checkbutton)
        menu.add_checkbutton(label=text, onvalue=1, offvalue=0, variable=checkbutton, command=lambda: func(widget),
                             activebackground='Red')


def create_menus(root: Tk, menu_names: list, text: Text, label: Label) -> Menu:
    main_menu = Menu(root)
    for name_submenu, subcommands in menu_names:
        menu = Menu(main_menu, tearoff=0)
        for subcommand in subcommands:
            subcommand_name, key_combination, subcommand_type, command = subcommand
            subcommand_name = connect_text_and_combination(subcommand_name, key_combination)
            widget = label if command == show_status_line else text
            make_menu(subcommand_type, subcommand_name, menu, command, widget)
            bind_key_combinations(text, key_combination, command)
        main_menu.add_cascade(label=name_submenu, menu=menu)
    return main_menu


def make_window() -> None:
    root = Tk()
    root.geometry('400x400')

    text = Text(root)
    text.pack(expand=1, fill=BOTH)

    label_status = Label(root, text='Line: 1, Char: 0')

    menu_names = [
        ['File', [('Create', 'CTRL+N', 'button', create_file),
                  ('New window', 'CTRL+SHIFT+N', 'button', make_window),
                  ('Open...', 'CTRL+O', 'button', open_file),
                  ('Save', 'CTRL+S', 'button', save_file),
                  ('Save as', 'CTRL+SHIFT+S', 'button', save_as_file),
                  ('', '', 'separator', None),
                  ('Print', 'CTRL+P', 'button', print_file),
                  ('', '', 'separator', None),
                  ('Exit', '', 'button', exit_programme)
                  ]],
        ['Edit', [('Back', 'CTRL+Z', 'button', back_text),
                  ('', '', 'separator', None),
                  ('Cut', 'CTRL+X', 'button', cut_text),
                  ('Copy', 'CTRL+C', 'button', copy_text),
                  ('Paste', 'CTRL+V', 'button', paste_text),
                  ('Delete', 'Delete', 'button', delete_text),
                  ('', '', 'separator', None),
                  ('Copy all', 'CTRL+A', 'button', copy_all_text),
                  ('Date', 'F5', 'button', add_date)
                  ]],
        ['Format', [('Wrap', '', 'checkbutton', change_wrap),
                    ('Font...', '', 'button', change_font)
                    ]],
        ['View', [('Status line', '', 'checkbutton', show_status_line)
                  ]]
    ]

    main_menu = create_menus(root, menu_names, text, label_status)

    popup_menu = make_popup_menu(text)

    text.bind('<Key>', return_state)
    text.bind('<Key>', add_log, add='+')
    text.bind('<Key>', lambda event: get_status(event, label_status), add='+')
    text.bind('<Control-Key>', russian_combination_control)
    text.bind('<Control-Shift-Key>', russian_combination_control_shift)
    text.bind('<Button-3>', lambda event: popup(event, popup_menu))
    root.config(menu=main_menu)
    root.mainloop()


make_window()
