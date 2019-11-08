"""
*** Postfix: A Simple Stack Language (Postfix)
*** Implementation with additional features

TODO:
 1. File not found error
 2. Special output signal
 3. Fix empty string stview none error

"""

import sys
import os
import signal

class Postfix(object):

    def __init__(self):
        self._vm = VirtualMachine()
        self.instructions = []
        self.nums = ['0','1','2','3','4','5','6','7','8','9','.']
        self.keywords = ['add','mul','sub','div','rem','lt','le','eq','ne','gt','ge','push','swap','pop','sel','get','put','prs','pri','exec','quit','stview','stclear']
        self.argsto = None

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
            if tokens[1][0] != 'postfix':
                self._vm.give_error('Lexing', 'Cannot recognize program, missing `postfix` token.')
            tokens.pop()
            tokens = tokens[2:]
            return tokens
        else:
            self._vm.give_error('Lexing', 'Cannot recognize program.')

    def prepare_instructions(self, tokens):
        instructions = []
        getseq = False
        seq = []
        for i in tokens:
            if getseq:
                if i[0][0] == ')':
                    getseq = False
                    oparg = ('push', tuple(seq))
                seq.append(i)
            elif i[0][0] == '"':
                oparg = ('push', i[0])
            elif i[0][0] in self.nums:
                oparg = ('push', self.convert_number(i[0]))
            elif i[0][0] == '(':
                getseq = True
            elif i[0] in self.keywords:
                oparg = (i[0], None)
            else:
                self._vm.give_error('Parse', 'Cannot parse program, undefined token.')
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

    def run_program(self, program):
        if self.argsto:
            self._vm.stack += self.check_args(self.argsto)
            self.argsto = None
        instructions = self.prepare_instructions(self.lexer(program))
        self._vm.cur_program = program
        self._vm.execute_program(instructions)

    def runFile(self, path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        rel_path = path
        abs_file_path = os.path.join(script_dir, rel_path)
        if os.path.exists(abs_file_path): full_path = abs_file_path
        else: full_path = path
        with open(full_path, 'r') as content_file:
            content = content_file.read()
            print(content)
            self.run_program(content)

    def repl(self):
        signal.signal(signal.SIGINT, self.keyboardInterruptHandler)
        print("Postfix Language REPL")
        while True:
            getin = input("postfix>> ")
            self.run_program(getin)

class VirtualMachine(object):

    def __init__(self):
        self.stack = []
        self.environment = {}
        self.counter = 0
        self.current_op = (None, None)
        self.executed_code = []
        self.cur_program = None
        self.special_output = False
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

    def is_empty(self):
        return not len(self.stack) > 0

    def __len__(self):
        return len(self.stack)

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
        self.executed_code += program
        while len(self.executed_code) > self.counter:
            opr = self.executed_code[self.counter]
            op = opr[0]
            fn,bin = self.find_op(op)
            arg = opr[1]
            char = opr[2]
            self.current_op = (op,char)
            if arg is not None:
                fn(arg)
            else:
                if bin:
                    fn(op)
                else:
                    fn()
            self.counter += 1
        if not self.special_output and not self.is_empty():
            print(self.stack[-1])
        elif self.is_empty():
            print('None')
        elif self.special_output:
            self.special_output = False

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
            if self.stack[-1] == 0: self.push_error('Cannot divide by zero')
            else: return True
        elif type=='two_numbers':
            if not self.type_check(self.stack[-1], self.numerals) or not self.type_check(self.stack[-2], self.numerals):
                self.push_error('Values should be integers')
        elif type=='last_number':
            if not self.type_check(self.stack[-1], self.numerals): self.push_error('Last value is not a number')
            else: return True
        elif type=='last_in_range':
            if self.stack[-1] >= 1 and self.stack <= len(self): self.push_error('Last value is not a valid stack index')
            else: return True
        elif type=='last_string':
            if not self.type_check(self.stack[-1], [str]): self.push_error('Last value is not a number')
            else: return True
        elif type=='last_executable':
            if not self.type_check(self.stack[-1], [tuple]): self.push_error('Last value is not an executable sequence')
            else: return True
        return True

    def cond_error(self, *args):
        l = []
        for arg in args:
            l.append(int(self.error_handler(arg)))
        if sum(l) == len(l):
            return True
        return False

    def give_error(self, type = 'Stack', message =''):
        print(type.upper() + ' Error: ' + message)
        exit(0)

    def push_error(self, message = ''):
        src, opref = self.current_op[0], self.current_op[1]
        print(src.upper() + ' Error: ' + message + '. [at character ' + str(opref) + ']')
        trace_beg = min(15,len(self.cur_program[:opref]))
        trace_end = min(15,len(self.cur_program[opref:]))
        print("Trace: \"" + ''.join(self.cur_program[opref-trace_beg:opref+trace_end]) + "\"")
        for i in range(trace_beg + 7):
            print(" ", end="")
        print("^")

    def op_push(self, *args):
        for arg in args:
            self.stack.append(arg)

    def op_swap(self):
        if self.cond_error('two_values'):
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack.append(a)
            self.stack.append(b)

    def op_pop(self):
        if self.cond_error('empty'):
            self.stack.pop()

    def do_binary(self, type):
        if self.cond_error('two_values', 'two_numbers'):
            a = self.stack.pop()
            b = self.stack.pop()
            if type in ['div', 'rem'] and not self.cond_error('zero_div'):
                self.stack.append(self.binary_op[type](a, b))
            else:
                self.stack.append(self.binary_op[type](a, b))

    def op_sel(self):
        if self.cond_error('three_values', 'last_number'):
            a = self.stack.pop()
            b = self.stack.pop()
            c = self.stack.pop()
            if c == 0:
                self.stack.append(a)
            else:
                self.stack.append(b)

    def op_get(self):
        if self.cond_error('empty', 'last_number', 'last_in_range'):
            a = self.stack.pop()
            self.stack.append(self.stack[-a])

    def op_put(self):
        if self.cond_error('two_values', 'last_number', 'last_in_range'):
            a = self.stack.pop()
            b = self.stack.pop()
            self.stack[-a] = b

    def op_prs(self):
        if self.cond_error('empty', 'last_string'):
            print(self.stack.pop())
            self.special_output = True

    def op_pri(self):
        if self.cond_error('empty', 'last_number'):
            print(self.stack.pop())
            self.special_output = True

    def op_exec(self):
        if self.cond_error('empty', 'last_executable'):
            self.executed_code = list(self.stack.pop()) + self.executed_code

    def op_stview(self):
        if self.cond_error('empty'):
            print('postfix.stack -> ' + ' '.join([str(i) for i in self.stack]))
            self.special_output = True

    def op_stclear(self):
        self.stack = []

    def op_quit(self):
        exit(0)

if __name__ == '__main__':
    pf = Postfix()
    pf.main()
