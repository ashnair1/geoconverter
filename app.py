import os
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk

# Root window
root = tk.Tk()
root.title("Converter")
root.resizable(True, False)
root.geometry("550x250")


tab_parent = ttk.Notebook(root)

tab1 = ttk.Frame(tab_parent)
tab2 = ttk.Frame(tab_parent)
tab3 = ttk.Frame(root)
tab3.pack(side="bottom", fill="both", expand=True)

tab_parent.add(tab1, text="File")
tab_parent.add(tab2, text="Directory")

tab_parent.pack(expand=1, fill="both")

ifilepath = tk.StringVar(tab1)
ofilepath = tk.StringVar(tab1)

ifolderpath = tk.StringVar(tab2)
ofolderpath = tk.StringVar(tab2)


# Dropdown menu options
bitres_opts = [
    "Byte",
    "UInt8",
    "UInt16",
    "UInt32",
    "Int16",
    "Int32",
    "Float32",
    "Float64",
]

outfmt_opts = [
    "COG",
    "GTiff",
    "JPEG2000",
    "IMG",
]

bitclicked = tk.StringVar(value="Byte")
outclicked = tk.StringVar(value="COG")

# Create Label
label = tk.Label(tab3, text="Options")
label.pack(side="top")

bitlbl = tk.Label(tab3, text="Dtype")
bitlbl.place(relx=0.4, rely=0.3, anchor=tk.CENTER)

fmtlbl = tk.Label(tab3, text="Format")
fmtlbl.place(relx=0.6, rely=0.3, anchor=tk.CENTER)

# Create Dropdown menu
bitopts = tk.OptionMenu(tab3, bitclicked, *bitres_opts)
bitopts.place(relx=0.4, rely=0.6, anchor=tk.CENTER)

outfmtopts = tk.OptionMenu(tab3, outclicked, *outfmt_opts)
outfmtopts.place(relx=0.6, rely=0.6, anchor=tk.CENTER)


ifilename = tk.Entry(tab1, textvariable=ifilepath)
ifilename.update()
ifilename.focus_set()
ifilename.place(y=10, x=10, relwidth=0.70, height=20)
# ifilename.pack(anchor='w', padx=10, pady=10)

ofilename = tk.Entry(tab1, textvariable=ofilepath)
ofilename.update()
ofilename.focus_set()
ofilename.place(y=50, x=10, relwidth=0.70, height=20)
# ifilename.pack(anchor='w', padx=10, pady=10)

ifoldername = tk.Entry(tab2, textvariable=ifolderpath)
ifoldername.update()
ifoldername.focus_set()
ifoldername.place(y=10, x=10, relwidth=0.70, height=20)
# ifoldername.pack(anchor='w', padx=10, pady=10)

ofoldername = tk.Entry(tab2, textvariable=ofolderpath)
ofoldername.update()
ofoldername.focus_set()
ofoldername.place(y=50, x=10, relwidth=0.70, height=20)
# ifoldername.pack(anchor='w', padx=10, pady=10)


def open_input_file():
    # file type
    filetypes = (
        ("TIF files", "*.tif .tiff .TIF .TIFF"),
        ("IMG files", "*.img .IMG"),
        ("JPEG2000 files", "*.jp2 .JP2"),
        ("All files", "*.*"),
    )
    # show the open file dialog
    file = fd.askopenfilename(filetypes=filetypes)
    if file:
        filepath = os.path.abspath(file)
        ifilepath.set(filepath)
    # Label(root, text="Input File: " + str(filepath), font=('Aerial 11')).pack()


def open_input_directory():
    dirs = fd.askdirectory()
    if dirs:
        folderpath = os.path.abspath(dirs)
        ifolderpath.set(folderpath)
    # Label(root, text="Input File: " + str(filepath), font=('Aerial 11')).pack()


def open_output_file():
    # file type
    filetypes = (
        ("TIF files", "*.tif .tiff .TIF .TIFF"),
        ("IMG files", "*.img .IMG"),
        ("JPEG2000 files", "*.jp2 .JP2"),
        ("All files", "*.*"),
    )
    # show the open file dialog
    file = fd.asksaveasfilename(filetypes=filetypes, defaultextension=".tif")
    if file:
        filepath = os.path.abspath(file)
        ofilepath.set(filepath)
    # Label(root, text="Input File: " + str(filepath), font=('Aerial 11')).pack()


def open_output_directory():
    dirs = fd.askdirectory()
    if dirs:
        folderpath = os.path.abspath(dirs)
        ofolderpath.set(folderpath)
    # Label(root, text="Input File: " + str(filepath), font=('Aerial 11')).pack()


def convert_file():
    infile = ifilepath.get()
    outfile = ofilepath.get()
    dtype = bitclicked.get()
    outfmt = outclicked.get()
    print(infile)
    print(outfile)
    print(outfmt)
    print(dtype)
    from gdal_extras.gdal_convert import cli_entrypoint
    cli_entrypoint(infile, outfile, outfmt, dtype)
    #root.destroy()



def convert_directory():
    infolder = ifolderpath.get()
    outfolder = ofolderpath.get()
    dtype = bitclicked.get()
    outfmt = outclicked.get()
    print(infolder)
    print(outfolder)
    print(outfmt)
    print(dtype)


# open file button
open_file_button = ttk.Button(tab1, text="Input File", command=open_input_file)

# open folder button
open_folder_button = ttk.Button(
    tab2, text="Input Directory", command=open_input_directory
)

# open output file button
open_ofile_button = ttk.Button(tab1, text="Output File", command=open_output_file)

# open output file button
open_ofolder_button = ttk.Button(
    tab2, text="Output Directory", command=open_output_directory
)

convert_button1 = ttk.Button(tab1, text="Convert", command=convert_file)

convert_button2 = ttk.Button(tab2, text="Convert", command=convert_directory)

# open_file_button.grid(column=400, columnspan=10, row=1, padx=10, pady=10)
# open_folder_button.grid(column=10, row=2, padx=10, pady=10)
# open_file_button.place(relx=0.5, rely=0.4, anchor=tk.CENTER)
# open_folder_button.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
open_file_button.pack(anchor="e", padx=20, pady=10)
open_folder_button.pack(anchor="e", padx=20, pady=10)
open_ofile_button.pack(anchor="e", padx=20, pady=10)
open_ofolder_button.pack(anchor="e", padx=20, pady=10)

convert_button1.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
convert_button2.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

root.mainloop()
