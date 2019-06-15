# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: messages.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='messages.proto',
  package='messages',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x0emessages.proto\x12\x08messages\"\xc5\x01\n\rCommonMessage\x12+\n\x0cmessage_type\x18\x01 \x02(\x0e\x32\x15.messages.MessageType\x12\x1e\n\x04join\x18\x02 \x01(\x0b\x32\x0e.messages.JoinH\x00\x12,\n\x0btransaction\x18\x03 \x01(\x0b\x32\x15.messages.TransactionH\x00\x12)\n\nnode_query\x18\x04 \x01(\x0b\x32\x13.messages.NodeQueryH\x00\x42\x0e\n\x0cmessage_body\"<\n\tNodeQuery\x12\x10\n\x08txn_hash\x18\x01 \x02(\t\x12\x1d\n\x15is_strongly_preferred\x18\x02 \x02(\x08\"\xe9\x01\n\x0bTransaction\x12\x0e\n\x06sender\x18\x01 \x02(\t\x12\x11\n\trecipient\x18\x02 \x02(\t\x12\r\n\x05nonce\x18\x03 \x02(\x04\x12\x0e\n\x06\x61mount\x18\x04 \x02(\x04\x12\x0c\n\x04\x64\x61ta\x18\x05 \x02(\t\x12\x0c\n\x04hash\x18\x06 \x02(\t\x12\x0f\n\x07parents\x18\x07 \x03(\t\x12\x10\n\x08\x63hildren\x18\x08 \x03(\t\x12\x11\n\tsignature\x18\t \x01(\t\x12\x15\n\rsender_pubkey\x18\n \x02(\t\x12\x0c\n\x04\x63hit\x18\x0b \x01(\x08\x12\x0f\n\x07queried\x18\x0c \x01(\x08\x12\x10\n\x08\x61\x63\x63\x65pted\x18\r \x01(\x08\"\x94\x01\n\x04Join\x12\x0f\n\x07\x61\x64\x64ress\x18\x01 \x02(\t\x12\x0c\n\x04port\x18\x02 \x02(\x05\x12\x0e\n\x06pubkey\x18\x03 \x02(\t\x12\x10\n\x08nickname\x18\x04 \x01(\t\x12&\n\tjoin_type\x18\x05 \x02(\x0e\x32\x13.messages.Join.Type\"#\n\x04Type\x12\r\n\tINIT_JOIN\x10\x00\x12\x0c\n\x08\x41\x43K_JOIN\x10\x01*P\n\x0bMessageType\x12\x10\n\x0cJOIN_MESSAGE\x10\x00\x12\x17\n\x13TRANSACTION_MESSAGE\x10\x01\x12\x16\n\x12NODE_QUERY_MESSAGE\x10\x02')
)

_MESSAGETYPE = _descriptor.EnumDescriptor(
  name='MessageType',
  full_name='messages.MessageType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='JOIN_MESSAGE', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TRANSACTION_MESSAGE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NODE_QUERY_MESSAGE', index=2, number=2,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=677,
  serialized_end=757,
)
_sym_db.RegisterEnumDescriptor(_MESSAGETYPE)

MessageType = enum_type_wrapper.EnumTypeWrapper(_MESSAGETYPE)
JOIN_MESSAGE = 0
TRANSACTION_MESSAGE = 1
NODE_QUERY_MESSAGE = 2


_JOIN_TYPE = _descriptor.EnumDescriptor(
  name='Type',
  full_name='messages.Join.Type',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='INIT_JOIN', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ACK_JOIN', index=1, number=1,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=640,
  serialized_end=675,
)
_sym_db.RegisterEnumDescriptor(_JOIN_TYPE)


_COMMONMESSAGE = _descriptor.Descriptor(
  name='CommonMessage',
  full_name='messages.CommonMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='message_type', full_name='messages.CommonMessage.message_type', index=0,
      number=1, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='join', full_name='messages.CommonMessage.join', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='transaction', full_name='messages.CommonMessage.transaction', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='node_query', full_name='messages.CommonMessage.node_query', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='message_body', full_name='messages.CommonMessage.message_body',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=29,
  serialized_end=226,
)


_NODEQUERY = _descriptor.Descriptor(
  name='NodeQuery',
  full_name='messages.NodeQuery',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='txn_hash', full_name='messages.NodeQuery.txn_hash', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_strongly_preferred', full_name='messages.NodeQuery.is_strongly_preferred', index=1,
      number=2, type=8, cpp_type=7, label=2,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=228,
  serialized_end=288,
)


