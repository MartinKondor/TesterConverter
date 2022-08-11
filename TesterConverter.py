#!/usr/bin/env python
# pyinstaller --noconsole __main__.py
import enum
from os import getcwd

import json
from tkinter import Tk, Menu, Listbox, Scrollbar, EXTENDED, SINGLE, END, CENTER, ACTIVE, LEFT, N, S, E, W
from tkinter.ttk import Button, Style
from tkinter.messagebox import showinfo, showerror, askquestion
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames

from tester import *

# Kérdezze meg hogy hány teszt pont jut a fájlokra,
# és ellenőrizze le hogy van e nagyobb szám a konvertálás után mint (teszt pont)*64
# "Max. tesztpontok száma?"
# "Elvárt teszt pontok száma kevesebb mint a beállított"

"""
Create importable file from the converted data.
importable = other programs can use the file as well
"""
def create_importable_file(converted_data):
    basic_header = """#NAME_DIRECT "{}"
!
#PARAMETER "{}"
@VERSION "NTControl"
@GOOD_LABEL OFF
@BAD_LABEL OFF
@HEAD_LABEL OFF
@ADD_LABEL OFF
@PRINTER_INTERNAL OFF
@PRINT_HEADER ON
@PRINT_PASSED ON
@PRINT_PARAMETERS ON
@PRINTER_EXTERNAL OFF
@PRINT_VALUE ON
@KEEP_FAULTS OFF
@PRINT_SEGMENT ON
@PRINT_COMP_NAME OFF
@RESULT_DOCUMENTATION_LEVEL 0
@PIN_FORMAT DIRECT
@MONITORING OFF
@STOP_ON_FAULTS ON
@RELAIS_TIME 750
@VISUAL_LED_TEST OFF
@ERROR_LIMIT 20
@LOOSE_CONTACT_TEST OFF
@PRINT_ADD_INFO ON
@PRINT_NEW_PAGE ON
@ABORT_ALL OFF
@EXTERNAL_VOLTAGE_TEST OFF
!
#PARAMETER "{}" "Segment 1"
:TEST_TYPE
    CONNECTION_LOW
    SHORT_LOW
@RESISTANCE_LOW 250.000000
@RESISTANCE_INSULATION 20000.000000
@VOLTAGE_LOW 12.000000
@TIME_LOW_VOLTAGE 0
!
#NET "{}" "Segment 1\"
"""
    one_row_str = '@-"{}"\n*-"Sub 1"\n'
    
    def create_type(index):
        
        def rotate_if(_p):
            if len(_p) != 2:
                return False
            
            p = [_p[0], _p[1]]
            p[0] = p[0][0]

            pp1 = ["65", "193", "321", "449"]
            pp2 = ["66", "194", "322", "450"]
            if (p[0].strip().replace('"', "") in pp1) and (p[1].strip().replace('"', "") in pp2):
                return True
            if (p[1].strip().replace('"', "") in pp1) and (p[0].strip().replace('"', "") in pp2):
                return True
            return False

        result = basic_header
        
        for i, row in enumerate(converted_data):
            if rotate_if(row):
                p0 = row[0]
                p1 = row[1]
                
                if isinstance(p0, list) and not isinstance(p1, list):
                    row = [[p1], *p0]
                elif isinstance(p0, list) and isinstance(p1, list):
                    row = [[*p1], *p0]
                else:
                    row = [[p1], p0]

            result += one_row_str.format(str(int(i) + 1))

            for r in row:
                if type(r) is list:
                    for l in r:
                        result += '"' + l + '" '
                else:
                    result += '"' + str(r) + '" ' 
                
            result += '\n'
                
        result += """!
#PARAMETER "{}"
:DESCRIPTION ($$)
!
        """
                
        return result
        
    return create_type(1)


