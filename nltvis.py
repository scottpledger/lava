import nltk.parse.stanford, nltk.tree
import argparse,math

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

class CountingProbabilisticNode(object):
    __ne__ = lambda self, other: not self == other
    __gt__ = lambda self, other: not (self < other or self == other)
    __le__ = lambda self, other: self < other or self == other
    __ge__ = lambda self, other: not self < other



class CountingProbabilisticLeaf(CountingProbabilisticNode,nltk.probability.ProbabilisticMixIn):

    def __init__(self,label,**prob_kwargs):
        self.count = 1
        self._label = label.upper()
        nltk.probability.ProbabilisticMixIn.__init__(self,**prob_kwargs)

    def label(self):
        return self._label

    def set_label(self,label):
        self._label = label

    def __eq__(self,other):
        if isinstance(other, CountingProbabilisticLeaf):
            return self._label == other.label()
        elif isinstance(other, nltk.compat.string_types):
            return self._label == other.upper()
        else:
            return False

    def __lt__(self,other):
        if isinstance(other, CountingProbabilisticNode):
            return self._label < other.label()
        elif isinstance(other, nltk.compat.string_types):
            return self._label < other.upper()
        return self.__class__.__name__ < other.__class__.__name__

    
    def __repr__(self):
        return '(%r (p=%r))' % (self._label, self.prob())

    def __str__(self):
        return '%s(p=%.6g)' % (self._label, self.prob())

    def normalize(self):
        pass

    def merge(self,other):
        pass

    def mprint(self,depth=0):
        return (' '*depth)+self._label+' '+str(self.count)

    def unique_labels(self,cls=CountingProbabilisticNode):
        return ['"'+self.label()+'"']

    def tcount(self):
        return self.count

class CountingProbabilisticTree(CountingProbabilisticNode,nltk.tree.ProbabilisticTree):

    def __init__(self,node, children=None, **prob_kwargs):
        self.count = 1
        node = node.upper()
        nltk.tree.ProbabilisticTree.__init__(self,node,children,**prob_kwargs)

    def merge(self,tree):
        if isinstance(tree,nltk.tree.Tree):
            for c in list(tree):
                cl = c if isinstance(c, nltk.compat.string_types) else c.label().upper()
                if cl in self:
                    self[cl].count += 1
                else:
                    nc = None
                    if isinstance(c,nltk.tree.Tree):
                        nc = CountingProbabilisticTree(cl, [])
                    else:
                        nc= CountingProbabilisticLeaf(cl)
                    self += [nc]
                self[cl].merge(c)

        self.normalize()

    def tcount(self):
        return sum(s.count for s in self)

    def __contains__(self,item):
        l = item.label() if isinstance(item,nltk.tree.Tree) else item
        for i in list(self):
            if isinstance(i,nltk.tree.Tree):
                if i.label()==l:
                    return True
            elif i==l or i==item:
                return True
        return False

    def __getitem__(self,item):
        if isinstance(item, nltk.compat.string_types):
            l = item
            if isinstance(item,nltk.tree.Tree):
                l = item.label()
            labels = [i.label() if isinstance(i,nltk.tree.Tree) else i for i in list(self)]
            item = labels.index(l)
        return nltk.tree.ProbabilisticTree.__getitem__(self,item)

    def __repr__(self):
        return '%s (p=%r)' % (nltk.tree.Tree.unicode_repr(self), self.prob())
    def __str__(self):
        return '%s (p=%.6g)' % (self.pprint(margin=60), self.prob())

    def normalize(self):
        s = sum(c.count for c in self)
        logs = math.log(s)
        for c in list(self):
            c.set_prob(float(c.count/s))
            c.normalize()

    def __eq__(self,other):
        if isinstance(other, CountingProbabilisticTree):
            return self.label().upper() == other.label().upper()
        return nltk.tree.ProbabilisticTree.__eq__(self,other)

    def __lt__(self,other):
        if isinstance(other, CountingProbabilisticNode):
            return self.label() < other.label()
        return nltk.tree.ProbabilisticTree.__lt__(self,other)

    def pprint(self,*args,**kwargs):
        return nltk.tree.ProbabilisticTree.pprint(self,*args,**kwargs)+' (p=%.6g)'%self.prob()

    def total_count(self):
        q = self.leaves()
        return sum(c.count for c in q)
    
    def mprint(self,depth=0):
        return (' '*depth)+self._label+' '+str(self.count)+'\n'+'\n'.join(c.mprint(depth+1) for c in list(self))

    def unique_labels(self,cls=CountingProbabilisticNode):
        subs = [self.label()]
        for c in list(self):
            if isinstance(c, cls):
                subs += c.unique_labels(cls)
        return list(set(subs))

    @classmethod
    def from_mprint(cls,s):
        
        lines = s.split("\n")
        line1 = lines[0].split(" ")

        parent = CountingProbabilisticTree(line1[0],[],prob=1.0)
        parent.count = int(line1[1])
        path = [parent] + [None for s in lines]

        for i in range(1,len(lines)):
            line = lines[i]
            parts = line.split(" ")
            
            cls = lambda x: CountingProbabilisticLeaf(x,prob=1.0)
            if i < len(lines)-1:
                nparts = lines[i+1].split(" ")
                if len(nparts)>len(parts):
                    cls = lambda x: CountingProbabilisticTree(x,[],prob=1.0)
            
            itm = cls(parts[-2])
            itm.count = int(parts[-1])
            
            path[len(parts)-3] += [itm]
            path[len(parts)-2] = itm
        parent.normalize()
        return parent