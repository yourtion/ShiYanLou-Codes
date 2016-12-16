"""md2pdf

translates markdwon file into html or pdf, and support picture insertion.

Usage: 
    md2pdf <sourcefile> <outputfile> [options]

Options:
    -h --help     show help document.
    -v --version  show version information.
    -o --output   translate sourcefile into html file.
    -p --print    translate sourcefile into pdf file and html file respectively.
    -P --Print    translate sourcefile into pdf file only.
"""

import os,re
import sys,getopt
from enum import Enum
from subprocess import call
from functools import reduce

from docopt import docopt

__version__ = '1.0'

class TABLE(Enum):
  Init = 1
  Format = 2
  Table = 3

class ORDERLIST(Enum):
  Init = 1
  List = 2

class BLOCK(Enum):
  Init = 1
  Block = 2
  CodeBlock = 3

table_state = TABLE.Init
orderList_state = ORDERLIST.Init
block_state = BLOCK.Init

is_code = False
is_normal = True

temp_table_first_line = []
temp_table_first_line_str = ""

need_mathjax = False

def run(source_file, dest_file, dest_pdf_file, only_pdf):
  file_name = source_file
  dest_name = dest_file
  dest_pdf_name = dest_pdf_file

  _, suffix = os.path.splitext(file_name)
  if suffix not in [".md", ".markdwon", ".mdown", ".mkd"]:
    print('Error: the file should be markdwon format')
    sys.exit(-1)
  if only_pdf:
    dest_name = ".~temp~.html"

  f = open(file_name, "r")
  f_r = open(dest_name, "w")

  f_r.write("""<style type="text/css">\
      div {display: block;font-family: "Times New Roman",Georgia,Serif}\
      #wrapper { width: 100%;height:100%; margin: 0; padding: 0;} \
      #left { float:left;  width: 10%;  height: 100%;  }\
      #second { float:left;   width: 80%;height: 100%; }  \
      #right {float:left;  width: 10%;  height: 100%; } \
    </style><div id="wrapper"> \
    <div id="left"></div><div id="second">""")
  f_r.write("""<meta charset="utf-8"/>""")

  for eachline in f:
    result = parse(eachline)
    if result != "":
      f_r.write(result)

  f_r.write("""</br></br></div><div id="right"></div></div>""")

  global need_mathjax
  if need_mathjax:
    f_r.write("""<script type="text/x-mathjax-config">\
      MathJax.Hub.Config({tex2jax: {inlineMath: [['$','$'], ['\\(','\\)']]}});\
      </script><script type="text/javascript" \
      src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>""")

  f_r.close()
  f.close()

  if dest_pdf_name != "" or only_pdf:
    call(["wkhtmltopdf", dest_name, dest_pdf_name])
    
  if only_pdf:
    call(["rm", dest_name])

def parse(input):
  global block_state, is_normal
  is_normal = True
  result = input

  result = test_state(input)

  if block_state == BLOCK.Block:
    return result

  title_rank = 0
  for i in range(6, 0, -1):
    if input[:i] == '#'*i:
      title_rank = i
      break
  if title_rank != 0:
    result = handleTitle(input, title_rank)
    return result

  if len(input)>2 and all_same(input[:-1], '-') and input[-1] == '\n':
    result = "<hr>"
    return result

  unorderd = ['+', '-']
  if result != "" and result[0] in unorderd:
    result = handleUnorderd(result)
    is_normal = False

  f = input[0]
  count = 0
  sys_q = False

  while f == '>':
    count += 1
    f = input[count]
    sys_q = True
  if sys_q:
    result = "<blockquote style=\"color:#8fbc8f\"> "*count + "<b>" + input[count:] + "</b>" + "</blockquote>"*count
    is_normal = False

  result = tokenHandler(result)

  result = link_image(result)
  pa = re.compile(r'^(\s)*$')
  a = pa.match(input)
  if input[-1] == "\n" and is_normal == True and not a :
    result += "</br>"

  return result

