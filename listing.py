#!/usr/bin/env python
# -*- coding: utf-8
#
# userlist.py - Creates a list of users currently online or from database.
# Copyright (c) 2010, Natenom / Natenom@googlemail.com
# Version: 0.0.5
# 2010-09-08

#Path to Murmur.ice
iceslice='/usr/share/slice/Murmur.ice'

iceport=60000
icesecret="secureme"

#ID of the virtual Server
serverid=1

def channeldb(server):
    '''Print id, name, description and length of description from all channels of a server'''
    channels=server.getChannels()

    retvar="<table border='1px'><tr><th>ChannelID</th><th>Name</th><th>Description</th><th>Size of Description</th></tr>"


    for channelid in channels:
        retvar+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (channels[channelid].id, channels[channelid].name, channels[channelid].description, len(channels[channelid].description))	

    retvar+="</table>"
    return retvar


def userdb(server):
    '''Print name, comment avatar and maybe more in future for every user in the datebase'''
    import base64
    users=server.getRegisteredUsers("")

    retvar="<table border='1px'><tr><th>UserID</th><th>Name</th><th>Letzter Besuch</th><th>Comment</th><th>Avatar</th></tr>"

    for userid in users:
        usercomment='';
        username='';
        useravatar='';
    
	try:
	    useravatar=base64.b64encode(server.getTexture(int(userid)))
	except:
	    useravatar=''

	userinfo=server.getRegistration(int(userid))
	for k,v in userinfo.items():
	    if (str(k) == "UserName"):
		username=v
	    if (str(k) == "UserComment"):
		usercomment=v
	    if (str(k) == "UserLastActive"):
		userlastactive=v

	retvar+="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td><img src='data:image/png;base64,%s' /></td></tr>" % (userid, username, userlastactive, usercomment, useravatar)
	
    retvar+="</table>"
    return retvar

def useronline(server):
    '''Print name, comment and avatar of every online user.'''
    import base64
    users=server.getUsers()
    retvar=''
    avatars=''
#    avatarlist=''
    page="<table border='1px'><tr><th>UserID</th><th>Name</th><th>Comment</th><th>Avatar</th></tr>"
    
    for user in users.iteritems():
	#Avatar des Benutzers holen
	try:
	    avatar=base64.b64encode(server.getTexture(int(user[1].userid)))
	except:
	    avatar=''

        page+='<tr><td valign="top">%s</td><td valign="top">%s</td></td><td>%s</td><td valign="top"><img src="data:image/png;base64,%s" /></tr>' % (user[1].userid, user[1].name, user[1].comment, avatar)
	    

    page+='</table>'
    
    return page


if __name__ == '__main__':
    import Ice, sys
    Ice.loadSlice("--all -I/usr/share/slice %s" % iceslice)		
    import Murmur
    
    prop = Ice.createProperties(sys.argv)
    prop.setProperty("Ice.ImplicitContext", "Shared")
    idd = Ice.InitializationData()
    idd.properties = prop
    ice = Ice.initialize(idd)
    ice.getImplicitContext().put("secret", icesecret) # If icesecret is set, we need to set it here as well.
    
    meta = Murmur.MetaPrx.checkedCast(ice.stringToProxy("Meta:tcp -h 127.0.0.1 -p %s" % (iceport)))
    serverid=1

    if (sys.argv[1:]):
	if (len(sys.argv) == 3):
	    serverid=int(sys.argv[2])

	server=meta.getServer(serverid)
	
	if (server==None): #Ice method getServer does not emit an exception if serverid does not exist. We need to check this by hand.
	    print "Server with ID \'%s\' does not exist." % sys.argv[2]
	    ice.shutdown()
	    sys.exit(1)

	if (sys.argv[1] == "all"):
	    print userdb(server)
	if (sys.argv[1] == "online"):
	    print useronline(server)
	if (sys.argv[1] == "channels"):
	    print channeldb(server)
    else:
	print "Creates a HTML-Page of users (online or all) with name, comment, avatar, lastactive, etc. or a list of all channels."
	print "%s all|online|channels [ServerID]" % sys.argv[0]

    ice.shutdown()
