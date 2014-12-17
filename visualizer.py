#!/usr/bin/python3

import nltk,argparse,queue,sys,threading
import multiprocessing as mp

from PyQt5 import QtCore, QtGui, QtWidgets
from nltvis import *
from nltvis_ui import Ui_MainWindow
from nltvis_image_dialog_ui import Ui_DimensionDialog

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

default_callback = (lambda *args: print(" ".join(str(a) for a in args)) )

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
        
        status_callback = default_callback if not hasattr(status_callback, '__call__') else status_callback
        complete_callback = default_callback if not hasattr(complete_callback, '__call__') else complete_callback
        
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

class Visualizer(object):

    @classmethod
    def gen_image(cls,tree, **kwargs):
        width=1000 if 'width' not in kwargs else kwargs['width']
        height=1000 if 'height' not in kwargs else kwargs['height']
        pixMin=3.0 if 'pixMin' not in kwargs else kwargs['pixMin']
        alphaMin=127 if 'alphaMin' not in kwargs else kwargs['alphaMin']
        status_callback = default_callback if 'status_callback' not in kwargs else status_callback
        complete_callback = default_callback if 'complete_callback' not in kwargs else complete_callback

        Q = queue.Queue()
        leaves = tree.leaves()
        

        U = sorted(tree.unique_labels())
        V = [u for u in U if u[0]!='"']
        magU = len(U)
        magV = len(V)
        L = len(leaves)
        rect = QtCore.QRectF(0.0,0.0,width-pixMin,height-pixMin)
        pxmp = QtGui.QPixmap(width,height)

        painter = QtGui.QPainter(pxmp)
        painter.fillRect(QtCore.QRectF(0,0,width,height),QtGui.QColor(127,127,127,255))

        def paintRect(rect,color):
            #print((rect,"QColor(%s, %s, %s, %s)"%(color.red(),color.green(),color.blue(),color.alpha())))
            painter.fillRect(rect,color)

        for vk in list(tree):
            uk = vk.label() 
            if not isinstance(vk,CountingProbabilisticTree):
                uk = '"'+uk+'"'
            k = V.index(uk)
            mrect = QtCore.QRectF(rect.x(),rect.y()+k*rect.height()/magV,rect.width(),rect.height()/magV)
            Q.put((mrect, vk, tree))

        pen = QtGui.QPen(QtGui.QColor(0,0,0,0))
        pen.setWidth(0)
        
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
                p = float(vk.count) / float(vl.tcount())
                nbar = sum(ci.count for ci in C)
            
            
                
            mrect = QtCore.QRectF(rect.x(),rect.y(),max(pixMin,rect.width()),max(pixMin,rect.height()))
            color = (int(255*k/magU), int(255*l/magU), int(255*p), alphaMin+int((255-alphaMin)*0.5*(rect.width()/mrect.width()+rect.height()/mrect.height())))
            paintRect(mrect, QtGui.QColor(*color))

            if not isinstance(vk,CountingProbabilisticLeaf):
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
                        
        del painter
        return pxmp

        #self.scene.addRect(rect,brush=QtGui.QBrush(QtGui.QColor(255,0,0,127)))

