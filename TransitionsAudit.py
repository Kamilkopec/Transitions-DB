import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def input_dir():

    # ask the user to input the file to be audited

    root = tk.Tk()
    root.state('withdrawn')
    messagebox.askokcancel('Welcome', 'Select the transitions csv file.\n'
                                      'Important: it needs to have Record ID# column.')

    root.filename = filedialog.askopenfilename(title="Select file",
                                               filetypes=(("csv files", "*.csv"), ("all files", "*.*")),
                                               parent=root)
    print('File directory created.\n\n')
    return root.filename


def get_columns(file_dir):
    # Returns a list of column names from Transitions file cleaned from caret returns '\r', '\n'
    # Caret returns are the main issue when people are copy/pasting data to QuickBase from other sources and the
    # formatting is copied alongside the data.
    # List is used with pandas to iterate over each column in a more controllable maner.
    # It's also used to generate filed of Record ID + Column name, needed for importing in QuickBase.
    print('Getting column list...')

    columnList = []
    with open(file_dir, 'r') as fieldNames:
        # first row has column names
        fieldNames = fieldNames.readlines()[0]
        fieldsList = fieldNames.split(',')

    for name in fieldsList:
        # removing caret returns
        name = name.strip('\r')
        name = name.strip('\n')
        columnList.append(name)

    print('{} columns found'.format(len(columnList)))
    return columnList


def iter_dataframe(file_dir):
    print('Creating iteration')
    # returns a pandas dataframe iterator which is a id + series pairs
    # series represent each column with data which then can be accessed like a dictionary

    transitionsFile = pd.read_csv(file_dir, header=0, encoding='windows-1252')
    # 1252 is the standard encoding for transition file
    columnIter = transitionsFile.iterrows()

    print('Iterator ready')
    return columnIter


def err_caretreturn(columnIter):
    print('Checking for caret errors')
    # returns a list of corrected caret returns and ',' in field names

    errorList = []
    correct_caretList = []
    column_range = range(0, len(columnList))

    for id, series in columnIter:
        print('Checking {} row.'.format(series['Record ID#']))
        for k in column_range:
            if '\r' in str(series[k]):
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))
            elif '\n' in str(series[k]):
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))
            elif ',' in str(series[k]):
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))

    print('Found {} caret or \',\' errors'.format(len(errorList)))

    print('Starting correction...')
    for error in errorList:
        error = error.strip('\n')
        error = error.strip('\r')
        error = error.replace('\r\n','')
        error = error.replace('\n\r','')
        error = error.replace(',', '')
        correct_caretList.append(error)

    print('Correction done...')
    return correct_caretList


def out_dir():
    out_dir = filedialog.askdirectory(title='Choose a folder for the output files')
    return out_dir


def out_files(out_dir, correctedList):
    print('Creating output files')
    # generating files with corrected errors files are created with Record ID# +

    file_columns = set([])

    for correction in correctedList:
        record_id, column_correction, item = correction.split('/')
        file_columns.add(column_correction)

    for column in file_columns:
        with open(out_dir + '/' + str(column) + '.csv', 'a+') as file:
            file.writelines('Record ID#,' + column + '\n')
            for correction in correctedList:
                record_id, column_correction, item = correction.split('/')
                if column == column_correction:
                    file.writelines(record_id + ',' + item + '\n')
    print('{} files created'.format(len(file_columns)))


print('Started... please wait')
file_dir = input_dir()
columnList = get_columns(file_dir)
columnIter = iter_dataframe(file_dir)
final_caretList = err_caretreturn(columnIter)
direc = out_dir()
out_files(direc,final_caretList)

input('Enter any key to terminate')

