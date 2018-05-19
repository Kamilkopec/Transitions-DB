import pandas as pd
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox


def input_dir():

    """
    Get transitions file dir from the user input.
    Displays a note that the file needs to contain Record ID# column which is the primery key of the QB database.
    """

    root = tk.Tk()
    root.state('withdrawn')
    messagebox.showinfo('Welcome', 'Select the transitions csv file.\nImportant: it needs to have Record ID# column.')
    root.filename = filedialog.askopenfilename(
        title="Select file", filetypes=(("csv files", "*.csv"), ('all files', "*.*")), parent=root)

    print('File directory created.\n\n')
    return root.filename


def get_columns(file_dir):

    """
    Returns a list of column names from Transitions file cleaned from caret returns '\r', '\n'
    Caret returns are the main issue when people are copy/pasting data to QuickBase from other sources and the
    formatting is copied alongside the data.
    List is used with pandas to iterate over each column in a more controllable manner.
    It's also used to generate files of Record ID + Column name, needed for importing in QuickBase
    Columns can change with time therefore is important not to hard code the headers.

    """
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


def iter_dataframe(file_dir, columnList):

    """
    Returns a pandas DataFrame iterator which is a id + series pairs.
    Series represent each column with data which then can be accessed like a dictionary
    """

    print('Creating iteration')

    transitionsFile = pd.read_csv(file_dir, header=0, encoding='windows-1252')
    # 1252 is the standard encoding for transition file downloaded from quickbase
    # UTF-8 creases the pandas read_csv function.

    columnIter = transitionsFile.iterrows()

    print('Iterator ready')
    return columnIter


def err_caretreturn(columnIter, columnList):

    """
    Iterates through all the filed in the iteration and check for '\r', '\n', or ','.
    Returns a corrected list

    """

    print('Checking for caret errors')
    # returns a list of corrected caret returns and ',' in field names

    errorList = []
    correct_caretList = []
    column_range = range(0, len(columnList))

    for id, series in columnIter:
        print('Checking {} record id#.'.format(series['Record ID#']))
        for k in column_range:
            if '\r' in str(series[k]):
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))
            elif '\n' in str(series[k]):
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))
            elif ',' in str(series[k]) and len(str(series[k])) >= 4 and str(columnList[k]) not in ['FILLING', 'ITEM PER PALLET']:
                errorList.append(str(series["Record ID#"]) + '/' + columnList[k] + '/' + str(series[k]))

    print('Found {} caret or \',\' errors'.format(len(errorList)))

    if len(errorList) > 0:

        print('Starting correction...')
        for error in errorList:
            error = error.strip('\n')
            error = error.strip('\r')
            error = error.replace('\r\n','')
            error = error.replace('\n\r','')
            error = error.replace(',', '')
            correct_caretList.append(error)

        print('Correction done...')
        print(correct_caretList)
        return correct_caretList


def out_dir():
    messagebox.showinfo('Output Folder', 'Please select the folder to save the corrected files.')
    out_dir = filedialog.askdirectory(title='Choose a folder for the output files')
    return out_dir


def out_files(out_dir, correctedList):
    print('Creating output files')
    # generating files with corrected errors files are created with Record ID#

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


def main():

    print('Started... please wait')
    file_dir = input_dir()
    columnList = get_columns(file_dir)
    columnIter = iter_dataframe(file_dir, columnList)
    final_caretList = err_caretreturn(columnIter, columnList)

    if final_caretList == None:
        messagebox.showinfo('Errors INFO', 'No errors found')
    else:
        direc = out_dir()
        out_files(direc,final_caretList)

    input('Enter any key to terminate')


if __name__ == '__main__':
    main()
