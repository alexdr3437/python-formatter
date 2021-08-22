

import sys
import os
import re
import argparse
import json
import ast


def clean_whitespace(content, indent=4):
	content = content.replace(' ' * indent, '\t')
	content = re.sub("[\\ \t]+\n", "\n", content)
	return content


def pad(L, N, dir=0):
	""" Add Nones a list until its length is N
	
	If dir is 0, the None's are added to the front of the list. If dir is 1,
	the None's are added to back of the list.

	"""

	if L == None: return [None] * N
	if len(L) >= N: return L

	for i in range(0, N - len(L)):
		L.insert(0, None)

	return L


def add_linebreak(content):
	if (content[-1] != "\n"):
		content += "\n"
	content += "\n"

	return content

def parse_FunctionDef(content, node):
	content += "def " + node.name + "("

	i = 0 
	N = len(node.args.args)
	for arg, val in zip(node.args.args, pad(node.args.defaults,N)):

		content += arg.arg

		if (val != None):
			content +=  "=" + repr(str(val.value))

		content += ", "

	if N: 
		content = content[:-2]

	content += "):"

	return content



def parse_node(content, node, level=0):

	print(node, level)

	if type(node) == ast.FunctionDef:
		content = add_linebreak(content)
		content = parse_FunctionDef(content, node)

		for n in node.body:
			content = parse_node(content, n, level=level+1) 

	elif type(node) == ast.If:
		content = add_linebreak(content)
		content += "\t"*level +  "if"
		content = parse_node(content, node.test, level=level) 

	elif type(node) == ast.Name:
		content += " " + node.id

	elif type(node) == ast.UnaryOp:
		content = parse_node(content, node.op, level=level)
		content = parse_node(content, node.operand, level=level)


	elif type(node) == ast.Not:
		content += " not"



	return content


def main():


	parser = argparse.ArgumentParser(description='Tool for formatting Python code')

	parser.add_argument('-i', '--input', type=str, required=True,
	                    help='input Python file to be formatted')
	parser.add_argument('-o', '--output', type=str, required=True,
	                    help='destination file for the formatted Python (existing file will be overwritten!)')

	args = vars(parser.parse_args())
	with open("prefs.json", "r") as fp:
		prefs = json.load(fp)

	# Open and read file
	with open(args["input"], "r") as inp:
		content =  inp.read()

	# convert tabs to spaces, trim trailing whitespace
	content = clean_whitespace(content, indent=prefs["indent"])

	# Create AST 
	with open("output.ast","w") as fp:
		tree = ast.parse(content)
		fp.write(ast.dump(tree, indent=4))

	content = ""

	# Load imports
	imports = []
	for node in next(ast.iter_fields(tree))[1]:
		if type(node) == ast.Import: 
			imports.append( ( node.names[0].name, node) )
		elif type(node) == ast.ImportFrom:
			imports.append( ( node.module, node) )

	# Sort imports into groups
	groups=[]
	for g in prefs["import_groups"]:
		group = []

		for f,m in imports:
			if f.split(".")[0] in g:
				group.append((f,m))

		if prefs["sort"]: group = sorted(group, key = lambda x: x[0])
		groups.append(group)

	print("Helo?")

	for g in groups:
		for f,n in g:
			content += ast.unparse(n)  + "\n"
		content += "\n"

	# Sort all other nodes
	for node in next(ast.iter_fields(tree))[1]:
		if type(node) != ast.Import and type(node) != ast.ImportFrom:
			content = parse_node(content, node)


	print("Writing to: ", args["output"])
	with open(args["output"], "w") as outp:
		outp.write(content)




if __name__ == "__main__":
	main()	
	