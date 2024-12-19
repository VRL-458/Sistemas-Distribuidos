// GENERATED CODE -- DO NOT EDIT!

'use strict';
var grpc = require('@grpc/grpc-js');
var master_pb = require('./master_pb.js');

function serialize_master_LogRequest(arg) {
  if (!(arg instanceof master_pb.LogRequest)) {
    throw new Error('Expected argument of type master.LogRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_master_LogRequest(buffer_arg) {
  return master_pb.LogRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_master_LogResponse(arg) {
  if (!(arg instanceof master_pb.LogResponse)) {
    throw new Error('Expected argument of type master.LogResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_master_LogResponse(buffer_arg) {
  return master_pb.LogResponse.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_master_RegisterWorkerRequest(arg) {
  if (!(arg instanceof master_pb.RegisterWorkerRequest)) {
    throw new Error('Expected argument of type master.RegisterWorkerRequest');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_master_RegisterWorkerRequest(buffer_arg) {
  return master_pb.RegisterWorkerRequest.deserializeBinary(new Uint8Array(buffer_arg));
}

function serialize_master_RegisterWorkerResponse(arg) {
  if (!(arg instanceof master_pb.RegisterWorkerResponse)) {
    throw new Error('Expected argument of type master.RegisterWorkerResponse');
  }
  return Buffer.from(arg.serializeBinary());
}

function deserialize_master_RegisterWorkerResponse(buffer_arg) {
  return master_pb.RegisterWorkerResponse.deserializeBinary(new Uint8Array(buffer_arg));
}


var MasterService = exports.MasterService = {
  registerWorker: {
    path: '/master.Master/RegisterWorker',
    requestStream: false,
    responseStream: false,
    requestType: master_pb.RegisterWorkerRequest,
    responseType: master_pb.RegisterWorkerResponse,
    requestSerialize: serialize_master_RegisterWorkerRequest,
    requestDeserialize: deserialize_master_RegisterWorkerRequest,
    responseSerialize: serialize_master_RegisterWorkerResponse,
    responseDeserialize: deserialize_master_RegisterWorkerResponse,
  },
  log: {
    path: '/master.Master/Log',
    requestStream: false,
    responseStream: false,
    requestType: master_pb.LogRequest,
    responseType: master_pb.LogResponse,
    requestSerialize: serialize_master_LogRequest,
    requestDeserialize: deserialize_master_LogRequest,
    responseSerialize: serialize_master_LogResponse,
    responseDeserialize: deserialize_master_LogResponse,
  },
};

exports.MasterClient = grpc.makeGenericClientConstructor(MasterService);
