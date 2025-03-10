// Auto-generated. Do not edit!

// (in-package ired_msgs.msg)


"use strict";

const _serializer = _ros_msg_utils.Serialize;
const _arraySerializer = _serializer.Array;
const _deserializer = _ros_msg_utils.Deserialize;
const _arrayDeserializer = _deserializer.Array;
const _finder = _ros_msg_utils.Find;
const _getByteLength = _ros_msg_utils.getByteLength;

//-----------------------------------------------------------

class Motor {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.speed_sp = null;
      this.speed_fb = null;
      this.pid_motor_front_left = null;
      this.pid_motor_front_right = null;
      this.pid_motor_rear_left = null;
      this.pid_motor_rear_right = null;
    }
    else {
      if (initObj.hasOwnProperty('speed_sp')) {
        this.speed_sp = initObj.speed_sp
      }
      else {
        this.speed_sp = new Array(4).fill(0);
      }
      if (initObj.hasOwnProperty('speed_fb')) {
        this.speed_fb = initObj.speed_fb
      }
      else {
        this.speed_fb = new Array(4).fill(0);
      }
      if (initObj.hasOwnProperty('pid_motor_front_left')) {
        this.pid_motor_front_left = initObj.pid_motor_front_left
      }
      else {
        this.pid_motor_front_left = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('pid_motor_front_right')) {
        this.pid_motor_front_right = initObj.pid_motor_front_right
      }
      else {
        this.pid_motor_front_right = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('pid_motor_rear_left')) {
        this.pid_motor_rear_left = initObj.pid_motor_rear_left
      }
      else {
        this.pid_motor_rear_left = new Array(3).fill(0);
      }
      if (initObj.hasOwnProperty('pid_motor_rear_right')) {
        this.pid_motor_rear_right = initObj.pid_motor_rear_right
      }
      else {
        this.pid_motor_rear_right = new Array(3).fill(0);
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Motor
    // Check that the constant length array field [speed_sp] has the right length
    if (obj.speed_sp.length !== 4) {
      throw new Error('Unable to serialize array field speed_sp - length must be 4')
    }
    // Serialize message field [speed_sp]
    bufferOffset = _arraySerializer.float64(obj.speed_sp, buffer, bufferOffset, 4);
    // Check that the constant length array field [speed_fb] has the right length
    if (obj.speed_fb.length !== 4) {
      throw new Error('Unable to serialize array field speed_fb - length must be 4')
    }
    // Serialize message field [speed_fb]
    bufferOffset = _arraySerializer.float64(obj.speed_fb, buffer, bufferOffset, 4);
    // Check that the constant length array field [pid_motor_front_left] has the right length
    if (obj.pid_motor_front_left.length !== 3) {
      throw new Error('Unable to serialize array field pid_motor_front_left - length must be 3')
    }
    // Serialize message field [pid_motor_front_left]
    bufferOffset = _arraySerializer.float64(obj.pid_motor_front_left, buffer, bufferOffset, 3);
    // Check that the constant length array field [pid_motor_front_right] has the right length
    if (obj.pid_motor_front_right.length !== 3) {
      throw new Error('Unable to serialize array field pid_motor_front_right - length must be 3')
    }
    // Serialize message field [pid_motor_front_right]
    bufferOffset = _arraySerializer.float64(obj.pid_motor_front_right, buffer, bufferOffset, 3);
    // Check that the constant length array field [pid_motor_rear_left] has the right length
    if (obj.pid_motor_rear_left.length !== 3) {
      throw new Error('Unable to serialize array field pid_motor_rear_left - length must be 3')
    }
    // Serialize message field [pid_motor_rear_left]
    bufferOffset = _arraySerializer.float64(obj.pid_motor_rear_left, buffer, bufferOffset, 3);
    // Check that the constant length array field [pid_motor_rear_right] has the right length
    if (obj.pid_motor_rear_right.length !== 3) {
      throw new Error('Unable to serialize array field pid_motor_rear_right - length must be 3')
    }
    // Serialize message field [pid_motor_rear_right]
    bufferOffset = _arraySerializer.float64(obj.pid_motor_rear_right, buffer, bufferOffset, 3);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Motor
    let len;
    let data = new Motor(null);
    // Deserialize message field [speed_sp]
    data.speed_sp = _arrayDeserializer.float64(buffer, bufferOffset, 4)
    // Deserialize message field [speed_fb]
    data.speed_fb = _arrayDeserializer.float64(buffer, bufferOffset, 4)
    // Deserialize message field [pid_motor_front_left]
    data.pid_motor_front_left = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [pid_motor_front_right]
    data.pid_motor_front_right = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [pid_motor_rear_left]
    data.pid_motor_rear_left = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    // Deserialize message field [pid_motor_rear_right]
    data.pid_motor_rear_right = _arrayDeserializer.float64(buffer, bufferOffset, 3)
    return data;
  }

  static getMessageSize(object) {
    return 160;
  }

  static datatype() {
    // Returns string type for a message object
    return 'ired_msgs/Motor';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'ec2526e9a146e07c0941072e0ef16c7b';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    float64[4] speed_sp
    float64[4] speed_fb
    float64[3] pid_motor_front_left
    float64[3] pid_motor_front_right
    float64[3] pid_motor_rear_left
    float64[3] pid_motor_rear_right
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Motor(null);
    if (msg.speed_sp !== undefined) {
      resolved.speed_sp = msg.speed_sp;
    }
    else {
      resolved.speed_sp = new Array(4).fill(0)
    }

    if (msg.speed_fb !== undefined) {
      resolved.speed_fb = msg.speed_fb;
    }
    else {
      resolved.speed_fb = new Array(4).fill(0)
    }

    if (msg.pid_motor_front_left !== undefined) {
      resolved.pid_motor_front_left = msg.pid_motor_front_left;
    }
    else {
      resolved.pid_motor_front_left = new Array(3).fill(0)
    }

    if (msg.pid_motor_front_right !== undefined) {
      resolved.pid_motor_front_right = msg.pid_motor_front_right;
    }
    else {
      resolved.pid_motor_front_right = new Array(3).fill(0)
    }

    if (msg.pid_motor_rear_left !== undefined) {
      resolved.pid_motor_rear_left = msg.pid_motor_rear_left;
    }
    else {
      resolved.pid_motor_rear_left = new Array(3).fill(0)
    }

    if (msg.pid_motor_rear_right !== undefined) {
      resolved.pid_motor_rear_right = msg.pid_motor_rear_right;
    }
    else {
      resolved.pid_motor_rear_right = new Array(3).fill(0)
    }

    return resolved;
    }
};

module.exports = Motor;
