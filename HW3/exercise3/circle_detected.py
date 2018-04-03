import rospy, os, sys
from sound_play.msg import SoundRequest
from sound_play.libsoundplay import SoundClient

rospy.init_node("soundplay_test", anonymous = True)
soundhandle = SoundClient()
rospy.sleep(1)

soundhandle.stopAll()
s3 = soundhandle.voiceSound("AAAAAAAAAAAAAAAAAA")
s3.repeat()
rospy.sleep(3)
s3.stop()