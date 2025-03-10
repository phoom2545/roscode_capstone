#ifndef IRED_ODOM_H__
#define IRED_ODOM_H__

#include <math.h>

#include <ros/ros.h>
#include <ros/time.h>
#include <ired_msgs/IMU.h>
#include <ired_msgs/Motor.h>
#include <nav_msgs/Odometry.h>
#include <sensor_msgs/JointState.h>
#include <std_msgs/Empty.h>
#include <tf/tf.h>
#include <tf/transform_broadcaster.h>

#define ROLL    0
#define PITCH   1
#define YAW     2
#define WHEEL_RADIUS    0.034
#define LEFT            0
#define RIGHT           1
#define DEG2RAD(x)      (x * 0.01745329252) // PI/180
#define RPM2MPS(x)      (x * 0.003560471674) // V = (2*PI*r)/60 * N


class IREDODOM{
    public:
        IREDODOM();
        ~IREDODOM();
        bool init();
        bool update();
    
    private:
        // ROS Nodes;
        ros::NodeHandle nh_;
        ros::NodeHandle nh_priv_;

        // ROS Time
        ros::Time last_cmd_vel_time_;
        ros::Time prev_update_time_;

        // ROS Publishers
        ros::Publisher joint_states_pub_;
        ros::Publisher odom_pub_;

        // ROS Subscribers
        ros::Subscriber motor_sub_;
        ros::Subscriber imu_sub_;
        ros::Subscriber reset_odom_;

        // ROS Variables
        sensor_msgs::JointState joint_states_;
        nav_msgs::Odometry odom_;
        tf::TransformBroadcaster tf_broadcaster_;

        double odom_pose_[3] = {0.0, 0.0, 0.0};
        double odom_vel_[3] = {0.0, 0.0, 0.0};
        bool odom_tf_publish_ = false;

        std::string joint_states_name_[2];
        double wheel_speed_cmd_[2];
        double angular_[3] = {0.0, 0.0, 0.0};
        double last_position_[2];
        double last_velocity_[2];
        

        void fetchMotorCallback(const ired_msgs::MotorConstPtr msg_);
        void fetchAngularCallback(const ired_msgs::IMUConstPtr msg_);
        void commandResetCallback(const std_msgs::EmptyConstPtr reset_odom);
        void updateJoint(void);
        bool updateOdometry(ros::Duration diff_time);
        void updateTF(geometry_msgs::TransformStamped& odom_tf);
};

#endif