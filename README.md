# Real-Time-Background-Replacement
A tool that takes video and replace with new background provided by user in real time.

## Table of contents
- [Description](#description)
- [Technologies used](#technologies-used)
- [Results](#results)
- [How it works](#how-it-works)
- [Contributors](#contributors)


### Description
 Background removal helps with creative portrait photography and much more, helping provide the ability to change the background to a location of your choice. There are 3 methods available to use. One is a simple live-method using the webcam, a user can change the background by pressing and holding 'a', 'b', or 'c'. Other is live streaming from a mobile app. The last one is by requesting the server with pre-recorded video and background picture of choice.
 
### Technologies Used
- Tensorflow
- OpenCV
- Flask

### Results
Input | Background | Result
:-------:|:---------:|:---------:
![input](https://drive.google.com/uc?id=13_bDk_G6u7Z2vZ4cMUqbmIU4j3bRVMX8) | ![background](https://drive.google.com/uc?id=1FpZqv_5Xt436K29Y5-ZAk_aOxC7Wdg29) | ![output](https://drive.google.com/uc?id=152GFmsJyxaOUjzUfMeEP7NbX5xYP5iIP)

### How It Works
```sh
$ git clone https://github.com/neatpun/real-time-background-replacement
```

1. Live Webcam Front
* ```cd "Live Webcam Front" ``` 
* install dependencies
* ```python live_webcam.py ```

2. Server Front
* ```cd "Server Front"```
* install dependencies
* ```FLASK_APP=index.py flask run```
* then open localhost:5000
* provide video and background image
* after processing download of required video will begin

3. Live Stream Output
* ```cd "Live Stream Output"```
* install dependencies
* connect any mobile device to same network and stream video.
* provide the ip address of mobile device in **IP_Webcam_Out.py**
* ```python IP_Webcam_Out.py```

### Contributors
- [Mohit Nathrani](https://github.com/Mohit-Nathrani)
- [Raghav Mahajan](https://github.com/Raghav-intrigue)
- [Prathamesh Naik](https://github.com/neatpun)
