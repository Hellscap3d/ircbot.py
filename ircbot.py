import socket
import sys
import time
import threading
import colorama

colorama.init()
class IRCRegistrationTimeout(Exception):pass

class Embed():
  def __init__(self, data):
    self.data = data
  def send(self, bot, channel):
    lines = []
    lines.append("="*25)
    lines.append("||" + self.data["title"] + " "*(21-len(self.data["title"])) + "||")
    lines.append("||" + self.data["description"] + " "*(21-len(self.data["description"])) + "||")
    for field in self.data["fields"]:
      lines.append("||" + field["name"] + " "*(21-len(field["name"])) + "||")
      lines.append("||" + field["value"] + " "*(21-len(field["value"])) + "||")
    lines.append("="*25)
    for line in lines:
      bot.send(channel.id, line)
      

class Message():
  def __init__(self,bot,message,channel,user):
    message = message[1:]
    self.content = message
    self.channel = channel
    self.author = user
    self.bot = bot

class Channel():
  def __init__(self,bot,channel):
    self.id = channel
    self.bot = bot
  def send(self,message):
    self.bot.send(self.id,message)

class User():
  def __init__(self,bot,user):
    print(user)
    user = user.split("!")[1].split("@")
    self.host = user[1] 
    self.name = user[0]
    self.id = None
    self.bot = bot
  def send(self,message):
    print(self.name)
    self.bot.send(self.name,message)

class IRCThread(threading.Thread):
    def __init__(self, bot):
        threading.Thread.__init__(self)
        self.bot = bot
        self.daemon = True
        self.last = None

    def run(self):
        while True:
            for response in self.bot.get_response():
              user = None
              message = None
              channel = None
              if response != self.last:
                self.last = response
              else:
                continue
              if response == "":
                continue
              if response.startswith("ERROR"):
                if response.find("(Registration Timeout)"):
                  raise IRCRegistrationTimeout()
                else:
                    # No matter what, an error is fatal
                    raise
              if response.split(" ")[1] == "PRIVMSG":
                args = response.split(" ")
                
                channel = Channel(self.bot,args[2])
                user = User(self.bot,args[0])
                print(f"[IRCBOT INCOMING] Message from {user.name} in {channel.id}")
                messagecontent = ""
                for i in range(0,len(args) - 3):
                  if i == 0:
                    messagecontent = messagecontent + args[i + 3]
                    continue
                  if not i == len(args) - 3:
                    messagecontent = messagecontent + " " + args[i + 3]
                  else:
                    continue
                if not channel.id.startswith("#"):
                  channel = user
                message = Message(self.bot,messagecontent,channel,user)
                # found the issue
                self.bot.on_message(message)
                


class Bot:

    
    def __init__(self):
        # Define the socket
        self.irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.thread = IRCThread(self)
 
    def send(self, channel, msg):
        # Transfer data
        self.irc.send(bytes("PRIVMSG " + channel + " " + msg + "\n", "UTF-8"))

    def join(self,channel):
      print("[IRCBOT] Joined channel: " + channel)
      self.irc.send(bytes("JOIN " + channel + "\n", "UTF-8"))
      return Channel(self,channel)
 
    def connect(self, server, port, botnick, botnickpass):
        # Connect to the server
        print("[IRCBOT] Connecting to: " + server)
        self.irc.connect((server, port))
        print("[IRCBOT] Starting daemon...")
        self.thread.start()
        # Perform user authentication
        print("[IRCBOT] Established connection!")
        self.irc.send(bytes("USER " + botnick + " 0 * :ircbot.py\n", "UTF-8"))
        time.sleep(1)
        print("[IRCBOT] Naming user acccount...")
        self.irc.send(bytes("NICK " + botnick + "\n", "UTF-8"))
        time.sleep(1)

      
        time.sleep(5)

        print("[IRCBOT] Performing auth...")
        self.irc.send(bytes("NICKSERV IDENTIFY " + botnickpass + "\n", "UTF-8"))


        print("[IRCBOT] Connected!")
        self.user = User(self,"!" + botnick + "@localhost")
        self.on_ready()
 
    def get_response(self):
        time.sleep(1)
        # Get the response
        resp = self.irc.recv(2040).decode("UTF-8")
        lines = resp.split("\n")
        for line in lines:
          if line.startswith('PING'):     
            self.irc.send(bytes('PONG ' + line[5:] + '\r\n', "UTF-8"))
            self.on_ping(line)
 
        return lines
    
    def on_message(self, response):return None
    def on_ready(self):return None
    def on_ping(self,line):return None
      
