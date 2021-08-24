# Text Processing Services
import re
import string

# Numeric and Mathematical Modules
import random

# Generic Operating System Services
import argparse
import os

# Internet Data Handling
import json

# Python Runtime Services
import sys

# Python Language Services
import ast


def clean_whitespace(content, indent='4'):
	content = content.replace((' '*indent), '\t')
	content = re.sub('[\\ \t]+\n', '\n', content)

	return content


def pad(L, N, dir='0'):
	" Add Nones a list until its length is N\n\n\tws_aslvh = 0\n\tIf dir is 0, the None's are added to the front of the list. If dir is 1,\n\tthe None's are added to back of the list.\n\n\tws_aslvh = 0\n\t"

	if L == None:

		return ([None]*N)

	if len(L) >= N:

		return L


	for i in range(0, (N - len(L))):
		L.insert(0, None)

	return L


def add_linebreak(content, t='default_linebreak'):
	global prefs

	content = content.strip()
	content += ('\n'*(prefs[t] + 1))

	return content


def add_newl(content):
	global prefs

	content = content.strip()
	content += '\n'

	return content


def parse_node(content, node, level, nested='False'):
	global cmt_uuid, ws_uuid

	if (type(node) == ast.FunctionDef or type(node) == ast.AsyncFunctionDef):
		content = add_linebreak(content, t = 'LINES_BEFORE_DEF')


		for n in node.decorator_list:
			content += (('\t'*level) + '@')
			content = parse_node(content, n, level)
			content = add_newl(content)

		content += ('\t'*level)

		if type(node) == ast.AsyncFunctionDef:
			content += 'async '

		content += (('def ' + node.name) + '(')
		content = parse_node(content, node.args, level)

		content += '):'
		content = add_linebreak(content, t = 'LINES_AFTER_DEF')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif type(node) == ast.Call:
		content = parse_node(content, node.func, level)

		content += '('


		for arg in node.args:
			content = parse_node(content, arg, level)
			content += ', '


		for arg in node.keywords:
			content = parse_node(content, arg, level)
			content += ', '

		if len(node.args):
			content = content[None:-2]

		content += ')'

	elif type(node) == ast.keyword:
		content += node.arg
		content += ' = '
		content = parse_node(content, node.value, level)

	elif type(node) == ast.ClassDef:
		content = add_linebreak(content)


		for n in node.decorator_list:
			content += (('\t'*level) + '@')
			content = parse_node(content, n, level)
			content = add_newl(content)

		content += (((('\t'*level) + 'class ') + node.name) + '(')


		for n in node.bases:
			content = parse_node(content, n, level)
			content += ', '


		for n in node.keywords:
			content = parse_node(content, n, level)
			content += ', '

		if (len(node.bases) or len(node.keywords)):
			content = content[None:-2]

		content += '):'
		content = add_linebreak(content)


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif type(node) == ast.Lambda:
		content += 'lambda '

		content = parse_node(content, node.args, level)

		content += ' : '
		content = parse_node(content, node.body, level)

	elif type(node) == ast.arguments:
		i = 0
		N = len(node.args)


		for (arg, val) in zip(node.args, pad(node.defaults, N)):
			content = parse_node(content, arg, level)

			if val != None:
				content += ('=' + repr(str(val.value)))

			content += ', '

		if node.vararg:
			content += '**'
			content = parse_node(content, node.vararg, level)
			content += ', '

		if node.kwarg:
			content += '*'
			content = parse_node(content, node.kwarg, level)
			content += ', '

		if N:
			content = content[None:-2]

	elif type(node) == ast.arg:
		content += node.arg

		if node.annotation:
			content += ': '
			content = parse_node(content, node.annotation, level)

	elif type(node) == ast.While:
		content = add_linebreak(content, t = 'LINES_BEFORE_WHILE')
		content += (('\t'*level) + 'while ')
		content = parse_node(content, node.test, level)
		content += ':'
		content = add_linebreak(content, t = 'LINES_AFTER_WHILE')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif (type(node) == ast.For or type(node) == ast.AsyncFor):
		content = add_linebreak(content, t = 'LINES_BEFORE_FOR')

		content += ('\t'*level)

		if type(node) == ast.AsyncFor:
			content += 'async '

		content += 'for '
		content = parse_node(content, node.target, level)
		content += ' in '
		content = parse_node(content, node.iter, level)
		content += ':\n'
		content = add_linebreak(content, t = 'LINES_AFTER_FOR')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

		if len(node.orelse):
			content += (('\t'*level) + 'else:\n')


			for n in node.orelse:
				content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif type(node) == ast.If:

		if content[-6:None] == 'KJSJWN':
			content = content[None:-6]
			content = add_linebreak(content, t = 'LINES_BEFORE_IF')
			content += (('\t'*level) + 'elif ')

		else:
			content = add_linebreak(content, t = 'LINES_BEFORE_IF')
			content += (('\t'*level) + 'if ')

		content = parse_node(content, node.test, (level + 1))
		content += ':\n'
		content = add_linebreak(content, t = 'LINES_AFTER_IF')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

		if len(node.orelse) and type(node.orelse[0]) == ast.If:
			content += (('\t'*level) + 'KJSJWN')
			level -= 1

		elif len(node.orelse):
			content += (('\t'*level) + 'else:\n')


		for n in node.orelse:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif type(node) == ast.IfExp:
		content = parse_node(content, node.body, level)
		content += ' if '
		content = parse_node(content, node.test, level)
		content += ' else '
		content = parse_node(content, node.orelse, level)

	elif (type(node) == ast.With or type(node) == ast.AsyncWith):
		content = add_linebreak(content, t = 'LINES_BEFORE_WITH')
		content += ('\t'*level)

		if type(node) == ast.AsyncWith:
			content += 'async '

		content += 'with '


		for n in node.items:
			content = parse_node(content, n, (level + 1))
			content += ', '

		content = content[None:-2]
		content += ':\n'
		content = add_linebreak(content, t = 'LINES_AFTER_WITH')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)

	elif type(node) == ast.withitem:
		content = parse_node(content, node.context_expr, level)
		content += ' as '
		content = parse_node(content, node.optional_vars, level)

	elif type(node) == ast.Try:
		content += (('\t'*level) + 'try:\n')


		for n in node.body:
			content = parse_node(content, n, (level + 1))

		content = add_linebreak(content)
		content += (('\t'*level) + 'except ')

		if len(node.handlers):


			for n in node.handlers:
				content = parse_node(content, n, level)

		if len(node.orelse):
			content += (('\t'*level) + 'else:\n')


			for n in node.orelse:
				content = parse_node(content, n, (level + 1))

		if len(node.finalbody):
			content += (('\t'*level) + 'finally:\n')


			for n in node.finalbody:
				content = parse_node(content, n, (level + 1))

	elif type(node) == ast.ExceptHandler:
		content = parse_node(content, node.type, level)
		content += ' as '
		content += node.name

		content += ':\n'


		for n in node.body:
			content = parse_node(content, n, (level + 1))

	elif type(node) == ast.Raise:
		content += (('\t'*level) + 'raise ')
		content = parse_node(content, node.exc, level)

		if node.cause:
			content += ' from '
			content = parse_node(content, node.cause, level)

	elif type(node) == ast.Assert:
		content += (('\t'*level) + 'assert ')
		content = parse_node(content, node.test, level)

		if node.msg:
			content += ', '
			content = parse_node(content, node.msg, level)

	elif type(node) == ast.Await:
		content += (('\t'*level) + 'await ')
		content = parse_node(content, node.value, level)

	elif type(node) == ast.Yield:
		content += (('\t'*level) + 'yield ')
		content = parse_node(content, node.value, level)

	elif type(node) == ast.YieldFrom:
		content += (('\t'*level) + 'yield from ')
		content = parse_node(content, node.value, level)

	elif type(node) == ast.Global:
		content += (('\t'*level) + 'global ')


		for n in node.names:
			content += (str(n) + ', ')

		if len(node.names):
			content = content[None:-2]

		content += '\n'

	elif type(node) == ast.Nonlocal:
		content += (('\t'*level) + 'nonlocal ')


		for n in node.names:
			content += (str(n) + ', ')

		if len(node.names):
			content = content[None:-2]

		content += '\n'

	elif type(node) == ast.Expr:
		content += ('\t'*level)
		content = parse_node(content, node.value, level)
		content += '\n'

	elif type(node) == ast.NamedExpr:
		content += '('
		content = parse_node(content, node.target, level)
		content += ' := '
		content = parse_node(content, node.value, level)
		content += ')'

	#  comment
	elif type(node) == ast.Assign and cmt_uuid in node.targets[0].id:

		if node.targets[0].id[None:4] == 'cmtn':
			content = content.strip()

			content = add_linebreak(content, t = 'LINES_BEFORE_COMMENT')
			content += (' # ' + node.value.value.strip())
			content = add_linebreak(content, t = 'LINES_AFTER_COMMENT')

		elif node.targets[0].id[None:3] == 'cmt':
			content = content.strip()

			content = add_linebreak(content, t = 'LINES_BEFORE_COMMENT')
			content += ((('\n\n' + ('\t'*level)) + '# ') + node.value.value.strip())
			content = add_linebreak(content, t = 'LINES_AFTER_COMMENT')

		content = add_newl(content)

	#  white space
	elif type(node) == ast.Assign and ws_uuid in node.targets[0].id:
		content += '\n'

	elif type(node) == ast.AugAssign:
		content += ('\t'*level)
		content = parse_node(content, node.target, level)

		if type(node.op) == ast.Sub:
			content += ' -= '

		elif type(node.op) == ast.Add:
			content += ' += '

		elif type(node.op) == ast.Mult:
			content += ' *= '

		elif type(node.op) == ast.Div:
			content += ' /= '

		elif type(node.op) == ast.Mod:
			content += ' %= '

		elif type(node.op) == ast.BitOr:
			content += ' |= '

		elif type(node.op) == ast.Pow:
			content += ' **= '

		elif type(node.op) == ast.BitXor:
			content += ' ^= '

		elif type(node.op) == ast.BitAnd:
			content += ' &= '

		elif type(node.op) == ast.MatMult:
			content += ' @= '

		content = parse_node(content, node.value, level)
		content += '\n'

	elif type(node) == ast.Assign:
		content += ('\t'*level)
		content = parse_node(content, node.targets, level)

		content += ' = '

		content = parse_node(content, node.value, level)
		content += '\n'

	elif type(node) == ast.AnnAssign:
		content += ('\t'*level)

		if not node.simple:
			content += '('

		content = parse_node(content, node.target, level)

		if not node.simple:
			content += ')'

		content += ': '
		content = parse_node(content, node.annotation, level)

		if node.value:
			content += ' = '
			content = parse_node(content, node.value, level)

		content += '\n'

	elif type(node) == ast.Name:
		content += node.id

	elif type(node) == ast.UnaryOp:
		content = parse_node(content, node.op, level)
		content = parse_node(content, node.operand, level)

	elif type(node) == ast.BinOp:

		if nested:
			content += '('

		content = parse_node(content, node.left, level, nested = True if type(node.left) == ast.BinOp else False)
		content = parse_node(content, node.op, level)
		content = parse_node(content, node.right, level, nested = True if type(node.right) == ast.BinOp else False)

		if nested:
			content += ')'

	elif type(node) == ast.USub:
		content += '-'

	elif type(node) == ast.UAdd:
		content += '+'

	elif type(node) == ast.Sub:
		content += ' - '

	elif type(node) == ast.Add:
		content += ' + '

	elif type(node) == ast.Mult:
		content += '*'

	elif type(node) == ast.Div:
		content += '/'

	elif type(node) == ast.FloorDiv:
		content += '//'

	elif type(node) == ast.Pow:
		content += '**'

	elif type(node) == ast.Mod:
		content += ' % '

	elif type(node) == ast.LShift:
		content += ' << '

	elif type(node) == ast.RShift:
		content += ' >> '

	elif type(node) == ast.BitOr:
		content += ' | '

	elif type(node) == ast.BitXor:
		content += ' ^ '

	elif type(node) == ast.BitAnd:
		content += ' & '

	elif type(node) == ast.MatMult:
		content += ' @ '

	elif type(node) == ast.And:
		content += ' and '

	elif type(node) == ast.Or:
		content += ' or '

	elif type(node) == ast.Not:
		content += 'not '

	elif type(node) == ast.Invert:
		content += '~'

	elif type(node) == ast.In:
		content += ' in '

	elif type(node) == ast.NotIn:
		content += ' not in '

	elif type(node) == ast.Continue:
		content += (('\t'*level) + 'continue\n')

	elif type(node) == ast.Break:
		content += (('\t'*level) + 'break\n')

	elif type(node) == ast.Pass:
		content += (('\t'*level) + 'pass\n')

	elif type(node) == ast.Eq:
		content += ' == '

	elif type(node) == ast.NotEq:
		content += ' != '

	elif type(node) == ast.Lt:
		content += ' < '

	elif type(node) == ast.LtE:
		content += ' <= '

	elif type(node) == ast.Gt:
		content += ' > '

	elif type(node) == ast.GtE:
		content += ' >= '

	elif type(node) == ast.Is:
		content += ' is '

	elif type(node) == ast.IsNot:
		content += ' is not '

	elif type(node) == ast.JoinedStr:
		content += 'f'
		flag = False


		for n in node.values:
			content = parse_node(content, n, level)

			if flag:
				idxs = [i for (i, x) in enumerate(content) if (x == '"' or x == "'")]
				content = (content[None:idxs[-2]] + content[(idxs[-2] + 1):None])
				flag = False

			if type(n) == ast.FormattedValue:
				flag = True

		if content[-1] != '"' and content[-1] != "'":
			content += "'"

	elif type(node) == ast.FormattedValue:

		if (content[-1] == '"' or content[-1] == "'"):
			content = content[None:-1]

		content += '{'
		content = parse_node(content, node.value, level)
		content += '}'

	elif type(node) == ast.BoolOp:

		if type(node.op) == ast.Or:
			content += '('


		for n in node.values[None:-1]:
			content = parse_node(content, n, level)
			content = parse_node(content, node.op, level)

		content = parse_node(content, node.values[-1], level)

		if type(node.op) == ast.Or:
			content += ')'

	elif type(node) == ast.Compare:
		content = parse_node(content, node.left, level)
		content = parse_node(content, node.ops, level)
		content = parse_node(content, node.comparators, level)

	elif type(node) == ast.Attribute:
		content = parse_node(content, node.value, level)
		content += '.'
		content += node.attr

	elif type(node) == ast.Subscript:
		content = parse_node(content, node.value, level)
		content += '['
		content = parse_node(content, node.slice, level)

		if type(node.slice) == ast.Tuple:
			content = content[None:-1]
			idxs = [i for (i, x) in enumerate(content) if x == '(']
			content = (content[None:idxs[-1]] + content[(idxs[-1] + 1):None])

		content += ']'

	elif type(node) == ast.Slice:
		content = parse_node(content, node.lower, level)
		content += ':'
		content = parse_node(content, node.upper, level)

		if node.step:
			content += ':'
			content = parse_node(content, node.step, level)

	elif type(node) == ast.Constant:
		content = parse_node(content, node.value, level)

	elif type(node) == ast.GeneratorExp:
		content = parse_node(content, node.elt, level)


		for n in node.generators:
			content = parse_node(content, n, level)

	elif type(node) == ast.ListComp:
		content += '['

		content = parse_node(content, node.elt, level)


		for n in node.generators:
			content = parse_node(content, n, level)

		content += ']'

	elif type(node) == ast.SetComp:
		content += '{'

		content = parse_node(content, node.elt, level)


		for n in node.generators:
			content = parse_node(content, n, level)

		content += '}'

	elif type(node) == ast.SetComp:
		content += '{'

		content = parse_node(content, node.elt, level)


		for n in node.generators:
			content = parse_node(content, n, level)

		content += '}'

	elif type(node) == ast.comprehension:

		if node.is_async:
			content += ' async'

		content += ' for '

		content = parse_node(content, node.target, level)
		content += ' in '
		content = parse_node(content, node.iter, level)

		if len(node.ifs):


			for n in node.ifs:
				content += ' if '
				content = parse_node(content, n, level)

	elif type(node) == ast.Return:
		content = add_linebreak(content)

		content += (('\t'*level) + 'return ')
		content = parse_node(content, node.value, level)

		content = add_linebreak(content)

	elif type(node) == ast.Tuple:
		content += '('


		for n in node.elts:
			content = parse_node(content, n, level)
			content += ', '

		if len(node.elts):
			content = content[None:-2]

		content += ')'

	elif type(node) == ast.List:
		content += '['


		for n in node.elts:
			content = parse_node(content, n, level)
			content += ', '

		if len(node.elts):
			content = content[None:-2]

		content += ']'

	elif type(node) == ast.Set:
		content += '{'


		for n in node.elts:
			content = parse_node(content, n, level)
			content += ', '

		if len(node.elts):
			content = content[None:-2]

		content += '}'

	elif type(node) == ast.Dict:
		content += '{'


		for (k, v) in zip(node.keys, node.values):

			if type(k) != type(None):
				content = parse_node(content, k, level)
				content += ' : '
				content = parse_node(content, v, level)

			else:
				content += '**'
				content = parse_node(content, v, level)

			content += ', '

		content = content[None:-2]
		content += '}'

	elif type(node) == ast.Starred:
		content += '*'
		content = parse_node(content, node.value, level)

	elif type(node) == bool:
		content += repr(node)

	elif type(node) == int:
		content += repr(node)

	elif type(node) == float:
		content += repr(node)

	elif type(node) == str:

		if "'" in node:
			content += (('"' + repr(node)[1:-1]) + '"')

		else:
			content += repr(node)

	elif type(node) == type(None):
		content += 'None'

	elif type(node) == list:


		for n in node:
			content = parse_node(content, n, level)

	else:
		print('Type not found: ', type(node))

	return content


