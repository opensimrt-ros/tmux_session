import rospy

def main():
    rospy.init_node("test_rate")
    r = rospy.Rate(200)
    while not rospy.is_shutdown():
        a = rospy.Time.now()
        r.sleep()
        b = rospy.Time.now()
        rospy.loginfo("sleep duration = %s "%(b-a))

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
