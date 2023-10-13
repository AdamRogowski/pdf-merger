import tkinter as tk
import os
import datetime
from tkinter import Label, Text, filedialog, ttk
from PyPDF2 import PdfReader, PdfWriter, PdfMerger

# list of pfditems (pdfReader, path)
listOfPDFs = []


def remove_from_list_by_id():
    try:
        index = get_selected_id_from_boxlist()
        del listOfPDFs[index]

        box_list.delete(index)

        if index == -1:
            pass
        elif box_list.size() < index+1:
            box_list.select_set(index-1)
        else:
            box_list.select_set(index)
        append_log("File successfully deleted")
    except IndexError:
        append_log("Error: No file is selected, action failed")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def remove_all_from_list():
    try:
        listOfPDFs.clear()
        box_list.delete(0, tk.END)
        append_log("All files successfully deleted")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def show_info_by_id():
    try:
        index = get_selected_id_from_boxlist()

        path = listOfPDFs[index][1]
        size = round(os.stat(path).st_size / (1024 * 1024), 2)
        pages = len(listOfPDFs[index][0].pages)
        info = "Path: {path}\nSize: {size} MB\nNumber of pages: {pages}".format(
            path=path, size=size, pages=pages)
        append_log(info)
    except IndexError:
        append_log("Error: No file is selected, action failed")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def append_log(message):
    ct = datetime.datetime.now()
    logs.insert(tk.END, ct.strftime('%H:%M:%S') + "\n" + message + "\n")
    logs.see("end")


def clear_log():
    logs.delete('1.0', tk.END)
    append_log("Logs cleared")


def show_list():
    output = "Uploaded pdf files:\nID  NAME\n"
    index = 0
    for pdf in listOfPDFs:
        output += ("{index}:  {name}\n".format(index=index,
                   name=os.path.basename(pdf[1])))
        index += 1
    append_log(
        output + "Total uploaded: {number}".format(number=len(listOfPDFs)))


def show_cwd():
    append_log(os.getcwd())


def change_dir():
    try:
        dirpath = filedialog.askdirectory()
        os.chdir(dirpath)
        append_log("cwd changed to: {0}".format(os.getcwd()))
    except FileNotFoundError:
        append_log("Error: Directory: {0} does not exist".format(dirpath))
    except NotADirectoryError:
        append_log("Error: {0} is not a directory".format(dirpath))
    except PermissionError:
        append_log(
            "Error: You do not have permissions to change to {0}".format(dirpath))
    except Exception as e:
        append_log(
            "An unexpected error occurred during changing working directory")


# no try, catch included in the function
def open_file(filepath):

    file = open(filepath, 'rb')
    pdf = PdfReader(file)

    pdfItem = (pdf, filepath)

    listOfPDFs.append(pdfItem)

    add_to_boxlist(filepath)
    box_list.select_clear(0, tk.END)
    box_list.select_set(0)


def upload_file():
    try:
        filepath = filedialog.askopenfilename()
        open_file(filepath)
        ##############
        append_log("Uploaded successfully")
    except FileNotFoundError:
        append_log("Error: File not found.")
    except PermissionError:
        append_log("Error: Permission denied.")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def upload_dir():
    try:
        dirpath = filedialog.askdirectory()
        count = 0
        for file in os.listdir(dirpath):
            if file.endswith(".pdf"):
                filepath = os.path.join(dirpath, file)
                open_file(filepath)
                count = count + 1
        append_log("pdfs uploaded from dir: {number}".format(number=count))
    except FileNotFoundError:
        append_log("Error: File not found.")
    except PermissionError:
        append_log("Error: Permission denied.")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def merge_from_list():
    try:
        if not listOfPDFs:
            raise IndexError
        merger = PdfMerger()
        for pdf in listOfPDFs:
            merger.append(pdf[0])

        with open(os.getcwd() + '/MergedFiles.pdf', 'wb') as pdfOutputFile:
            merger.write(pdfOutputFile)
        # print("Merged successfully")
        append_log("Merged succesfully")
    except IndexError:
        append_log("Error: No pdf file to be merged")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def split_pdf_pages():
    # Open the PDF file
    try:
        index = get_selected_id_from_boxlist()
        pdf_reader = listOfPDFs[index][0]

        # Iterate over each page in the PDF file
        for page_num in range(len(pdf_reader.pages)):
            # Create a new PDF writer object
            pdf_writer = PdfWriter()

            # Add the current page to the writer
            pdf_writer.add_page(pdf_reader.pages[page_num])

            # Build the output PDF file path
            # file_name = os.path.splitext(os.path.basename(pdf_path))[0]
            basename = os.path.basename(
                listOfPDFs[index][1])
            output_path = os.path.join(
                os.getcwd(), f'{basename[:-4]}_page_{page_num + 1}.pdf')

            # Write the output PDF file
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
        append_log("Splitted successfully")
    except IndexError:
        append_log("Error: No pdf file to be splitted")
    except Exception as e:
        append_log(f"An unexpected error occurred: {e}")


