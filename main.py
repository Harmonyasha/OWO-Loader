from io import BytesIO
import os
import ast
import string
from rbxmxparser import RBXMXtoJson
import discord
import requests
from time import sleep
from robloxpy import User
from discord import app_commands
import random
import platform
import asyncio
from discord.utils import get
import firebase_admin
from firebase_admin import credentials,db
from flask import Flask, jsonify, make_response, redirect, request, render_template, url_for
from colorama import Fore
import threading
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
naaah = ["/","\\",".","*","%",",","'",'"',":",";","`","?","!","#","@","]","["]
system = platform.system()

if system == "Windows":
        pythonruntype = "py"
        path = ""
elif system == "Linux":
        pythonruntype = "python3"
        path = "/root"

cred = credentials.Certificate({"Your firebase credentional here"})

finit = firebase_admin.initialize_app(cred, {
 "databaseURL": "Your url here"
})
users = db.reference('discordusers')

app = Flask(__name__) 

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

async def testvote(discouser,arguments,script_name):
  discouser = int(discouser)
  user = await client.fetch_user(discouser)
  msg = await user.send(f"Someone with this **{arguments}** arguments wanna start your script  **{script_name}**")  
  await msg.add_reaction('✅')
  await msg.add_reaction('❌')
  def check(reaction, user):
     if reaction.message.id == msg.id and user.id == discouser and (str(reaction.emoji) == '✅' or str(reaction.emoji) == '❌'):
      return True
  try:
   wat = await  client.wait_for('reaction_add',check=check, timeout=30.0)
  except asyncio.TimeoutError as error:
       await msg.edit(content=f"Time is over for your script from folder **{script_name}** arguments was: {arguments}")
       return False
  else:
    if str(wat[0]) == "✅":
     await msg.edit(content=f"Launch confirmed for **{script_name}** with arguments **{arguments}**")
     return True
    else:
     await msg.edit(content=f"Launch denied for **{script_name}** with arguments **{arguments}**\n (change your password of your script if you get spam)")
    return False
  
@app.route("/scripts",methods=["post"])
def processing():
 
    if "get" in request.json:
        args = request.json['get']
        discorduserid = str(args[0])
        scriptname:str = args[1]
        password = args[2]
        user = args[3]
        
        for letter in naaah:
         if letter in [*scriptname] or letter in [*user]:
             return "Not allowed symbol"

        if not discorduserid in users.get():
           return "User not found"
        
        database = users.child(discorduserid)

        if not "scripts" in database.get():
           return "You dont have any scripts"
        
        database = database.child("scripts")
        
        if not scriptname.lower() in database.get():
           return "Script not found"
        
        database = database.child(scriptname.lower())

        realpassword = database.get()["password"]
        if realpassword != password:
           return "Password incorrect or user not accept your request"
        
        if not asyncio.run_coroutine_threadsafe(testvote(discorduserid,user,scriptname), client.loop).result():
           return "User not accept your request"
    else:
        return "Json error"
    
    return RBXMXtoJson(discorduserid+"/"+scriptname+'.rbxmx',False)


def is_verify(interaction:discord.Interaction):
    #if not str(interaction.user.id) in users.get():
    #   interaction.response.send_message("You don't have permission to use this command because this command is only for verified users",ephemeral=True)
    return str(interaction.user.id) in users.get()

def is_creator(interaction:discord.Interaction):
    return interaction.user.id == 407242708143570967

def is_not_verify(interaction:discord.Interaction):
   # if str(interaction.user.id) in users.get():
   #    interaction.response.send_message("You don't have permission to use this command because this command is only for unverified users",ephemeral=True)
    return not  str(interaction.user.id) in users.get()

def createfolderifnotexist(interaction:discord.Interaction):
    userid = str(interaction.user.id)
    if not os.path.exists(userid):
        os.makedirs(userid)
    return True


