import queue
import socket
import threading
import time
from datetime import date, datetime
from datetime import time as datetime_time
from datetime import timedelta
from logging import Logger, getLogger
from typing import Any, Dict, List, Optional, Tuple, Union, overload

from .ads_symbol import ADSSymbol
from .ams.ads_add_device_notification import ADSAddDeviceNotificationRequest, ADSAddDeviceNotificationResponse
from .ams.ads_delete_device_notification import ADSDeleteDeviceNotificationRequest, ADSDeleteDeviceNotificationResponse
from .ams.ads_device_notification import ADSDeviceNotificationResponse, AdsNotificationSample
from .ams.ads_read import ADSReadRequest, ADSReadResponse
from .ams.ads_read_device_info import ADSReadDeviceInfoResponse
from .ams.ads_read_state import ADSReadStateResponse
from .ams.ads_read_write import ADSReadWriteRequest, ADSReadWriteResponse
from .ams.ads_write import ADSWriteRequest, ADSWriteResponse
from .ams.ads_write_control import ADSWriteControlRequest, ADSWriteControlResponse
from .ams.ams_header import AMSHeader
from .constants.ads_state import ADSState
from .constants.command_id import ADSCommand
from .constants.index_group import IndexGroup
from .constants.return_code import ADSErrorCode
from .constants.state_flag import StateFlag
from .constants.transmission_mode import TransmissionMode
from .helpers.decode_ams_payload import decode_ams_payload
from .helpers.encode_ams_payload import encode_ams_payload
from .types import (
    ARRAY,
    STRING,
    STRUCT,
    WSTRING,
    PLCData,
    _PLCBoolType,
    _PLCDateAndTimeType,
    _PLCDateType,
    _PLCFloatType,
    _PLCIntType,
    _PLCTimeDeltaType,
    _PLCTimeOfDayType,
)

ADSResponse = Union[
    ADSReadResponse,
    ADSReadDeviceInfoResponse,
    ADSReadWriteResponse,
    ADSWriteResponse,
    ADSAddDeviceNotificationResponse,
    ADSDeleteDeviceNotificationResponse,
    ADSReadStateResponse,
    ADSWriteControlResponse,
]