def main():
	global prefs, cmt_uuid, ws_uuid

	parser = argparse.ArgumentParser(description = 'Tool for formatting Python code', )

	parser.add_argument('-i', '--input', type = str, required = True, help = 'input Python file to be formatted')
	parser.add_argument('-o', '--output', type = str, required = True, help = 'destination file for the formatted Python (existing file will be overwritten!)')
	parser.add_argument('-g--custom-group', nargs = '+', action = 'append', help = 'Custom grouping')

	args = vars(parser.parse_args())


	with open('prefs.json', 'r') as fp:
		prefs = json.load(fp)

		if 'g__custom_group' in prefs and prefs['g__custom_group']:
			prefs['import_groups'].append(args['g__custom_group'][0])

			#  Open and read file


	with open(args['input'], 'r') as inp:
		content = inp.read()

		#  convert tabs to spaces, trim trailing whitespace

	content = clean_whitespace(content, indent = prefs['indent'])

	#  add comment decorators
	cmt_uuid = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

	#  replace offending hashtags
	ht_uuid = ''.join(random.choice(string.ascii_lowercase) for i in range(5))

	content = re.sub("(')(.*)(#)(.*|)(')", f'\\1\\2ht_{ht_uuid}\\4\\5', content)
	content = re.sub('(\\")(.*)(#)(.*|)(\\")', f'\\1\\2ht_{ht_uuid}\\4\\5', content)

	content = re.sub('(\\n[\\s]+)#(.*)', '\ncmt_{0} = "\\2"'.format(cmt_uuid), content)
	content = re.sub('([\t]+)(.*)#(.*)', '\ncmtn_{0} = "\\3"'.format(cmt_uuid), content)

	content = content.replace(f'ht_{ht_uuid}', '#')

	comments = re.findall('cmt_{0} = "(.*)"'.format(cmt_uuid), content)


	for c in comments:
		content = content.replace(c, c.replace('"', '\\"'))

	comments = re.findall('cmtn_{0} = "(.*)"'.format(cmt_uuid), content)


	for c in comments:
		content = content.replace(c, c.replace('"', '\\"'))


	while re.search(f'(?m)([\\t]+)([^\\t]+)((\\(([^\\(]+)\\))|)([\\n]+)cmt_{cmt_uuid}', content):
		content = re.sub(f'(?m)([\\t]+)([^\\t]+)((\\(([^\\(]+)\\))|)([\\n]+)cmt_{cmt_uuid}', f'\\1\\2\\3\\n\\1cmt_{cmt_uuid}', content)


	while re.search(f'(?m)([\\t]+)([^\\t]+)((\\(([^\\(]+)\\))|)([\\n]+)cmtn_{cmt_uuid}', content):
		content = re.sub(f'(?m)([\\t]+)([^\\t]+)((\\(([^\\(]+)\\))|)([\\n]+)cmtn_{cmt_uuid}', f'\\1\\2\\3\\n\\1cmtn_{cmt_uuid}', content)

		#  add whitespace decorators

	ws_uuid = ''.join(random.choice(string.ascii_lowercase) for i in range(5))
	content = re.sub('(?m)([\\t]+)([^\\t:]+)(^\\n)', f'\\1\\2\\nws_{ws_uuid} = 0\\n', content)
	content = re.sub(f'(?m)([\\t]+)([^\\t]+)((\\(([^\\(]+)\\))|)([\\n]+)ws_{ws_uuid}', f'\\1\\2\\3\\n\\1ws_{ws_uuid}', content)

	print('Writing to: ', args['output'])


	with open(args['output'], 'w') as outp:
		outp.write(content)

		#  Create AST


	with open('output.ast', 'w') as fp:
		tree = ast.parse(content)
		fp.write(ast.dump(tree, indent = 4))

	content = ''

	#  Load imports
	imports = []


	for node in next(ast.iter_fields(tree))[1]:

		if type(node) == ast.Import:
			imports.append((node.names[0].name, node))

		elif type(node) == ast.ImportFrom:
			imports.append((node.module, node))

			#  Sort imports into groups

	groups = []
	added = []


	for (k, g) in prefs['import_groups'].items():
		group = []


		for (f, m) in imports:

			if f.split('.')[0] in g:
				group.append((f, m))
				added.append(f)

		if prefs['sort']:
			group = sorted(group, key = lambda x : x[0])

		groups.append((k, group))

	#  Add remaining imports to the end
	group = []


	for (f, m) in imports:

		if f not in added:
			group.append((f, m))

	if prefs['sort']:
		group = sorted(group, key = lambda x : x[0])

	groups.append(('Miscellaneous', group))

	#  Print imports


	for (k, g) in groups:

		if not len(g):
			continue

		content += '# {0}\n'.format(k)


		for (f, n) in g:
			content += (ast.unparse(n) + '\n')

		content += '\n'

	content = add_linebreak(content)

	#  Sort all other nodes


	for node in next(ast.iter_fields(tree))[1]:

		if type(node) != ast.Import and type(node) != ast.ImportFrom:
			content = parse_node(content, node, 0)

	print('Writing to: ', args['output'])


	with open(args['output'], 'w') as outp:
		outp.write(content)

if __name__ == '__main__':
	main()

