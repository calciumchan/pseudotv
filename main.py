import os
import json
import random
import math
import cv2
import subprocess
from datetime import datetime

#OPEN JSON DATA FOR CHANNELS
print(os.listdir("./"))
with open("channels.json","r") as file:
	data = json.load(file)

#MAKE SURE PLAYLIST FOLDER EXISTS
if not os.path.isdir("playlists"):
	os.mkdir("playlists")

#LIST OF FILE EXTENSIONS
file_extensions = [
	"3g2",
	"3gp",
	"aaf",
	"asf",
	"avchd",
	"avi",
	"drc",
	"flv",
	"m2v",
	"m3u8",
	"m4p",
	"m4v",
	"mkv",
	"mng",
	"mov",
	"mp2",
	"mp4",
	"mpe",
	"mpeg",
	"mpg",
	"mpv",
	"mxf",
	"nsv",
	"ogg",
	"ogv",
	"qt",
	"rm",
	"rmvb",
	"roq",
	"svi",
	"vob",
	"webm",
	"wmv",
	"yuv"
]
#---------------------------------------------------------------------------------------------------- GET EPISODES
def get_episode(list):
	show = None
	while show == None:
		show = random.choice(list)
		if not random.randrange(0,show["chance"]) <= 1:
			show = None

	#print(show["path"])
	path = show["path"]
	while os.path.isdir(path):
		addition = random.choice(os.listdir(path))
		if not "." in addition or addition.split(".")[-1] in file_extensions:
			path += "/" + addition

	return path

#---------------------------------------------------------------------------------------------------- GENERATES A PLAYLIST



#LOOP THROUGH CHANNELS AND MAKE PLAYLISTS
def generate_playlist(channel, week):
	#GET VARIABLES
	name = channel["name"]
	playlist_filename = "playlists/" + name + " " + datetime.today().strftime("%Y-") + str(week) + ".m3u"

	#MAKE PLAYLIST FILE
	if not os.path.isfile(playlist_filename):
		print(name + " playlist doesnt exist")
		#OPEN PLAYLIST FOR WRITING
		playlist_file = open(playlist_filename,"w")
		#WRITE TO PLAYLIST
		time = 0
		buffer_episode = []
		buffer_commercial = []
		checks_episode = 0
		commercial_time = 0;
		while time < 604800:
			#GET PATH TO VIDEO
			episode_path = ""
			while episode_path == "":
				#COMMERCIAL
				if commercial_time != None and commercial_time > 0:
					episode_path = get_episode(channel["commercials"])
					#BUFFER CHECK
					if episode_path in buffer_commercial:
						episode_path = ""
					else:
						buffer_commercial.append(episode_path)
					
				#SHOW
				else:
					episode_path = get_episode(channel["shows"])
					#LET THEM KNOW YOU WANT COMMERCIALS NOW
					commercial_time = None
					#BUFFER CHECK
					if episode_path in buffer_episode:
						episode_path = ""
						checks_episode += 1
						if(checks_episode > 1000):
							checks_episode = 0
							buffer_episode.clear() #clear buffer after too many checks
							print("BUFFER CLEARED")
					else:
						buffer_episode.append(episode_path)


			#TICK UP THE TIME BASED ON VIDEO LENGTHs
			try:
				video = cv2.VideoCapture(episode_path)
				frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
				fps = video.get(cv2.CAP_PROP_FPS)
				duration = math.ceil(frames/fps)
				#print(str(time) + " + " + str(duration))
				time += duration
				if commercial_time == None:
					commercial_time = channel["commercial_time"]
					buffer_commercial.clear() #clear buffer
				else:
					commercial_time -= duration

				#WRITE PATH TO PLAYLIST
				playlist_file.write("#T" + str(time - duration) + "\n" + episode_path + "\n")
			except:
				print("ERROR OCCURED")
			
		#CLOSE PLAYLIST
		playlist_file.close()




for channel in data:
	weektocheck = int(datetime.today().strftime("%W"))
	for i in range(2):
		generate_playlist(channel,weektocheck)
		weektocheck += 1

print("\n\n\n\n")

#---------------------------------------------------------------------------------------------------- OPEN CHANNEL
index = 0
for channel in data:
	print(str(index) + " " + channel["name"])
	index += 1
desired_channel = int(input("channel: "))

playlist_filename = "playlists/" + data[desired_channel]["name"] + " " + datetime.today().strftime("%Y-%W") + ".m3u"
playlist_file = open(playlist_filename,"r")

#current_time = (datetime.now().hour * 3600) + (datetime.now().minute * 60) + datetime.now().second
current_time = (datetime.now().weekday() * 86400) + (datetime.now() - datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
print("current time: " + str(current_time))
print(datetime.now().weekday())
playlistindex = 0
video_filename = ""
lasttime = 0
for line in playlist_file.readlines():
	if line[:2] == "#T":
		#print(line[1:])
		filetime = int(line[2:])
		if current_time <= filetime:
			print(playlistindex)
			print(video_filename)
			subprocess.run([
				"mpv",
				"--fullscreen",#"--no-osc",
				"--{",
				"--start=+" + str(math.floor(current_time - lasttime)),
				video_filename,
				"--}",
				"--{",
				"--playlist-start=" + str(playlistindex),
				playlist_filename,
				"--}"
			])
			break
		else:
			lasttime = filetime
		playlistindex += 1
	else:
		video_filename = line.replace("\n", "")