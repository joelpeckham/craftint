# Lox.py
# This is the main entry point for the Lox interpreter.
# Written by: Joel Peckham.
# Last Modified: 2022-03-17.

import argparse, traceback
from LoxErrors import LoxError, TokenError, LoxRuntimeError
from Token import TokenType, Token
from Scanner import Scanner
# from Parser import Parser
# from Interpreter import Interpreter
# from Resolver import Resolver
# interpreter = Interpreter()

def run(source):
    scanner = Scanner(source)
    tokens = scanner.scanTokens()
    for token in tokens:
        print(token)
    # parser = Parser(tokens)
    # statements = parser.parse()


def runPrompt():
    while True:
        try:
            print("> ", end="")
            source = input()
            run(source)
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break
        except Exception as e:
            print(e)
            traceback.print_exc()
            exit(70)
            

def runFile(path):
    with open(path, "r") as f:
        source = f.read()
    try:
        run(source)
    except LoxError as e:
        print(e)
        exit(65)
    except LoxRuntimeError as e:
        print(e)
        exit(70)

# Get args from command line.
parser = argparse.ArgumentParser(description='Lox interpreter.')
parser.add_argument('file', nargs='?', default=None, help='The file to run.')
args = parser.parse_args()

# If no file is specified, run the REPL.
if args.file is None:
    runPrompt()
else:
    runFile(args.file)
