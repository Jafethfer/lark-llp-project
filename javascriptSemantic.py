# -*- coding: utf-8 -*-
import re
from lark import Transformer, v_args
from lark import Tree
from lark import Token

errorMessage = "\033[1;31m%s"
class javascriptSemantic (Transformer):

    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.paramidentifier = {}
        self.currentfunc = None

    def sum (self,param):
        if(re.match(r"\d+(\.\d+)?", param[0]) and re.match(r"\d+(\.\d+)?", param[2])):
            if(re.match(r"\d+",param[0]) and re.match(r"\d+", param[2])): 
                return int(param[0]) + int(param[2])
            elif(re.match(r"\d+(\.\d+)", param[0]) and re.match(r"\d+(\.\d+)", param[2])):
                return float(param[0]) + float(param[2])
            else:
                return float(param[0]) + float(param[2])
        elif(re.match(r"\"[^\"]*\"", param[0]) and re.match(r"\"[^\"]*\"", param[2])):
            return str(param[0]+param[2])
        elif(re.match(r"[a-zA-Z]\w*", param[0]) and re.match(r"[a-zA-Z]\w*", param[2])):
            
        else:
            raise Exception("No se puede operar (int or float) con string")

    def sub (self,param):
        new,new2 = int(param[0]), int(param[2]) 
        return float(new) - float(new2)

    def multi(self,param):
        new,new2 = int(param[0]), int(param[2]) 
        return (float(new)*float(new2))

    def div(self,param):
        new,new2 = int(param[0]), int(param[2]) 
        return (float(new)/float(new2))

    #Imprime el length de un string o numero.
    def length(self,param):
        if(self.getvar(param[2]) is None):
            print('Null has no length attribute.')
        elif(isinstance(self.getvar(param[2]),bool)):
            print('Boolean has no length attribute.')
        else:
            print (len(self.cleanParam(self.getvar(param[2]))))
    
    #Asigna valor a una variable.
    def assignvar(self, param):
        if(isinstance(param[3],str)):
            self.variables[param[1]] = self.cleanParam(param[3])
        else:
            self.variables[param[1]] = param[3]
    
    #Asigna valores dentro de un if
    def assignvarinif(self, param):
       return param

    #Asigna valores dentro de una funcion
    def assignvarinfunc(self,param):
        return param

    #Declaración de una variable con alguna otra variable o string.
    def assignvaralt(self, param):
        self.variables[param[0]] = ("%s %s" % (param[1],self.getvar(param[2])))
    
    #Devuelve el valor de una variable.
    def getvar(self, param):
        try:
            return self.variables[param[0]]
        except:
            return self.variables[param]
    
    #Devuelve el valor de un parametro de funcion
    def getparam(self, param):
        try:
            return self.paramidentifier[param]
        except:
            raise Exception ("El parametro no existe")
    
    #Impresión de 'console.log' con una cadena.
    def print_(self, param):
        print("%s" % self.cleanParam(param[2]))

    #Impresión de 'console.log' con un numero.
    def printnum(self,param):
        print(int(param[2]))

    #Impresión de 'console.log' con dos numeros.
    def printnum_alt(self,param):
        print(int(param[2])+int(param[3]))

    #Impresión de 'console.log' con una cadena.
    def print_error(self, param):
        print(errorMessage % self.cleanParam(param[2]))

    #Impresión de 'console.log' con concatenado de una cadena o variable.
    def print_alt(self, param):
        print("%s %s" % (self.cleanParam(param[2]),self.getvar(param[4])))
    
    #Impresión de 'console.log' de una variable.
    def printvar(self, param):
        print("%s" % self.cleanParam((self.getvar(param[2]))))

    #Impresión de 'console.log' con concatenado de dos variables.
    def printvar_alt(self, param):
        if(isinstance(self.getvar(param[2]),str) and isinstance(self.getvar(param[3]),str)):
            print("%s %s" % (self.cleanParam(self.getvar(param[2])),self.cleanParam(self.getvar(param[3]))))
        else:
            print(int(self.getvar(param[2]))+int(self.getvar(param[3])))

    #Limpia las ' "" ' y " '' " a la hora de impresión.
    def cleanParam(self, param):
        if re.match(r"^((\"[^\"]*\")|('[^']*'))$", param):
            return param[1:-1]
        return param

    #Guarda la funcion junto con sus expresiones como value
    def createfunc(self,param):
        self.functions[param[1]] = param[2:]
 
  
    #funcexists verifica si la funcion existe para ser ejecutada.
    #Las funciones deben contener dos parametros o menos. 
    #Estos parametros obtendran el valor de los parametros en el llamado de la funcion
    def funcexists(self,param):
        if param[0] in self.functions:
            if(len(param)==6):
                param1 = str(param[0]+"_param_1_"+self.functions[param[0]][1])
                param2 = str(param[0]+"_param_2_"+self.functions[param[0]][2])
                if(self.functions[param[0]][1]==self.functions[param[0]][2]):
                    raise Exception ("Las funciones de "+param[0]+" no pueden contener dos parametros con el mismo nombre")
                self.paramidentifier[param1] = param[2]
                self.paramidentifier[param2] = param[3]
            elif(len(param==5)):
                param = str(param[0]+"_param_1_"+self.functions[param[0]][1])
                self.paramidentifier[param] = param[2]
            else:
                pass
            self.currentfunc = param[0]
            self.execfunc(param[0])
        else:
            raise Exception ("La función "+param[0]+" no existe.")

    """
    execfunc ejecuta la funcion si se encuentra su identificador en la lista de funciones.
    Si se encuentra un arbol de expresiones dentro de la funcion, se itera en sus hijos mediante creepexp.
    Si no hay arboles de expresion se evalua si los hijos de la funcion contienen 'if', 'for', 'while' para ser 
    ejecutados en sus metodos respectivos

    """
    def execfunc(self, identifier):
        for node in self.functions[identifier]:
            if(isinstance(node,Tree)):
                if(node.data=='infuncexp' or node.data=='infunc'):
                    self.creepexp(node.children)
                elif(node.children[0]=='if'):
                    self.ifelse(node.children)
                elif(node.children[0]=='while'):
                    pass
                elif(node.children[0]=='for'):
                    pass
            else:
                pass

    """
    creepexp se 'arrastra' en los hijos de un arbol, si el hijo de un arbol contiene un metodo como 'if', 'while', 'for'
    este se enviara a su metodo de ejecucion respectiva

    """

    def creepexp(self, children):
        for node in children:
            if(isinstance(node,Tree)):
                if(node.children[0]=='if'):
                    self.ifelse(node.children)
                if(node.children[0]=='while'):
                    pass
                if(node.children[0]=='for'):
                    pass
            elif(isinstance(node,list)):
                if(node[0]=="var"):
                    varname = str(self.currentfunc+"_"+node[1])
                    self.variables[varname]=node[3]
                elif(node[0]=="console" and node[2]=="log"):
                    print (self.cleanParam(node[3][1]))
                elif(node[0]=="console" and node[2]=="error"):
                    print ("Error: "+self.cleanParam(node[3][1]))

    
    """
    Ejecuta todos los if-else dentro de la funcion ejecutandose, se evaluan los tipos de Token siguientes:
    __ANON_0 : Identifier
    __ANON_6 : float
    __ANON_7 : int

    En caso de encontrarse un 'while', 'for' anidado al if, este se enviara a creepexp para dirigirse a su ejecucion correspondiente

    Se separan los casos dependiendo del operador y los tokens:
    Caso 1: identifier (operador) identifier
    Caso 2: int (operador) identifier
    Caso 3: float (operador) identifier
    Caso 4: identifier (operador) int 
    Caso 5: identifier (operador) float
    Caso 6: int (operador) int
    Caso 7: float (operador) float
    Caso 8: int (operador) float
    Caso 9: float (operador) int
    """
    def ifelse(self,param):
        for node in param:
            if(isinstance(node,Tree)):
                if(node.children[0]=='if'):
                    self.ifelse(node.children)
                    param.remove(node)
                else:
                    self.creepexp(node.children)
            else:
                pass
        if(param[2].type=="__ANON_0" and param[4].type=="__ANON_0"):
            if(param[3]=='>'):
                self.ifcondgnames(param)
            elif(param[3]=='<'):
                self.ifcondlnames(param)
            elif(param[3]=='=='):
                self.ifcondenames(param)
            elif(param[3]=='<='):
                self.ifcondgenames(param)
            elif(param[3]=='>='):
                self.ifcondlenames(param)
        if(param[2].type=="__ANON_7" and param[4].type=="__ANON_0"):
            if(param[3]=='>'):
                pass
            elif(param[3]=='<'):
                pass
            elif(param[3]=='=='):
                pass
            elif(param[3]=='<='):
                pass
            elif(param[3]=='>='):
                pass
            
            """elif(param[2].type=="__ANON_7" and param[4].type=="__ANON_0"):
                if(param[i] == '>'):
                    if(int(param[2]) > int(self.getvar(param[4]))):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[18+count] != '}':
                                print(param[18+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1
                elif(param[i] == '<'):
                    if(int(param[2]) < int(self.getvar(param[4]))):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[19+count] != '}':
                                print(param[19+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1

                elif(param[i] == '=='):
                    if(int(param[2]) == int(self.getvar(param[4]))):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[18+count] != '}':
                                print(param[18+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1
            elif(param[2].type=="__ANON_7" and param[4].type=="__ANON_7"):
                if(param[i] == '>'):
                    if(int(param[2]) > int(param[4])):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[18+count] != '}':
                                print(param[18+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1
                elif(param[i] == '<'):
                    if(int(param[2]) < int(param[4])):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[19+count] != '}':
                                print(param[19+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1
                elif(param[i] == '=='):
                    if(int(param[2]) == int(param[4])):
                        while param[6+count] != '}':
                            print(param[6+count]) 
                            count += 1
                    else:
                        try:
                            while param[18+count] != '}':
                                print(param[18+count]) 
                                count += 1
                        except:
                            while param[10+count] != '}':
                                print(param[10+count]) 
                                count += 1"""

    #Para '>'
    def ifcondgnames(self, param):
        param1 = str(self.currentfunc+"_param_1_"+param[2])
        param2 = str(self.currentfunc+"_param_2_"+param[4])
        if(param1 in self.paramidentifier):
            param1 = float(self.getparam(param1).value)
        if(param2 in self.paramidentifier):
            param2 = float(self.getparam(param2).value)
        funcvar1 = str(self.currentfunc+"_"+param[2])
        funcvar2 = str(self.currentfunc+"_"+param[4])
        if(funcvar1 in self.variables):
            param1 = self.getvar(funcvar1)
        if(funcvar2 in self.variables):
            param2 = self.getvar(funcvar2) 
        count = 7
        reversecount = -1
        if(param1>param2):
            while (param[count]!= '}'):
                if(isinstance(param[count], list)):
                    self.execif(param[count])
                    count+=1
        else:
            while(param[reversecount]!='{'):
                if(isinstance(param[count], list)):
                    self.execif(param[reversecount])
                    reversecount-=1

    #Para '<'
    def ifcondlnames(self,param):
        count = 1
        for i in range (len(param)):
            if(param[i] == '<'):
                if(int(self.getvar(param[2])) < int(self.getvar(param[4]))):
                    while param[6+count] != '}':
                        print(param[6+count]) 
                        count += 1
                else:
                    try:
                        while param[19+count] != '}':
                            print(param[19+count]) 
                            count += 1
                    except:
                        while param[10+count] != '}':
                            print(param[10+count]) 
                            count += 1

    #Para '=='
    def ifcondenames(self,param):
        count = 1
        for i in range (len(param)):
            if(param[i] == '=='):
                if(int(self.getvar(param[2])) == int(self.getvar(param[4]))):
                    while param[6+count] != '}':
                        print(param[6+count]) 
                        count += 1
                else:
                    try:
                        while param[18+count] != '}':
                            print(param[18+count]) 
                            count += 1
                    except:
                        while param[10+count] != '}':
                            print(param[10+count]) 
                            count += 1 

    #Para '>='
    def ifcondgenames(self,param):
        count = 1
        for i in range (len(param)):
            if(param[i] == '>='):
                if(int(self.getvar(param[2])) >= int(self.getvar(param[4]))):
                    while param[6+count] != '}':
                        print(param[6+count]) 
                        count += 1
                else:
                    try:
                        while param[18+count] != '}':
                            print(param[18+count]) 
                            count += 1
                    except:
                        while param[10+count] != '}':
                            print(param[10+count]) 
                            count += 1 

    #Para '<='
    def ifcondlenames(self,param):
        count = 1
        for i in range (len(param)):
            if(param[i] == '>='):
                if(int(self.getvar(param[2])) >= int(self.getvar(param[4]))):
                    while param[6+count] != '}':
                        print(param[6+count]) 
                        count += 1
                else:
                    try:
                        while param[18+count] != '}':
                            print(param[18+count]) 
                            count += 1
                    except:
                        while param[10+count] != '}':
                            print(param[10+count]) 
                            count += 1 

    #Para '>'
    def ifcondg(self,param):
        if(isinstance(param[2],str) and isinstance(param[4],str)):
            if(int(self.getvar(param[2])) > int(param[4])):
                print(param[7])
            else:
                pass     


   

    #Para '=='
    def ifconde(self,param):
        if(isinstance(param[2],str)):
            if(int(self.getvar(param[2])) == int(param[4])):
                print(param[7])
            else:
                pass
    
    #Para '<'
    def ifcondl(self, param):
        if(isinstance(param[2],str)):
            if(int(self.getvar(param[2])) < int(self.getvar(param[4]))):
                print(param[7])
            else:
                pass

    #Ejecuta todo lo que está dentro del if
    def execif(self, param):
        if(param[0]=="console" and param[2]=="log"):
            print (self.cleanParam(param[3][1]))
        elif(param[0]=='var'):
            self.variables[param[1].value]=param[3]
        elif(param[0]=="console" and param[2]=="error"):
            print("Error: "+self.cleanParam(param[3][1]))

    def whiles(self,param):
        increment = int(self.getvar(param[2]))
        for i in range (len(param)):
            try:
                if(isinstance(int(self.getvar(param[2])),int) and param[3] == '>' and isinstance(int(param[4]),int)):
                    while(increment > int(param[4])):
                        print(param[7])
                        increment += 1

                elif(isinstance(int(self.getvar(param[2])),int) and param[3] == '<' and isinstance(int(param[4]),int)):
                
                    while(increment < int(param[4])):
                        print(param[7])
                        increment += 1

                elif(isinstance(int(self.getvar(param[2])),int) and param[3] == '==' and isinstance(int(param[4]),int)):
                
                    while(increment < int(param[4])):
                        print(param[7])
                        increment += 1
            except:
                pass

            try:
                if(isinstance(int(self.getvar(param[2])),int) and param[3] == '>' and isinstance(int(self.getvar(param[4])),int)):

                    while(increment > int(self.getvar(param[4]))):
                        print(param[7])
                        increment += 1

                elif(isinstance(int(self.getvar(param[2])),int) and param[3] == '<' and isinstance(int(self.getvar(param[4])),int)):
                
                    while(increment < int(self.getvar(param[4]))):
                        print(param[7])
                        increment += 1

                elif(isinstance(int(self.getvar(param[2])),int) and param[3] == '==' and isinstance(int(self.getvar(param[4])),int)):
                
                    while(increment < int(self.getvar(param[4]))):
                        print(param[7])
                        increment += 1
            except:
                pass

    def fors(self,param):
        increment = int(self.getvar(param[2]))
        for increment in range(int(param[8])):
            print(param[13])


    def returnrecur(self, param):
        #print(param[3],param[7])
        pass
    
    def boolt(self,A):
        return True
    
    def boolf(self,A):
        return False
    
    def booln(self,A):
        return None
    
    def eos(self,param):
        return param[0]

    def consolelogfunc(self,param):
        print(self.cleanParam(param[2]))

    def consoleloglengthfunc(self,param):
        if(self.getvar(param[2]) is None):
            print('Null has no length attribute.')
        elif(isinstance(self.getvar(param[2]),bool)):
            print('Boolean has no length attribute.')
        else:
            print(len(self.cleanParam(self.getvar(param[2]))))

    def consolelogatomfunc(self,param):
        print(int(param[2])+int(param[3]))

    def consolelogsifunc(self,param):
        print("%s %s" % (self.getvar(param[4]),self.cleanParam(param[2])))

    def consolelogidentfunc(self,param):
        print(self.cleanParam(self.getvar(param[2])))

    def consolelogident_altfunc(self, param):
        if(isinstance(self.getvar(param[2]),str) and isinstance(self.getvar(param[3]),str)):
            print("%s %s" % (self.cleanParam(self.getvar(param[2])),self.cleanParam(self.getvar(param[3]))))
        else:
            print(int(self.getvar(param[2]))+int(self.getvar(param[3])))

    def consoleerrorfunc(self,param):
        pass
        #print(self.cleanParam(param[2]))

    def consolelogcond(self,param):
        list = param[0].children
        list.append(param[1:])
        return list

    def consoleloglengthcond(self,param):
        if((self.getvar(param[2]) or self.getparam(param[2])) is None):
            return('Null has no length attribute.')
        elif(isinstance(self.getvar(param[2]),bool) or isinstance(self.getparam(param[2]),bool)):
            return('Boolean has no length attribute.')
        else:
            list = param[0].children
            list.append(param[1:])
            return list

    def consolelogatomcond(self,param):
        return (int(param[2])+int(param[3]))

    def consolelogsicond(self,param):
        return("%s %s" % (self.getvar(param[4]),self.cleanParam(param[2])))

    def consolelogidentcond(self,param):
        return self.cleanParam(self.getvar(param[2]))

    def consolelogident_altcond(self, param):
        if(isinstance(self.getvar(param[2]),str) and isinstance(self.getvar(param[3]),str)):
            return("%s %s" % (self.cleanParam(self.getvar(param[2])),self.cleanParam(self.getvar(param[3]))))
        else:
            return(int(self.getvar(param[2]))+int(self.getvar(param[3])))

    def consoleerrorcond(self,param):
        list = param[0].children
        list.append(param[1:])
        return list

    def opsum(self,param):
        return param[0]

    def opsub(self,param):
        return param[0]

    def opmult(self,param):
        return param[0]

    def opdiv(self,param):
        return param[0]

    def ifw(self,param):
        return param[0]

    def elsew(self,param):
        return param[0]

    def funcw(self,param):
        return param[0]

    def retw(self,param):
        return param[0]

    def whilew(self,param):
        return param[0]

    def leftpar(self,param):
        return param[0]

    def rightpar(self,param):
        return param[0]

    def varkeyword(self,param):
        return param[0]

    def leftbrace(self,param):
        return param[0]

    def rightbrace(self,param):
        return param[0]

    def opequals(self,param):
        return param[0]

    def opcompare(self,param):
        return param[0]

    def opgrtrthan(self,param):
        return param[0]

    def oplessthan(self,param):
        return param[0]

    def forw(self,param):
        return param[0]
