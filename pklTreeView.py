import sys, pickle, tkinter, os, ctypes
from tkinter import *
from tkinter import filedialog
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


class TKTree:

    def __init__(self, root: Tk, pklTreeRoot=None):
        self.root = root

        self.pklTreeRoot = pklTreeRoot

        self.pklTreePointer = {id(pklTreeRoot): pklTreeRoot}

        self.tkTree = ttk.Treeview(root)
        self.load(pklTreeRoot)

        self.setup_UI(root)

    def setup_UI(self, root: Tk):
        menubar = Menu(root)

        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.open_file)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Convert")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        editmenu = Menu(menubar, tearoff=0)
        editmenu.add_command(label="Cut")
        editmenu.add_command(label="Copy")
        editmenu.add_command(label="Paste")
        editmenu.add_command(label='Hard refresh', command=self.hrefresh)
        menubar.add_cascade(label="Edit", menu=editmenu)

        helpmenu = Menu(menubar, tearoff=0)
        helpmenu.add_command(label="About")
        menubar.add_cascade(label="Help", menu=helpmenu)

        root.config(menu=menubar)

        edit = Button(root, text='Edit', command=self.edit)
        edit.pack()

        self.entry = Entry(root)
        self.entry.pack()

        self.tkTree.config(columns=('type', 'value'))
        self.tkTree.heading('#0', text='key')
        self.tkTree.heading('type', text='type')
        self.tkTree.heading('value', text='value')
        self.tkTree.pack()

    def open_file(self):
        file = filedialog.askopenfilename(initialdir=root_path, title='Select file',
                                          filetypes=(('PolyPickle Files', '*.plypk'), ('All files', '*.*')))
        name = os.path.splitext(os.path.basename(file))[0]
        with open(file, 'rb') as pkl:
            item = PklTreeItem().load(pickle.load(pkl), self.pklTreeRoot, name)
            self.load(item, self.pklTreeRoot)
            self.pklTreeRoot.appendChild(item)

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

    def edit(self):
        tree_selection = self.tkTree.selection()[0]
        selection_id = int(tree_selection)
        selection = self.pklTreePointer[selection_id]
        try:
            if selection.type() != 'None':
                selection.setValue(self.entry.get())
                self.tkTree.item(tree_selection, values=(selection.type(), selection.value()))

        except:
            pass

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
        converted = self.pklTreeRoot.convert()
        with open('{}.dbpk'.format(file), 'wb') as output:
            pickle.dump(converted, output, pickle.HIGHEST_PROTOCOL)



root = Tk()

mainPklTree = PklTreeItem()
mainPklTree.setKey('main')
mainPklTree.setType('list')
mainPklTree.setValue('None')

tktree = TKTree(root, mainPklTree)


root.mainloop()