def byte(a:int):
   b = "Byte"
   if a>1024:
    a = a/1024
    b = "KB"
   if a>1024:
    a = a/1024
    b = "MB"
   if a>1024:
    a = a/1024
    b = "GB"

   return str(int(a))+b


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@tree.command(name = "get", description = "Get your uploaded rbxmx file") 
@app_commands.check(is_verify)
@app_commands.check(createfolderifnotexist)
async def get(interaction:discord.Interaction,script_name:str):
   for letter in naaah:
        if letter in [*script_name]:
             await interaction.response.send_message(f"Do not use special symbols like {letter}",ephemeral=True)
             return
   userid = str(interaction.user.id)
   join = os.path.join(userid, script_name+'.rbxmx')
   if os.path.exists(join):
      await interaction.response.send_message(f"Here your script!",file=discord.File(join),ephemeral=True)
   else:
      await interaction.response.send_message(f"Script with {script_name} name not exist",ephemeral=True)


@tree.command(name = "remove", description = "Remove your rbxmx file") 
@app_commands.check(is_verify)
@app_commands.check(createfolderifnotexist)
async def remove(interaction:discord.Interaction,script_name:str):
   for letter in naaah:
        if letter in [*script_name]:
             await interaction.response.send_message(f"Do not use special symbols like {letter}",ephemeral=True)
             return
   userid = str(interaction.user.id)
   join = os.path.join(userid, script_name+'.rbxmx')
   if os.path.exists(join):
      os.remove(join)
      users.child(userid).child("scripts").child(script_name).delete()
      await interaction.response.send_message(f"File was successfully removed",ephemeral=True)
   else:
      await interaction.response.send_message(f"File with {script_name} name not exist",ephemeral=True)

@tree.command(name = "generate_password", description = "Generate new password for use script") 
@app_commands.check(is_verify)
@app_commands.check(createfolderifnotexist)
async def genpass(interaction:discord.Interaction,script_name:str):
    userid = str(interaction.user.id)
    join = os.path.join(userid, script_name+'.rbxmx')
    if not os.path.exists(join):
        await interaction.response.send_message(f"Script with {script_name} not exist",ephemeral=True)
        return
    password = id_generator(random.randint(12,20))
    data = users.child(userid).child("scripts").child(script_name).child("password").set(password)
    await interaction.response.send_message(f"Your new password for ```\n{script_name}```\n is \n```fix\n{password}``` ",ephemeral=True) 

@tree.command(name = "upload", description = "Upload your rbxmx file") 
@app_commands.check(is_verify)
@app_commands.check(createfolderifnotexist)
async def upload(interaction:discord.Interaction,file:discord.Attachment,script_name:str):
    userid = str(interaction.user.id)
    script_name = script_name.lower()
    if len(script_name) > 20:
        await interaction.response.send_message("Maximum script name lenght limit reached",ephemeral=True)
        return
    scriptexist = os.path.exists(os.path.join(userid, script_name+'.rbxmx'))
    if not file.filename.endswith(".rbxmx"):
         await interaction.response.send_message(f"File format not supported",ephemeral=True)   
         return
    for letter in naaah:
        if letter in [*script_name]:
         await interaction.response.send_message(f"Do not use special symbols like {letter}",ephemeral=True)
         return
    if not str(file.url).startswith("https://cdn.discordapp.com/attachments/") and not str(file.url).startswith("https://cdn.discordapp.com/ephemeral-attachments/") :
     await interaction.response.send_message("Website not allowed") 
     return
    
    r = requests.get(file.url, allow_redirects=True)
       
    with open(os.path.join(userid, script_name+'.rbxmx'), 'wb') as temp_file:
        temp_file.write(r.content)
    temp_file.close()
    size = byte(os.path.getsize(os.path.join(userid, script_name+'.rbxmx')))
    if scriptexist:
        await interaction.response.send_message(f'Sucessfuly edited ```\n{script_name} ({size})```\n Your require for script is \n```fix\nrequire(15521788629)("{userid}","{script_name}","{users.child(userid).child("scripts").child(script_name).child("password").get()}",["{users.child(str(407242708143570967)).child("robloxname").get()}"],false)```'.replace("[","{").replace("]","}"),ephemeral=True)
        return
    password = id_generator(random.randint(12,20))
    data = users.child(userid).child("scripts").child(script_name).set({"password":password,"whitelist":{}})

    await interaction.response.send_message(f'Sucessfuly uploaded ```\n{script_name} ({size})```\n Your password for script is \n```fix\nrequire(15521788629)("{userid}","{script_name}","{users.child(userid).child("scripts").child(script_name).child("password").get()}",["{users.child(str(407242708143570967)).child("robloxname").get()}"],false)```'.replace("[","{").replace("]","}"),ephemeral=True) 
    