def validate_entry(text):
    return text.isdecimal()


def add_to_boxlist(path):
    box_list.insert(tk.END, os.path.basename(path))


def update_boxlist():
    box_list.delete(0, tk.END)
    for file in listOfPDFs:
        box_list.insert(tk.END, os.path.basename(file[1]))


def get_selected_id_from_boxlist():
    if box_list.size() == 0:
        return -1
    return box_list.curselection()[0]


root = tk.Tk()
root.title("PDF Merger")
root.geometry("400x600")
tabControl = ttk.Notebook(root)

tab1 = ttk.Frame(tabControl)
tab2 = ttk.Frame(tabControl)

tabControl.add(tab1, text='Upload')
tabControl.add(tab2, text='Actions')
tabControl.pack(expand=1, fill="both")


upload_button = tk.Button(tab1, text="Upload PDF",
                          command=upload_file).place(x=10, y=10, width=80)

upload_dir_button = tk.Button(tab1, text="Upload dir",
                              command=upload_dir).place(x=10, y=44, width=80)

remove_by_id_button = tk.Button(tab1, text="Delete",
                                command=remove_from_list_by_id).place(x=100, y=10, width=80)


remove_all_button = tk.Button(tab1, text="Del all",
                              command=remove_all_from_list).place(x=100, y=44, width=80)

show_info_button = tk.Button(tab1, text="Show info",
                             command=show_info_by_id).place(x=190, y=10, width=80)

box_list = tk.Listbox(tab1)
box_list.place(x=10, y=80, width=182, height=200)

boxlistscrolly = tk.Scrollbar(tab1, orient="vertical", command=box_list.yview)
box_list.configure(yscrollcommand=boxlistscrolly.set)
boxlistscrolly.place(x=192, y=81, height=198)

boxlistscrollx = tk.Scrollbar(
    tab1, orient="horizontal", command=box_list.xview)
box_list.configure(xscrollcommand=boxlistscrollx.set)
boxlistscrollx.place(x=10, y=281, width=182)


merge_button = tk.Button(tab2, text="Merge PDF",
                         command=merge_from_list).place(x=10, y=10, width=80)

split_button = tk.Button(tab2, text="Split PDF",
                         command=split_pdf_pages).place(x=10, y=44, width=80)


showcwd_button = tk.Button(root, text="Show cwd", background='#C0C0C0', activebackground='#C0C0C0',
                           command=show_cwd).place(x=11, y=340, width=80)

chdir_button = tk.Button(root, text="Chdir", background='#C0C0C0', activebackground='#C0C0C0',
                         command=change_dir).place(x=101, y=340, width=80)

show_list_button = tk.Button(root, text="Show pdfs", background='#C0C0C0', activebackground='#C0C0C0',
                             command=show_list).place(x=191, y=340, width=80)

clearlog_button = tk.Button(root, text="Clear", background='#C0C0C0', activebackground='#C0C0C0',
                            command=clear_log).place(x=281, y=340, width=80)


logs = Text(root)
logs.place(x=15, y=380, width=362, height=200)

scrollb = tk.Scrollbar(root, orient="vertical", command=logs.yview)
logs.configure(yscrollcommand=scrollb.set)
scrollb.place(x=367, y=381, height=198)

logs.insert(tk.END, "Logs\n")


root.mainloop()
