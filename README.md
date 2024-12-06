# Automatic Youtube Short Creator
Makes shorts automatically given a minecraft_parkour.mp4 and also a subscripting model


You can replace the file names for the minecraft_parkour.mp4 if you want to or just change the entire file to some other background.

Here is how you get all of the Credentials:

For the tiktok voice generator:

https://github.com/Steve0929/tiktok-tts
refer to the get session ID part with the cookies

To get the google cloud authentication stuff:

Go to Google cloud, make a project and enable the Youtube Data API v3
Make an oAuth screen, and also make sure you have the scopes for uploading and seeing channel data.
Then install the client_secret.json and put that inside of the same diretory.

To get the vosk model:

https://alphacephei.com/vosk/install

You can change to code so that it uses the default vosk model for python, but you have more variety with the present code, and make sure to edit the file name in both main.py and the test_srt.py

**MAKE SURE YOU KNOW THIS**
Youtube only allows for 6 uploads a day