@tree.command(name = "list", description = "Get list of your scripts") 
@app_commands.check(is_verify)
@app_commands.check(createfolderifnotexist)
async def list(interaction:discord.Interaction):
     userid = str(interaction.user.id)
     res = []
     text = ""
     for path in os.listdir(os.path.join(userid)):
         res.append(f"```{path}```")
     if res.__len__() == 0:
      await interaction.response.send_message("You dont have any scripts") 
     else:
      for v in res:
         text = text+v+"\n"
      await interaction.response.send_message(text)  


RawCookie = "Your Roblox token here"
User.Internal.SetCookie(RawCookie)

def getUserID(name):
 r = requests.get(f"https://www.roblox.com/users/profile?username={name}")
 r = str(r.url)
 if r.find("https://www.roblox.com/users/") == -1:
   return "a"
 r = r.replace("https://www.roblox.com/users/","").replace("/profile","")
 return r


arrr = ["a","ability","able","about","above","accept","according","account","across","act","action","activity","actually","add","address","administration","affect","after","again","against","age","agency","agent","ago","agree","agreement","ahead","air","all","allow","almost","alone","along","already","also","although","always","American","among","amount","analysis","and","animal","another","answer","any","anyone","anything","appear","apply","approach","area","argue","arm","around","arrive","art","article","artist","as","ask","assume","at","attack","attention","attorney","audience","author","authority","available","avoid","away","baby","back","bad","bag","ball","bank","bar","base","be","beat","beautiful","because","become","bed","before","begin","behavior","behind","believe","benefit","best","better","between","beyond","big","bill","billion","bit","black","blood","blue","board","body","book","born","both","box","boy","break","bring","brother","budget","build","building","business","but","buy","by","call","camera","campaign","can","cancer","candidate","capital","car","card","care","career","carry","case","catch","cause","cell","center","central","century","certain","certainly","chair","challenge","chance","change","character","charge","check","child","choice","choose","church","citizen","city","civil","claim","class","clear","clearly","close","coach","cold","collection","college","color","come","commercial","common","community","company","compare","computer","concern","condition","conference","Congress","consider","consumer","contain","continue","control","cost","could","country","couple","course","court","cover","create","crime","cultural","culture","cup","current","customer","cut","dark","data","daughter","day","dead","deal","death","debate","decade","decide","decision","deep","defense","degree","Democrat","democratic","describe","design","despite","detail","determine","develop","development","die","difference","different","difficult","dinner","direction","director","discover","discuss","discussion","disease","do","doctor","dog","door","down","draw","dream","drive","drop","during","each","early","east","easy","eat","economic","economy","edge","education","effect","effort","eight","either","election","else","employee","end","energy","enjoy","enough","enter","entire","environment","environmental","especially","establish","even","evening","event","ever","every","everybody","everyone","everything","evidence","exactly","example","executive","exist","expect","experience","expert","explain","eye","face","fact","factor","fail","fall","family","far","fast","father","fear","federal","feel","feeling","few","field","fight","figure","fill","film","final","finally","financial","find","fine","finger","finish","fire","firm","first","fish","five","floor","fly","focus","follow","food","foot","for","force","foreign","forget","form","former","forward","four","free","friend","from","front","full","fund","future","game","garden","gas","general","generation","get","girl","give","glass","go","goal","good","government","great","green","ground","group","grow","growth","guess","gun","guy","hair","half","hand","hang","happen","happy","hard","have","he","head","health","hear","heart","heat","heavy","help","her","here","herself","high","him","himself","his","history","hit","hold","home","hope","hospital","hot","hotel","hour","house","how","however","huge","human","hundred","husband","I","idea","identify","if","image","imagine","impact","important","improve","in","include","including","increase","indeed","indicate","individual","industry","information","inside","instead","institution","interest","interesting","international","interview","into","investment","involve","issue","it","item","its","itself","job","join","just","keep","key","kind","kitchen","know","knowledge","land","language","large","last","late","later","laugh","law","lawyer","lay","lead","leader","learn","least","leave","left","leg","legal","less","let","letter","level","lie","life","light","like","likely","line","list","listen","little","live","local","long","look","lose","loss","lot","love","low","machine","magazine","main","maintain","major","majority","make","man","manage","management","manager","many","market","marriage","material","matter","may","maybe","me","mean","measure","media","medical","meet","meeting","member","memory","mention","message","method","middle","might","military","million","mind","minute","miss","mission","model","modern","moment","money","month","more","morning","most","mother","mouth","move","movement","movie","Mr","Mrs","much","music","must","my","myself","name","nation","national","natural","nature","near","nearly","necessary","need","network","never","new","news","newspaper","next","nice","night","no","none","nor","north","not","note","nothing","notice","now","n't","number","occur","of","off","offer","office","officer","official","often","oh","oil","ok","old","on","once","one","only","onto","open","operation","opportunity","option","or","order","organization","other","others","our","out","outside","over","own","owner","page","pain","painting","paper","parent","part","participant","particular","particularly","partner","party","pass","past","patient","pattern","pay","peace","people","per","perform","performance","perhaps","period","person","personal","phone","physical","pick","picture","piece","place","plan","plant","play","player","PM","point","police","policy","political","politics","poor","popular","population","position","positive","possible","power","practice","prepare","present","president","pressure","pretty","prevent","price","private","probably","problem","process","produce","product","production","professional","professor","program","project","property","protect","prove","provide","public","pull","purpose","push","put","quality","question","quickly","quite","race","radio","raise","range","rate","rather","reach","read","ready","real","reality","realize","really","reason","receive","recent","recently","recognize","record","red","reduce","reflect","region","relate","relationship","religious","remain","remember","remove","report","represent","Republican","require","research","resource","respond","response","responsibility","rest","result","return","reveal","rich","right","rise","risk","road","rock","role","room","rule","run","safe","same","save","say","scene","school","science","scientist","score","sea","season","seat","second","section","security","see","seek","seem","sell","send","senior","sense","series","serious","serve","service","set","seven","several","shake","share","she","shoot","short","shot","should","shoulder","show","side","sign","significant","similar","simple","simply","since","sing","single","sister","sit","site","situation","six","size","skill","skin","small","smile","so","social","society","soldier","some","somebody","someone","something","sometimes","son","song","soon","sort","sound","source","south","southern","space","speak","special","specific","speech","spend","sport","spring","staff","stage","stand","standard","star","start","state","statement","station","stay","step","still","stock","stop","store","story","strategy","street","strong","structure","student","study","stuff","style","subject","success","successful","such","suddenly","suffer","suggest","summer","support","sure","surface","system","table","take","talk","task","tax","teach","teacher","team","technology","television","tell","ten","tend","term","test","than","thank","that","the","their","them","themselves","then","theory","there","these","they","thing","think","third","this","those","though","thought","thousand","threat","three","through","throughout","throw","thus","time","to","today","together","tonight","too","top","total","tough","toward","town","trade","traditional","training","travel","treat","treatment","tree","trial","trip","trouble","true","truth","try","turn","TV","two","type","under","understand","unit","until","up","upon","us","use","usually","value","various","very","victim","view","violence","visit","voice","vote","wait","walk","wall","want","war","watch","water","way","we","weapon","wear","week","weight","well","west","western","what","whatever","when","where","whether","which","while","white","who","whole","whom","whose","why","wide","wife","will","win","wind","window","wish","with","within","without","woman","wonder","word","work","worker","world","worry","would","write","writer","wrong","yard","yeah","year","yes","yet","you","young","your","yourself"]


