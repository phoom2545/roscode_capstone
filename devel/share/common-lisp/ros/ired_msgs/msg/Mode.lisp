; Auto-generated. Do not edit!


(cl:in-package ired_msgs-msg)


;//! \htmlinclude Mode.msg.html

(cl:defclass <Mode> (roslisp-msg-protocol:ros-message)
  ((differential_wheel
    :reader differential_wheel
    :initarg :differential_wheel
    :type cl:boolean
    :initform cl:nil))
)

(cl:defclass Mode (<Mode>)
  ())

(cl:defmethod cl:initialize-instance :after ((m <Mode>) cl:&rest args)
  (cl:declare (cl:ignorable args))
  (cl:unless (cl:typep m 'Mode)
    (roslisp-msg-protocol:msg-deprecation-warning "using old message class name ired_msgs-msg:<Mode> is deprecated: use ired_msgs-msg:Mode instead.")))

(cl:ensure-generic-function 'differential_wheel-val :lambda-list '(m))
(cl:defmethod differential_wheel-val ((m <Mode>))
  (roslisp-msg-protocol:msg-deprecation-warning "Using old-style slot reader ired_msgs-msg:differential_wheel-val is deprecated.  Use ired_msgs-msg:differential_wheel instead.")
  (differential_wheel m))
(cl:defmethod roslisp-msg-protocol:serialize ((msg <Mode>) ostream)
  "Serializes a message object of type '<Mode>"
  (cl:write-byte (cl:ldb (cl:byte 8 0) (cl:if (cl:slot-value msg 'differential_wheel) 1 0)) ostream)
)
(cl:defmethod roslisp-msg-protocol:deserialize ((msg <Mode>) istream)
  "Deserializes a message object of type '<Mode>"
    (cl:setf (cl:slot-value msg 'differential_wheel) (cl:not (cl:zerop (cl:read-byte istream))))
  msg
)
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql '<Mode>)))
  "Returns string type for a message object of type '<Mode>"
  "ired_msgs/Mode")
(cl:defmethod roslisp-msg-protocol:ros-datatype ((msg (cl:eql 'Mode)))
  "Returns string type for a message object of type 'Mode"
  "ired_msgs/Mode")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql '<Mode>)))
  "Returns md5sum for a message object of type '<Mode>"
  "e0f5377ca955b8c348e5de93be73c07e")
(cl:defmethod roslisp-msg-protocol:md5sum ((type (cl:eql 'Mode)))
  "Returns md5sum for a message object of type 'Mode"
  "e0f5377ca955b8c348e5de93be73c07e")
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql '<Mode>)))
  "Returns full string definition for message of type '<Mode>"
  (cl:format cl:nil "bool differential_wheel~%~%~%"))
(cl:defmethod roslisp-msg-protocol:message-definition ((type (cl:eql 'Mode)))
  "Returns full string definition for message of type 'Mode"
  (cl:format cl:nil "bool differential_wheel~%~%~%"))
(cl:defmethod roslisp-msg-protocol:serialization-length ((msg <Mode>))
  (cl:+ 0
     1
))
(cl:defmethod roslisp-msg-protocol:ros-message-to-list ((msg <Mode>))
  "Converts a ROS message object to a list"
  (cl:list 'Mode
    (cl:cons ':differential_wheel (differential_wheel msg))
))
