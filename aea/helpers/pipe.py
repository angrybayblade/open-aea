#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2018-2019 Fetch.AI Limited
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""Portable pipe implementation for Linux, MacOS, and Windows."""

import asyncio
import errno
import logging
import os
import socket
import struct
import tempfile
from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from shutil import rmtree
from typing import IO, Optional

_default_logger = logging.getLogger(__name__)

PIPE_CONN_TIMEOUT = 10.0
PIPE_CONN_ATTEMPTS = 10

TCP_SOCKET_PIPE_CLIENT_CONN_ATTEMPTS = 5
TCP_SOCKET_PIPE_CLIENT_CONN_TIMEOUT = 0.1


class IPCChannelClient(ABC):
    """
    Multi-platform interprocess communication channel for the client side
    """

    @abstractmethod
    async def connect(self, timeout=PIPE_CONN_TIMEOUT) -> bool:
        """
        Connect to communication channel

        :param timeout: timeout for other end to connect
        """

    @abstractmethod
    async def write(self, data: bytes) -> None:
        """
        Write `data` bytes to the other end of the channel
        Will first write the size than the actual data

        :param data: bytes to write
        """

    @abstractmethod
    async def read(self) -> Optional[bytes]:
        """
        Read bytes from the other end of the channel
        Will first read the size than the actual data

        :return: read bytes
        """

    @abstractmethod
    async def close(self) -> None:
        """
        Close the communication channel
        """


class IPCChannel(IPCChannelClient):
    """
    Multi-platform interprocess communication channel
    """

    @property
    @abstractmethod
    def in_path(self) -> str:
        """
        Rendezvous point for incoming communication
        """

    @property
    @abstractmethod
    def out_path(self) -> str:
        """
        Rendezvous point for outgoing communication
        """


class PosixNamedPipeProtocol:
    """
    Posix named pipes async wrapper communication protocol
    """

    def __init__(
        self,
        in_path: str,
        out_path: str,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """
        Initialize a new posix named pipe

        :param in_path: rendezvous point for incoming data
        :param out_path: rendezvous point for outgoing daa
        """

        self.logger = logger
        self._loop = loop
        self._in_path = in_path
        self._out_path = out_path
        self._in = -1
        self._out = -1

        self._stream_reader = None  # type: Optional[asyncio.StreamReader]
        self._log_file_desc = None  # type: Optional[IO[str]]
        self._reader_protocol = None  # type: Optional[asyncio.StreamReaderProtocol]
        self._fileobj = None  # type: Optional[IO[str]]
        #self._out_fo = None

        self._connection_attempts = PIPE_CONN_ATTEMPTS
        self._connection_timeout = PIPE_CONN_TIMEOUT

    async def connect(self, timeout: float = PIPE_CONN_TIMEOUT) -> bool:
        """
        Connect to the other end of the pipe

        :param timeout: timeout before failing
        :return: connection success
        """

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        self._connection_timeout = timeout / PIPE_CONN_ATTEMPTS if timeout > 0 else 0
        if self._connection_attempts <= 1:  # pragma: no cover
            return False
        self._connection_attempts -= 1

        self.logger.debug(
            "Attempt opening pipes {}, {}...".format(self._in_path, self._out_path)
        )

        self._in = os.open(self._in_path, os.O_RDONLY | os.O_NONBLOCK | os.O_SYNC)

        try:
            self._out = os.open(self._out_path, os.O_WRONLY | os.O_NONBLOCK)
        except OSError as e:
            if e.errno == errno.ENXIO:
                self.logger.debug("Sleeping for {}...".format(self._connection_timeout))
                await asyncio.sleep(self._connection_timeout)
                return await self.connect(timeout)
            else:
                raise e  # pragma: no cover

        # setup reader
        assert (
            self._in != -1 and self._out != -1 and self._loop is not None
        ), "Incomplete initialization."
        self._stream_reader = asyncio.StreamReader(loop=self._loop)
        self._reader_protocol = asyncio.StreamReaderProtocol(
            self._stream_reader, loop=self._loop
        )
        self._fileobj = os.fdopen(self._in, "r")
        await self._loop.connect_read_pipe(
            lambda: self.__reader_protocol, self._fileobj
        )
        #self._out_fo = os.fdopen(self._out, "wb")

        return True

    @property
    def __reader_protocol(self) -> asyncio.StreamReaderProtocol:
        """Get reader protocol."""
        assert self._reader_protocol is not None, "reader protocol not set!"
        return self._reader_protocol

    async def write(self, data: bytes) -> None:
        """
        Write to pipe.

        :param data: bytes to write to pipe
        """
        self.logger.debug("writing {}...".format(len(data)))
        size = struct.pack("!I", len(data))
        os.write(self._out, size + data)
        asyncio.sleep(0.0)
        #self._out_fo.write(size + data)
        #self._out_fo.flush()

    async def read(self) -> Optional[bytes]:
        """
        Read from pipe.

        :return: read bytes
        """
        assert (
            self._stream_reader is not None
        ), "StreamReader not set, call connect first!"
        try:
            self.logger.debug("waiting for messages ({})...".format(self._in_path))
            buf = await self._stream_reader.readexactly(4)
            if not buf:  # pragma: no cover
                return None
            size = struct.unpack("!I", buf)[0]
            data = await self._stream_reader.readexactly(size)
            if not data:  # pragma: no cover
                return None
            self.logger.debug("received message: {}".format(data))
            return data
        except asyncio.IncompleteReadError as e:  # pragma: no cover
            self.logger.info(
                "Connection disconnected while reading from pipe ({}/{})".format(
                    len(e.partial), e.expected
                )
            )
            return None
        except asyncio.CancelledError:  # pragma: no cover
            return None

    async def close(self) -> None:
        """ Disconnect pipe """
        self.logger.debug("closing pipe (in={})...".format(self._in_path))
        assert self._fileobj is not None, "Pipe not connected"
        os.close(self._out)
        self._fileobj.close()
        await asyncio.sleep(0)


class TCPSocketProtocol:
    """
    TCP socket communication protocol
    """

    def __init__(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """
        Initialize the tcp socket protocol

        :param reader: established asyncio reader
        :param writer: established asyncio writer
        """

        self.logger = logger
        self.loop = loop if loop is not None else asyncio.get_event_loop()
        self._reader = reader
        self._writer = writer

    async def write(self, data: bytes) -> None:
        """
        Write to socket.

        :param data: bytes to write
        """
        assert self._writer is not None
        self.logger.debug("writing {}...".format(len(data)))
        size = struct.pack("!I", len(data))
        self._writer.write(size + data)
        await self._writer.drain()

    async def read(self) -> Optional[bytes]:
        """
        Read from socket.

        :return: read bytes
        """
        try:
            self.logger.debug("waiting for messages...")
            buf = await self._reader.readexactly(4)
            if not buf:  # pragma: no cover
                return None
            size = struct.unpack("!I", buf)[0]
            data = await self._reader.readexactly(size)
            if not data:  # pragma: no cover
                return None
            return data
        except asyncio.IncompleteReadError as e:  # pragma: no cover
            self.logger.info(
                "Connection disconnected while reading from pipe ({}/{})".format(
                    len(e.partial), e.expected
                )
            )
            return None
        except asyncio.CancelledError:  # pragma: no cover
            return None

    async def close(self) -> None:
        """ Disconnect socket """
        self._writer.write_eof()
        await self._writer.drain()
        self._writer.close()


class TCPSocketChannel(IPCChannel):
    """
    Interprocess communication channel implementation using tcp sockets
    """

    def __init__(
        self,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """ Initialize tcp socket interprocess communication channel"""
        self.logger = logger
        self._loop = loop
        self._timeout = 0.0
        self._server = None  # type: Optional[asyncio.AbstractServer]
        self._connected = None  # type: Optional[asyncio.Event]
        self._sock = None  # type: Optional[TCPSocketProtocol]

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 0))
        s.listen(1)
        self._port = s.getsockname()[1]
        s.close()

    async def connect(self, timeout: float = PIPE_CONN_TIMEOUT) -> bool:
        """
        Setup communication channel and wait for other end to connect

        :param timeout: timeout for the connection to be established
        """

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        self._connected = asyncio.Event()
        self._timeout = timeout if timeout > 0 else 0
        self._server = await asyncio.start_server(
            self._handle_connection, host="127.0.0.1", port=self._port
        )
        assert self._server.sockets is not None
        self._port = self._server.sockets[0].getsockname()[1]
        self.logger.debug("socket pipe rdv point: {}".format(self._port))

        try:
            await asyncio.wait_for(self._connected.wait(), self._timeout)
        except asyncio.TimeoutError:  # pragma: no cover
            return False

        self._server.close()
        await self._server.wait_closed()

        return True

    async def _handle_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ):
        assert self._connected is not None
        self._connected.set()
        self._sock = TCPSocketProtocol(
            reader, writer, logger=self.logger, loop=self._loop
        )

    async def write(self, data: bytes) -> None:
        """
        Write to channel.

        :param data: bytes to write
        """

        assert self._sock is not None, "Socket pipe not connected"
        await self._sock.write(data)

    async def read(self) -> Optional[bytes]:
        """
        Read from channel.

        :param data: read bytes
        """

        assert self._sock is not None, "Socket pipe not connected"
        return await self._sock.read()

    async def close(self) -> None:
        """ Disconnect from channel and clean it up """
        assert self._sock is not None, "Socket pipe not connected"
        await self._sock.close()

    @property
    def in_path(self) -> str:
        """ Rendezvous point for incoming communication """
        return str(self._port)

    @property
    def out_path(self) -> str:
        """ Rendezvous point for outgoing communication """
        return str(self._port)


class PosixNamedPipeChannel(IPCChannel):
    """
    Interprocess communication channel implementation using Posix named pipes
    """

    def __init__(
        self,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """ Initialize posix named pipe interprocess communication channel """
        self.logger = logger
        self._loop = loop

        self._pipe_dir = tempfile.mkdtemp()
        self._in_path = "{}/process_to_aea".format(self._pipe_dir)
        self._out_path = "{}/aea_to_process".format(self._pipe_dir)

        # setup fifos
        self.logger.debug(
            "Creating pipes ({}, {})...".format(self._in_path, self._out_path)
        )
        if os.path.exists(self._in_path):
            os.remove(self._in_path)  # pragma: no cover
        if os.path.exists(self._out_path):
            os.remove(self._out_path)  # pragma: no cover
        os.mkfifo(self._in_path)
        os.mkfifo(self._out_path)

        self._pipe = PosixNamedPipeProtocol(
            self._in_path, self._out_path, logger=logger, loop=loop
        )

    async def connect(self, timeout: float = PIPE_CONN_TIMEOUT) -> bool:
        """
        Setup communication channel and wait for other end to connect

        :param timeout: timeout for connection to be established
        """

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        return await self._pipe.connect(timeout)

    async def write(self, data: bytes) -> None:
        """
        Write to the channel.

        :param data: data to write to channel
        """
        await self._pipe.write(data)

    async def read(self) -> Optional[bytes]:
        """
        Read from the channel.

        :return: read bytes
        """
        return await self._pipe.read()

    async def close(self) -> None:
        """
        Close the channel and clean it up
        """
        await self._pipe.close()
        rmtree(self._pipe_dir)

    @property
    def in_path(self) -> str:
        """ Rendezvous point for incoming communication """
        return self._in_path

    @property
    def out_path(self) -> str:
        """ Rendezvous point for outgoing communication """
        return self._out_path


class TCPSocketChannelClient(IPCChannelClient):
    """
    Interprocess communication channel client using tcp sockets
    """

    def __init__(
        self,
        in_path: str,
        out_path: str,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """
        Initialize a tcp socket communication channel client

        :param in_path: rendezvous point for incoming data
        :param out_path: rendezvous point for outgoing data
        """
        self.logger = logger
        self._loop = loop

        self._port = int(in_path)
        self._sock = None  # type: Optional[TCPSocketProtocol]

        self._attempts = TCP_SOCKET_PIPE_CLIENT_CONN_ATTEMPTS

    async def connect(self, timeout: float = PIPE_CONN_TIMEOUT) -> bool:
        """
        Connect to the other end of the communication channel

        :param timeout: timeout for connection to be established
        """

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        self.logger.debug(
            "Attempting to connect to {}:{}.....".format("127.0.0.1", self._port)
        )

        connected = False
        while self._attempts > 0:
            self._attempts -= 1
            try:
                reader, writer = await asyncio.open_connection(
                    "127.0.0.1",
                    self._port,  # pylint: disable=protected-access
                    loop=self._loop,
                )
                self._sock = TCPSocketProtocol(
                    reader, writer, logger=self.logger, loop=self._loop
                )
                connected = True
                break
            except ConnectionRefusedError:
                await asyncio.sleep(TCP_SOCKET_PIPE_CLIENT_CONN_TIMEOUT)
            except Exception:  # pylint: disable=broad-except  # pragma: nocover
                return False

        return connected

    async def write(self, data: bytes) -> None:
        """
        Write data to channel

        :param data: bytes to write
        """

        assert self._sock is not None, "Socket pipe not connected"
        await self._sock.write(data)

    async def read(self) -> Optional[bytes]:
        """
        Read data from channel

        :return: read bytes
        """

        assert self._sock is not None, "Socket pipe not connected"
        return await self._sock.read()

    async def close(self) -> None:
        """ Disconnect from communication channel """
        assert self._sock is not None, "Socket pipe not connected"
        await self._sock.close()


class PosixNamedPipeChannelClient(IPCChannelClient):
    """
    Interprocess communication channel client using Posix named pipes
    """

    def __init__(
        self,
        in_path: str,
        out_path: str,
        logger: logging.Logger = _default_logger,
        loop: Optional[AbstractEventLoop] = None,
    ):
        """
        Initialize a posix named pipe communication channel client

        :param in_path: rendezvous point for incoming data
        :param out_path: rendezvous point for outgoing data
        """

        self.logger = logger
        self._loop = loop

        self._in_path = in_path
        self._out_path = out_path
        self._pipe = None  # type: Optional[PosixNamedPipeProtocol]

    async def connect(self, timeout: float = PIPE_CONN_TIMEOUT) -> bool:
        """
        Connect to the other end of the communication channel

        :param timeout: timeout for connection to be established
        """

        if self._loop is None:
            self._loop = asyncio.get_event_loop()

        self._pipe = PosixNamedPipeProtocol(
            self._in_path, self._out_path, logger=self.logger, loop=self._loop
        )
        return await self._pipe.connect()

    async def write(self, data: bytes) -> None:
        """
        Write data to channel

        :param data: bytes to write
        """

        assert self._pipe is not None, "Pipe not connected"
        await self._pipe.write(data)

    async def read(self) -> Optional[bytes]:
        """
        Read data from channel

        :return: read bytes
        """

        assert self._pipe is not None, "Pipe not connected"
        return await self._pipe.read()

    async def close(self) -> None:
        """ Disconnect from communication channel """
        assert self._pipe is not None, "Pipe not connected"
        return await self._pipe.close()


def make_ipc_channel(
    logger: logging.Logger = _default_logger, loop: Optional[AbstractEventLoop] = None
) -> IPCChannel:
    """
    Build a portable bidirectional InterProcess Communication channel
    """

    if os.name == "posix":
        return PosixNamedPipeChannel(logger=logger, loop=loop)
    elif os.name == "nt":  # pragma: nocover
        return TCPSocketChannel(logger=logger, loop=loop)
    else:  # pragma: nocover
        raise Exception(
            "make ipc channel is not supported on platform {}".format(os.name)
        )


def make_ipc_channel_client(
    in_path: str,
    out_path: str,
    logger: logging.Logger = _default_logger,
    loop: Optional[AbstractEventLoop] = None,
) -> IPCChannelClient:
    """
    Build a portable bidirectional InterProcess Communication client channel

    :param in_path: rendezvous point for incoming communication
    :param out_path: rendezvous point for outgoing outgoing
    """

    if os.name == "posix":
        return PosixNamedPipeChannelClient(in_path, out_path, logger=logger, loop=loop)
    elif os.name == "nt":  # pragma: nocover
        return TCPSocketChannelClient(in_path, out_path, logger=logger, loop=loop)
    else:  # pragma: nocover
        raise Exception(
            "make ip channel client is not supported on platform {}".format(os.name)
        )