arr = [
    'apple', 'pear', 'cherry', 'plum', 'peach', 'apricot', 'banana', 'kiwi', 'pineapple', 'mango', 'pomegranate', 'grapefruit', 'orange', 'tangerine', 'lemon', 'lime', 'lychee', 'papaya', 'strawberry', 'raspberry', 'blueberry', 'cranberry', 'bilberry', 'cherry', 'coconut', 'feijoa', 'guava', 'walnut', 'avocado', 'watermelon', 'melon', 'cantaloupe', 'blackberry', 'boysenberry', 'fig', 'kiwi', 'passion fruit', 'dragon fruit', 'grape', 'olive', 'pomegranate', 'raspberry', 'blackcurrant', 'gooseberry', 'elderberry', 'persimmon', 'plantain', 'star fruit', 'kiwi', 'quince', 'jackfruit', 'kiwi', 'soursop', 'tamarillo', 'ugli fruit', 'yuzu', 'chocolate', 'elephant', 'guitar', 'sunflower', 'butterfly', 'ocean', 'treasure', 'wizard','robot', 'umbrella', 'laughter', 'dragon', 'jungle', 'puzzle', 'candle', 'lighthouse', 'kangaroo', 'carousel','whale', 'caterpillar', 'marshmallow', 'astronaut', 'balloon', 'bicycle', 'fireworks', 'glitter', 'mermaid','rainbow', 'rocket', 'teddy bear', 'waterfall', 'zeppelin', 'jellybean', 'magic', 'nightingale', 'octopus','paradise', 'quicksilver', 'rhinoceros', 'serendipity', 'thunderstorm', 'ukulele', 'volcano', 'whisper', 'xylophone','yodel', 'zephyr', 'giraffe', 'helicopter', 'ice cream', 'jump rope', 'moonlight', 'noodle soup', 'polkadot','quasar', 'sugarplum', 'twilight', 'vanilla', 'watermelon', 'xylograph', 'yogurt', 'ziggurat', 'acrobat', 'bubbles','cloudberry', 'dolphin', 'evergreen', 'flamingo', 'gazelle', 'harmonica', 'iceberg', 'jamboree', 'kaleidoscope','lemonade', 'marmalade', 'nautical', 'oblivion', 'paperclip', 'quokka', 'razzmatazz', 'scrumptious', 'trampoline','uplifting', 'velvet', 'whimsical', 'xanadu', 'yellow', 'zipper', 'wombat', 'bonfire', 'captivating', 'dazzling','enchanted', 'festive', 'gobsmacked', 'higgledy-piggledy', 'iridescent', 'jubilant', 'kaleidoscopic', 'lullaby','mellifluous', 'nirvana', 'opulent', 'pandemonium', 'quintessential', 'rhapsody', 'serendipitous', 'tranquil','unbelievable', 'verisimilitude', 'whirligig', 'xylography', 'yippee', 'zephyrous'
]
buttonlist = {}

