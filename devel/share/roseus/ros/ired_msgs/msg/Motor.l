;; Auto-generated. Do not edit!


(when (boundp 'ired_msgs::Motor)
  (if (not (find-package "IRED_MSGS"))
    (make-package "IRED_MSGS"))
  (shadow 'Motor (find-package "IRED_MSGS")))
(unless (find-package "IRED_MSGS::MOTOR")
  (make-package "IRED_MSGS::MOTOR"))

(in-package "ROS")
;;//! \htmlinclude Motor.msg.html


(defclass ired_msgs::Motor
  :super ros::object
  :slots (_speed_sp _speed_fb _pid_motor_front_left _pid_motor_front_right _pid_motor_rear_left _pid_motor_rear_right ))

(defmethod ired_msgs::Motor
  (:init
   (&key
    ((:speed_sp __speed_sp) (make-array 4 :initial-element 0.0 :element-type :float))
    ((:speed_fb __speed_fb) (make-array 4 :initial-element 0.0 :element-type :float))
    ((:pid_motor_front_left __pid_motor_front_left) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:pid_motor_front_right __pid_motor_front_right) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:pid_motor_rear_left __pid_motor_rear_left) (make-array 3 :initial-element 0.0 :element-type :float))
    ((:pid_motor_rear_right __pid_motor_rear_right) (make-array 3 :initial-element 0.0 :element-type :float))
    )
   (send-super :init)
   (setq _speed_sp __speed_sp)
   (setq _speed_fb __speed_fb)
   (setq _pid_motor_front_left __pid_motor_front_left)
   (setq _pid_motor_front_right __pid_motor_front_right)
   (setq _pid_motor_rear_left __pid_motor_rear_left)
   (setq _pid_motor_rear_right __pid_motor_rear_right)
   self)
  (:speed_sp
   (&optional __speed_sp)
   (if __speed_sp (setq _speed_sp __speed_sp)) _speed_sp)
  (:speed_fb
   (&optional __speed_fb)
   (if __speed_fb (setq _speed_fb __speed_fb)) _speed_fb)
  (:pid_motor_front_left
   (&optional __pid_motor_front_left)
   (if __pid_motor_front_left (setq _pid_motor_front_left __pid_motor_front_left)) _pid_motor_front_left)
  (:pid_motor_front_right
   (&optional __pid_motor_front_right)
   (if __pid_motor_front_right (setq _pid_motor_front_right __pid_motor_front_right)) _pid_motor_front_right)
  (:pid_motor_rear_left
   (&optional __pid_motor_rear_left)
   (if __pid_motor_rear_left (setq _pid_motor_rear_left __pid_motor_rear_left)) _pid_motor_rear_left)
  (:pid_motor_rear_right
   (&optional __pid_motor_rear_right)
   (if __pid_motor_rear_right (setq _pid_motor_rear_right __pid_motor_rear_right)) _pid_motor_rear_right)
  (:serialization-length
   ()
   (+
    ;; float64[4] _speed_sp
    (* 8    4)
    ;; float64[4] _speed_fb
    (* 8    4)
    ;; float64[3] _pid_motor_front_left
    (* 8    3)
    ;; float64[3] _pid_motor_front_right
    (* 8    3)
    ;; float64[3] _pid_motor_rear_left
    (* 8    3)
    ;; float64[3] _pid_motor_rear_right
    (* 8    3)
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; float64[4] _speed_sp
     (dotimes (i 4)
       (sys::poke (elt _speed_sp i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[4] _speed_fb
     (dotimes (i 4)
       (sys::poke (elt _speed_fb i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _pid_motor_front_left
     (dotimes (i 3)
       (sys::poke (elt _pid_motor_front_left i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _pid_motor_front_right
     (dotimes (i 3)
       (sys::poke (elt _pid_motor_front_right i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _pid_motor_rear_left
     (dotimes (i 3)
       (sys::poke (elt _pid_motor_rear_left i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;; float64[3] _pid_motor_rear_right
     (dotimes (i 3)
       (sys::poke (elt _pid_motor_rear_right i) (send s :buffer) (send s :count) :double) (incf (stream-count s) 8)
       )
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; float64[4] _speed_sp
   (dotimes (i (length _speed_sp))
     (setf (elt _speed_sp i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[4] _speed_fb
   (dotimes (i (length _speed_fb))
     (setf (elt _speed_fb i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _pid_motor_front_left
   (dotimes (i (length _pid_motor_front_left))
     (setf (elt _pid_motor_front_left i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _pid_motor_front_right
   (dotimes (i (length _pid_motor_front_right))
     (setf (elt _pid_motor_front_right i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _pid_motor_rear_left
   (dotimes (i (length _pid_motor_rear_left))
     (setf (elt _pid_motor_rear_left i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;; float64[3] _pid_motor_rear_right
   (dotimes (i (length _pid_motor_rear_right))
     (setf (elt _pid_motor_rear_right i) (sys::peek buf ptr- :double)) (incf ptr- 8)
     )
   ;;
   self)
  )

(setf (get ired_msgs::Motor :md5sum-) "ec2526e9a146e07c0941072e0ef16c7b")
(setf (get ired_msgs::Motor :datatype-) "ired_msgs/Motor")
(setf (get ired_msgs::Motor :definition-)
      "float64[4] speed_sp
float64[4] speed_fb
float64[3] pid_motor_front_left
float64[3] pid_motor_front_right
float64[3] pid_motor_rear_left
float64[3] pid_motor_rear_right
")



(provide :ired_msgs/Motor "ec2526e9a146e07c0941072e0ef16c7b")


