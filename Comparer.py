"""
Fájl ellenőrző:

- Az utolsó alsóvonásig egybe tartoznak.
- Régi ktx-et az új ktx-hez
- Kiemelni a hibákat egy szerkesztőben
"""
#!/usr/bin/env python
# pyinstaller --noconsole __main__.py
import enum
from os import getcwd

import json
from tkinter import Tk, Menu, Listbox, Scrollbar, EXTENDED, SINGLE, END, CENTER, ACTIVE, LEFT, RIGHT, N, S, E, W
from tkinter.ttk import Button, Style
from tkinter.messagebox import showinfo, showerror, askquestion
from tkinter.filedialog import askopenfilename, asksaveasfilename, askopenfilenames

from tester import *


class Comparer(Tk):

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

        self.compare_button = Button(self, text='Ellenőrzés', command=self.compare, width=15)
        self.old_list = Listbox(self, selectmode=EXTENDED, height=9, width=40, borderwidth=1)
        self.choose_old_button = Button(self, text='Régi fájl hozzáadása', command=self.choose_old, width=15)
        self.choose_new_button = Button(self, text='Új fájl hozzáadása', command=self.choose_new, width=15)
        self.new_list = Listbox(self, selectmode=EXTENDED, height=9, width=40, borderwidth=1)

        scb = Scrollbar(self, orient='vertical')
        scb.grid(padx=0, pady=0, row=0, column=1, sticky=N + S)
        self.old_list.config(yscrollcommand=scb.set)
        scb.config(command=self.old_list.yview)

        scb = Scrollbar(self, orient='vertical')
        scb.grid(padx=0, pady=0, row=0, column=3, sticky=N + S)
        self.new_list.config(yscrollcommand=scb.set)
        scb.config(command=self.new_list.yview)

        self.old_list.configure(justify=LEFT)
        self.new_list.configure(justify=RIGHT)

        self.old_list.grid(padx=2, pady=2, row=0, column=0)
        self.new_list.grid(padx=2, pady=2, row=0, column=2)
        self.choose_old_button.grid(padx=2, pady=2, row=1, column=0)
        self.choose_new_button.grid(padx=2, pady=2, row=1, column=2)
        self.compare_button.grid(padx=2, pady=2, row=2, column=0)

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

    def _choose_files(self):
        files = list(askopenfilenames(initialdir=self.last_open_dir,
            filetypes=[
            'ktx .ktx'
        ]))
        if not files:
            showerror('Hiba', 'Nincs kiválasztott fájl.')
            return []
        return files

    def _format_file_name(self, file_path):
        return file_path.replace('\\', '/').split('/')[-1]

    def choose_old(self):
        files = self._choose_files()
        for file in files:
            self.old_list.insert(END, file)

    def choose_new(self):
        files = self._choose_files()
        for file in files:
            self.new_list.insert(END, file)

    def compare(self):
        pairs = []

        # for oldf, newf in zip(self.old_list.get(0, END), self.new_list.get(0, END)):
        for newf in self.new_list.get(0, END):
            for oldf in self.old_list.get(0, END):
                if '_' not in oldf:
                    showinfo('Hiba', 'Nincs _ az "{}" nevű fájl nevében, ezért nem tudni mivel kell összehasonlítani.'.format(oldf))
                    return False
                if '_' not in newf:
                    showinfo('Hiba', 'Nincs _ az "{}" nevű fájl nevében, ezért nem tudni mivel kell összehasonlítani.'.format(oldf))
                    return False

                if newf.split('_')[0] == oldf.split('_')[0]:
                    pairs.append([oldf, newf])

        # Compare pairs
        for o, n in pairs:
            f = open(o, 'r')
            oc = f.readlines()
            f.close()
            f = open(n, 'r')
            nc = f.readlines()
            f.close()

            self._compare_lines(o, n, oc, nc)

        return True

    def _compare_lines(self, ofile, nfile, old_lines, new_lines):
        errors = []
        if len(old_lines) != len(new_lines):
            showerror('Hiba', 'A fájlok nem egyenlő hosszúak!')

        for i, (ol, nl) in enumerate(zip(old_lines, new_lines)):
            if ol != nl:
                errors.append([i, ol, nl])

        # Show errors
        err_msg = ""
        err_template = """
        {}. sorban a "{}" fájlban:
          "{}"
        de az "{}" fájlban:
          "{}" 
        """.strip()
        for i, o, n in errors:
            err_msg += "\n"
            err_msg += err_template.format(
                i,
                self._format_file_name(ofile.strip()),
                o.strip(),
                self._format_file_name(nfile.strip()),
                n.strip()
            )
            err_msg += "\n"

        showinfo("Hibák", err_msg)

    def help(self):
        showinfo('Segítség', """
        ...
        """)

    def on_closing(self):

        # Save attributes to config file
        with open('config.json', 'w+') as file:
            json.dump({'last_open_dir': self.last_open_dir, 'last_save_dir': self.last_save_dir}, file)
    
        self.destroy()

    def keypress(self, event):
        #print(repr(event.char))
        pass


if __name__ == '__main__':
    Comparer()
