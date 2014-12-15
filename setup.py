#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
	name = "LaVa",
	version = "0.1",
	packages = find_packages(),
	scripts = ['analyser.py', 'visualizer.py'],
	install_requires = [
		'nltk>=3.0.0'
	],
	package_data = {
		'': ['*.txt']
	},
	author = "Scott R. Pledger",
	author_email = "pledger@colorado.edu",
	description = "Tool to visualize how authors use language.",
	license = "GPL",
	url = "https://github.com/scottpledger/lava"
)