class DimensionInputDialog(QtWidgets.QDialog):

    def __init__(self, argv, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = Ui_DimensionDialog()
        self.ui.setupUi(self)

    def get_dimensions(self):
        return (self.ui.spinBox.value(), self.ui.spinBox_2.value())

    def get_min_pixel_size(self):
        return self.ui.doubleSpinBox.value()

class GuiForm(QtWidgets.QMainWindow):
    def __init__(self, argv, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.visualized = False
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        self.ui.actionNew_Analysis.triggered.connect(self.actionNew_Analysis)
        self.ui.actionOpen_Analysis.triggered.connect(self.actionOpen_Analysis)
        self.ui.actionSave_Analysis.triggered.connect(self.actionSave_Analysis)

        self.ui.actionOpen_File_to_Analyze.triggered.connect(self.actionOpen_File_to_Analyze)

        self.ui.actionSave_Image.triggered.connect(self.actionSave_Image)

        self.dimDialog = DimensionInputDialog(self)

        self.a = Analyzer()
        self.argv = argv

        self.scene = QtWidgets.QGraphicsScene(self.ui.graphicsView)
        
        self.ui.graphicsView.setScene(self.scene)
        self.pxmp_itm = self.scene.addPixmap(QtGui.QPixmap(1000,1000))

        if self.argv.inFile is not None:
            with self.argv.inFile as f:
                self.a = Analyzer.from_dump(f)
            self.updateVisualization()

    def actionNew_Analysis(self):
        self.a = Analyzer()
    
    def actionOpen_Analysis(self):
        fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getOpenFileName(self, filter="*.lava")
        from os.path import isfile
        if isfile(fname):
            
            d = QtWidgets.QProgressDialog("Opening Analysis","Sorry, can't cancel this shit.",0,100,self)
            d.setAutoClose(False)
            d.setAutoReset(False)
            d.show()

            def openFile(self,fname,d):
                with open(fname,'r') as f:
                    self.a = Analyzer.from_dump(f)
                self._updateVisualization()
                d.close()

            t = threading.Thread(
                target=openFile,
                args=(self,fname,d)
            )

            t.start()


    def actionSave_Analysis(self):
        fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getSaveFileName(self, filter="LaVa Files(*.lava)")
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
                            (lambda s,i: d.setLabelText(s) and d.setValue(int(i*100))),
                            (lambda: d.close() and self._updateVisualization())
                        )
                    )
                    #print(dir(d.canceled.connect(lambda: t.)))
                    t.start()

    def actionSave_Image(self):
        status = self.dimDialog.exec()

        if status == 1:
            
            #print(dims)
            fname,somethingElseIDontUnderstand = QtWidgets.QFileDialog.getSaveFileName(self, filter="Images(*.bmp *.gif *.jpg *.jpeg *.png)")

            d = QtWidgets.QProgressDialog("Saving Image","Sorry, can't cancel this shit.",0,100,self)
            d.setAutoClose(False)
            d.setAutoReset(False)
            d.show()

            def exportImg(self, fname, d):
                dims = self.dimDialog.get_dimensions()
                w,h = dims
                pxmp = Visualizer.gen_image(self.a.tree, width=w, height=h, pixMin=self.dimDialog.get_min_pixel_size())
                pxmp.save(fname)
                d.close()

            t = threading.Thread(
                target=exportImg,
                args=(self,fname,d)
            )

            t.start()

    def updateVisualization(self,threaded=True):
        if threaded:
            t = threading.Thread(
                target=self._updateVisualization,
                args=()
            )
            t.start()
        else:
            self._updateVisualization()

    def _updateVisualization(self):
        if self.visualized == False:
            self.visualized = True
        else:
            return
        print("Updating...")
        pxmp = Visualizer.gen_image(self.a.tree)
        self.pxmp_itm.setPixmap(pxmp)
        print("Done.")
        self.visualized = False



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
    app = QtWidgets.QApplication(sys.argv)
    print("Reading in Analysis...")
    lyzer = Analyzer.from_dump(args.inFile)
    print("Generating Image...")
    pxmp = Visualizer.gen_image(lyzer.tree, width=args.width, height=args.height, pixMin=args.pixMin)
    ofN = args.outFile.name
    print("Writing Image to %s..."%ofN)
    args.outFile.close()

    pxmp.save(ofN)
    #sys.exit(app.exec_())

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
    parser_viz.add_argument('width',type=int,help='Width of image')
    parser_viz.add_argument('height',type=int,help='Height of image')
    parser_viz.add_argument('pixMin',type=float,help='Minimum Pixel Size')
    parser_viz.add_argument(
        'outFile', type=argparse.FileType('w', encoding='UTF-8'),
        help='Image file to save to.')
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
