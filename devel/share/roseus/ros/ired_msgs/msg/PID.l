;; Auto-generated. Do not edit!


(when (boundp 'ired_msgs::PID)
  (if (not (find-package "IRED_MSGS"))
    (make-package "IRED_MSGS"))
  (shadow 'PID (find-package "IRED_MSGS")))
(unless (find-package "IRED_MSGS::PID")
  (make-package "IRED_MSGS::PID"))

(in-package "ROS")
;;//! \htmlinclude PID.msg.html


(defclass ired_msgs::PID
  :super ros::object
  :slots (_motor _kp _ki _kd ))

(defmethod ired_msgs::PID
  (:init
   (&key
    ((:motor __motor) "")
    ((:kp __kp) 0.0)
    ((:ki __ki) 0.0)
    ((:kd __kd) 0.0)
    )
   (send-super :init)
   (setq _motor (string __motor))
   (setq _kp (float __kp))
   (setq _ki (float __ki))
   (setq _kd (float __kd))
   self)
  (:motor
   (&optional __motor)
   (if __motor (setq _motor __motor)) _motor)
  (:kp
   (&optional __kp)
   (if __kp (setq _kp __kp)) _kp)
  (:ki
   (&optional __ki)
   (if __ki (setq _ki __ki)) _ki)
  (:kd
   (&optional __kd)
   (if __kd (setq _kd __kd)) _kd)
  (:serialization-length
   ()
   (+
    ;; string _motor
    4 (length _motor)
    ;; float64 _kp
    8
    ;; float64 _ki
    8
    ;; float64 _kd
    8
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; string _motor
       (write-long (length _motor) s) (princ _motor s)
     ;; float64 _kp
       (sys::poke _kp (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;; float64 _ki
       (sys::poke _ki (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;; float64 _kd
       (sys::poke _kd (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; string _motor
     (let (n) (setq n (sys::peek buf ptr- :integer)) (incf ptr- 4) (setq _motor (subseq buf ptr- (+ ptr- n))) (incf ptr- n))
   ;; float64 _kp
     (setq _kp (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;; float64 _ki
     (setq _ki (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;; float64 _kd
     (setq _kd (sys::peek buf ptr- :double)) (incf ptr- 8)
   ;;
   self)
  )

(setf (get ired_msgs::PID :md5sum-) "2169d9d8246848be6270c046ce9df384")
(setf (get ired_msgs::PID :datatype-) "ired_msgs/PID")
(setf (get ired_msgs::PID :definition-)
      "string motor
float64 kp
float64 ki
float64 kd
")



(provide :ired_msgs/PID "2169d9d8246848be6270c046ce9df384")


