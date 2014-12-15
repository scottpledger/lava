#!/usr/bin/python3
"""
stuff.
"""
import argparse,json,re


class MyHelpFormatter(argparse.HelpFormatter):
    """
    MyHelpFormatter
    """

    def _format_action(self, action):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        help_width = max(self._width - help_position, 11)
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)

        # ho nelp; start on same line and add a final newline
        if not action.help:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup

        # short action name; start on the same line and pad two spaces
        elif len(action_header) <= action_width:
            tup = self._current_indent, '', action_width, action_header
            action_header = '%*s%-*s  ' % tup
            indent_first = 0

        # long action name; start on the next line
        else:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [action_header]

        # if there was help for the action, add lines of help text
        if action.help:
            help_text = self._expand_help(action)
            help_lines = self._split_lines(help_text, help_width)
            parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            for line in help_lines[1:]:
                parts.append('%*s%s\n' % (help_position, '', line))

        # or add a newline if the description doesn't end with one
        elif not action_header.endswith('\n'):
            parts.append('\n')
        if hasattr(action, 'choices') and isinstance(action.choices, dict):
            #parts.append('%*s%s\n' % (indent_first, '', "Choices:"))
            for choice in action.choices:
                parts.append('%*s%s\n' % (indent_first, '', ' * %s:' % choice))
                if action.choices[choice]:
                    parts.append(
                        '%*s%s\n' %
                        (indent_first, '', '      ' + action.choices[choice]))

        # if there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # return a single string
        return self._join_parts(parts)


class Analyzer(object):
    """
    Analyser
    """

    def __init__(self):
        self.method_counts = dict()

    def analyse(self, text, method=None):
        """
        A method to analyze some given text.
        """
        if method is None:
            for method in Analyzer.Methods:
                method(self, text)
        else:
            method(self, text)

    def dump_analysis(self, outfile):
        """
        Dumps the analysis to a given file.
        """

        # First, we need to normalize each count
        normed_counts = {}
        for method in self.method_counts:
            m_counts = self.method_counts[method]
            total = sum(m_counts.values())

            counts = []
            for letter in sorted(m_counts.keys()):
                counts += [(letter,m_counts[letter]/total)]
            print(counts)
            normed_counts[method] = counts

        outfile.write(json.dumps(normed_counts))

    def _method_letters(self, text):
        """
        Counts the number of every letter in the given
        text.
        """
        counts = dict()
        excludes = "[^a-zA-Z]"
        for letter in text:
            if not re.match(excludes, letter):
                letter = letter.upper()
                if letter not in counts:
                    counts[letter] = 0
                counts[letter]+=1
        self.method_counts['letters']=counts

    Methods = [_method_letters]


class Comparator(object):
    """
    Shut up already, pylint!
    """

    def __init__(self):
        pass

    def compare(self, file1, file2):
        """
        Stuff
        """
        pass

    def dump_stats(self, file1, file2):
        """
        Shut up already, pylint!
        """
        pass


def analyse(args):
    """
    Handles the analyse subcommand.
    """
    analyzer = Analyzer()

    for filen in args.inFile:
        analyzer.analyse(filen.read())

    analyzer.dump_analysis(args.outFile)


def compare(args):
    """
    Handles the compare command.
    """
    args.gofuckyourself()


def main():
    """
    Executes main program flow.
    """

    parser = argparse.ArgumentParser(
        description='Analyse one or more files.',
    )
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_analyse = subparsers.add_parser(
        'analyse', help='analyse help', aliases=['a'])
    parser_analyse.add_argument(
        'outFile', type=argparse.FileType('w', encoding='UTF-8'),
        help='File to dump analysis to.')
    parser_analyse.add_argument(
        'inFile', nargs='+', type=argparse.FileType('r', encoding='UTF-8'),
        help='Files to analyse.')
    parser_analyse.set_defaults(func=analyse)

    parser_compare = subparsers.add_parser(
        'compare', help='compare help', aliases=['c'])
    parser_compare.add_argument(
        'file1', nargs=1, type=argparse.FileType('r', encoding='UTF-8'),
        help='File to compare against.')
    parser_compare.add_argument(
        'files', nargs='+', type=argparse.FileType('r', encoding='UTF-8'),
        help='Files to compare.')
    parser_compare.set_defaults(func=compare)

    args = parser.parse_args()
    if 'func' in args:

        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":

    main()
