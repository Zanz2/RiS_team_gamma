from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient
import os
import sys
import rospy

rospy.init_node('just_sound', anonymous=True)

soundhandle = SoundClient()
rospy.sleep(1)
soundhandle.stopAll()

s3 = soundhandle.voiceSound("Cilinder found" ,5)
s3.play()
rospy.sleep(3)
s3.stop()

'''
soundhandle = SoundClient()
soundhandle.stopAll()
    
s3 = soundhandle.voiceSound("Cylinder found" ,5)
s3.play()
sleep(3)
'''
