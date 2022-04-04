import abc
import os
import subprocess
import sys
import tkinter as tk
import traceback
from tkinter import filedialog as fd
from tkinter import ttk
from tkinter.messagebox import showerror
from typing import Any, Tuple, Union

from geoconverter.gdal_convert import cli_entrypoint

if getattr(sys, "frozen", False):
    application_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    os.environ["PROJ_LIB"] = os.path.join(application_path, "proj")
    os.chdir(application_path)

WINDOW_SIZE = "550x300"

FILETYPES = (
    ("TIF files", "*.tif .tiff .TIF .TIFF"),
    ("IMG files", "*.img .IMG"),
    ("JPEG2000 files", "*.jp2 .JP2"),
    ("All files", "*.*"),
)

# TODO: Do we really need this mapping?
DRIVER_MAP = {"JPEG2000": "JP2OpenJPEG", "IMG": "HFA"}

STATUS_COLORS = {"Idle": "light gray", "Processing": "light green", "ERROR": "red"}


def showtraceback(widget: "DefaultTab", msg: str) -> None:
    """Display error traceback.

    Args:
        widget (DefaultTab): current widget
        msg (str): error message to be displayed.
    """
    root: Union[tk.Tk, tk.Toplevel] = widget.winfo_toplevel()
    errWindow = tk.Toplevel(root)
    errWindow.title("Traceback")

    # sets the geometry of toplevel
    errWindow.geometry("500x500")
    T = tk.Text(errWindow, height=100, width=500)
    T.pack()
    T.insert(tk.END, msg)
    T.configure(state="disabled")


class DefaultTab(ttk.Frame):
    def __init__(
        self, master: ttk.Notebook, io_callbacks: Tuple[Any, Any], **kwargs: Any
    ):
        if kwargs:
            super().__init__(master, **kwargs)
        else:
            super().__init__(master)

        self.ipath = tk.StringVar(self)
        self.opath = tk.StringVar(self)
        self.status = tk.StringVar(self, value="Idle")

        assert len(io_callbacks) == 2
        self.input_callback: Any = io_callbacks[0]
        self.output_callback: Any = io_callbacks[1]
        self.create_widgets()

    def open_input(self) -> None:
        if self.input_callback == fd.askopenfilename:
            _input = self.input_callback(filetypes=FILETYPES)
        else:
            _input = self.input_callback()
        if _input:
            path = os.path.abspath(_input)
            self.ipath.set(path)

    def open_output(self) -> None:
        if self.output_callback == fd.asksaveasfilename:
            _output = self.output_callback(filetypes=FILETYPES)
        else:
            _output = self.output_callback()
        if _output:
            path = os.path.abspath(_output)
            self.opath.set(path)

    def change_status(self, status_msg: str) -> None:
        self.status.set(status_msg)
        self.statusval.config(text=status_msg, bg=STATUS_COLORS[status_msg])
        self.update()

    def create_widgets(self) -> None:

        statuslbl = tk.Label(self, text="Status:")
        statuslbl.place(relx=0.7, rely=0.7, anchor="e")
        self.statusval = tk.Label(self, textvariable=self.status)
        self.statusval.config(bg=STATUS_COLORS[self.status.get()])
        self.statusval.place(relx=0.85, rely=0.7, anchor="e")

        inputpath = tk.Entry(self, textvariable=self.ipath)
        inputpath.update()
        inputpath.focus_set()
        inputpath.place(y=10, x=10, relwidth=0.70, height=20)

        outputpath = tk.Entry(self, textvariable=self.opath)
        outputpath.update()
        outputpath.focus_set()
        outputpath.place(y=50, x=10, relwidth=0.70, height=20)

        # Buttons
        open_input_button = ttk.Button(self, text="Input", command=self.open_input)
        open_output_button = ttk.Button(self, text="Output", command=self.open_output)
        convert_button = ttk.Button(self, text="Convert", command=self.convert)

        open_input_button.pack(anchor="e", padx=20, pady=10)
        open_output_button.pack(anchor="e", padx=20, pady=10)
        convert_button.place(relx=0.3, rely=0.7, anchor=tk.CENTER)

    @abc.abstractmethod
    def convert(self) -> None:
        pass


class NotebookTab(DefaultTab):
    def __init__(
        self,
        master: ttk.Notebook,
        io_callbacks: Tuple[Any, Any],
        dtype: tk.StringVar,
        format: tk.StringVar,
        contrast: tk.IntVar,
        lower: tk.DoubleVar,
        upper: tk.DoubleVar,
        **kwargs: Any,
    ) -> None:
        self.dtype = dtype
        self.format = format
        self.contrast = contrast
        self.low = lower
        self.high = upper
        if kwargs:
            super().__init__(master, io_callbacks, **kwargs)
        else:
            super().__init__(master, io_callbacks)

    def convert(self) -> None:
        inpath = self.ipath.get()
        outpath = self.opath.get()

        dtype = self.dtype.get()
        outfmt = self.format.get()
        do_contrast = bool(self.contrast.get())
        lower = self.low.get()
        upper = self.high.get()
        assert outfmt not in {"Terrain", "Mesh"}
        if outfmt in DRIVER_MAP:
            outfmt = DRIVER_MAP[outfmt]

        self.change_status("Processing")

        try:
            cli_entrypoint(inpath, outpath, outfmt, dtype, do_contrast, lower, upper)
            self.change_status("Idle")
            self.ipath.set("")
            self.opath.set("")
        except Exception:
            self.change_status("ERROR")
            showerror(
                title="Error",
                message="An unexpected error occurred."
                "Close window or press OK to view traceback",
            )
            showtraceback(self, msg=traceback.format_exc())
            raise