def test_state(input):
  global table_state, orderList_state, block_state, is_code, temp_table_first_line, temp_table_first_line_str
  code_list = ["Python\n", "c++\n", "c\n"]

  result = input

  pattern = re.compile(r'```(\s)*\n')
  a = pattern.match(input)

  if a and block_state == BLOCK.Init:
    result = "<blockquote>"
    block_state = BLOCK.Block
    is_normal = False
  elif len(input) > 4 and input[0:3] == '```' and (input[3:9] == "python" or input[3:6] == "c++" or input[3:4]== "c") and block_state == BLOCK.Init:
    block_state = BLOCK.Block
    result = "<code></br>"
    is_code = True
    is_normal = False
  elif block_state == BLOCK.Block and input == '```\n':
    if is_code:
      result = "</code>"
    else:
      result = "</blockquote>"
    block_state = BLOCK.Init
    is_code = False
    is_normal = False
  elif block_state == BLOCK.Block:
    pattern = re.compile(r'[\n\r\v\f\ ]')
    result = pattern.sub("&nbsp", result)
    pattern = re.compile(r'\t')
    result = pattern.sub("&nbsp" * 4, result)
    result = "<span>" + result + "</span></br>"
    is_normal = False
  if len(input) > 2 and input[0].isdigit() and input[1] == '.' and orderList_state == ORDERLIST.Init:
    orderList_state = ORDERLIST.List
    result = "<ol><li>" + input[2:] + "</li>"
    is_normal = False
  elif len(input) > 2 and  input[0].isdigit() and input[1] == '.' and orderList_state == ORDERLIST.List:
    result = "<li>" + input[2:] + "</li>"
    is_normal = False
  elif orderList_state == ORDERLIST.List and (len(input) <= 2 or input[0].isdigit() == False or input[1] != '.'):
    result = "</ol>" + input
    orderList_state = ORDERLIST.Init

  pattern = re.compile(r'^((.+)\|)+((.+))$')
  match = pattern.match(input)
  if match:
    l = input.split('|')
    l[-1] = l[-1][:-1]

    if l[0] == '':
      l.pop(0)
    if l[-1] == '':
      l.pop(-1)
    if table_state == TABLE.Init:
      table_state = TABLE.Format
      temp_table_first_line = l
      temp_table_first_line_str = input
      result = ""

    elif table_state == TABLE.Format:

      if reduce(lambda a, b: a and b, [all_same(i,'-') for i in l], True):
        table_state = TABLE.Table
        result = "<table><thread><tr>"
        is_normal = False

        for i in temp_table_first_line:
          result += "<th>" + i + "</th>"
        result += "</tr>"
        result += "</thread><tbody>"
        is_normal = False
      else:
        result = temp_table_first_line_str + "</br>" + input
        table_state = TABLE.Init

    elif table_state == TABLE.Table:
      result = "<tr>"
      for i in l:
        result += "<td>" + i + "</td>"
      result += "</tr>"

  elif table_state == TABLE.Table:
    table_state = TABLE.Init
    result = "</tbody></table>" + result
  elif table_state == TABLE.Format:
    pass

  return result

def all_same(lst, sym):
  return not lst or sym * len(lst) == lst

def handleTitle(s, n):
  return "<h" + repr(n) + ">" + s[n:] + "</h" + repr(n) + ">"

def handleUnorderd(s):
  return "<ul><li>" + s[1:] + "</li></ul>"

def tokenTemplate(s, match):
  pattern = ""
  if match == '*':
    pattern = "\*([^\*]*)\*"
  if match == '~~':
    pattern = "\~\~([^\~\~]*)\~\~"
  if match == '**':
    pattern = "\*\*([^\*\*]*)\*\*"
  return pattern

def tokenHandler(s):
  l = ['b', 'i', 'S']
  j = 0
  for i in ['**', '*', '~~']:
    pattern = re.compile(tokenTemplate(s,i))
    match = pattern.finditer(s)
    k = 0
    for a in match:
      if a:
        content = a.group(1)
        x,y = a.span()
        c = 3
        if i == '*':
          c = 5
        s = s[:x+c*k] + "<" + l[j] + ">" + content + "</" + l[j] + ">" + s[y+c*k:]
        k += 1
    pattern = re.compile(r'\$([^\$]*)\$')
    a = pattern.search(s)
    if a:
      global need_mathjax
      need_mathjax = True
    j += 1
  return s

def link_image(s):
  pattern = re.compile(r'\\\[(.*)\]\((.*)\)')
  match = pattern.finditer(s)
  for a in match:
    if a:
      text, url = a.group(1,2)
      x, y = a.span()
      s = s[:x] + "<a href=" + url + " target=\"_blank\">" + text + "</a>" + s[y:]

  pattern = re.compile(r'!\[(.*)\]\((.*)\)')
  match = pattern.finditer(s)
  for a in match:
    if a:
      text, url = a.group(1,2)
      x, y = a.span()
      s = s[:x] + "<img src=" + url + " target=\"_blank\">" + "</a>" + s[y:]

  pattern = re.compile(r'(.)\^\[([^\]]*)\]')
  match = pattern.finditer(s)
  k = 0
  for a in match:
    if a:
      sym,index = a.group(1,2)
      x, y = a.span()
      s = s[:x+8*k] + sym + "<sup>" + index + "</sup>" + s[y+8*k:]
    k += 1

  return s

def main():
  dest_file = "translation_result.html"
  dest_pdf_file = "translation_result.pdf"
  only_pdf = False

  args = docopt(__doc__, version=__version__)
  
  dest_file = args['<outputfile>'] if args['--output'] else dest_file
  dest_pdf_file = args['<outputfile>'] if args['--print'] or args['--Print'] else ""

  run(args['<sourcefile>'], dest_file, dest_pdf_file, args['--Print'])

if __name__=="__main__":
  main()

