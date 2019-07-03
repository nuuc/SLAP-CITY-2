import sys, pickle, tkinter, os, copy
from tkinter import *
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import ttk

root_path = os.path.dirname(os.path.realpath(__file__))

output_dict = {}

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
        self.load(pklTreeRoot)

        self.setup_UI(root)

    def setup_UI(self, root: Tk):
        menubar = Menu(root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_separator()
        filemenu.add_command(label='Hard refresh', command=self.hrefresh)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Copy", accelerator='Control+C', command=self.ctrlc)
        self.tkTree.bind('<Control-c>', self.copy)
        editmenu.add_command(label="Paste", accelerator='Control+V', command=self.ctrlv)
        self.tkTree.bind('<Control-v>', self.paste)
        editmenu.add_command(label="Delete", accelerator='Control+V', command=self.ctrlx)
        self.tkTree.bind('<Control-x>', self.delete)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        root.config(menu=menubar)

        self.tkTree.config(columns=('type', 'value'))
        self.tkTree.heading('#0', text='key')
        self.tkTree.heading('type', text='type')
        self.tkTree.heading('value', text='value')
        self.tkTree.bind('<B1-Motion>', self.move)
        self.tkTree.bind('<Double-Button-1>', self.edit)
        self.tkTree.bind('<Double-Button-3>', self.multi_edit)
        self.tkTree.grid(row=0, column=0)


    def open_file(self):
        file = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(('PolyPickle Files', '*.plypk'), ('All files', '*.*')))
        name = os.path.splitext(os.path.basename(file))[0]

        popup = Toplevel()
        popup.wm_title('Progress')

        progressbar = ttk.Progressbar(popup, orient='horizontal', length=100, mode='indeterminate')
        progressbar.pack()

        with open(file, 'rb') as pkl:
            item = PklTreeItem().load(pickle.load(pkl), self.pklTreeRoot, name)
            self.load(item, self.pklTreeRoot)
            self.pklTreeRoot.appendChild(item)

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
        column = self.tkTree.identify_column(self.tkTree.winfo_pointerxy()[0] - self.tkTree.winfo_rootx())
        tree_selection = self.tkTree.selection()[0]
        selection = self.lookup(tree_selection)
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
        tree_selection = self.tkTree.selection()
        value = simpledialog.askstring('Edit', 'Edit Value:')
        for item in tree_selection:
            selection = self.lookup(item)
            selection.setValue(value)
            self.tkTree.set(item, '#2', value)

    def ctrlc(self):
        self.copy('')

    def ctrlv(self):
        self.paste('')

    def ctrlx(self):
        self.delete('')

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
            tree_selection = self.tkTree.selection()[0]
            for item in self.copied:
                pkl_item = self.lookup(item)
                self.load(pkl_item, self.lookup(tree_selection))
        except:
            pass

    def delete(self, event):
        tree_selection = self.tkTree.selection()
        for item in tree_selection:
            pkl_item = self.lookup(item)
            pkl_item.Parent.Children.remove(pkl_item)
            del pkl_item
            self.tkTree.delete(item)

    def move(self, event):
        hover = self.tkTree.identify_row(self.tkTree.winfo_pointerxy()[1] - self.tkTree.winfo_rooty())
        if hover != '':
            tree_selection = self.tkTree.selection()
            pkl_hover = self.lookup(hover)
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

    def hrefresh(self):
        for children in self.pklTreeRoot.Children:
            self.tkTree.delete(id(children))
            self.load(children, self.pklTreeRoot)

    def save(self):
        file = filedialog.asksaveasfilename(initialdir=root_path,
                                            title="Select file",
                                            filetypes=(("Database pickle files", "*.dbpkl"),
                                                        ("All files", "*.*")))
        if file == '':
            return
        popup = Toplevel()
        popup.wm_title('Progress')

        progressbar = ttk.Progressbar(popup, orient='horizontal', length=100, mode='indeterminate')
        progressbar.pack()

        converted = self.pklTreeRoot.convert()
        with open('{}.dbpk'.format(file), 'wb') as output:
            pickle.dump(converted, output, pickle.HIGHEST_PROTOCOL)

        popup.destroy()



root = Tk()
root.geometry('600x800+600+50')

mainPklTree = PklTreeItem()
mainPklTree.setKey('main')
mainPklTree.setType('dict')
mainPklTree.setValue('None')

tktree = TKTree(root, mainPklTree)
with open('C:/Users/Tony/PycharmProjects/experimental branch v0.22/assets/jumpboitest.plypk', 'rb') as pkl:
    item = PklTreeItem().load(pickle.load(pkl), tktree.pklTreeRoot, 'jumpboitest')
    tktree.load(item, tktree.pklTreeRoot)
    tktree.pklTreeRoot.appendChild(item)


root.mainloop()
