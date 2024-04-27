from unittest import mock

import pytest

from ..ads_client import ADSClient
from ..ams.ads_read import ADSReadResponse
from ..ams.ads_read_device_info import ADSReadDeviceInfoResponse
from ..ams.ams_header import AMSHeader
from ..constants.command_id import ADSCommand
from ..constants.return_code import ADSErrorCode
from ..constants.state_flag import StateFlag


def test_current_invoke_id() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1")
    invoke_id_1 = client.get_invoke_id()
    invoke_id_2 = client.get_invoke_id()
    assert invoke_id_1 != invoke_id_2
    assert invoke_id_1 + 1 == invoke_id_2

    client._current_invoke_id = 0xFFFFFFFF - 1
    invoke_id_3 = client.get_invoke_id()
    assert invoke_id_3 == 0xFFFFFFFF
    invoke_id_4 = client.get_invoke_id()
    assert invoke_id_4 == 1


def test_send_ams_packet_timeout() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    with pytest.raises(AssertionError, match="Socket is not open"):
        client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")

    target_ip = "192.168.88.20"

    with mock.patch("socket.socket") as mock_socket_class:
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b""

        mock_socket_class.side_effect = [mock_socket]

        client.open(target_ip=target_ip, target_ams_net_id="192.168.88.20.1.1")
        mock_socket.connect.assert_called_once_with((target_ip, 48898))

        assert len(client._responses) == 0

        with pytest.raises(TimeoutError):
            client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")

        mock_socket.sendall.assert_called_once_with(
            bytes.fromhex(
                "00 00"
                + "24 00 00 00"
                + "c0 a8 58 14 01 01 53 03 c0 a8 58 64 01 01 40 1f"
                + "02 00 04 00 04 00 00 00 00 00 00 00 01 00 00 00"
                + "01 02 03 04"
            )
        )

        assert len(client._responses) == 0

        def mock_sendall(data: bytes) -> None:
            client._responses[2] = ADSErrorCode.ADSERR_DEVICE_ERROR

        mock_socket.sendall.side_effect = mock_sendall

        with pytest.raises(RuntimeError):
            client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")


def test_send_ams_packet_error() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    with pytest.raises(AssertionError, match="Socket is not open"):
        client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")

    target_ip = "192.168.88.20"

    with mock.patch("socket.socket") as mock_socket_class:
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b""

        mock_socket_class.side_effect = [mock_socket]

        client.open(target_ip=target_ip, target_ams_net_id="192.168.88.20.1.1")
        mock_socket.connect.assert_called_once_with((target_ip, 48898))

        def mock_sendall(data: bytes) -> None:
            client._responses[1] = ADSErrorCode.ADSERR_DEVICE_ERROR

        mock_socket.sendall.side_effect = mock_sendall

        with pytest.raises(RuntimeError):
            client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")


def test_send_ams_packet_normal() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    with pytest.raises(AssertionError, match="Socket is not open"):
        client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")

    target_ip = "192.168.88.20"

    with mock.patch("socket.socket") as mock_socket_class:
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b""

        mock_socket_class.side_effect = [mock_socket]

        client.open(target_ip=target_ip, target_ams_net_id="192.168.88.20.1.1")
        mock_socket.connect.assert_called_once_with((target_ip, 48898))

        response = ADSReadResponse(result=ADSErrorCode.ERR_NOERROR, data=b"\x01\x02\x03\x04")

        def mock_sendall(data: bytes) -> None:
            client._responses[1] = response

        mock_socket.sendall.side_effect = mock_sendall

        r = client._send_ams_packet(command=ADSCommand.ADSSRVID_READ, payload=b"\x01\x02\x03\x04")

        assert r is response


def test_client_close() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    target_ip = "192.168.88.20"

    with mock.patch("socket.socket") as mock_socket_class:
        mock_socket = mock.Mock()
        mock_socket.recv.return_value = b""

        mock_socket_class.side_effect = [mock_socket]

        client.open(target_ip=target_ip, target_ams_net_id="192.168.88.20.1.1")
        mock_socket.connect.assert_called_once_with((target_ip, 48898))

        client.close()
        mock_socket.close.assert_called_once()


def test_read_socket_background() -> None:
    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    tcp_header = bytes.fromhex("00 00 24 00 00 00")
    ams_header = bytes.fromhex(
        "c0 a8 58 14 01 01 53 03 c0 a8 58 64 01 01 40 1f 02 00 04 00 04 00 00 00 00 00 00 00 01 00 00 00"
    )
    ams_body = bytes.fromhex("01 02 03 04")
    tcp_header_2 = bytes.fromhex("00 00 24 00 00 00")

    mock_socket = mock.Mock()
    mock_socket.recv.side_effect = [tcp_header, ams_header, ams_body, tcp_header_2, b""]

    with mock.patch.object(client, "_handle_ams_raw_packet") as mock_handle_ams_raw_packet:
        client._read_socket_background(socket=mock_socket)
        mock_handle_ams_raw_packet.assert_called_once_with(packet=ams_header + ams_body)


def test_handle_ams_raw_packet() -> None:

    client = ADSClient(local_ams_net_id="192.168.88.100.1.1", timeout_s=0.1)

    payload = ADSReadDeviceInfoResponse(
        result=ADSErrorCode.ADSERR_DEVICE_ERROR,
        major_version=1,
        minor_version=2,
        build_version=3,
        device_name="DeviceName",
    )

    payload_bytes = payload.to_bytes()

    header = AMSHeader(
        target_net_id="192.168.88.20.1.1",
        target_port=8000,
        source_net_id="192.168.88.100.1.1",
        source_port=851,
        command_id=ADSCommand.ADSSRVID_READDEVICEINFO,
        state_flags=StateFlag.AMSCMDSF_ADSCMD,
        length=len(payload_bytes),
        error_code=ADSErrorCode.ERR_INTERNAL,
        invoke_id=1,
    )

    client._handle_ams_raw_packet(packet=header.to_bytes() + payload_bytes)
    assert client._responses[1] == header.error_code

    client._responses.pop(1)
    header.error_code = ADSErrorCode.ERR_NOERROR
    client._handle_ams_raw_packet(packet=header.to_bytes() + payload_bytes)
    assert client._responses[1] == payload.result

    client._responses.pop(1)
    payload.result = ADSErrorCode.ERR_NOERROR
    client._handle_ams_raw_packet(packet=header.to_bytes() + payload.to_bytes())
    assert client._responses[1] == payload