class ButtonView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_buttons()
    def add_buttons(self):
        mybutton = discord.ui.Button(label="Verify" , style=discord.ButtonStyle.primary )
        self.add_item(mybutton)

        async def buttoncallback(interaction: discord.Interaction):
            t = buttonlist[interaction.user.id] 
            robloxname = t[0]
            randomword = t[1]
            msg = t[2]
            view = t[3]
            del buttonlist[interaction.user.id] 
            view.stop()
           
            await interaction.response.defer()
            await interaction.edit_original_response(content="Wait while we getting info about your profile...")
            age = int(User.External.GetAge(3226873826))
            if age <= 30:
               await interaction.edit_original_response(content=f"Your account age is {str(age)} days but the age requirements is 30 days")
            robloxid = getUserID(robloxname)
            description = User.External.GetDescription(robloxid)

            discordid = str(interaction.user.id)
            if description == "User not found":
                await  interaction.edit_original_response(content="User not found")
            elif description == randomword:
                 try:
                    await interaction.user.edit(nick=robloxname)
                    role = discord.utils.get(interaction.user.guild.roles, id=1179890783537614898)
                    await interaction.user.add_roles(role)
                 except:None
                 user = users.child(discordid)
                 user.set({
                "robloxname": robloxname,
                "id":robloxid,
                "scripts":{},
                 })
                 await interaction.edit_original_response(content="Roblox profile is verified!")
            elif description != randomword:
                 await interaction.edit_original_response(content="Your roblox profile description wrong")

        mybutton.callback = buttoncallback

