"""
Module used in grading EGR260 essays

Directory structure:

essayN
--> essays
--> ungraded_sheets
--> graded_sheets

Grading workflow:
1.) Download all documents as zip file to new directory. Will include all submissions (as pdf, doc or docx) and a txt file describing the submitter name, puid, and other extraneous details.
2.) Run generate_comment_files() using customized file content to automatically generate a file in 'comments' subfolder for each submission that includes the student's scores in various rubric categories, the total score, and comments 
   **ensure global variable graded_lines represents the line numbers that hold individual grades, and that total_grade_line represents the line on which the total grade is indicated**
   **ensure resulting txt files are printable (grade lines do not run off page)**
3.) Print out all documents using:

find ./essays/ -regex '.*\.doc.*' -exec libreoffice -p {} \;
find ./essays/ -regex '.*\.pdf$' -exec lpr -o sides=two-sided-long-edge {} \;

4.) Grade printed documents and fill out ungraded form, running add_total_score_and_print() after each document is finished to print out an ordered stack of evaluations with the total score calculated
5.) Staple together documents with printed evaluation forms
6.) Download entire grade sheet from Blackboard as csv
7.) (optional) check grade distribution by running get_grade_distribution()
8.) Run set_grades() with the proper filename to set the student's grades, saving as finalgrades.csv
9.) Upload finalgrades.csv to Blackboard, confirming only the desired column has been edited
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import glob
import os
import subprocess

graded_lines = [4,5,7,8,10]
total_grade_line = 12

def generate_comment_files():
    """Generates comment/evaluation txt files that indicate a students grade and also include comments on writing"""
    count = 0
    for filename in glob.glob(os.path.join('./essays/', '*.txt')):
        with open(filename, 'r') as f:
            name = f.readline().strip()
            colon_loc = name.find(':')
            open_paren_loc = name.find('(')
            name = name[colon_loc+2:open_paren_loc-1]
            file_content = 'Grading for ' + name + ' EGR260 essay one:' + ('\n\n'
                                'Argument quality:\n'
                                '\t Added personal opinion/elaborated on points (out of 1.5): \n'
                                '\t Arguments are logical and follow from presented material (out of 2.5): \n'
                                'Presentation effectiveness:\n'
                                '\t Use of outside material (quotes, citations) (out of 3.0): \n'
                                '\t Flow of essay (out of 1.5): \n'
                                'Mechanics:\n'
                                '\t Grammar, spelling (out of 1.5): \n\n'
                                'Total (out of 10.0):\n\n'
                                'Comments:\n')
            with open('./comments/' + name + '.txt', 'w') as cf:
                cf.write(file_content)
        count += 1
    print count, 'files processed'


def add_total_score_and_print(filename):
    """Calculates total grade and prints to klab"""
    total_grade = 0
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()
    for i in [k-1 for k in graded_lines]:
        total_grade += float(lines[i][lines[i].find(':')+1:])

    lines[total_grade_line-1] = lines[total_grade_line-1][:lines[total_grade_line-1].find(':')+1] + ' %1.2f' % total_grade + '\n'

    graded_file = './graded/' + filename
    with open(graded_file, 'w') as f:
        f.writelines(lines)

    print filename[:filename.find('.')-1], 'grade:', total_grade
    print 'Comments:', lines[-1]

    subprocess.call(['lpr', graded_file])

def get_grade_distribution():
    """Pulls out final grades from txt files and plots in histogram"""
    grades = []
    for filename in glob.glob(os.path.join('./graded/', '*.txt')):
        with open(filename, 'r') as f:
            line = None
            for i in range(12):
                line = f.readline()
            grades.append(float(line[line.find(':')+1:]))
            if grades[-1] == 6.5:
                print filename

    print 'Avg:', np.average(grades)
    print 'Std dev:', np.std(grades)
    unique_grades, counts = np.unique(grades, return_counts=True)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.hist(grades, bins=6)
        
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.scatter(unique_grades, counts)
    plt.show()


def set_grades(full_grade_sheet_csv):
    """Sets grades based on text files"""
    grades = pd.read_csv(full_grade_sheet_csv)
    grades.set_index('Username', inplace=True)
    for filename in glob.glob(os.path.join('./essays/', '*.txt')):
        if 'Essay' in filename:
            with open(filename, 'r') as f:
                line = f.readline().strip()
                colon_loc = line.find(':')
                open_paren = line.find('(')
                name = line[colon_loc+2:open_paren-1]

                close_paren = line.find(')')
                uid = line[open_paren+1:close_paren]

                with open('./graded/' + name + '.txt', 'r') as gf:

                    for i in range(total_grade_line):
                        line = gf.readline().strip()
                    grade = float(line[line.find(':')+1:])

                    grades.set_value(uid, 'Essay #1 [Total Pts: 100] |316818', grade)

    grade_columns = grades.columns.values
    for i, col in enumerate(grade_columns):
        if 'Last Name' in col:
            grade_columns[i] = 'Last Name'
    grades.to_csv('./finalgrades.csv')
    

if __name__=='__main__':
    # grade_and_print(sys.argv[1])
    # get_grade_distribution()
    # set_grades()
