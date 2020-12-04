from antlr4 import *
from gen.Python3Parser import Python3Parser
from gen.Python3Visitor import Python3Visitor

class DefinitionsVisitor(Python3Visitor):

    definitions = {
        'functions': [],
        'imports': []
    }
    
    def visitFile_input(self, ctx:Python3Parser.FuncdefContext):
        self.visitChildren(ctx)
        return self.definitions

    def visitFuncdef(self, ctx:Python3Parser.FuncdefContext):
        self.definitions['functions'].append({
            'name': ctx.NAME().getText(),
            'line': ctx.NAME().getSymbol().line
        })
    
    def visitDotted_as_names(self, ctx:Python3Parser.FuncdefContext):
        self.definitions['imports'].extend(
            [self.visitDotted_as_name(node) for node in ctx.dotted_as_name()])

    def visitDotted_as_name(self, ctx:Python3Parser.Dotted_as_nameContext):
        alias = ctx.NAME()
        path, lib = self.visitDotted_name(ctx.dotted_name())
        
        return {
            'namespace': lib,
            'path': path,
            'alias': alias.getText() if alias else ''
        }

    def visitDotted_name(self, ctx:Python3Parser.Dotted_as_nameContext):
        name = ctx.getText()
        return name, name.split('.')[-1] 
    
    def visitImport_from(self, ctx:Python3Parser.Dotted_as_nameContext):
        full_line = ctx.getText()
        full_line = full_line.replace('from', '')

        path = full_line.split('import')[0]

        if ctx.STAR():
            self.definitions['imports'].append({
            'namespace': 'wildcard',
            'path': path,
            'alias': ''
        })
        else:
            self.visitImport_as_names(ctx.import_as_names(), path)

    def visitImport_as_names(self, ctx:Python3Parser.Dotted_as_nameContext, path):
        for node in ctx.import_as_name():
            self.visitImport_as_name(node, path)

    def visitImport_as_name(self, ctx:Python3Parser.Dotted_as_nameContext, path):
        names = ctx.NAME()
        lib = names[0]
        alias = names[1] if len(names) > 1 else None
        
        self.definitions['imports'].append({
            'namespace': lib.getText(),
            'path': path,
            'alias': alias.getText() if alias else ''
        })