_TRANSACTION = _descriptor.Descriptor(
  name='Transaction',
  full_name='messages.Transaction',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='messages.Transaction.sender', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='recipient', full_name='messages.Transaction.recipient', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nonce', full_name='messages.Transaction.nonce', index=2,
      number=3, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='amount', full_name='messages.Transaction.amount', index=3,
      number=4, type=4, cpp_type=4, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data', full_name='messages.Transaction.data', index=4,
      number=5, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='hash', full_name='messages.Transaction.hash', index=5,
      number=6, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='parents', full_name='messages.Transaction.parents', index=6,
      number=7, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='children', full_name='messages.Transaction.children', index=7,
      number=8, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='signature', full_name='messages.Transaction.signature', index=8,
      number=9, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='sender_pubkey', full_name='messages.Transaction.sender_pubkey', index=9,
      number=10, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='chit', full_name='messages.Transaction.chit', index=10,
      number=11, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='queried', full_name='messages.Transaction.queried', index=11,
      number=12, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='accepted', full_name='messages.Transaction.accepted', index=12,
      number=13, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=291,
  serialized_end=524,
)


_JOIN = _descriptor.Descriptor(
  name='Join',
  full_name='messages.Join',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='address', full_name='messages.Join.address', index=0,
      number=1, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='port', full_name='messages.Join.port', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pubkey', full_name='messages.Join.pubkey', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='nickname', full_name='messages.Join.nickname', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='join_type', full_name='messages.Join.join_type', index=4,
      number=5, type=14, cpp_type=8, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _JOIN_TYPE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=527,
  serialized_end=675,
)

_COMMONMESSAGE.fields_by_name['message_type'].enum_type = _MESSAGETYPE
_COMMONMESSAGE.fields_by_name['join'].message_type = _JOIN
_COMMONMESSAGE.fields_by_name['transaction'].message_type = _TRANSACTION
_COMMONMESSAGE.fields_by_name['node_query'].message_type = _NODEQUERY
_COMMONMESSAGE.oneofs_by_name['message_body'].fields.append(
  _COMMONMESSAGE.fields_by_name['join'])
_COMMONMESSAGE.fields_by_name['join'].containing_oneof = _COMMONMESSAGE.oneofs_by_name['message_body']
_COMMONMESSAGE.oneofs_by_name['message_body'].fields.append(
  _COMMONMESSAGE.fields_by_name['transaction'])
_COMMONMESSAGE.fields_by_name['transaction'].containing_oneof = _COMMONMESSAGE.oneofs_by_name['message_body']
_COMMONMESSAGE.oneofs_by_name['message_body'].fields.append(
  _COMMONMESSAGE.fields_by_name['node_query'])
_COMMONMESSAGE.fields_by_name['node_query'].containing_oneof = _COMMONMESSAGE.oneofs_by_name['message_body']
_JOIN.fields_by_name['join_type'].enum_type = _JOIN_TYPE
_JOIN_TYPE.containing_type = _JOIN
DESCRIPTOR.message_types_by_name['CommonMessage'] = _COMMONMESSAGE
DESCRIPTOR.message_types_by_name['NodeQuery'] = _NODEQUERY
DESCRIPTOR.message_types_by_name['Transaction'] = _TRANSACTION
DESCRIPTOR.message_types_by_name['Join'] = _JOIN
DESCRIPTOR.enum_types_by_name['MessageType'] = _MESSAGETYPE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

CommonMessage = _reflection.GeneratedProtocolMessageType('CommonMessage', (_message.Message,), dict(
  DESCRIPTOR = _COMMONMESSAGE,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:messages.CommonMessage)
  ))
_sym_db.RegisterMessage(CommonMessage)

NodeQuery = _reflection.GeneratedProtocolMessageType('NodeQuery', (_message.Message,), dict(
  DESCRIPTOR = _NODEQUERY,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:messages.NodeQuery)
  ))
_sym_db.RegisterMessage(NodeQuery)

Transaction = _reflection.GeneratedProtocolMessageType('Transaction', (_message.Message,), dict(
  DESCRIPTOR = _TRANSACTION,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:messages.Transaction)
  ))
_sym_db.RegisterMessage(Transaction)

Join = _reflection.GeneratedProtocolMessageType('Join', (_message.Message,), dict(
  DESCRIPTOR = _JOIN,
  __module__ = 'messages_pb2'
  # @@protoc_insertion_point(class_scope:messages.Join)
  ))
_sym_db.RegisterMessage(Join)


# @@protoc_insertion_point(module_scope)
