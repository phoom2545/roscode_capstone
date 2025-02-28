#include <ired_bringup/ired_odom.h>

IREDODOM::IREDODOM()
: nh_priv_("~"){
    bool init_result = init();
    ROS_ASSERT(init_result);
}

IREDODOM::~IREDODOM(){

}

bool IREDODOM::init(){
    nh_priv_.param("base_frame", odom_.child_frame_id, std::string("base_footprint"));
    nh_priv_.param("joint_states_frame", joint_states_.header.frame_id, std::string("base_footprint"));
    nh_priv_.param("odom_frame", odom_.header.frame_id, std::string("odom"));
    nh_priv_.param("odom_tf_publish", odom_tf_publish_, false);
    nh_priv_.param("wheel_left_joint_name", joint_states_name_[LEFT],  std::string("wheel_left_joint"));
    nh_priv_.param("wheel_right_joint_name", joint_states_name_[RIGHT],  std::string("wheel_right_joint"));

    double pcov[36] = { 0.1, 0,   0,   0,   0, 0,
                        0, 0.1,   0,   0,   0, 0,
                        0,   0, 1e6,   0,   0, 0,
                        0,   0,   0, 1e6,   0, 0,
                        0,   0,   0,   0, 1e6, 0,
                        0,   0,   0,   0,   0, 0.2};
    memcpy(&(odom_.pose.covariance),pcov,sizeof(double)*36);
    memcpy(&(odom_.twist.covariance),pcov,sizeof(double)*36);

    joint_states_.name.push_back(joint_states_name_[LEFT]);
    joint_states_.name.push_back(joint_states_name_[RIGHT]);
    joint_states_.position.resize(2,0.0);
    joint_states_.velocity.resize(2,0.0);
    joint_states_.effort.resize(2,0.0);

    ROS_INFO("Initialize variables.");

    // Initialize publishers
    joint_states_pub_   = nh_.advertise<sensor_msgs::JointState>("/joint_states", 100);
    odom_pub_           = nh_.advertise<nav_msgs::Odometry>("/odom/encoder", 100);
    ROS_INFO("ROS publisher on /joint_states [sensor_msgs/JointState]");
    ROS_INFO("ROS publisher on /odom/encoder [nav_msgs/Odometry]");

    // Initialize subscribers
    motor_sub_          = nh_.subscribe("/ired/motor", 100, &IREDODOM::fetchMotorCallback, this);
    imu_sub_            = nh_.subscribe("/ired/rollpitchyaw", 100, &IREDODOM::fetchAngularCallback, this);
    ROS_INFO("ROS subscriber on /ired/rollpitchyaw [ired_msgs/IMU]");
    ROS_INFO("ROS subscriber on /ired/motor [ired_msgs/Motor]");

    prev_update_time_ = ros::Time::now();

    return true;
}

void IREDODOM::fetchMotorCallback(const ired_msgs::MotorConstPtr msg_){
    last_cmd_vel_time_ = ros::Time::now();

    wheel_speed_cmd_[LEFT] = RPM2MPS((double)msg_->speed_fb[LEFT]);
    wheel_speed_cmd_[RIGHT] = RPM2MPS((double)msg_->speed_fb[RIGHT]);
}

void IREDODOM::fetchAngularCallback(const ired_msgs::IMUConstPtr msg_){
    angular_[ROLL] = (double)msg_->roll;
    angular_[PITCH] = (double)msg_->pitch;
    angular_[YAW] = (double)msg_->yaw;
}

void IREDODOM::commandResetCallback(const std_msgs::EmptyConstPtr reset_odom)
{
    wheel_speed_cmd_[LEFT]  = 0.0;
    wheel_speed_cmd_[RIGHT] = 0.0;
    angular_[ROLL]          = 0.0;
    angular_[PITCH]         = 0.0;
    angular_[YAW]           = 0.0;
    last_position_[LEFT]    = 0.0;
    last_position_[RIGHT]   = 0.0;

    double pcov[36] = { 0.1, 0,   0,   0,   0, 0,
                        0, 0.1,   0,   0,   0, 0,
                        0,   0, 1e6,   0,   0, 0,
                        0,   0,   0, 1e6,   0, 0,
                        0,   0,   0,   0, 1e6, 0,
                        0,   0,   0,   0,   0, 0.2};
    memcpy(&(odom_.pose.covariance),pcov,sizeof(double)*36);
    memcpy(&(odom_.twist.covariance),pcov,sizeof(double)*36);

    odom_pose_[0] = 0.0;
    odom_pose_[1] = 0.0;
    odom_pose_[2] = 0.0;

    odom_vel_[0] = 0.0;
    odom_vel_[1] = 0.0;
    odom_vel_[2] = 0.0;

    ROS_INFO("Reset Odometry.");
}

