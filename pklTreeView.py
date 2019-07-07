import sys, pickle, tkinter, os, copy
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk

root_path = os.path.dirname(os.path.realpath(__file__))

class PklTreeItem:

    def __init__(self, parent=None):
        self.Parent = parent
        self.Children = []
        self.Type = None
        self.Value = None

    def appendChild(self, item):
        self.Children.append(item)

    def child(self, row: int):
        return self.Children[row]

    def parent(self):
        return self.Parent

    def childrenCount(self):
        return len(self.Children)

    def row(self):
        if self.Parent is not None:
            return self.Parent.Children.index(self)
        return 0

    def setKey(self, key: str):
        self.Key = key

    def setValue(self, value: str):
        self.Value = value

    def setType(self, type):
        self.Type = type

    def key(self):
        return self.Key

    def value(self):
        return self.Value

    def type(self):
        return self.Type

    def selective_search(self, key):
        results = []
        for children in self.Children:
            rsearch = children.selective_search(key)
            if rsearch is not None:
                results.extend(rsearch)
        if self.key() == key:
            return [self]
        if results:
            return results
        return None

    def load(self, value, parent=None, name='root'):
        rootItem = PklTreeItem(parent)
        rootItem.setKey(name)
        pklType = None
        try:
            pklType = type(value).__name__
        except AttributeError:
            pass
        rootItem.setType(pklType)

        if isinstance(value, dict):
            for key in value:
                v = value[key]
                child = self.load(v, rootItem)
                child.setKey(key)
                child.setType(type(v).__name__)
                rootItem.appendChild(child)

        elif isinstance(value, list):
            for i, v in enumerate(value):
                child = self.load(v, rootItem)
                child.setKey(str(i))
                child.setType(type(v).__name__)
                rootItem.appendChild(child)

        else:
            rootItem.setKey(type(value).__name__)
            rootItem.setValue(value)
            rootItem.setType(type(value).__name__)
        return rootItem

    def convert(self):
        if self.type() == 'dict':
            item_dict = {}
            for item in self.Children:
                item_dict[item.key()] = item.convert()
            return item_dict

        if self.type() == 'list':
            item_list = []
            for item in self.Children:
                item_list.append(item.convert())
            return item_list

        else:
            if self.type() == 'int':
                return int(self.value())
            return self.value()


