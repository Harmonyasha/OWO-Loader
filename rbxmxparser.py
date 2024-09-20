import os
from flask import Flask, jsonify, make_response, redirect, request, render_template, url_for
from colorama import Fore
printdebug = False

def color3uint8_to_rgb(color_value):
    red = (color_value & 0xFF0000) >> 16
    green = (color_value & 0x00FF00) >> 8
    blue = color_value & 0x0000FF
    red /= 255.0
    green /= 255.0
    blue /= 255.0
    return [red, green, blue]

def replace_html_entities(text):
    html_entities = {
        "&amp;": "&",
        "&quot;": "\"",
        "&apos;": "'",
        "&gt;": ">",
        "&lt;": "<"
    }
    for entity, value in html_entities.items():
        text = text.replace(entity, value)
    return text
def anotherprint(*args):
    if not printdebug:
        return
    print(args)
def RBXMXtoJson(patch,debug):
    global printdebug
    printdebug = debug
    file1 = open(os.path.join(patch), 'r',errors='ignore')


    Lines = file1.readlines()
    file1.close()

    classes = []
    templist = []
    record = False
    refetents = []
    parents = []
    isscript = False
    for line in Lines:
        line = line.replace("\n","").replace("\t","")
        if line.find("<Item class") != -1:
            new = line[13:].replace(" ","").replace(">","").replace("<","").split("\"",1)
            new[1] = new[1].replace("\"","").replace("referent=","")
            refetents.append(new)
        elif line == '</Item>':
            if refetents[refetents.__len__()-1][1] == refetents[refetents.__len__()-2][1]:
                parents.append(f'{refetents[refetents.__len__()-1][1]} parent of OWOLOADER' )
            else:
                parents.append(f'{refetents[refetents.__len__()-1][1]} parent of {refetents[refetents.__len__()-2][1]}' )
            del refetents[refetents.__len__()-1]




    for line in Lines:
            if not isscript:
                 line = line.replace("\n","").replace("\t","")

            if line.find("<Item class") != -1:
                record = True
                templist.append(line )
            elif record:
                if line.find('<ProtectedString name="Source"><![CDATA[') != -1:
                  isscript = True
                #print(Fore.BLUE,line)
                templist.append(line )

            if line.find("</Properties>") != -1:
                record = False
                isscript = False
                classes.append(templist)
                templist = []



    
    finallist = {}

    for d in classes:
        classs = d[0][13:].replace(" ","").replace(">","").replace("<","").split("\"",1)
        #print(Fore.WHITE,"-"*999)
        #print(classs)
        classs[1] = classs[1].split("=")[1].replace("\"","")
        #print(Fore.MAGENTA,classs[0],classs[1]) #class

        del d[0]
        del d[0]
        record = False
        recordedsource = []
        bool_anothermethodofrecord = False
        list_anothermethodofrecord = []
        lastsuccesfulrecord = None

        finallist[classs[1]] = {}
        finallist[classs[1]]["propertytype"] = classs[0]
        for v in d:
            
            if record:
                if v.find("]]></ProtectedString>") != -1:
                    recordedsource.append(replace_html_entities(v.replace("]]></ProtectedString>","")))
                    record = False
                else:
                    recordedsource.append(replace_html_entities(v))
            #        print(Fore.RED,f"RECORDING SOURCE {v}")
                    continue

            arg = v.split(">")
            if arg[0][0:1] == "<" and arg[0][0:2] != "</" :
                propertyt = arg[0].split(" ")
                
                propertyt[0] = propertyt[0]+">"
                #print(Fore.MAGENTA,arg)
                #print(Fore.BLUE,propertyt)

                if arg[1].find("<![CDATA[") == -1:
                    while arg[1][0:1] == "<":
                            del arg[1]
                
                #print(arg)
                argument = arg[1]+">"
                argument = argument.replace("</"+propertyt[0][1:],'')
                if argument.find("<") != -1 and argument.find("/") != -1:
                    argument = argument.split("<",1)[0]
                if bool_anothermethodofrecord == True:
                    new = v.replace(propertyt[0],"").replace(f"</{propertyt[0][1:]}","")
                    #print(Fore.MAGENTA,f"Record by another method data is {new}")
                    list_anothermethodofrecord.append(new)
               
                argument = argument.replace("<null>","nil")
                if argument == "" or argument == " ":
                    argument = "nil"
                try:
                  clearproperty = propertyt[1].split("=")[1].replace("\"","")
                  if clearproperty == "Color3uint8":
                      argument = color3uint8_to_rgb(int(argument))
                  finallist[classs[1]][clearproperty] = argument

                  if bool_anothermethodofrecord == True:
                    #print(Fore.YELLOW,"Record method set on default")
                    if list_anothermethodofrecord.__len__() == 0:
                        list_anothermethodofrecord = "nil"
                    elif list_anothermethodofrecord[list_anothermethodofrecord.__len__()-1].find(">") != -1:
                        del list_anothermethodofrecord[list_anothermethodofrecord.__len__()-1]
                    finallist[classs[1]][lastsuccesfulrecord] = list_anothermethodofrecord
                    #print(Fore.GREEN,f'RESULT OF ANOTHER RECORD METHOD {lastsuccesfulrecord}={finallist[classs[1]][lastsuccesfulrecord]}')
                    list_anothermethodofrecord = []
                    bool_anothermethodofrecord = False
              
                  #print(Fore.GREEN,f'{clearproperty}={argument}')
                  if clearproperty == "Source" :
                    if argument.find("<![CDATA[") != -1:
                       # print(argument.find("<![CDATA["))
                        recordedsource.append(replace_html_entities(v.split("[CDATA[")[1]))
                       # print(Fore.RED,f"RECORDING SOURCE {recordedsource[0]}")
                        record= True
                    else:
                        recordedsource.append(replace_html_entities(argument))
                  
                  lastsuccesfulrecord = clearproperty
                except Exception  as err:
                 #print(Fore.RED,err)
                 if not bool_anothermethodofrecord:
                    record = False
                    #print(Fore.RED,f"ERROR PROPERTY NOT SUPPORTED {lastsuccesfulrecord} INSTANCE {classs[0]} ATTEMPTING TO USE ANOTHER RECORD METHOD")

                    new = v.replace(propertyt[0],"").replace(f"</{propertyt[0][1:]}","")
                    #print(Fore.MAGENTA,f"Record by another method data is {new}")
                    list_anothermethodofrecord.append(new)

                    bool_anothermethodofrecord = True
                    continue


        if bool_anothermethodofrecord == True:
                
                if list_anothermethodofrecord.__len__() == 0:
                        list_anothermethodofrecord = "nil"
                elif list_anothermethodofrecord[list_anothermethodofrecord.__len__()-1].find(">") != -1:
                        del list_anothermethodofrecord[list_anothermethodofrecord.__len__()-1]
                
                finallist[classs[1]][lastsuccesfulrecord] = list_anothermethodofrecord
                #print(Fore.GREEN,f'RESULT OF ANOTHER RECORD METHOD {lastsuccesfulrecord}={finallist[classs[1]][lastsuccesfulrecord]}')

        if classs[0].lower().find("script") != -1:
          finallist[classs[1]]["Source"] = recordedsource
          #print(Fore.GREEN,f"New source successfully set on processed source ")

        

    #print(Fore.BLUE,finallist)
    finallist["parents"] = parents
    return jsonify(finallist)