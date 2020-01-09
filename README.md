# Postfix
A mini stack language implemented from scratch in python.
* Stack-based VM
* Store and load variables
* Stack operations
* Error traceback
* Repl

## Usage
* Run the 'postfix' executable. The read-eval-print-loop for postfix will pop up. Start writing code.
* Running on the terminal: ``` python postfix.py ``` for the Postfix REPL
* ``` python postfix.py [file_path] [args] ``` to run a *.postfix file and pass in some arguments
* Additionally, you can initialize the REPL with optional arguments using the following command ``` python postfix.py 'repl' [args] ```

## Examples
* ``` (begin "Hello, world!" prs) ``` prints "Hello, world!"
* ``` (begin 1 2 3 add add) ``` results in __7__
* ``` (begin (3 2 sub) exec (4 2 mul) exec mul)  ``` results in __8__
* ``` (begin (1 get mul) prog store 1 2 3 prog load exec) ``` results in __9__

## Additional details
* Every command is either a stack instruction, a list of literals, or a literal
* Executed lists begin with the keyword 'begin'
* Executable lists do not have a prefix keyword, they can be executed by pushing the 'exec' command to the stack

## Syntax
Full specification of this language can be found here: https://cs.wellesley.edu/~cs251/s05/postfix.pdf
