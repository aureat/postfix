"""
*** Postfix: A Simple Stack Language (Postfix)
*** Implementation with additional features

https://github.com/altunh/postfix
"""

import sys
import os
import signal

class Postfix(object):

    def __init__(self):
        self._vm = VirtualMachine()
        self.instructions = []
        self.nums = ['0','1','2','3','4','5','6','7','8','9','.']
        self.keywords = ['add','mul','sub','div','rem','lt','le','eq','ne','gt','ge',
                         'push','swap','pop','sel','get','put','prs','pri','exec',
                         'quit','stview','stclear','sysenv','store','load','del']
        self.argsto = None
        self.program = None

    def main(self):
        arglen = len(sys.argv)
        pyfile = sys.argv[0]
        if arglen < 2:
            self.repl()
        elif sys.argv[1] == 'repl':
            if arglen > 2:
                self.argsto = sys.argv[2:]
            self.repl()
        elif arglen == 2:
            self.runFile(sys.argv[1])
        elif arglen > 2:
            self.argsto = sys.argv[2:]
            self.runFile(sys.argv[1])
        else:
            self._vm.give_error('Usage', 'usage : postfix repl/[path] args')

    def keyboardInterruptHandler(self, signal, frame):
        exit(0)

    def lexer(self, program):
        if type(program) is str:
            if program[0] != '(':
                self.error(program, 'Lexer', 0,'Missing paranthesis.')
                return []
            if program[-1] != ')':
                self.error(program, 'Lexer', len(program)+1, 'Missing paranthesis')
                return []
            self.program = program
            code = program[:]
            tokens = []
            char = 0
            token = ''
            get = False
            for i,c in enumerate(code):
                if get and c == ' ':
                    tokens.append((token, char))
                    get = False
                    token = ''
                elif c == ' ': pass
                elif c == '(' or c == ')': tokens.append((c, i))
                else:
                    if not get:
                        char = i
                    token += c
                    get = True
                    try:
                        if code[i+1] == '(' or code[i+1] == ')':
                            tokens.append((token, char))
                            get = False
                            token = ''
                    except IndexError:
                        pass
            # if tokens[1][0] != 'postfix':
            #     self._vm.give_error('Lexing', 'Cannot recognize program, missing `postfix` token.')
            tokens.pop()
            tokens = tokens[1:]
            return tokens
        else:
            self._vm.give_error('Lexer', 'Cannot recognize program.')

    def prepare_instructions(self, tokens):
        instructions = []
        getseq = False
        seq = []
        for i in tokens:
            f = True
            if getseq:
                if i[0][0] == ')':
                    getseq = False
                    oparg = ('push', self.prepare_instructions(seq))
                    seq = []
                    f = True
                else:
                    getseq = True
                    seq.append(i)
                    f = False
            elif i[0][0] == '"':
                oparg = ('push', i[0][1:-1])
            elif i[0][0] in self.nums:
                oparg = ('push', self.convert_number(i[0]))
            elif i[0][0] == '(':
                getseq = True
                f = False
            elif i[0] in self.keywords:
                oparg = (i[0], None)
            else:
                self.error(self.program, 'Parse', i[1], 'Cannot parse program, undefined token')
                f = False
            if f:
                instructions.append((oparg[0], oparg[1], i[1]))
        return instructions

    def convert_number(self, num):
        try:
            num = int(num)
        except ValueError:
            try:
                num = float(num)
            except ValueError:
                self._vm.give_error('Parse','Cannot parse numbers.')
                quit()
        return num

    def check_args(self, args):
        truth = []
        for e,i in enumerate(args):
            if i[0] == "\'" and i[-1] == "\'":
                args[e] = str(i[1:-1])
            else:
                args[e] = self.convert_number(i)
            for ty in [int,float,str]:
                if type(i) is ty:
                    truth.append(1)
                    continue
                truth.append(0)
        if sum(truth) < len(args):
            self._vm.give_error('Argument','`' + str(args[truth.index(0)]) + '` is not a valid argument.')
        return args

    def error(self, program, name, char, text):
        self._vm.env['program'] = program
        self._vm.env['operation'] = (name,char)
        self._vm.push_error(text)

    def run_program(self, program):
        if self.argsto:
            self._vm.env['stack'] += self.check_args(self.argsto)
            self.argsto = None
        instructions = self.prepare_instructions(self.lexer(program))
        self._vm.env['program'] = program
        self._vm.execute_program(instructions)

    def runFile(self, path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = path
        abs_file_path = os.path.join(script_dir, rel_path)
        if os.path.exists(abs_file_path):
            full_path = abs_file_path
        else:
            full_path = path
        try:
            with open(full_path, 'r') as content_file:
                content = content_file.read()
                self.run_program(content)
        except IOError:
            self._vm.give_error('File', 'No such file found')

    def repl(self):
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)
        print("Postfix Language REPL")
        while True:
            getin = input("postfix]> ")
            self.run_program(getin)

