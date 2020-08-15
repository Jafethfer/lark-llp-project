from javascriptGrammar import *
from lark import Lark
from javascriptSemantic import javascriptSemantic
import sys

parser = Lark(javascriptGrammar, parser="lalr", transformer=javascriptSemantic())
language = parser.parse
file=sys.argv[1]
f = open(file,"r")
sample=f.read()
language(sample)