bool IREDODOM::updateOdometry(ros::Duration diff_time){
    double wheel_l, wheel_r;
    double delta_s, theta, delta_theta;
    double v[2], w[2];
    static double last_theta = 0.0;

    wheel_l = wheel_r       = 0.0;
    delta_s = theta = delta_theta  = 0.0;

    v[LEFT]  = wheel_speed_cmd_[LEFT];
    w[LEFT]  = v[LEFT] / WHEEL_RADIUS;
    v[RIGHT] = wheel_speed_cmd_[RIGHT];
    w[RIGHT] = v[RIGHT] / WHEEL_RADIUS;

    wheel_l = w[LEFT]   * diff_time.toSec();
    wheel_r = w[RIGHT]  * diff_time.toSec();

    if(isnan(wheel_l))  wheel_l = 0.0;
    if(isnan(wheel_r))  wheel_r = 0.0;

    delta_s     = WHEEL_RADIUS * (wheel_r + wheel_l) / 2.0;
    theta       = DEG2RAD(angular_[YAW]);
    delta_theta = theta - last_theta;
    
    // compute odometric pose
    odom_pose_[0] += delta_s * cos(odom_pose_[2] + (delta_theta / 2.0));
    odom_pose_[1] += delta_s * sin(odom_pose_[2] + (delta_theta / 2.0));
    odom_pose_[2] += delta_theta;

    // compute odometric instantaneouse velocity
    odom_vel_[0] = delta_s / diff_time.toSec();     // v
    odom_vel_[1] = 0.0;
    odom_vel_[2] = delta_theta / diff_time.toSec(); // w

    odom_.pose.pose.position.x = odom_pose_[0];
    odom_.pose.pose.position.y = odom_pose_[1];
    odom_.pose.pose.position.z = 0;
    odom_.pose.pose.orientation = tf::createQuaternionMsgFromYaw(odom_pose_[2]);

    // We should update the twist of the odometry
    odom_.twist.twist.linear.x  = odom_vel_[0];
    odom_.twist.twist.angular.z = odom_vel_[2];

    // Update Data
    last_velocity_[LEFT]  = w[LEFT];
    last_velocity_[RIGHT] = w[RIGHT];
    last_position_[LEFT]  += wheel_l;
    last_position_[RIGHT] += wheel_r;
    last_theta = theta;

    return true;
}

void IREDODOM::updateJoint(void){
    joint_states_.position[LEFT]    = last_position_[LEFT];
    joint_states_.position[RIGHT]   = last_position_[RIGHT];
    joint_states_.velocity[LEFT]    = last_velocity_[LEFT];
    joint_states_.velocity[RIGHT]   = last_velocity_[RIGHT];
}

void IREDODOM::updateTF(geometry_msgs::TransformStamped& odom_tf)
{
    odom_tf.header = odom_.header;
    odom_tf.child_frame_id = odom_.child_frame_id;
    odom_tf.transform.translation.x = odom_.pose.pose.position.x;
    odom_tf.transform.translation.y = odom_.pose.pose.position.y;
    odom_tf.transform.translation.z = odom_.pose.pose.position.z;
    odom_tf.transform.rotation = odom_.pose.pose.orientation;
}

bool IREDODOM::update(){
    ros::Time time_now = ros::Time::now();
    ros::Duration step_time = time_now - prev_update_time_;
    prev_update_time_ = time_now;

    if((time_now - last_cmd_vel_time_).toSec() > 1.0){
        wheel_speed_cmd_[LEFT]  = 0.0;
        wheel_speed_cmd_[RIGHT] = 0.0;
    }

    updateOdometry(step_time);
    odom_.header.stamp = time_now;
    odom_pub_.publish(odom_);

    updateJoint();
    joint_states_.header.stamp = time_now;
    joint_states_pub_.publish(joint_states_);

    if(odom_tf_publish_){
        geometry_msgs::TransformStamped odom_tf;
        updateTF(odom_tf);
        tf_broadcaster_.sendTransform(odom_tf);
    }

    return true;
}

int main(int argc, char* argv[]){
    ros::init(argc, argv, "ired_odom_node");
    IREDODOM ired_odom_;

    ros::Rate loop_rate(30);

    while (ros::ok()){
        ired_odom_.update();
        ros::spinOnce();
        loop_rate.sleep();
    }
    
    return 0;
}