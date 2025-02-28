;; Auto-generated. Do not edit!


(when (boundp 'ired_msgs::Mode)
  (if (not (find-package "IRED_MSGS"))
    (make-package "IRED_MSGS"))
  (shadow 'Mode (find-package "IRED_MSGS")))
(unless (find-package "IRED_MSGS::MODE")
  (make-package "IRED_MSGS::MODE"))

(in-package "ROS")
;;//! \htmlinclude Mode.msg.html


(defclass ired_msgs::Mode
  :super ros::object
  :slots (_differential_wheel ))

(defmethod ired_msgs::Mode
  (:init
   (&key
    ((:differential_wheel __differential_wheel) nil)
    )
   (send-super :init)
   (setq _differential_wheel __differential_wheel)
   self)
  (:differential_wheel
   (&optional (__differential_wheel :null))
   (if (not (eq __differential_wheel :null)) (setq _differential_wheel __differential_wheel)) _differential_wheel)
  (:serialization-length
   ()
   (+
    ;; bool _differential_wheel
    1
    ))
  (:serialize
   (&optional strm)
   (let ((s (if strm strm
              (make-string-output-stream (send self :serialization-length)))))
     ;; bool _differential_wheel
       (if _differential_wheel (write-byte -1 s) (write-byte 0 s))
     ;;
     (if (null strm) (get-output-stream-string s))))
  (:deserialize
   (buf &optional (ptr- 0))
   ;; bool _differential_wheel
     (setq _differential_wheel (not (= 0 (sys::peek buf ptr- :char)))) (incf ptr- 1)
   ;;
   self)
  )

(setf (get ired_msgs::Mode :md5sum-) "e0f5377ca955b8c348e5de93be73c07e")
(setf (get ired_msgs::Mode :datatype-) "ired_msgs/Mode")
(setf (get ired_msgs::Mode :definition-)
      "bool differential_wheel

")



(provide :ired_msgs/Mode "e0f5377ca955b8c348e5de93be73c07e")


