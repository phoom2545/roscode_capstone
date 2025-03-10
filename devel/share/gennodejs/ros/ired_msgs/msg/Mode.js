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

class Mode {
  constructor(initObj={}) {
    if (initObj === null) {
      // initObj === null is a special case for deserialization where we don't initialize fields
      this.differential_wheel = null;
    }
    else {
      if (initObj.hasOwnProperty('differential_wheel')) {
        this.differential_wheel = initObj.differential_wheel
      }
      else {
        this.differential_wheel = false;
      }
    }
  }

  static serialize(obj, buffer, bufferOffset) {
    // Serializes a message object of type Mode
    // Serialize message field [differential_wheel]
    bufferOffset = _serializer.bool(obj.differential_wheel, buffer, bufferOffset);
    return bufferOffset;
  }

  static deserialize(buffer, bufferOffset=[0]) {
    //deserializes a message object of type Mode
    let len;
    let data = new Mode(null);
    // Deserialize message field [differential_wheel]
    data.differential_wheel = _deserializer.bool(buffer, bufferOffset);
    return data;
  }

  static getMessageSize(object) {
    return 1;
  }

  static datatype() {
    // Returns string type for a message object
    return 'ired_msgs/Mode';
  }

  static md5sum() {
    //Returns md5sum for a message object
    return 'e0f5377ca955b8c348e5de93be73c07e';
  }

  static messageDefinition() {
    // Returns full string definition for message
    return `
    bool differential_wheel
    
    `;
  }

  static Resolve(msg) {
    // deep-construct a valid message object instance of whatever was passed in
    if (typeof msg !== 'object' || msg === null) {
      msg = {};
    }
    const resolved = new Mode(null);
    if (msg.differential_wheel !== undefined) {
      resolved.differential_wheel = msg.differential_wheel;
    }
    else {
      resolved.differential_wheel = false
    }

    return resolved;
    }
};

module.exports = Mode;
