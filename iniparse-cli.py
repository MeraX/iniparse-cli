#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""iniparse-cli  - cli-wrapper tool for the python-library
Version 1.0.2 (build 20141122)

Usage
-----
iniparse-cli.py config.ini                                 // returns list of sections
iniparse-cli.py config.ini {SECTION                        // returns list of items in SECTION
iniparse-cli.py config.ini {SECTION} {OPTION}              // returns value of OPTION in SECTION
iniparse-cli.py config.ini {SECTION} {OPTION} {VALUE}      // sets VALUE of OPTION in SECTION

iniparse-cli.py -d config.ini {SECTION}                    // deletes SECTION
iniparse-cli.py -d config.ini {SECTION} {OPTION}           // deletes OPTION in SECTION
iniparse-cli.py -d config.ini {SECTION} {OPTION} {VALUE}   // deletes value of OPTION in SECTION when VALUE matches

iniparse-cli.py --silent {...}  // suppress all error messages

License & Copyright
-------------------
Copyright (C) 2013 - 2014 Marek Jacob

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, version 3 of the License only.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__version__ = '1.0.2'
__build__ = '20141122'

import sys
import iniparse
import argparse
import os

# in some versions of iniparse, this attribute does not exist.
try:
	iniparse.DuplicateSectionError
except AttributeError:
	import ConfigParser
	iniparse.DuplicateSectionError = ConfigParser.DuplicateSectionError

#__DEBUG__ = True

def getArgParser():
	"""setup an argument parser to collect the values we need
Returns
-------
	parser: instance of argparse.ArgumentParser
"""

	parser = argparse.ArgumentParser(usage='%(prog)s [-s|--silent] [-d|--delete] [-h] {INIFILE} [SECTION] [OPTION] [VALUE]',
		description='Returns, edits and deletes sections and options of an ini file.')

	# input
	parser.add_argument('inifile', action='store', nargs='?',
		help='path to ini file',
		metavar='{INIFILE}')
	parser.add_argument('input', action='store', nargs='*',
		help="""pass SECTION, OPTION and VALUE to set the value of OPTION in SECTION to VALUE.
			Passing SECTION and OPTION returns the value of OPTION in SECTION.
			To return a list of all options in SECTION, just pass SECTION.
			Omit all parameters to return a list of all sections""",
		metavar="[SECTION] [OPTION] [VALUE]")

	parser.add_argument('-d', '--delete', '--del', action='store_true',
		help='deletes given option or section. When deleting an option, pass VALUE to delete it just when the value matches')

	parser.add_argument('--version', action='store_true',
		help="show program's version number and license and exit")

	parser.add_argument('-s','--silent', action='store_true',
		help="suppress all error messages")

	return parser


def parseArgs(parser):
	""" checks the count of arguments and prints version
Returns
-------
args : argparse.Namespace
	args.inifile : string
	args.input : list
	args.delete : bool
	args.silent : bool
"""
	args = parser.parse_args()

	if args.version:
		print os.path.basename(sys.argv[0]), __version__, 'Build', __build__
		print """Copyright (C) 2013 - 2014 Marek Jacob

License GPLv3: GNU GPL version 3 only <http://gnu.org/licenses/gpl.html>.
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law."""
		sys.exit(0)

	if args.silent:
		def silent_excepthook(type, value, traceback):
			sys.exit(2)
		sys.excepthook = silent_excepthook

	if args.inifile is None:
		raise UsageError('too few arguments. missing inifile.')
	if len(args.input) > 4:
		raise UsageError('too many arguments')
	elif len(args.input) > 0 and args.input[0] == "":
		raise UsageError('section name cannot be empty')
	elif len(args.input) > 1 and args.input[1] == "":
		raise UsageError('option name cannot be empty')#

	return args


def delete(inifile,section=None,option=None,value=None):
	"""deletes given option or section. When deleting an option, pass VALUE to delete it just when the value matches"""
	ini = openIni(inifile)

	if section is None and option is None and value is None:
		raise UsageError('no section specified')

	elif option is None and value is None:
		ini.options(section) # test
		# delete section
		ini.remove_section(section)

	elif value is None:
		ini.get(section,option)
		# delete section->option
		ini.remove_option(section,option)

	else:
		# delete section->option in case of equal values
		if ini.get(section,option) != value:
			raise DeletionMissmatchError("value of option '%s' in section '%s' (value: '%s') mismatches required '%s'" % (option,section,ini.get(section,option),value))

		ini.remove_option(section,option)

	with open(inifile,'w') as f:
		ini.write(f)


def manage(inifile,section=None,option=None,value=None):
	"""pass SECTION, OPTION and VALUE to set the value of OPTION in SECTION to VALUE.
Passing SECTION and OPTION returns the value of OPTION in SECTION.
To return a list of all options in SECTION, just pass SECTION.
Omit all parameters to return a list of all sections"""

	if section is None and option is None and value is None:
		ini = openIni(inifile)
		# get list of sections
		return '\n'.join(ini.sections())

	elif option is None and value is None:
		ini = openIni(inifile)
		# get list of options in section
		return '\n'.join(ini.options(section))

	elif value is None:
		ini = openIni(inifile)
		# get value of section->option
		value = ini.get(section,option)
		if value.startswith('"') and value.endswith('"'):
			return value[1:-1]
		elif value.startswith("'") and value.endswith("'"):
			return value[1:-1]
		else:
			return value

	else:
		# set value of section->option
		ini = openIni(inifile,True)
		try:
			# create section when necessary
			ini.add_section(section)
		except iniparse.DuplicateSectionError:
			pass

		ini.set(section,option,value)
		with open(inifile,'w') as f:
			ini.write(f)
		return


def openIni(inifile,ignoreFileDoesNotExist=False):
	"""open inifile and return ConfigParser"""
	ini = iniparse.ConfigParser()
	if len(ini.read(inifile)) < 1:
		if not os.path.isfile(inifile):
			if not ignoreFileDoesNotExist:
				raise IOError("unable to open '%s': no such file" % inifile)
		else:
			raise IOError("unable to open '%s': permission denied" % inifile)
	return ini


class UsageError(Exception):
	"""Exception that triggers to print usage"""

class DeletionMissmatchError(Exception):
	"""Exception that triggers when trying to delete OPTION with mismatching VALUE"""


def excepthook(type, value, traceback):
	"""define new excepthook to create a user friendly output"""
	try:
		if __DEBUG__:
			return sys.__excepthook__(type,value,traceback)
	except NameError:
		pass

	message = str(value)
	sys.stderr.write(os.path.basename(sys.argv[0]) + ': error: ' + message[0].lower() + message[1:] + '\n')

	if (isinstance(value, UsageError)):
		getArgParser().print_usage()
	sys.exit(2)


def main():
	sys.excepthook = excepthook

	parser = getArgParser()
	args = parseArgs(parser)

	if args.delete:
		delete(args.inifile,*args.input)
	else:
		result = manage(args.inifile,*args.input)
		if result:
			print result

if __name__ == '__main__':
	main()