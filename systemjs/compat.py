from django import VERSION
from django.template.base import Lexer


if VERSION < (1, 9):
    class Lexer19(Lexer):

        def __init__(self, template_string):
            super(Lexer19, self).__init__(template_string, None)

    Lexer = Lexer19
