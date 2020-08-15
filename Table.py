# -*- coding: utf-8 -*-

class Table:
    def __init__(self): pass

    def printInfoTable(self,param):
            print("*"*40)
            print("{1} {0:36s} {1}".format("","*"))
            print("{1} {0:36s} {1}".format("Intérprete de Lenguajes","*"))
            print("{1} {0:36s} {1}".format("@authors:","*"))
            print("{1} {0:31s} {1}".format("\tlemartinezm@unah.hn","*"))
            print("{1} {0:31s} {1}".format("\tdaniel.arteaga@unah.hn","*"))
            print("{1} {0:31s} {1}".format("\teglopezl@unah.hn","*"))
            print("{1} {0:31s} {1}".format("\tcorreos","*"))
            print("{1} {0:36s} {1}".format("@version 0.0.1","*"))
            print("*"*40)
            print("{1} {0:36s} {1}".format("Opción Elegida:","*"))
            print("{1} {0:31s} {1}".format("\t%s" % param,"*"))
            print("{1} {0:36s} {1}".format("","*"))
            print("*"*40)