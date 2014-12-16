#!/usr/bin/python3

import nltk,argparse,queue,sys,threading
import multiprocessing as mp

from PyQt5 import QtCore, QtGui, QtWidgets
from nltvis import *
from nltvis_ui import Ui_MainWindow

def get_parser_location():
    import os, urllib.request, zipfile
    __path__ = os.path.dirname(os.path.realpath(__file__))
    if not os.path.isdir(__path__+'/lib'):
        os.mkdir(__path__+'/lib')
    if not os.path.isdir(__path__+'/lib/stanford-parser-full-2014-10-31'):
        file_name, headers = urllib.request.urlretrieve("http://nlp.stanford.edu/software/stanford-parser-full-2014-10-31.zip")
        zfile = zipfile.ZipFile(file_name)
        zfile.extractall(__path__+'/lib/')
    nltk.download('punkt')
    return __path__+'/lib/stanford-parser-full-2014-10-31'

class Analyzer(object):

    def __init__(self,*args,**kwargs):
        parser_loc = get_parser_location()
        self.parser = nltk.parse.stanford.StanfordParser(
            path_to_jar=parser_loc+"/stanford-parser.jar",
            path_to_models_jar=parser_loc+"/stanford-parser-3.5.0-models.jar",
            model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz",
            encoding = 'UTF-8',
            verbose = True,
            java_options = '-mx2000m'
        )
        self.sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
        self.tree = CountingProbabilisticTree('ROOT', [], prob=1.0)

    def analyse(self, s, status_callback=None, complete_callback=None):
        
        status_callback = (lambda *args: print(" ".join(str(a) for a in args)) ) if not hasattr(status_callback, '__call__') else status_callback
        complete_callback = (lambda *args: print(" ".join(str(a) for a in args)) ) if not hasattr(complete_callback, '__call__') else complete_callback
        
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
        status_callback("Merging Parse Trees... %s/%s"%(n,ntrees), 0.2+0.8*(n/ntrees))
        
        for tree in trees:
            tc += len(tree.leaves())
            self.tree.merge(tree)
            n+=1
            status_callback("Merging Parse Trees... %s/%s"%(n,ntrees), 0.2+0.8*(n/ntrees))
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

        self.scene = QtWidgets.QGraphicsScene(self.ui.graphicsView)
        
        self.ui.graphicsView.setScene(self.scene)

        if self.argv.inFile is not None:
            with self.argv.inFile as f:
                self.a = Analyzer.from_dump(f)
            self.updateVisualization()
    
    def actionOpen_Analysis(self):
        fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getOpenFileName(self)
        from os.path import isfile
        if isfile(fname):
            with open(fname,'r') as f:
                self.a = Analyzer.from_dump(f)
            self.updateVisualization()

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

                    t = threading.Thread(
                        target=self.a.analyse, 
                        args=(data,
                            (lambda s,i: d.setLabelText(s) and d.setValue(i*100)),
                            (lambda: d.close() and self.updateVisualization())
                        )
                    )
                    t.start()

    def updateVisualization(self):
        Q = queue.Queue()
        leaves = self.a.tree.leaves()
        U = sorted(self.a.tree.unique_labels())
        magU = len(U)
        L = len(leaves)
        rect = QtCore.QRectF(0.0,0.0,3000.0,3000.0)
        for vk in list(self.a.tree):
            uk = vk.label() 
            if not isinstance(vk,CountingProbabilisticTree):
                uk = '"'+uk+'"'
            k = U.index(uk)
            mrect = QtCore.QRectF(rect.x(),rect.y()+k*rect.height()/magU,rect.width(),rect.height()/magU)
            Q.put((mrect, vk, self.a.tree))

        pen = QtGui.QPen()
        pen.setWidth(0)
        self.scene.addRect(rect, pen=pen, brush=QtGui.QBrush(QtGui.QColor(255,255,255,127)) )
        while not Q.empty():
            rect,vk,vl = Q.get()
            uk = vk.label() 
            if not isinstance(vk,CountingProbabilisticTree):
                uk = '"'+uk+'"'
            k = U.index(uk)
            l = 0
            p = 0.5
            C = list(vk) if isinstance(vk,CountingProbabilisticTree) else []
            nbar = L

            if vl is not None:
                l = U.index(vl.label())
                p = float(vk.count) / float(vl.count)
                nbar = sum(ci.count for ci in C)
            
            if isinstance(vk,CountingProbabilisticLeaf):
                color = QtGui.QColor(int(255*k/magU),int(255*l/magU),int(255*p),255)
                print((rect,(int(255*k/magU),int(255*l/magU),int(255*p),255)))

                self.scene.addRect(rect, pen=pen, brush=QtGui.QBrush(color) )
            else:
                x0 = rect.x()
                y0 = rect.y()
                deltaX = rect.width()
                deltaY = rect.height()
                if deltaX<deltaY:
                    for vj in C:
                        uj = vj.label()
                        if not isinstance(vj,CountingProbabilisticTree):
                            uj = '"' + uj + '"'
                        y1=y0+(U.index(uj)/magU)*deltaY
                        Q.put((QtCore.QRectF(x0,y1,deltaX,deltaY/magU),vj,vk))
                else:
                    for vj in C:
                        uj = vj.label()
                        if not isinstance(vj,CountingProbabilisticTree):
                            uj = '"' + uj + '"'
                        x1=x0+(U.index(uj)/magU)*deltaX
                        Q.put((QtCore.QRectF(x1,y0,deltaX/magU,deltaY),vj,vk))
                        #x0 += deltaX*p


        #self.scene.addRect(rect,brush=QtGui.QBrush(QtGui.QColor(255,0,0,127)))



def analyse(args):
    """
    Handles the analyse subcommand.
    """
    lyzer = Analyzer()
    outFile = args.outFile
    ofN = outFile.name
    outFile.close()

    n = 0
    N = len(args.inFile)

    for filen in args.inFile:
        n += 1
        print("Analyzing %d/%d: %s"%(n,N,filen.name))
        try:
            lyzer.analyse(filen.read())
        except Exception as ex:
            print(ex)
        finally:
            with open(ofN,'w') as outFile:
                lyzer.dump_analysis(outFile)

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
    #parser.set_defaults(func=gui)
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
        'inFile', nargs='?', type=argparse.FileType('r', encoding='UTF-8'),
        help='Output of analyze to visualize.')
    parser_gui.set_defaults(func=gui)


    args = parser.parse_args()

    if 'func' in args:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":

    main()