class ADSClient:

    def __init__(
        self, local_ams_net_id: str, local_ams_port: int = 8000, timeout_s: float = 3, logger: Optional[Logger] = None
    ) -> None:
        self.__local_ams_net_id = local_ams_net_id
        self.__local_ams_port = local_ams_port
        if logger is None:
            logger = getLogger(name=self.__class__.__name__)

        self.__logger = logger
        self.__timeout = timeout_s
        self.__socket: Optional[socket.socket] = None

        self._current_invoke_id = 0
        self.__invoke_id_lock = threading.Lock()

        self._responses: Dict[int, Union[ADSErrorCode, ADSResponse]] = {}  # key is invoke_id
        self.__response_condition = threading.Condition()

        self.__variable_handles: Dict[str, int] = {}  # key is variable name, value is handle
        self.__variable_handles_lock = threading.Lock()

        self.device_notification_queue: queue.SimpleQueue[Tuple[ADSSymbol[PLCData], AdsNotificationSample, Any]] = (
            queue.SimpleQueue()
        )
        self.__device_notification_handles: Dict[int, ADSSymbol[PLCData]] = {}  # key is handle
        self.__device_notification_handles_lock = threading.Lock()

    def get_invoke_id(self) -> int:
        max_invoke_id = 0xFFFFFFFF
        with self.__invoke_id_lock:
            if self._current_invoke_id >= max_invoke_id:
                self._current_invoke_id = 0
            self._current_invoke_id += 1
            return self._current_invoke_id

    def close(self) -> None:
        with self.__device_notification_handles_lock:
            device_notification_handles = set(self.__device_notification_handles.keys())
        for handle in device_notification_handles:
            self.del_device_notification_by_handle(handle=handle)

        variable_handles = set(self.__variable_handles.values())
        for handle in variable_handles:
            self.release_handle(handle=handle)
        self.__variable_handles.clear()

        if self.__socket is not None:
            self.__socket.close()
            self.__socket = None

    def _read_socket_background(self, socket: socket.socket) -> None:
        buffer: bytes = b""
        while True:
            data = socket.recv(4096)
            # A returned empty bytes object indicates that the client has disconnected.
            if len(data) == 0:
                self.__logger.info("connection disconnected")
                break

            buffer += data
            while True:
                TCP_HEADER_LENGTH = 6
                if len(buffer) < TCP_HEADER_LENGTH:
                    break
                if buffer[:2] != b"\x00\x00":
                    self.__logger.warning(f"Received invalid TCP header: {buffer[:2].hex()}")
                length = int.from_bytes(buffer[2:TCP_HEADER_LENGTH], byteorder="little", signed=False)
                if len(buffer) < length + TCP_HEADER_LENGTH:
                    break
                packet = buffer[TCP_HEADER_LENGTH : length + TCP_HEADER_LENGTH]
                buffer = buffer[length + TCP_HEADER_LENGTH :]
                try:
                    self._handle_ams_raw_packet(packet=packet)
                except Exception as e:
                    self.__logger.error(f"Error while handling AMS packet: {e}")

    def _handle_ams_raw_packet(self, packet: bytes) -> None:
        AMS_HEADER_LENGTH = 32
        ams_header = packet[:AMS_HEADER_LENGTH]
        ads_body = packet[AMS_HEADER_LENGTH:]
        header_str = ams_header.hex(sep=" ")
        ads_body_str = ads_body.hex(sep=" ")
        self.__logger.info(f"Received AMS packet: {header_str}, {ads_body_str}")

        header = AMSHeader.from_bytes(ams_header)

        if header.error_code != ADSErrorCode.ERR_NOERROR:
            with self.__response_condition:
                self._responses[header.invoke_id] = header.error_code
                self.__response_condition.notify_all()
            return

        response: Optional[ADSResponse] = None

        if header.command_id == ADSCommand.ADSSRVID_READDEVICEINFO:
            response = ADSReadDeviceInfoResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_READ:
            response = ADSReadResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_WRITE:
            response = ADSWriteResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_READSTATE:
            response = ADSReadStateResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_WRITECTRL:
            response = ADSWriteControlResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_ADDDEVICENOTE:
            response = ADSAddDeviceNotificationResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_DELDEVICENOTE:
            response = ADSDeleteDeviceNotificationResponse.from_bytes(ads_body)
        elif header.command_id == ADSCommand.ADSSRVID_DEVICENOTE:
            notification_response = ADSDeviceNotificationResponse.from_bytes(ads_body)
            self._handle_device_notification(notification_response)
            return
        elif header.command_id == ADSCommand.ADSSRVID_READWRITE:
            response = ADSReadWriteResponse.from_bytes(ads_body)
        else:
            self.__logger.warning(f"Received unknown command_id: {header.command_id}, {packet.hex()}")

        if response:
            self.__logger.info(f"Received ADSResponse: {response}")
            with self.__response_condition:
                if response.result == ADSErrorCode.ERR_NOERROR:
                    self._responses[header.invoke_id] = response
                else:
                    self._responses[header.invoke_id] = response.result
                self.__response_condition.notify_all()

    def _handle_device_notification(self, notification_response: ADSDeviceNotificationResponse) -> None:
        for sample in notification_response.samples:
            handle = sample.handle
            with self.__device_notification_handles_lock:
                symbol = self.__device_notification_handles.get(handle, None)
            if symbol is None:
                self.__logger.warning(f"Received device notification for unknown handle: {handle}")
                continue
            decoded = decode_ams_payload(raw_data=sample.data, plc_t=symbol.plc_t)  # type: ignore
            self.device_notification_queue.put((symbol, sample, decoded))

    def open(self, target_ip: str, target_ams_net_id: str, target_ams_port: int = 851) -> None:
        """Open a connection to the target ADS device.

        Port 851: TC3 PLC runtime system 1
        https://infosys.beckhoff.com/content/1033/tc3_ads_intro/116159883.html
        """
        self.__target_ams_net_id = target_ams_net_id
        self.__target_ams_port = target_ams_port
        self.__socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

        ADS_TCP_PORT = 48898
        # https://infosys.beckhoff.com/content/1033/ipc_security_win7/11019143435.html
        try:
            self.__socket.connect((target_ip, ADS_TCP_PORT))
        except Exception:
            self.__logger.error(f"Could not connect to {target_ip}:{ADS_TCP_PORT}")
            return

        self.__read_socket_thread = threading.Thread(
            target=self._read_socket_background, kwargs={"socket": self.__socket}, daemon=True
        )
        self.__read_socket_thread.start()

    def read_device_info(self) -> ADSReadDeviceInfoResponse:
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_READDEVICEINFO, payload=b"")
        assert isinstance(response, ADSReadDeviceInfoResponse)
        return response

    def get_handle_by_name(self, name: str) -> int:
        # TODO: if get handle by name is called by multiple client, is the handle unique?
        request = ADSReadWriteRequest.get_handle_by_name(name=name)
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_READWRITE, payload=request_raw)
        assert isinstance(response, ADSReadWriteResponse)
        handle = int.from_bytes(bytes=response.data, byteorder="little", signed=False)
        return handle

    def release_handle(self, handle: int) -> None:
        request = ADSWriteRequest.release_handle(handle=handle)
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_WRITE, payload=request_raw)
        assert isinstance(response, ADSWriteResponse)

    def add_device_notification(self, symbol: ADSSymbol[PLCData], max_delay_ms: int = 0, cycle_time_ms: int = 0) -> int:
        with self.__variable_handles_lock:
            variable_handle = self.__variable_handles.get(symbol.name, None)

        if variable_handle is None:
            variable_handle = self.get_handle_by_name(name=symbol.name)
            with self.__variable_handles_lock:
                self.__variable_handles[symbol.name] = variable_handle

        request = ADSAddDeviceNotificationRequest(
            index_group=IndexGroup.SYMVAL_BYHANDLE,
            index_offset=variable_handle,
            length=symbol.plc_t.bytes_length,
            max_delay_ms=max_delay_ms,
            cycle_time_ms=cycle_time_ms,
            transmission_mode=TransmissionMode.ADSTRANS_SERVERONCHA,
        )
        request_raw = request.to_bytes()
        with self.__device_notification_handles_lock:
            response = self._send_ams_packet(command=ADSCommand.ADSSRVID_ADDDEVICENOTE, payload=request_raw)
            assert isinstance(response, ADSAddDeviceNotificationResponse)
            self.__device_notification_handles[response.handle] = symbol
        return response.handle

    def del_device_notification(self, symbol: ADSSymbol[PLCData]) -> None:
        with self.__device_notification_handles_lock:
            handles = [handle for handle, s in self.__device_notification_handles.items() if s == symbol]
        for handle in handles:
            self.del_device_notification_by_handle(handle=handle)
            with self.__device_notification_handles_lock:
                self.__device_notification_handles.pop(handle, None)

    def del_device_notification_by_handle(self, handle: int) -> None:
        request = ADSDeleteDeviceNotificationRequest(handle=handle)
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_DELDEVICENOTE, payload=request_raw)
        assert isinstance(response, ADSDeleteDeviceNotificationResponse)

    def read_value_by_handle(self, handle: int, data_length: int) -> bytes:
        request = ADSReadRequest(index_group=IndexGroup.SYMVAL_BYHANDLE, index_offset=handle, length=data_length)
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=request_raw)
        assert isinstance(response, ADSReadResponse)
        return response.data

    def write_value_by_handle(self, handle: int, data: bytes) -> ADSWriteResponse:
        request = ADSWriteRequest(index_group=IndexGroup.SYMVAL_BYHANDLE, index_offset=handle, data=data)
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_WRITE, payload=request_raw)
        assert isinstance(response, ADSWriteResponse)
        return response

    def read_state(self) -> ADSReadStateResponse:
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_READSTATE, payload=b"")
        assert isinstance(response, ADSReadStateResponse)
        return response

    def write_control(self, ads_state: ADSState, device_state: int) -> None:
        request = ADSWriteControlRequest(ads_state=ads_state, device_state=device_state, data=b"")
        request_raw = request.to_bytes()
        response = self._send_ams_packet(command=ADSCommand.ADSSRVID_WRITECTRL, payload=request_raw)
        assert isinstance(response, ADSWriteControlResponse)

    def _send_ams_packet(self, *, command: ADSCommand, payload: bytes) -> ADSResponse:
        assert self.__socket is not None, "Socket is not open"

        invoke_id = self.get_invoke_id()
        ams_header = AMSHeader(
            target_net_id=self.__target_ams_net_id,
            target_port=self.__target_ams_port,
            source_net_id=self.__local_ams_net_id,
            source_port=self.__local_ams_port,
            command_id=command,
            state_flags=StateFlag.AMSCMDSF_ADSCMD,
            length=len(payload),
            error_code=ADSErrorCode.ERR_NOERROR,
            invoke_id=invoke_id,
        )

        header_raw = ams_header.to_bytes()
        total_length = len(header_raw) + len(payload)
        length_bytes = total_length.to_bytes(4, byteorder="little", signed=False)

        with self.__response_condition:
            self._responses.pop(invoke_id, None)

        self.__logger.info(f"Sending AMS packet: {header_raw.hex(' ')}, {payload.hex(' ')}")
        self.__socket.sendall(b"\x00\x00" + length_bytes + header_raw + payload)

        start_time = time.perf_counter()
        timeout = self.__timeout
        with self.__response_condition:
            while invoke_id not in self._responses:
                timeout -= time.perf_counter() - start_time
                if timeout <= 0:
                    break
                self.__response_condition.wait(timeout=timeout)

            response = self._responses.pop(invoke_id, None)
            if response is None:
                raise TimeoutError(f"Timeout while waiting for response to invoke_id: {ams_header.invoke_id}")
            if isinstance(response, ADSErrorCode):
                raise RuntimeError(f"Received error code: {response}")
            return response

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCBoolType]) -> bool: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCIntType]) -> int: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCFloatType]) -> float: ...

    @overload
    def read_symbol(self, symbol: Union[ADSSymbol[STRING], ADSSymbol[WSTRING]]) -> str: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCTimeDeltaType]) -> timedelta: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCDateType]) -> date: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCDateAndTimeType]) -> datetime: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[_PLCTimeOfDayType]) -> datetime_time: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[STRUCT]) -> Dict[str, Any]: ...

    @overload
    def read_symbol(self, symbol: ADSSymbol[ARRAY]) -> List[Any]: ...

    def read_symbol(self, symbol: Any) -> Any:
        assert isinstance(symbol, ADSSymbol)
        assert isinstance(symbol.plc_t, PLCData)

        with self.__variable_handles_lock:
            handle = self.__variable_handles.get(symbol.name, None)

        if handle is None:
            handle = self.get_handle_by_name(name=symbol.name)
            with self.__variable_handles_lock:
                self.__variable_handles[symbol.name] = handle

        raw_data = self.read_value_by_handle(handle=handle, data_length=symbol.plc_t.bytes_length)
        decode_value = decode_ams_payload(raw_data=raw_data, plc_t=symbol.plc_t)  # type: ignore
        return decode_value

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCBoolType], value: bool) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCIntType], value: int) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCFloatType], value: float) -> None: ...

    @overload
    def write_symbol(self, symbol: Union[ADSSymbol[STRING], ADSSymbol[WSTRING]], value: str) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCTimeDeltaType], value: timedelta) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCDateType], value: date) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCDateAndTimeType], value: datetime) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[_PLCTimeOfDayType], value: datetime_time) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[STRUCT], value: Dict[str, Any]) -> None: ...

    @overload
    def write_symbol(self, symbol: ADSSymbol[ARRAY], value: List[Any]) -> None: ...

    def write_symbol(self, symbol: Any, value: Any) -> None:
        assert isinstance(symbol, ADSSymbol)
        assert isinstance(symbol.plc_t, PLCData)

        if isinstance(symbol.plc_t, _PLCBoolType):
            assert isinstance(value, bool)
        elif isinstance(symbol.plc_t, _PLCIntType):
            assert isinstance(value, int)
        elif isinstance(symbol.plc_t, _PLCFloatType):
            assert isinstance(value, float)
        elif isinstance(symbol.plc_t, (STRING, WSTRING)):
            assert isinstance(value, str)
        elif isinstance(symbol.plc_t, _PLCTimeDeltaType):
            assert isinstance(value, timedelta)
        elif isinstance(symbol.plc_t, _PLCDateType):
            assert isinstance(value, date)
        elif isinstance(symbol.plc_t, _PLCDateAndTimeType):
            assert isinstance(value, datetime)
        elif isinstance(symbol.plc_t, _PLCTimeOfDayType):
            assert isinstance(value, datetime_time)
        elif isinstance(symbol.plc_t, STRUCT):
            assert isinstance(value, dict)
        elif isinstance(symbol.plc_t, ARRAY):
            assert isinstance(value, list)
        else:
            raise ValueError(f"Unsupported PLC data type: {symbol.plc_t}")

        with self.__variable_handles_lock:
            handle = self.__variable_handles.get(symbol.name, None)

        if handle is None:
            handle = self.get_handle_by_name(name=symbol.name)
            with self.__variable_handles_lock:
                self.__variable_handles[symbol.name] = handle

        raw_data = encode_ams_payload(data=value, plc_t=symbol.plc_t)  # type: ignore
        self.write_value_by_handle(handle=handle, data=raw_data)
