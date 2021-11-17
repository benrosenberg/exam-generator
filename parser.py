import yaml
import os

filename = input('Enter the name of the YAML file to parse and convert: ')

# load yaml file as dictionary
with open(filename, "r") as stream:
    try:
        contents = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
        exit()

default_cover_contents = '''\\Huge Cover option selected but no `cover-contents` specified. \\normalsize\n'''

output = []

if 'margin' in contents:
    margin = contents['margin']
else:
    margin = '0.85in'

if 'fontsize' in contents:
    fontsize = contents['fontsize']
else:
    fontsize = '12pt'

yaml_header = ['---',
              f'fontsize: {fontsize}',
               'header-includes: |',
              f'    \\usepackage[margin={margin}]'+'{geometry}',
               '    \\usepackage{xcolor}',
               '    \\usepackage{amsmath}',
               '    \\usepackage{lastpage}']

if 'header' in contents or 'footer' in contents:
    yaml_header.append('    \\usepackage{fancyhdr}')
    yaml_header.append('    \\pagestyle{fancy}')

# header token
if 'header' in contents:
    contents['header'] = contents['header'].replace('<pagenum>', '\\thepage\\hspace{1pt}')
    contents['header'] = contents['header'].replace('<date>', '\\today')
    contents['header'] = contents['header'].replace('<pages>', '\\pageref{LastPage}')
    contents['header'] = contents['header'].replace('_', '\\_')
    lhead, chead, rhead = [_.strip() for _ in contents['header'].split('-=-')]
    if lhead != '':
        yaml_header.append('    \\lhead{' + lhead + '}')
    if chead != '':
        yaml_header.append('    \\chead{' + chead + '}')
    if rhead != '':
        yaml_header.append('    \\rhead{' + rhead + '}')
# footer token
if 'footer' in contents:
    contents['footer'] = contents['footer'].replace('<pagenum>', '\\thepage\\hspace{1pt}')
    contents['footer'] = contents['footer'].replace('<date>', '\\today')
    contents['footer'] = contents['footer'].replace('<pages>', '\\pageref{LastPage}')
    contents['footer'] = contents['footer'].replace('_', '\\_')
    lfoot, cfoot, rfoot = [_.strip() for _ in contents['footer'].split('-=-')]
    if lfoot != '':
        yaml_header.append('    \\lfoot{' + lfoot + '}')
    if cfoot != '':
        yaml_header.append('    \\cfoot{' + cfoot + '}')
    if rfoot != '':
        yaml_header.append('    \\rfoot{' + rfoot + '}')

yaml_header.append('---')

output = yaml_header + output

# cover-page token
if 'cover-page' in contents:
    if contents['cover-page']:
        output.append('\n\\thispagestyle{empty}\n')
        if 'cover-contents' in contents:
            output.append(contents['cover-contents'])
        else:
            output.append(default_cover_contents)
        output.append('\\newpage\n')

# all-disp token
if 'all-disp' in contents:
    if contents['all-disp']:
        output.append('\\everymath{\displaystyle}\n')
else:
    output.append('\\everymath{\displaystyle}\n')

# answer-color token
allowed_color_list = ['black', 'blue', 'brown', 'cyan', 'darkgray', 'gray',
                      'green', 'lightgray', 'lime', 'magenta', 'olive', 'orange',
                      'pink', 'purple', 'red', 'teal', 'violet', 'white', 'yellow']
answer_color = 'blue'
if 'answer-color' in contents:
    if contents['answer-color'] in allowed_color_list:
        answer_color = contents['answer-color']
    else:
        raise Exception('Something went wrong: answer-color ' + contents['answer-color'] + ' not in list of possible choices.')

# full-page token
ADD_NEWPAGES = False
if 'full-page' in contents:
    if contents['full-page']:
        ADD_NEWPAGES = True

# answer-line token
answer_line = False
if 'answer-line' in contents:
    if contents['answer-line']:
        answer_line = True

# parse questions
lines = list(contents.items()) 
digits = [str(i) for i in range(10)]
questions_answers = [(int(l[0][1]), l[0][0], l[1]) for l in lines if l[0][0] in 'qa' and l[0][1] in digits]
# print(questions_answers)

# different accumulator lists for exam and answer key
q_out = []
qa_out = []
for qa_number, q_or_a, content in questions_answers:
    if q_or_a == 'q':
        qa_out.append(f'## {qa_number}. {content}\n')
        q_out.append(f'## {qa_number}. {content}\n' + ADD_NEWPAGES * '\\newpage')
    elif q_or_a == 'a':
        if answer_line:
            qa_out.append('\n---\n')    # adds horizontal line between questions and answers
        qa_out.append('\\color{' + answer_color + '}\n')
        qa_out.append(content + '\n')
        qa_out.append('\\color{black}\n' + ADD_NEWPAGES * '\\newpage')
    else:
        raise Exception(f'Something went wrong: q_or_a was {q_or_a} instead of "q" or "a".')

# print(q_out)
# print(qa_out)

output_q = output + q_out
output_qa = output + qa_out

# write q to file
q_filename = filename[:filename.rfind('.')] + '_EXAM'
with open(q_filename + '.md', 'w') as outfile_q:
    outfile_q.write('\n'.join(output_q))

# write qa to file
qa_filename = filename[:filename.rfind('.')] + '_ANSWERS'
with open(qa_filename + '.md', 'w') as outfile_qa:
    outfile_qa.write('\n'.join(output_qa))

# convert using pandoc
os.system(f'pandoc --pdf-engine-opt=-shell-escape --pdf-engine=xelatex {q_filename}.md -o {q_filename}.pdf')
os.system(f'pandoc --pdf-engine-opt=-shell-escape --pdf-engine=xelatex {qa_filename}.md -o {qa_filename}.pdf')

# remove unnecessary .md files (comment out if debugging)
os.system(f'rm {q_filename}.md')
os.system(f'rm {qa_filename}.md')