# noinspection SpellCheckingInspection,PyAttributeOutsideInit
class TKTree:

    def __init__(self, root: Tk, pklTreeRoot=None):
        self.root = root

        self.pklTreeRoot = pklTreeRoot

        self.pklTreePointer = {id(pklTreeRoot): pklTreeRoot}

        self.tkTree = ttk.Treeview(root, height=40)
        if pklTreeRoot is not None:
            self.load(pklTreeRoot)

        self.logs = []
        self.rlogs = []

        self.setup_UI(root)

    def setup_UI(self, root: Tk):
        style = ttk.Style()
        style.theme_use('clam')

        menubar = Menu(root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label='Hard refresh', command=self.refresh)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Undo", accelerator='Control+Z', command=self.ctrlz)
        editmenu.add_command(label="Redo", accelerator='Control+Shift+Z', command=self.ctrlsz)
        editmenu.add_command(label="Copy", accelerator='Control+C', command=self.ctrlc)
        editmenu.add_command(label="Paste", accelerator='Control+V', command=self.ctrlv)
        editmenu.add_command(label="Delete", accelerator='Control+X', command=self.ctrlx)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        root.config(menu=menubar)

        self.tkTree.config(columns=('type', 'value'))
        self.tkTree.heading('#0', text='key')
        self.tkTree.heading('type', text='type')
        self.tkTree.heading('value', text='value')
        self.tkTree.bind('<Control-z>', self.undo)
        self.tkTree.bind('<Control-Z>', self.redo)
        self.tkTree.bind('<Control-c>', self.copy)
        self.tkTree.bind('<B1-Motion>', self.move)
        self.tkTree.bind('<Control-v>', self.paste)
        self.tkTree.bind('<Control-x>', self.delete)
        self.tkTree.bind('<Control-e>', self.edit)
        self.tkTree.bind('r', self.rrefresh)
        self.tkTree.grid(row=0, column=0, columnspan=20, rowspan=16)

        special_edit = ttk.Button(root, text='Special edit', width=20)
        edit_multiple = ttk.Button(root, text='Edit Multiple Values', width=20)
        add_entry = ttk.Button(root, text='Add entry', width=20)
        selective_search = ttk.Button(root, text='Select with keyword', width=20)

        special_edit.grid(row=0, column=21)
        edit_multiple.grid(row=0, column=22)
        add_entry.grid(row=1, column=21)
        selective_search.grid(row=1, column=22)

        special_edit.bind('<Button-1>', self.special_edit_dialog)
        edit_multiple.bind('<Button-1>', self.multi_edit)
        add_entry.bind('<Button-1>', self.add_entry_dialog)
        selective_search.bind('<Button-1>', self.selective_select_dialog)

    def open_file(self):
        file = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(('PolyPickle Files', '*.plypk'),
                                                     ('DatabasePickle Files', '*.dbpk'),
                                                     ('All Files', '*.*')))
        name = os.path.splitext(os.path.basename(file))[0]

        popup = Toplevel(root)
        style = ttk.Style()
        style.theme_use('clam')
        popup.geometry('200x100+600+50')
        popup.wm_title('Progress')

        progressbar = ttk.Progressbar(popup, orient='horizontal', length=100, mode='indeterminate')
        progressbar.pack()

        if file != '' and file is not None:
            with open(file, 'rb') as pkl:
                if self.pklTreeRoot is not None:
                    item = PklTreeItem().load(pickle.load(pkl), self.pklTreeRoot, name)
                    self.load(item, self.pklTreeRoot)
                    self.pklTreeRoot.appendChild(item)
                else:
                    item = PklTreeItem().load(pickle.load(pkl), name=name)
                    self.load(item)

        popup.destroy()

    def save(self):
        file = filedialog.asksaveasfilename(initialdir=root_path,
                                            title="Select file",
                                            filetypes=(("Database pickle files", "*.dbpkl"),
                                                        ("All files", "*.*")))
        if file == '':
            return
        popup = Toplevel(root)
        style = ttk.Style()
        style.theme_use('clam')
        popup.geometry('200x100+600+50')
        popup.wm_title('Progress')

        progressbar = ttk.Progressbar(popup, orient='horizontal', length=100, mode='indeterminate')
        progressbar.pack()

        converted = self.pklTreeRoot.convert()
        if file != '' and file is not None:
            with open('{}.dbpk'.format(file), 'wb') as output:
                pickle.dump(converted, output, pickle.HIGHEST_PROTOCOL)

        popup.destroy()

    def load(self, item: PklTreeItem, parent=None):
        item_id = id(item)
        self.pklTreePointer[item_id] = item
        if parent is None:
            self.pklTreeRoot = item
            self.tkTree.insert('', '0', item_id, text=item.key())
            self.tkTree.item(item_id, values=(item.type(), item.value()))
            for children in item.Children:
                self.load(children, item)
        else:
            parent_id = id(parent)
            self.tkTree.insert(parent_id, 'end', item_id, text=item.key())
            self.tkTree.item(item_id, values=(item.type(), item.value()))
            for children in item.Children:
                self.load(children, item)

    def lookup(self, item: str):
        if item == '':
            return ''
        return self.pklTreePointer[int(item)]

    def edit(self, event):
        self.log()
        column = self.tkTree.identify_column(self.tkTree.winfo_pointerxy()[0] - self.tkTree.winfo_rootx())
        tree_selection = self.tkTree.selection()[0]
        selection = self.lookup(tree_selection)
        style = ttk.Style()
        style.theme_use('clam')
        value = simpledialog.askstring('Edit', 'Edit Value:')
        if value != '' and value is not None:
            if column == '#0':
                selection.setKey(value)
                self.tkTree.item(tree_selection, text=value)
            elif column == '#1':
                selection.setType(value)
                self.tkTree.set(tree_selection, column, value)
            elif column == '#2':
                selection.setValue(value)
                self.tkTree.set(tree_selection, column, value)

    def multi_edit(self, event):
        self.log()
        tree_selection = self.tkTree.selection()
        style = ttk.Style()
        style.theme_use('clam')
        value = simpledialog.askstring('Edit', 'Edit Value:')
        for item in tree_selection:
            selection = self.lookup(item)
            selection.setValue(value)
            self.tkTree.set(item, '#2', value)

    def copy(self, event):
        tree_selection = self.tkTree.selection()
        pti_copy = []
        item_ids = []
        for item in tree_selection:
            _copy = copy.deepcopy(self.lookup(item))
            pti_copy.append(_copy)
            item_ids.append(str(id(_copy)))
            self.pklTreePointer[id(_copy)] = _copy
        self.copied = item_ids

    def paste(self, event):
        try:
            self.log()
            tree_selection = self.tkTree.selection()[0]
            for item in self.copied:
                pkl_item = self.lookup(item)
                self.load(pkl_item, self.lookup(tree_selection))
        except:
            pass

    def delete(self, event):
        self.log()
        tree_selection = self.tkTree.selection()
        for item in tree_selection:
            pkl_item = self.lookup(item)
            if pkl_item is not self.pklTreeRoot:
                pkl_item.Parent.Children.remove(pkl_item)
                del self.pklTreePointer[int(item)]
                del pkl_item
                self.tkTree.delete(item)
            else:
                self.pklTreeRoot = None
                self.tkTree.delete(item)

    def add_entry_dialog(self, event):
        style = ttk.Style()
        style.theme_use('clam')
        self.entry = Toplevel(root)
        self.entry.geometry('400x100+600+50')
        Label(self.entry, text='Key:').grid(row=0, column=0)
        Label(self.entry, text='Type:').grid(row=0, column=1)
        Label(self.entry, text='Value:').grid(row=0, column=2)
        self.equation = Entry(self.entry)
        self.equation.grid(row=1, column=0)
        self._type = ttk.Combobox(self.entry, values=('int', 'str', 'list', 'dict'))
        self._type.current(0)
        self._type.grid(row=1, column=1)
        self.value = Entry(self.entry)
        self.value.grid(row=1, column=2)
        Button(self.entry, text='Add', width=15, command=self.tadd_entry).grid(row=2, column=0)
        Button(self.entry, text='Add to children', width=15, command=self.tadd_entry_children).grid(row=2, column=1)
        Button(self.entry, text='Cancel', command=self.entry.destroy, width=15).grid(row=2, column=2)

    def tadd_entry(self):
        self.log()
        self.add_entry(self.equation.get(), self._type.get(), self.value.get())
        self.entry.destroy()
        self.equation = self._type = self.value = None

    def tadd_entry_children(self):
        self.log()
        self.add_entry_children(self.equation.get(), self._type.get(), self.value.get())
        self.entry.destroy()
        self.equation = self._type = self.value = None

    def add_entry(self, key, _type, value, pre_selection=None):
        if pre_selection is None:
            tree_selection = self.tkTree.selection()
            if not tree_selection:
                if self.pklTreeRoot is None:
                    entry = PklTreeItem()
                    entry.setKey(key)
                    entry.setType(_type)
                    entry.setValue(value)
                    self.pklTreeRoot = entry
                    entry_id = id(entry)
                    self.pklTreePointer[entry_id] = entry
                    self.tkTree.insert('', '0', entry_id, text=entry.key())
                    self.tkTree.item(entry_id, values=(entry.type(), entry.value()))

            for item in tree_selection:
                selection = self.lookup(item)
                entry = PklTreeItem(selection)
                entry.Parent.Children.insert(0, entry)
                entry.setKey(key)
                entry.setType(_type)
                entry.setValue(value)
                entry_id = id(entry)
                self.pklTreePointer[entry_id] = entry
                self.tkTree.insert(item, '0', entry_id, text=entry.key())
                self.tkTree.item(entry_id, values=(entry.type(), entry.value()))
        else:
            pre_selection_id = id(pre_selection)
            entry = PklTreeItem(pre_selection)
            entry.Parent.Children.insert(0, entry)
            entry.setKey(key)
            entry.setType(_type)
            entry.setValue(value)
            entry_id = id(entry)
            self.pklTreePointer[entry_id] = entry
            self.tkTree.insert(pre_selection_id, '0', entry_id, text=entry.key())
            self.tkTree.item(entry_id, values=(entry.type(), entry.value()))

    def add_entry_children(self, key, _type, value):
        tree_selection = self.tkTree.selection()[0]
        selection = self.lookup(tree_selection)
        for children in selection.Children:
            self.add_entry(key, _type, value, children)

    def selective_select_dialog(self, event):
        self.popup = Toplevel(root)
        style = ttk.Style()
        style.theme_use('clam')
        self.popup.geometry('175x75+600+50')
        Label(self.popup, text='Key:').grid(row=0, column=0, columnspan=2)
        self.equation = Entry(self.popup)
        self.equation.grid(row=1, column=0, columnspan=2)
        Button(self.popup, text='Select', command=self.selective_select, width=10).grid(row=2, column=0)
        Button(self.popup, text='Select and see', command=lambda: self.selective_select(see=True),
               width=10).grid(row=2, column=1)

    def selective_select(self, see=False):
        tree_selection = self.tkTree.selection()
        for item in tree_selection:
            self.tkTree.selection_remove(item)
            selection = self.lookup(item)
            selections = selection.selective_search(self.equation.get())
            for _item in selections:
                _item_id = id(_item)
                self.tkTree.selection_add(_item_id)
                if see:
                    self.tkTree.see(_item_id)
        self.popup.destroy()

    def special_edit_dialog(self, event):
        self.popup = Toplevel(root)
        style = ttk.Style()
        style.theme_use('clam')
        self.popup.geometry('175x75+600+50')
        Label(self.popup, text='Equation:').grid(row=0, column=0)
        self.equation = Entry(self.popup)
        self.equation.grid(row=1, column=0)
        Button(self.popup, text='OK', command=self.special_edit, width=10).grid(row=2, column=0)

    def special_edit(self):
        tree_selection = self.tkTree.selection()
        for x, item in reversed(list(enumerate(tree_selection))):
            selection = self.lookup(tree_selection[x])
            value = str(eval(self.equation.get()))
            selection.setValue(value)
            self.tkTree.set(tree_selection[x], '#2', value)
        self.popup.destroy()

    def return_pointer_mapping(self, old_pklTreeRoot, new_pklTreeRoot):
        return self.rpm_helper(old_pklTreeRoot, new_pklTreeRoot)

    def rpm_helper(self, old_pklItem, new_pklItem):
        pointer = {}
        pointer[id(old_pklItem)] = id(new_pklItem)
        for old_item, new_item in zip(old_pklItem.Children, new_pklItem.Children):
            pointer.update(self.rpm_helper(old_item, new_item))
        return pointer

    def pklTree_copy(self):
        try:
            pklTreeRoot_copy = copy.deepcopy(self.pklTreeRoot)
            pklTreePointer_copy = copy.deepcopy(self.pklTreePointer)
            pointer_mapping = self.return_pointer_mapping(self.pklTreeRoot, pklTreeRoot_copy)
            return [pklTreeRoot_copy, pklTreePointer_copy, pointer_mapping]
        except:
            return [None, {}, {}]

    def log(self, log=None):
        if log is None:
            _copy = self.pklTree_copy()
            self.logs.append(_copy)
            self.pointer_mapping = _copy[2]
        else:
            self.logs.append(log)
            self.pointer_mapping = log[2]
        if len(self.logs) > 20:
            del self.logs[0]

    def rlog(self, log=None):
        if log is None:
            _copy = self.pklTree_copy()
            self.rlogs.append(_copy)
            self.pointer_mapping = _copy[2]
        else:
            self.rlogs.append(log)
            self.pointer_mapping = log[2]
        if len(self.rlogs) > 20:
            del self.rlogs[0]

    def undo(self, event):
        if self.logs:
            curr_state = self.pklTree_copy()
            log = self.logs.pop()
            self.pklTreeRoot = log[0]
            self.pklTreePointer = log[1]
            self.refresh()
            self.rlog(curr_state)

    def redo(self, event):
        if self.rlogs:
            curr_state = self.pklTree_copy()
            log = self.rlogs.pop()
            self.pklTreeRoot = log[0]
            self.pklTreePointer = log[1]
            self.refresh()
            self.log(curr_state)

    def move(self, event):
        hover = self.tkTree.identify_row(self.tkTree.winfo_pointerxy()[1] - self.tkTree.winfo_rooty())
        if hover != '':
            tree_selection = self.tkTree.selection()
            hover_index = self.lookup(hover).row()
            hover_parent = self.tkTree.parent(hover)
            pkl_hover_parent = self.lookup(hover_parent)
            for item in tree_selection:
                if hover_parent != '':
                    pkl_item = self.lookup(item)
                    pkl_item_parent = pkl_item.Parent
                    if pkl_item_parent == self.lookup(hover_parent):
                        pkl_item_parent.Children.insert(hover_index, pkl_item_parent.Children.pop(pkl_item.row()))
                    else:
                        pkl_hover_parent.Children.insert(hover_index, pkl_item_parent.Children.pop(pkl_item.row()))
                        pkl_item.Parent = pkl_hover_parent

                self.tkTree.move(item, hover_parent, hover_index)

    def rrefresh(self, event):
        self.refresh()

    def refresh(self):
        state = self.get_openstate(self.pointer_mapping)
        self.tkTree.delete(*self.tkTree.get_children())
        self.load(self.pklTreeRoot)
        self.restore_openstate(state)

    def get_openstate(self, id_mapping):
        state = {}
        for ids in id_mapping:
            try:
                state[id_mapping[ids]] = self.tkTree.item(ids, 'open')
            except:
                pass
        return state

    def restore_openstate(self, state):
        for ids in state:
            try:
                self.tkTree.item(ids, open=state[ids])
            except:
                pass

    def ctrlc(self):
        self.copy('')

    def ctrlv(self):
        self.paste('')

    def ctrlx(self):
        self.delete('')

    def ctrlz(self):
        self.undo('')

    def ctrlsz(self):
        self.redo('')


if __name__ == '__main__':
    root = Tk()
    root.geometry('900x800+600+50')

    tktree = TKTree(root)

    root.mainloop()