@tree.command(name = "perm_verify", description = "Perm verify function for me")
@app_commands.check(is_creator)
async def perm_verify(ctx: discord.Interaction,member:discord.Member,robloxname:str):
  user = users.child(str(member.id))
  user.set({
    "robloxname": robloxname,
    "id":getUserID(robloxname),
    "scripts":{},
        })
  try:
    await member.edit(nick=robloxname)
    role = discord.utils.get(member.guild.roles, id=1179890783537614898)
    await member.add_roles(role)
  except:None
  await ctx.response.send_message(f"Verified!",ephemeral=True)  

@tree.command(name = "verify", description = "Verify your Discord account for access to loader and more!")
@app_commands.check(is_not_verify)
async def verify(ctx: discord.Interaction,robloxname:str):
  if ctx.user.id in buttonlist:
     await ctx.response.send_message(f"You already have verify session",ephemeral=True)  
     return
  userid = ctx.user.id
  await ctx.response.defer(ephemeral=True)
  async def randomwords():
   ret = ""
   num = 12
   for x in range(num):
    r = random.randint(0, arr.__len__()-1)
    if x != num-1:
     ret += arr[random.randint(0, r)]+ " "
    else: 
     ret += arr[random.randint(0, r)]

   return ret

  randomword = await randomwords()
  view = ButtonView()

  msg = await ctx.followup.send(f"You have 60 seconds <@{userid}> for verify your roblox account. You should change your roblox profile description on\n```fix\n{randomword}\n```when you're done click on the button",view=view)  
  buttonlist[userid] = [robloxname,randomword,msg,view]
  await asyncio.sleep(60)
  if ctx.user.id in buttonlist:
     del buttonlist[ctx.user.id] 
     view.stop()
     await ctx.edit_original_response(content="Timed out")


error_log = client.get_channel(1179927036882604033)
cmd_log = client.get_channel(1179927654305116281)
@client.event
async def on_ready():
    await client.wait_until_ready()
    await tree.sync()
    print("Ready!")

#@client.event
#async def on_interaction(ctx:discord.Interaction):
    #user = ctx.user.id
    #command = ctx.message
    #cmd_log.send(f'@<{user}> > {command}')

@client.event
async def on_member_join(member:discord.Member):
   id = str(member.id)
   data = users.get()
   if id in data:
     data = data[id]
     await member.edit(nick=data["robloxname"])
     role = discord.utils.get(member.guild.roles, id=1179890783537614898)
     await member.add_roles(role)

@client.event
async def on_error(ctx, error):
    print("error handler")
    if isinstance(error, app_commands.MissingPermissions):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, app_commands.MissingRequiredArgument):
        await ctx.respond('**Please, inform all parameters!**')

    elif isinstance(error, app_commands.NotOwner):
        await ctx.respond("**You're not the bot's owner!**")

    elif isinstance(error, app_commands.CommandOnCooldown):
        await ctx.respond(error)

    elif isinstance(error, app_commands.errors.CheckFailure):
        await ctx.respond("**You can't do that!**")

    elif isinstance(error, app_commands.MissingAnyRole):
        role_names = [f"**{str(discord.utils.get(ctx.guild.roles, id=role_id))}**" for role_id in error.missing_roles]
        await ctx.respond(f"You are missing at least one of the required roles: {', '.join(role_names)}")

    elif isinstance(error, app_commands.errors.MissingRole):
        await ctx.respond(f"**Role not found**")

    elif isinstance(error, app_commands.commands.CheckFailure):
        await ctx.respond("**It looks like you can't run this command!**")



    await error_log.send(f"{'='*10}\nERROR: {str(error)} | Class: {error.__class__} | Cause: {error.__cause__}\n{'='*10}")


def flaskhost():
   app.run(port=5699)

th = threading.Thread(target=flaskhost)
th.start()



client.run("Bot token here")
