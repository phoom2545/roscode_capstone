#!/use/bin/env python3
import rospy
import sys, select, tty, termios
from geometry_msgs.msg import Twist

INIT_LINEAR_SPEED   = 0.0
INIT_ANGULAR_SPEED  = 0.0
MAX_LINEAR_SPEED    = 0.45
MAX_ANGULAR_SPEED   = 0.6
STEP_LINEAR_SIZE    = 0.05
STEP_ANGULAR_SIZE   = 0.1

message = """
Moving key:

        w
    a   s   d
        x
        
w/x or W/X : increase/decrease linear x velocity(MAX: ~ 0.66 m/s)
A/D : increase/decrease linear y velocity(MAX: ~ 0.66 m/s)
a/d : increase/decrease angular velocity(MAX: ~ 0.6 rad/s)

space key, s: force stop

CTRL-C to quit
"""

e = """
Communications Failed
"""

def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
    if rlist:
        key = sys.stdin.read(1)
    else:
        key = ''

    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key

def vels(target_linear_vel_x, target_linear_vel_y, target_angular_vel):
    return "currently:\tlinear x %s  m/s\tlinear y %s  m/s\t angular vel %s rad/s" % (target_linear_vel_x, target_linear_vel_y,target_angular_vel)

def makeSimpleProfile(output, input, slop):
    if input > output:
        output = min( input, output + slop )
    elif input < output:
        output = max( input, output - slop )
    else:
        output = input

    return output

def constrain(input, low, high):
    if input < low:
      input = low
    elif input > high:
      input = high
    else:
      input = input

    return input

def checkLinearLimitVelocity(vel):
    vel = constrain(vel, -MAX_LINEAR_SPEED, MAX_LINEAR_SPEED)

    return vel

def checkAngularLimitVelocity(vel):
    vel = constrain(vel, -MAX_ANGULAR_SPEED, MAX_ANGULAR_SPEED)

    return vel

if __name__ == '__main__' :
    settings = termios.tcgetattr(sys.stdin)
    rospy.init_node('ired_teleop_node')
    topic = rospy.get_param('~topic', '/cmd_vel')
    cmd_vel_pub = rospy.Publisher(topic, Twist, queue_size=10)
    
    target_linear_vel   = 0.0
    target_angular_vel  = 0.0
    control_linear_vel  = 0.0
    control_angular_vel = 0.0
    target_holonomic_linear_x = 0.0
    target_holonomic_linear_y = 0.0
    control_holominic_linear_x = 0.0
    control_holominic_linear_y = 0.0
    holonomic = False
    vel_stop = False
    
    try:
        print(message)
        while not rospy.is_shutdown():
            key = getKey()
            if key == 'w':
                target_linear_vel = checkLinearLimitVelocity(target_linear_vel + STEP_LINEAR_SIZE)
                holonomic = False
                vel_stop = False
                print(vels(target_linear_vel, 0.0, target_angular_vel))
            elif key == 'x':
                target_linear_vel = checkLinearLimitVelocity(target_linear_vel - STEP_LINEAR_SIZE)
                holonomic = False
                vel_stop = False
                print(vels(target_linear_vel, 0.0, target_angular_vel))
            elif key == 'a' :
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel + STEP_ANGULAR_SIZE)
                holonomic = False
                vel_stop = False
                print(vels(target_linear_vel, 0.0, target_angular_vel))
            elif key == 'd' :
                target_angular_vel = checkAngularLimitVelocity(target_angular_vel - STEP_ANGULAR_SIZE)
                holonomic = False
                vel_stop = False
                print(vels(target_linear_vel, 0.0, target_angular_vel))
            elif key == 'W':
                target_holonomic_linear_x = checkLinearLimitVelocity(target_holonomic_linear_x + STEP_LINEAR_SIZE)
                holonomic = True
                vel_stop = False
                print(vels(target_holonomic_linear_x,target_holonomic_linear_y, 0.0))
            elif key == 'X':
                target_holonomic_linear_x = checkLinearLimitVelocity(target_holonomic_linear_x - STEP_LINEAR_SIZE)
                holonomic = True
                vel_stop = False
                print(vels(target_holonomic_linear_x,target_holonomic_linear_y, 0.0))
            elif key == 'A' :
                target_holonomic_linear_y = checkAngularLimitVelocity(target_holonomic_linear_y + STEP_ANGULAR_SIZE)
                holonomic = True
                vel_stop = False
                print(vels(target_holonomic_linear_x,target_holonomic_linear_y, 0.0))
            elif key == 'D' :
                target_holonomic_linear_y = checkAngularLimitVelocity(target_holonomic_linear_y - STEP_ANGULAR_SIZE)
                holonomic = True
                vel_stop = False
                print(vels(target_holonomic_linear_x,target_holonomic_linear_y, 0.0))
            elif key == ' ' or key == 's' or key =='S':
                target_linear_vel   = 0.0
                target_angular_vel  = 0.0
                control_linear_vel  = 0.0
                control_angular_vel = 0.0
                target_holonomic_linear_x = 0.0
                target_holonomic_linear_y = 0.0
                control_holominic_linear_x = 0.0
                control_holominic_linear_y = 0.0
                print(vels(0.0, 0.0, 0.0))
                vel_stop = True
            else:
                if (key == '\x03'):
                    break
            if not holonomic and not vel_stop:
                twist = Twist()
                control_linear_vel = makeSimpleProfile(control_linear_vel, target_linear_vel, (STEP_LINEAR_SIZE/2.0))
                twist.linear.x = control_linear_vel; twist.linear.y = 0.0; twist.linear.z = 0.0
                control_angular_vel = makeSimpleProfile(control_angular_vel, target_angular_vel, (STEP_ANGULAR_SIZE/2.0))
                twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = control_angular_vel
                cmd_vel_pub.publish(twist)
            elif holonomic and not vel_stop: 
                twist = Twist()
                control_holominic_linear_x = makeSimpleProfile(control_holominic_linear_x, target_holonomic_linear_x, (STEP_LINEAR_SIZE/2.0))
                control_holominic_linear_y = makeSimpleProfile(control_holominic_linear_y, target_holonomic_linear_y, (STEP_ANGULAR_SIZE/2.0))
                twist.linear.x = control_holominic_linear_x; twist.linear.y = control_holominic_linear_y; twist.linear.z = 0.0
                twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
                cmd_vel_pub.publish(twist)
            elif vel_stop:
                twist.linear.x = 0.0; twist.linear.y = 0.0; twist.linear.z = 0.0
                twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
                cmd_vel_pub.publish(twist)
        
    except:
        print(e)
        
    finally:
        twist = Twist()
        twist.linear.x = 0.0; twist.linear.y = 0.0; twist.linear.z = 0.0
        twist.angular.x = 0.0; twist.angular.y = 0.0; twist.angular.z = 0.0
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)