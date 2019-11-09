# Postfix
A mini stack language implemented from scratch in python.
* Read-eval-print-loop
* Store and load variables
* Stack operations
* Error traceback

## Usage
* Run the 'postfix' executable. The read-eval-print-loop for postfix will pop up. Start writing code.
* Running on the terminal: ``` python postfix.py ``` for the Postfix REPL
* ``` python postfix.py [file_path] [args] ``` to run a *.postfix file and pass in some arguments
* Additionally, you can initialize the REPL with optional arguments using the following command ``` python postfix.py 'repl' [args] ```

## Examples
* ``` ("Hello, world!" prs) ``` prints "Hello, world!"
* ``` (1 2 3 add add) ``` results in __7__
* ``` ((3 2 sub) exec (4 2 mul) exec mul)  ``` results in __8__
* ``` ((1 get mul) "prog" store 1 2 3 "prog" load exec) results in __9__

## Syntax
Full specification of this language can be found here: https://cs.wellesley.edu/~cs251/s05/postfix.pdf