class TesterConverter(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        try:
            self.iconbitmap('./icon.ico')
        except:
            pass

        self.wm_title('Teszter Konvertáló')
        self.resizable(False, False)
        self.eval('tk::PlaceWindow . center')
        self.bind('<Key>', self.keypress)

        self.last_save_dir = ''
        self.last_open_dir = ''
        self.protocol('WM_DELETE_WINDOW', self.on_closing)

        self.menubar = Menu(self)
        self.menubar.add_command(label='Segítség', command=self.help)
        # self.menubar.add_command(label='Segítség', command=self.help)

        self.choose_file_button = Button(self, text='\n\n\n\nFájl hozzáadása\n\n\n\n', command=self.choose_file, width=15)
        self.delete_file_button = Button(self, text='\n\n\n\nFájl törlése\n\n\n\n', command=self.delete_selected_file, width=15)
        self.convert_button = Button(self, text='\nKonvertálás\n', command=self.convert, width=70)
        self.file_list = Listbox(self, selectmode=EXTENDED, height=9, width=70, borderwidth=1)
        self.dict_list = Listbox(self, selectmode=SINGLE, height=9, width=70, borderwidth=1)

        # Scrollbar listákhoz
        scb = Scrollbar(self, orient='vertical')
        scb.grid(padx=0, pady=0, row=0, column=2, sticky=N + S)
        self.dict_list.config(yscrollcommand=scb.set)
        scb.config(command=self.dict_list.yview)

        scb = Scrollbar(self, orient='vertical')
        scb.grid(padx=0, pady=0, row=1, column=2, sticky=N + S)
        self.file_list.config(yscrollcommand=scb.set)
        scb.config(command=self.file_list.yview)

        self.file_list.configure(justify=LEFT)
        self.dict_list.configure(justify=CENTER)

        # Lista feltöltése
        data = build_dict()
        for i, k in enumerate(data):
            self.dict_list.insert(END, '{}            ->            {}'.format(data[k], k))

        # Elemek elhelyezese
        self.choose_file_button.grid(padx=0, pady=0, row=0, column=0)
        self.delete_file_button.grid(padx=0, pady=0, row=1, column=0)
        self.convert_button.grid(padx=0, pady=0, row=2, column=1)
        self.dict_list.grid(padx=2, pady=0, row=0, column=1)
        self.file_list.grid(padx=0, pady=0, row=1, column=1)

        # Read out config file
        try:
            data = {}
            
            with open('config.json', 'r') as file:
                data = json.load(file)
                
            self.last_open_dir = data['last_open_dir']
            self.last_save_dir = data['last_save_dir']
        except:
            pass

        self.config(menu=self.menubar)
        self.mainloop()

    def convert(self):
        files = self.file_list.get(0, END)

        if not files:
            showerror('Hiba', 'Nincs kiválasztott fájl.')
            return 0

        converted_data = []

        for i, file_name in enumerate(files):
            file = open(file_name, 'r')
            contents = file.read()
            file.close()
            
            numbers = []
            for l in contents.splitlines():
                numbers.append(int(l.strip()) + (i * 128))

            d = build_dict()
            pairs = create_pairs(numbers, i)
            new_pairs = {}

            for i in pairs:
                new_pairs[d[i]] = [d[k] for k in pairs[i]]

            table = build_table()
            pairs = []

            for i in new_pairs:
                if len(new_pairs[i]) == 0:
                    continue
            
                nums = [table[i][0], [table[k][0] for k in new_pairs[i]]][::-1]
                #nums = self._change_nums(nums)
                pairs.append(nums)

            converted_data.extend(pairs)

        self.create_ktx(converted_data)
        return 0

    def _change_nums(self, nums):
        new_nums = nums
        return new_nums

    def create_ktx(self, content):
        filename = asksaveasfilename(initialdir=self.last_save_dir, filetypes=[('Adaptronic ktx fájl', '.ktx')], defaultextension='.ktx')
        
        if not filename:
            return 

        self.last_save_dir = '/'.join(filename.replace('\\', '/').split('/')[:-1])
        with open(filename, 'w+') as file:
            file.write(create_importable_file(content).replace('{}', '.'.join(filename.replace('\\', '/').split('/')[-1].split('.')[:-1])))
    
        showinfo('Konvertálás kész', 'A(z) {} fájl elkészült.'.format(filename))

    def choose_file(self):
        files = list(askopenfilenames(initialdir=self.last_open_dir,
            filetypes=[
            'txt .txt'
        ]))

        for of in self.file_list.get(0, END):
            files.append(of)
        self.file_list.delete(0, END)

        if len(files) > 1:
            files = sorted(files)

        for file in files:
            if not file:
                continue

            ext = file.split('.')[-1]
            if ext != 'txt' and ext != 'TXT':
                showerror('Hiba', 'Nem megfelelő a "{}" fájl fájlformátuma.\n\nKérlek csak ".txt" formátumot használj.'.format(file))
                return 0

            try:
                self.file_list.insert(END, file)
            except Exception as e:
                showerror('Hiba', 'Nem megfelelő a kiválasztott fájl tartalma.\n'.format(str(e)))

    def help(self):
        showinfo('Segítség', """
        Ctrl + T - Törli a kiválasztott fájlt a listából.
        Ctrl + H - Fájl(ok) hozzáadása.
        Ctrl + N - Konvertálás indítása.
        Ctrl + X - Minden fájl törlése a listából.
        """)

    def delete_selected_file(self):
        file = self.file_list.curselection()
        active = self.file_list.get(ACTIVE)

        if not active or not file:
            return 0
        if askquestion('Törli?', 'Biztos törli a kiválasztott "{}" fájlt a listából?'.format(active)) == 'yes':
            self.file_list.delete(file[0])

    def delete_all_files(self):
        if askquestion('Törli?', 'Biztos töröl minden fájlt a listából?') == 'yes':
            self.file_list.delete(0, END)

    def keypress(self, event):
        #print(repr(event.char))
        # Turned off because \x08 == Ctrl + h and \x08 == Backspace
        # if event.char == '\x08':  # Ctrl + h
            # self.help()

        if event.char == '\x14' or event.char == 't':  # Ctrl + T
            self.delete_selected_file()
        if event.char == '\x08' or event.char == 'h':  # Ctrl + H
            self.choose_file()
        if event.char == '\x0e' or event.char == 'n':  # Ctrl + N
            self.convert()
        if event.char == '\x18' or event.char == 'x':  # Ctrl + X
            self.delete_all_files()

    def on_closing(self):

        # Save attributes to config file
        with open('config.json', 'w+') as file:
            json.dump({'last_open_dir': self.last_open_dir, 'last_save_dir': self.last_save_dir}, file)
    
        self.destroy()


if __name__ == '__main__':
    TesterConverter()
