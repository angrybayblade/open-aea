# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: oef_search.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x10oef_search.proto\x12\x1d\x61\x65\x61.fetchai.oef_search.v1_0_0"\x89\r\n\x10OefSearchMessage\x12[\n\toef_error\x18\x05 \x01(\x0b\x32\x46.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Oef_Error_PerformativeH\x00\x12i\n\x10register_service\x18\x06 \x01(\x0b\x32M.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Register_Service_PerformativeH\x00\x12\x63\n\rsearch_result\x18\x07 \x01(\x0b\x32J.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Search_Result_PerformativeH\x00\x12g\n\x0fsearch_services\x18\x08 \x01(\x0b\x32L.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Search_Services_PerformativeH\x00\x12W\n\x07success\x18\t \x01(\x0b\x32\x44.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Success_PerformativeH\x00\x12m\n\x12unregister_service\x18\n \x01(\x0b\x32O.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Unregister_Service_PerformativeH\x00\x1a!\n\nAgentsInfo\x12\x13\n\x0b\x61gents_info\x18\x01 \x01(\x0c\x1a(\n\x0b\x44\x65scription\x12\x19\n\x11\x64\x65scription_bytes\x18\x01 \x01(\x0c\x1a\xdb\x01\n\x11OefErrorOperation\x12\x61\n\toef_error\x18\x01 \x01(\x0e\x32N.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.OefErrorOperation.OefErrorEnum"c\n\x0cOefErrorEnum\x12\x14\n\x10REGISTER_SERVICE\x10\x00\x12\x16\n\x12UNREGISTER_SERVICE\x10\x01\x12\x13\n\x0fSEARCH_SERVICES\x10\x02\x12\x10\n\x0cSEND_MESSAGE\x10\x03\x1a\x1c\n\x05Query\x12\x13\n\x0bquery_bytes\x18\x01 \x01(\x0c\x1ay\n\x1dRegister_Service_Performative\x12X\n\x13service_description\x18\x01 \x01(\x0b\x32;.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Description\x1a{\n\x1fUnregister_Service_Performative\x12X\n\x13service_description\x18\x01 \x01(\x0b\x32;.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Description\x1a\x64\n\x1cSearch_Services_Performative\x12\x44\n\x05query\x18\x01 \x01(\x0b\x32\x35.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Query\x1a}\n\x1aSearch_Result_Performative\x12\x0e\n\x06\x61gents\x18\x01 \x03(\t\x12O\n\x0b\x61gents_info\x18\x02 \x01(\x0b\x32:.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.AgentsInfo\x1ag\n\x14Success_Performative\x12O\n\x0b\x61gents_info\x18\x01 \x01(\x0b\x32:.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.AgentsInfo\x1ax\n\x16Oef_Error_Performative\x12^\n\x13oef_error_operation\x18\x01 \x01(\x0b\x32\x41.aea.fetchai.oef_search.v1_0_0.OefSearchMessage.OefErrorOperationB\x0e\n\x0cperformativeb\x06proto3'
)