class DEMTab(DefaultTab):
    def __init__(
        self, master: ttk.Notebook, io_callbacks: Tuple[Any, Any], format: tk.StringVar
    ) -> None:
        super().__init__(master, io_callbacks)
        self.format = format

    def convert(self) -> None:
        inpath = self.ipath.get()
        outpath = self.opath.get()
        outfmt = self.format.get()
        if outfmt in DRIVER_MAP:
            outfmt = DRIVER_MAP[outfmt]
        self.change_status("Processing")

        try:
            subprocess.Popen(
                ["ctb-tile", "-C", "-f", outfmt, "-o", outpath, inpath]
            ).wait()
            subprocess.Popen(["ctb-tile", "-C", "-l", "-o", outpath, inpath]).wait()
            self.change_status("Idle")
            self.ipath.set("")
            self.opath.set("")
        except Exception:
            self.change_status("ERROR")
            showerror(
                title="Error",
                message="An unexpected error occurred."
                "Close window or press OK to view traceback",
            )
            showtraceback(self, msg=traceback.format_exc())
            raise


class OptionsTab(ttk.Frame):
    def __init__(self, master: tk.Tk, **kwargs: Any) -> None:
        if kwargs:
            super().__init__(master, **kwargs)
        else:
            super().__init__(master)

        # Set up options
        self.dtype = tk.StringVar(value="Native")
        self.format = tk.StringVar(value="Native")
        self.contrast = tk.IntVar(value=0)
        self.low = tk.DoubleVar(value=2.0)
        self.upper = tk.DoubleVar(value=98.0)

        self.create_widgets()

    def create_widgets(self) -> None:
        # Dropdown menu options
        bitres_opts = [
            "Native",
            "Byte",
            "UInt8",
            "UInt16",
            "UInt32",
            "Int16",
            "Int32",
            "Float32",
            "Float64",
        ]

        outfmt_opts = ["Native", "COG", "GTiff", "JPEG2000", "IMG", "Terrain", "Mesh"]
        # Create Label
        label = tk.Label(self, text="Options")
        label.pack(side="top")

        bitlbl = tk.Label(self, text="DType")
        bitlbl.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

        fmtlbl = tk.Label(self, text="Format")
        fmtlbl.place(relx=0.7, rely=0.35, anchor=tk.CENTER)

        self.lowerbox = tk.Text(self, height=1, width=2)
        self.lowerbox.place(relx=0.25, rely=0.6, anchor=tk.CENTER)

        self.upperbox = tk.Text(self, height=1, width=2)
        self.upperbox.place(relx=0.35, rely=0.6, anchor=tk.CENTER)

        self.lowerbox.insert(tk.END, str(self.low.get()))
        self.upperbox.insert(tk.END, str(self.upper.get()))

        self.lowerbox.configure(state="disabled")
        self.upperbox.configure(state="disabled")

        def lock_fields() -> None:
            if self.contrast.get():
                self.lowerbox.configure(state="normal")
                self.upperbox.configure(state="normal")
            else:
                self.lowerbox.configure(state="disabled")
                self.upperbox.configure(state="disabled")

        contrastlbl = tk.Checkbutton(
            self, text=" Enhancement", variable=self.contrast, command=lock_fields
        )
        contrastlbl.place(relx=0.3, rely=0.35, anchor=tk.CENTER)

        # Create Dropdown menu
        bitopts = tk.OptionMenu(self, self.dtype, *bitres_opts)
        bitopts.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

        outfmtopts = tk.OptionMenu(self, self.format, *outfmt_opts)
        outfmtopts.place(relx=0.7, rely=0.6, anchor=tk.CENTER)


def main() -> None:

    # Root window
    root = tk.Tk()
    root.title("Converter")
    root.resizable(True, True)
    root.geometry(WINDOW_SIZE)

    tab_parent = ttk.Notebook(root)

    # Create tabs
    opt_tab = OptionsTab(root)

    file_tab = NotebookTab(
        tab_parent,
        (fd.askopenfilename, fd.asksaveasfilename),
        opt_tab.dtype,
        opt_tab.format,
        opt_tab.contrast,
        opt_tab.low,
        opt_tab.upper,
    )
    dir_tab = NotebookTab(
        tab_parent,
        (fd.askdirectory, fd.askdirectory),
        opt_tab.dtype,
        opt_tab.format,
        opt_tab.contrast,
        opt_tab.low,
        opt_tab.upper,
    )

    dem_tab = DEMTab(tab_parent, (fd.askopenfilename, fd.askdirectory), opt_tab.format)

    tab_parent.add(file_tab, text="File")
    tab_parent.add(dir_tab, text="Directory")
    tab_parent.add(dem_tab, text="DEM")
    tab_parent.pack(expand=1, fill="both")
    opt_tab.pack(side="bottom", fill="both", expand=True, pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
