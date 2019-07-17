### TELEMBY
##### A simple Telegram Bot for Emby
###### Powered by Docker

This is a simple python-based bot to carry out some trivial Emby tasks and retrieve some data.

For ease, it is held inside a Docker Container.

It is configured to only allow input from one user (i.e You) so you need to specify your telegram user id in the config.

N.B - This has been done with approx 1 weeks worth of python under my belt, so the code may be (is) ugly!

### Known Issues:
- Json formatting isn't pretty

### To Do:
- Slim down the base image
- Search Library
- Add/Disable Users
- Reset User Passwords 

### Setup:

#### Telegram  
- Retrieve your Telegram UID using a tool such as JSON Dump Bot
- Create a Bot Using Botfather
- Retrieve your Bot Token
- Edit the bots commands in botfather and paste in the below:

```
status - Check your Emby Server is Online
refreshlibrary - Refreshes all Media Libraries
refreshguide - Refreshes TV Guide Data
users - Lists Emby Users
devices - Lists Emby Devices
activity - Lists Last 10 Activity Items
backup - Triggers a Configuration Backup
help - Prints this message
```
    
#### Docker

##### From Source

- Clone this Repo
- Add your details to ./app/config.ini - eg:
	
	```
	
		[BOT]

		API_TOKEN =  8079943032202020131323321323
		USER_ID = 123456

		[EMBY]

		SERVER = http://emby.media:8096/
		API_KEY = 5454545454549abedea814939dad
  	```

- Build the Image:
    ` docker build -t telemby .`
   
- Run Container from Image
    `docker run -d --name=telemby telemby`
    
##### From DockerHub

You need to specify the config vars in the docker run command:

- BOT: Telegram Bot Token
- USER: Telegram User ID
- SERVER: Address of Emby Server - this requires the http(s):// prefix as well as a trailing slash (see below example)
- API: Emby API Key


`docker run -d --env BOT=BOTTOKEN--env USER=TELEGRAM-UID--env SERVER=http://emby-server.domain:port/ --env API=EMBY-API-KEY --name telemby matty87a/telemby`


