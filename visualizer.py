#!/usr/bin/python3

import nltk,argparse,queue,sys,threading
import multiprocessing as mp

from PyQt5 import QtCore, QtGui, QtWidgets
from nltvis import *
from nltvis_ui import Ui_MainWindow

class Analyzer(object):

    def __init__(self,*args,**kwargs):
        
        self.parser=nltk.parse.stanford.StanfordParser(
            path_to_jar="stanford-parser-full-2014-10-31/stanford-parser.jar",
            path_to_models_jar="stanford-parser-full-2014-10-31/stanford-parser-3.5.0-models.jar",
            model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz"
        )
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tree = CountingProbabilisticTree('ROOT', [], prob=1.0)

    def analyse(self, s, status_callback=None, complete_callback=None):
        
        status_callback = (lambda *args: print(" ".join(args)) ) if not hasattr(status_callback, '__call__') else status_callback
        complete_callback = (lambda *args: print(" ".join(args)) ) if not hasattr(complete_callback, '__call__') else complete_callback
        
        data = " ".join(s.split())
        status_callback("Tokenizing Sentences...", 0.0)
        sentences = self.sent_detector.tokenize(data)
        status_callback("Tokenizing Sentences...", 0.1)
        status_callback("Parsing Sentences...", 0.1)
        trees = self.parser.raw_parse_sents(sentences)
        status_callback("Parsing Sentences...", 0.2)
        tc = 0
        ntrees = len(trees)
        n = 0
        status_callback("Merging Parse Trees... %s/%s"%(n,ntrees), (ntrees+5*n)/(5*ntrees))
        
        for tree in trees:
            tc += len(tree.leaves())
            self.tree.merge(tree)
            n+=1
            status_callback("Merging Parse Trees... %s/%s"%(n,ntrees), (ntrees+5*n)/(5*ntrees))
        status_callback("Done Merging Parse Trees!", 1.0)
        complete_callback()
        
    
    def get_status(self):
        pass

    def dump_analysis(self, f):
        f.write(self.tree.mprint())

    @classmethod
    def from_dump(cls,f):
        s = f.read()
        v = Analyzer()
        v.tree = CountingProbabilisticTree.from_mprint(s)
        
        return v

class GuiForm(QtWidgets.QMainWindow):
    def __init__(self, argv, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.actionOpen_Analysis.triggered.connect(self.actionOpen_Analysis)
        self.ui.actionSave_Analysis.triggered.connect(self.actionSave_Analysis)
        self.ui.actionOpen_File_to_Analyze.triggered.connect(self.actionOpen_File_to_Analyze)
        self.a = Analyzer()
        self.argv = argv
        if self.argv.inFile:
            with self.argv.inFile as f:
                self.a = Analyzer.from_dump(f)
    
    def actionOpen_Analysis(self):
        fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getOpenFileName(self)
        from os.path import isfile
        if isfile(fname):
            with open(fname,'r') as f:
                self.a = Analyzer.from_dump(f)

    def actionSave_Analysis(self):
        fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getSaveFileName(self)
        with open(fname,'w') as f:
            self.a.dump_analysis(f)

    def actionOpen_File_to_Analyze(self):
        files,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getOpenFileNames(self)
        from os.path import isfile
        for fname in files:

            if isfile(fname):
                with open(fname,'r') as f:
                    d = QtWidgets.QProgressDialog("Analyzing File","Sorry, can't cancel this shit.",0,100,self)
                    data = f.read()
                    d.setAutoClose(False)
                    d.setAutoReset(False)
                    d.show()

                    t = threading.Thread(target=self.a.analyse, args=(data,(lambda s,i: d.setLabelText(s) and d.setValue(i*100)),(lambda: d.close())))
                    t.start()


def analyse(args):
    """
    Handles the analyse subcommand.
    """
    lyzer = Analyzer()

    for filen in args.inFile:
        lyzer.analyse(filen.read())

    outFile = args.outFile
    ofN = outFile.name

    lyzer.dump_analysis(args.outFile)

    outFile.close()

def visualize(args):
    lyzer = Analyzer.from_dump(args.inFile)

def gui(args):
    
    app = QtWidgets.QApplication(sys.argv)
    myapp = GuiForm(args)
    myapp.show()
    sys.exit(app.exec_())

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

    parser_viz = subparsers.add_parser(
        'visualize', help='visualize help', aliases=['v'])
    parser_viz.add_argument(
        'inFile', type=argparse.FileType('r', encoding='UTF-8'),
        help='Output of analyze to visualize.')
    parser_viz.set_defaults(func=visualize)

    parser_gui = subparsers.add_parser(
        'gui', help='gui help', aliases=['g'])
    parser_gui.add_argument(
        'inFile',nargs='?', type=argparse.FileType('r', encoding='UTF-8'),
        help='Output of analyze to visualize.')
    parser_gui.set_defaults(func=gui)


    args = parser.parse_args()
    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":

    main()