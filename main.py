

import sys
import os
import re
import argparse


def clean_whitespace(content, wp):
	content = content.replace(' ' * wp, '\t')
	content = re.sub("[\\ \t]+\n", "\n", content)
	return content

if __name__ == "__main__":
	
	parser = argparse.ArgumentParser(description='Tool for formatting Python code')

	parser.add_argument('-i', '--input', type=str, required=True,
	                    help='input Python file to be formatted')

	parser.add_argument('-o', '--output', type=str, required=True,
	                    help='destination file for the formatted Python (existing file will be overwritten!)')

	parser.add_argument('-t', '--num-tabs', type=int, default=4,
	                    help='number of spaces that represent a tab')


	args = vars(parser.parse_args())

	print(args)

	with open(args["input"], "r") as inp:
		with open(args["output"], "w") as outp:
			outp.write(clean_whitespace(inp.read(), args["num_tabs"]))


