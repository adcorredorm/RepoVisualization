import sys
import json
from antlr4 import FileStream, CommonTokenStream
from gen.Python3Lexer import Python3Lexer
from gen.Python3Parser import Python3Parser
from definitionsVisitor import DefinitionsVisitor

def get_definitions(file_path):
    input_stream = FileStream(file_path)
    lexer = Python3Lexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = Python3Parser(stream)
    
    tree = parser.file_input()
    visitor = DefinitionsVisitor()
    return visitor.visit(tree)

if __name__ == "__main__":
    definitions = get_definitions(sys.argv[0])
    with open('definitions.json', 'w+') as f:
        f.write(json.dumps(definitions, indent = 2))
