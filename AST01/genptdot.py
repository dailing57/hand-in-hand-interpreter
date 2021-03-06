import argparse
import textwrap

from numpy import save

from spi import PLUS, MINUS, MUL, DIV, INTEGER, LPAREN, RPAREN, Lexer


class Node(object):
    def __init__(self, name):
        self.name = name
        self.children = []

    def add(self, node):
        self.children.append(node)


class RuleNode(Node):
    pass


class TokenNode(Node):
    pass


class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.root = None
        self.current_node = None

    def error(self):
        raise Exception('Invalid syntax')

    def eat(self, token_type):
        if(self.current_token.type == token_type):
            self.current_node.add(TokenNode(self.current_token.value))
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        node = RuleNode('factor')
        self.current_node.add(node)
        _save = self.current_node
        self.current_node = node
        token = self.current_token
        if(token.type == INTEGER):
            self.eat(INTEGER)
        elif(token.type == LPAREN):
            self.eat(LPAREN)
            self.expr()
            self.eat(RPAREN)
        self.current_node = _save

    def term(self):
        node = RuleNode('term')
        self.current_node.add(node)
        _save = self.current_node
        self.current_node = node
        self.factor()
        while(self.current_token.type in (MUL, DIV)):
            token = self.current_token
            if(token.type == MUL):
                self.eat(MUL)
            elif(token.type == DIV):
                self.eat(DIV)
            self.factor()
        self.current_node = _save

    def expr(self):
        node = RuleNode('expr')
        if(self.root is None):
            self.root = node
        else:
            self.current_node.add(node)
        _save = self.current_node
        self.current_node = node
        self.term()
        while(self.current_token.type in (PLUS, MINUS)):
            token = self.current_token
            if(token.type == PLUS):
                self.eat(PLUS)
            elif(token.type == MINUS):
                self.eat(MINUS)
            self.term()
        self.current_node = _save

    def parse(self):
        self.expr()
        return self.root


class ParseTreeVisualizer(object):
    def __init__(self, parser) -> None:
        self.parser = parser
        self.ncount = 1
        self.dot_header = [textwrap.dedent("""\
        digraph astgraph {
          node [shape=none, fontsize=12, fontname="Courier", height=.1];
          ranksep=.3;
          edge [arrowsize=.5]

        """)]
        self.dot_body = []
        self.dot_footer = ['}']

    def bfs(self, node):
        ncount = 1
        queue = []
        queue.append(node)
        s = '  node{} [label="{}"]\n'.format(ncount, node.name)
        self.dot_body.append(s)
        node._num = ncount
        ncount += 1

        while queue:
            node = queue.pop(0)
            for child_node in node.children:
                s = '  node{} [label="{}"]\n'.format(ncount, child_node.name)
                self.dot_body.append(s)
                child_node._num = ncount
                ncount += 1
                s = '  node{} -> node{}\n'.format(node._num, child_node._num)
                self.dot_body.append(s)
                queue.append(child_node)

    def gendot(self):
        tree = self.parser.parse()
        self.bfs(tree)
        return ''.join(self.dot_header+self.dot_body+self.dot_footer)


argparser = argparse.ArgumentParser(
    description='Generate a Parse Tree DOT file.'
)
argparser.add_argument(
    'text',
    help='Arithmetic expression (in quotes): "1 + 2 * 3"'
)
args = argparser.parse_args()
text = args.text

lexer = Lexer(text)
parser = Parser(lexer)

viz = ParseTreeVisualizer(parser)
content = viz.gendot()
print(content)
