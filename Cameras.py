""" Module Cameras """
##Copyright 2016 Clint H. O'Connor
##
##   Licensed under the Apache License, Version 2.0 (the "License");
##   you may not use this file except in compliance with the License.
##   You may obtain a copy of the License at
##
##       http://www.apache.org/licenses/LICENSE-2.0
##
##   Unless required by applicable law or agreed to in writing, software
##   distributed under the License is distributed on an "AS IS" BASIS,
##   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##   See the License for the specific language governing permissions and
##   limitations under the License.


##----- imports -----------------------------------------------------------------
import time
import datetime
from io import BytesIO
from picamera import PiCamera
from PIL import Image


##----- classes --------------------------------------------------------------------

class Cameras:
""" Cameras is a base class for different sensor types """

    still_formats = ('jpeg', 'gif', 'png', 'bmp', 'yuv', 'rgb', 'rgba', 'bgr', 'bgra')
    video_formats = ('h264', 'mjpeg')
    VGA = (640, 480)
    SVGA = (800, 600)
    XGA = (1024, 768)
    SXGA = (1400, 1050)
    HD720 = (1280, 720)
    HD1080 = (1920, 1080)
    PI = (2592, 1944)
    PI2 = (3280, 2464)

class Camera_Pi(object):
""" Camera_Pi is a Pi camera class of camera """

    def __init__(self, resolution=Cameras.HD720, iformat='jpeg', usevideoport=False):
        try:
            self.camera = PiCamera()
            self.resolution = resolution
            self.format = iformat
            self.usevideoport = usevideoport
            if (iformat in Cameras.still_formats) or (iformat in Cameras.video_formats):
                return
            else:
                raise Exception("error: Camera_Pi::__init__ invalid format")
        
        except:
            raise Exception("crashed: Camera_Pi::__init__")

    def __del__(self):
        try:
            if self.camera is not None:
                self.camera.close()
            return
        except:
            raise Exception("crashed: Camera_Pi::__del__")

    def snap(self, capture):
""" snap a picture using current settings """
        try:
            if capture is not None:
                self.camera.capture(capture, self.format)
                return True
            else:
                return False
        except:
            raise Exception("crashed: Camera_Pi::snap")

    def snap_timelapse(self, capture, interval=0.5):
""" snap a sequence of pictures using a specified timelapse interval """
        try:
            if capture is not None and interval > 0:
                self.camera.start_preview()
                imgfilename = capture + datetime.datetime.utcnow().strftime("-%Y-%m-%d-%H-%M-%S")
                for filename in self.camera.capture_continuous(imgfilename + '{counter:03d}.' + self.format, self.format):
                    time.sleep(interval)
                self.camera.stop_preview()
                return True
            else:
                return False
        except:
            raise Exception("crashed: Camera_Pi::snap")

    def snap_jpeg_sequence(self, capture, framerate=30, frames=300):

        def _framename():
            frame = 0
            fname = capture + datetime.datetime.utcnow().strftime("-%Y-%m-%d-%H-%M-%S-")
            while frame < frames:
                yield (fname + "%03d.jpeg") % frame
                frame += 1
            
        try:
            if capture is not None and framerate > 0:
                self.camera.framerate = framerate
                self.camera.start_preview()
                name = _framename()
                self.camera.capture_sequence(_framename(), use_video_port = True)
                self.camera.stop_preview()
                return True
            else:
                return False
        except:
            raise Exception("crashed: Camera_Pi::snap")

    def record(self, capture, vformat= 'h264', framerate=30, seconds=None):
""" record a video at a specific frame rate for a number of seconds """
        try:
            if vformat in Cameras.video_formats:
                self.camera.framerate = framerate
                self.camera.start_recording(capture + "." + vformat)
                self.camera.capture(capture + ".jpeg")
                if seconds is None:
                    return True
                else:
                    self.camera.wait_recording(seconds)
                    self.camera.stop_recording()
                    return True
            else:
                return False
        except:
            raise Exception("crashed: Camera_Pi::record")

    def stop(self):
        try:
            self.camera.stop_recording()
            return True
        except:
            raise Exception("crashed: Camera_Pi::stop")
             