class VirtualMachine(object):

    def __init__(self):
        self.env = {
            'program': None,
            'operation': (None, None),
            'stack': [],
            'spoutput': False,
            'excode': [],
            'haserror': False,
            'counter': 0,
        }
        self.binary_op = {
            'add': lambda a,b: a+b,
            'sub': lambda a,b: b-a,
            'mul': lambda a,b: a*b,
            'div': lambda a,b: b/a,
            'rem': lambda a,b: b - (b/a)*a,
            'lt': lambda a,b: int(a>b),
            'le': lambda a,b: int(a>=b),
            'eq': lambda a,b: int(a==b),
            'ne': lambda a,b: int(a!=b),
            'gt': lambda a,b: int(a<b),
            'ge': lambda a,b: int(a<=b),
        }
        self.numerals = [int, float]
        self.signals = {
            'lexer_error': False
        }

    def is_empty(self):
        return not len(self.env['stack']) > 0

    def __len__(self):
        return len(self.env['stack'])

    def find_op(self, op):
        try:
            main = getattr(self, 'op_'+op)
            return main, False
        except AttributeError:
            if op in self.binary_op:
                main = getattr(self, 'do_binary')
                return main, True
            else:
                self.give_error('VirtualMachine', 'Operation not found')

    def execute_program(self, program):
        self.env['haserror'] = False
        self.env['excode'] += program
        while len(self.env['excode']) > self.env['counter']:
            opr = self.env['excode'][self.env['counter']]
            op = opr[0]
            fn,bin = self.find_op(op)
            arg = opr[1]
            char = opr[2]
            self.env['operation'] = (op,char)
            if arg is not None:
                fn(arg)
            else:
                if bin:
                    fn(op)
                else:
                    fn()
            self.env['counter'] += 1
        if self.env['spoutput']:
            self.env['spoutput'] = False
        elif not self.env['haserror'] and not self.is_empty():
            print(self.env['stack'][-1])
        elif not self.env['haserror'] and self.is_empty():
            print('None')

    def type_check(self, obj, lst):
        for i in lst:
            if type(obj) is i:
                return True
        return False

    def error_handler(self, type):
        if type=='empty':
            if not self.is_empty(): return True
            else: self.push_error('No value to perform operation')
        elif type=='two_values':
            if len(self) > 1: return True
            else: self.push_error('Not enough values to perform operation')
        elif type=='three_values':
            if len(self) > 2: return True
            else: self.push_error('Not enough values to perform operation')
        elif type=='zero_div':
            if self.env['stack'][-1] == 0: self.push_error('Cannot divide by zero')
            else: return True
        elif type=='two_numbers':
            if not self.type_check(self.env['stack'][-1], self.numerals) or not self.type_check(self.env['stack'][-2], self.numerals):
                self.push_error('Values should be integers')
        elif type=='last_number':
            if not self.type_check(self.env['stack'][-1], self.numerals): self.push_error('Last value is not a number')
            else: return True
        elif type=='last_in_range':
            if self.env['stack'][-1] >= 1 and self.env['stack'][-1] <= len(self): return True
            else: self.push_error('Last value is not a valid stack index')
        elif type=='last_string':
            if not self.type_check(self.env['stack'][-1], [str]): self.push_error('Last value is not a number')
            else: return True
        elif type=='last_executable':
            if not self.type_check(self.env['stack'][-1], [list]): self.push_error('Last value is not an executable sequence')
            else: return True
        return True

    def cond_error(self, *args):
        l = []
        for arg in args:
            l.append(int(self.error_handler(arg)))
            if self.env['haserror']:
                return False
        if sum(l) == len(l):
            return True
        return False

    def give_error(self, type = 'Stack', message =''):
        print(type.upper() + ' Error: ' + message)
        exit(0)

    def push_error(self, message = ''):
        self.env['haserror'] = True
        src, opref = self.env['operation'][0], self.env['operation'][1]
        print(src.upper() + ' Error: ' + message + ' [at character ' + str(opref) + ']')
        trace_beg = min(25,len(self.env['program'][:opref]))
        trace_end = min(25,len(self.env['program'][opref:]))
        print("Trace: \"" + ''.join(self.env['program'][opref-trace_beg:opref+trace_end]) + "\"")
        for i in range(trace_beg + 7):
            print(" ", end="")
        print("^")

    def op_push(self, *args):
        for arg in args:
            self.env['stack'].append(arg)

    def op_swap(self):
        if self.cond_error('two_values'):
            a = self.env['stack'].pop()
            b = self.env['stack'].pop()
            self.env['stack'].append(a)
            self.env['stack'].append(b)

    def op_pop(self):
        if self.cond_error('empty'):
            self.env['stack'].pop()

    def do_binary(self, type):
        if self.cond_error('two_values', 'two_numbers'):
            a = self.env['stack'].pop()
            b = self.env['stack'].pop()
            if type in ['div', 'rem'] and not self.cond_error('zero_div'):
                self.env['stack'].append(self.binary_op[type](a, b))
            else:
                self.env['stack'].append(self.binary_op[type](a, b))

    def op_sel(self):
        if self.cond_error('three_values', 'last_number'):
            a = self.env['stack'].pop()
            b = self.env['stack'].pop()
            c = self.env['stack'].pop()
            if c == 0:
                self.env['stack'].append(a)
            else:
                self.env['stack'].append(b)

    def op_get(self):
        if self.cond_error('empty', 'last_number', 'last_in_range'):
            a = self.env['stack'].pop()
            self.env['stack'].append(self.env['stack'][-a])

    def op_put(self):
        if self.cond_error('two_values', 'last_number', 'last_in_range'):
            a = self.env['stack'].pop()
            b = self.env['stack'].pop()
            self.env['stack'][-a] = b

    def op_prs(self):
        if self.cond_error('empty', 'last_string'):
            print(self.env['stack'].pop())
            self.env['spoutput'] = True

    def op_pri(self):
        if self.cond_error('empty', 'last_number'):
            print(self.env['stack'].pop())
            self.env['spoutput'] = True

    def op_exec(self):
        if self.cond_error('empty', 'last_executable'):
            self.env['excode'] += list(self.env['stack'].pop())

    def op_stview(self):
        if self.cond_error('empty'):
            print('postfix.stack -> ' + ' '.join([str(i) for i in self.env['stack']]))
            self.env['spoutput'] = True

    def op_stclear(self):
        self.env['stack'] = []

    def op_quit(self):
        exit(0)

    def op_store(self):
        if self.cond_error('two_values','last_string'):
            v1 = self.env['stack'].pop()
            v2 = self.env['stack'].pop()
            self.env.update({v1: v2})

    def op_load(self):
        name = self.env['stack'].pop()
        self.env['stack'].append(self.env[name])

    def op_del(self):
        name = self.env['stack'].pop()
        val = self.env.pop(name, None)

    def op_sysenv(self):
        print(self.env)

if __name__ == '__main__':
    pf = Postfix()
    pf.main()