_OEFSEARCHMESSAGE = DESCRIPTOR.message_types_by_name["OefSearchMessage"]
_OEFSEARCHMESSAGE_AGENTSINFO = _OEFSEARCHMESSAGE.nested_types_by_name["AgentsInfo"]
_OEFSEARCHMESSAGE_DESCRIPTION = _OEFSEARCHMESSAGE.nested_types_by_name["Description"]
_OEFSEARCHMESSAGE_OEFERROROPERATION = _OEFSEARCHMESSAGE.nested_types_by_name[
    "OefErrorOperation"
]
_OEFSEARCHMESSAGE_QUERY = _OEFSEARCHMESSAGE.nested_types_by_name["Query"]
_OEFSEARCHMESSAGE_REGISTER_SERVICE_PERFORMATIVE = (
    _OEFSEARCHMESSAGE.nested_types_by_name["Register_Service_Performative"]
)
_OEFSEARCHMESSAGE_UNREGISTER_SERVICE_PERFORMATIVE = (
    _OEFSEARCHMESSAGE.nested_types_by_name["Unregister_Service_Performative"]
)
_OEFSEARCHMESSAGE_SEARCH_SERVICES_PERFORMATIVE = _OEFSEARCHMESSAGE.nested_types_by_name[
    "Search_Services_Performative"
]
_OEFSEARCHMESSAGE_SEARCH_RESULT_PERFORMATIVE = _OEFSEARCHMESSAGE.nested_types_by_name[
    "Search_Result_Performative"
]
_OEFSEARCHMESSAGE_SUCCESS_PERFORMATIVE = _OEFSEARCHMESSAGE.nested_types_by_name[
    "Success_Performative"
]
_OEFSEARCHMESSAGE_OEF_ERROR_PERFORMATIVE = _OEFSEARCHMESSAGE.nested_types_by_name[
    "Oef_Error_Performative"
]
_OEFSEARCHMESSAGE_OEFERROROPERATION_OEFERRORENUM = (
    _OEFSEARCHMESSAGE_OEFERROROPERATION.enum_types_by_name["OefErrorEnum"]
)
OefSearchMessage = _reflection.GeneratedProtocolMessageType(
    "OefSearchMessage",
    (_message.Message,),
    {
        "AgentsInfo": _reflection.GeneratedProtocolMessageType(
            "AgentsInfo",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_AGENTSINFO,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.AgentsInfo)
            },
        ),
        "Description": _reflection.GeneratedProtocolMessageType(
            "Description",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_DESCRIPTION,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Description)
            },
        ),
        "OefErrorOperation": _reflection.GeneratedProtocolMessageType(
            "OefErrorOperation",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_OEFERROROPERATION,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.OefErrorOperation)
            },
        ),
        "Query": _reflection.GeneratedProtocolMessageType(
            "Query",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_QUERY,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Query)
            },
        ),
        "Register_Service_Performative": _reflection.GeneratedProtocolMessageType(
            "Register_Service_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_REGISTER_SERVICE_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Register_Service_Performative)
            },
        ),
        "Unregister_Service_Performative": _reflection.GeneratedProtocolMessageType(
            "Unregister_Service_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_UNREGISTER_SERVICE_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Unregister_Service_Performative)
            },
        ),
        "Search_Services_Performative": _reflection.GeneratedProtocolMessageType(
            "Search_Services_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_SEARCH_SERVICES_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Search_Services_Performative)
            },
        ),
        "Search_Result_Performative": _reflection.GeneratedProtocolMessageType(
            "Search_Result_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_SEARCH_RESULT_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Search_Result_Performative)
            },
        ),
        "Success_Performative": _reflection.GeneratedProtocolMessageType(
            "Success_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_SUCCESS_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Success_Performative)
            },
        ),
        "Oef_Error_Performative": _reflection.GeneratedProtocolMessageType(
            "Oef_Error_Performative",
            (_message.Message,),
            {
                "DESCRIPTOR": _OEFSEARCHMESSAGE_OEF_ERROR_PERFORMATIVE,
                "__module__": "oef_search_pb2"
                # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage.Oef_Error_Performative)
            },
        ),
        "DESCRIPTOR": _OEFSEARCHMESSAGE,
        "__module__": "oef_search_pb2"
        # @@protoc_insertion_point(class_scope:aea.fetchai.oef_search.v1_0_0.OefSearchMessage)
    },
)
_sym_db.RegisterMessage(OefSearchMessage)
_sym_db.RegisterMessage(OefSearchMessage.AgentsInfo)
_sym_db.RegisterMessage(OefSearchMessage.Description)
_sym_db.RegisterMessage(OefSearchMessage.OefErrorOperation)
_sym_db.RegisterMessage(OefSearchMessage.Query)
_sym_db.RegisterMessage(OefSearchMessage.Register_Service_Performative)
_sym_db.RegisterMessage(OefSearchMessage.Unregister_Service_Performative)
_sym_db.RegisterMessage(OefSearchMessage.Search_Services_Performative)
_sym_db.RegisterMessage(OefSearchMessage.Search_Result_Performative)
_sym_db.RegisterMessage(OefSearchMessage.Success_Performative)
_sym_db.RegisterMessage(OefSearchMessage.Oef_Error_Performative)

if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _OEFSEARCHMESSAGE._serialized_start = 52
    _OEFSEARCHMESSAGE._serialized_end = 1725
    _OEFSEARCHMESSAGE_AGENTSINFO._serialized_start = 678
    _OEFSEARCHMESSAGE_AGENTSINFO._serialized_end = 711
    _OEFSEARCHMESSAGE_DESCRIPTION._serialized_start = 713
    _OEFSEARCHMESSAGE_DESCRIPTION._serialized_end = 753
    _OEFSEARCHMESSAGE_OEFERROROPERATION._serialized_start = 756
    _OEFSEARCHMESSAGE_OEFERROROPERATION._serialized_end = 975
    _OEFSEARCHMESSAGE_OEFERROROPERATION_OEFERRORENUM._serialized_start = 876
    _OEFSEARCHMESSAGE_OEFERROROPERATION_OEFERRORENUM._serialized_end = 975
    _OEFSEARCHMESSAGE_QUERY._serialized_start = 977
    _OEFSEARCHMESSAGE_QUERY._serialized_end = 1005
    _OEFSEARCHMESSAGE_REGISTER_SERVICE_PERFORMATIVE._serialized_start = 1007
    _OEFSEARCHMESSAGE_REGISTER_SERVICE_PERFORMATIVE._serialized_end = 1128
    _OEFSEARCHMESSAGE_UNREGISTER_SERVICE_PERFORMATIVE._serialized_start = 1130
    _OEFSEARCHMESSAGE_UNREGISTER_SERVICE_PERFORMATIVE._serialized_end = 1253
    _OEFSEARCHMESSAGE_SEARCH_SERVICES_PERFORMATIVE._serialized_start = 1255
    _OEFSEARCHMESSAGE_SEARCH_SERVICES_PERFORMATIVE._serialized_end = 1355
    _OEFSEARCHMESSAGE_SEARCH_RESULT_PERFORMATIVE._serialized_start = 1357
    _OEFSEARCHMESSAGE_SEARCH_RESULT_PERFORMATIVE._serialized_end = 1482
    _OEFSEARCHMESSAGE_SUCCESS_PERFORMATIVE._serialized_start = 1484
    _OEFSEARCHMESSAGE_SUCCESS_PERFORMATIVE._serialized_end = 1587
    _OEFSEARCHMESSAGE_OEF_ERROR_PERFORMATIVE._serialized_start = 1589
    _OEFSEARCHMESSAGE_OEF_ERROR_PERFORMATIVE._serialized_end = 1709
# @@protoc_insertion_point(module_scope)
