TX/RX with auto acknowledge enabled
====================================

:github:`/examples/rx_tx_aa_enabled/` demonstrate how to transfer data between two RFM devices with auto aknowledge enabled.

This mode forces transmitter repeat last packet until confirmation from receiver obtained.

If no confirmation from receiver get after 15 retransmittion :code:`MAX_RT` flag is set and could be detected by 
:code:`controller.is_max_rt()` call. After this python program should decide what to do with failed packet.
To be able to continue transmition MAX_RT flag must be unset calling :code:`controller.unset_max_rt()`

In this example there are two scripts: :github:`/examples/rx_tx_aa_enabled/rx.py` to receive data 
and :github:`/examples/rx_tx_aa_enabled/tx.py` to transfer data

Each script runs infinite loop to transmit/receive data. 

Payload is 5 byte length and contains magic sequence **cafeb0baxx**, where xx is a counter

Configuration parameters
------------------------
After RFM device wired to FTDI, you need to provide URL for FTDI device.
Check `pyFTDI documentation <https://eblot.github.io/pyftdi/urlscheme.html>`_ how to obtain correct url.

For both rx and tx scripts this value controlled by varible

.. code-block:: python
    :linenos:

    FTDI_URL = 'ftdi://ftdi:232h:555551/1'  # Url for ftdi chip, used to control RX

Make sure to use correct URL's for TX and RX script. This example assume that rx and tx devices connected to different FTDI boards.

Next parameter required for pairing:

.. code-block:: python
    :linenos:
    
    CE_PIN = 7                              # FTDI pin used to as CE for RFM device

This is `FTDI GPIO <https://eblot.github.io/pyftdi/api/spi.html#gpios>`_ pin used to send CE signal to RFM device

Rest of parameters are related to RFM chip config and explained in comments

.. code-block:: python
    :linenos:

    PIPE_NO = 0                             # Pipe number used to receive data
    ADDR_WIDTH = Rfm75AddressWidth.ADDR_5   # How many bytes used for address
    PIPE_ADDR = b'\x11\x22\x33\x22\x11'     # Addres for selected pipe
    RF_CHANNEL = 0x02                       # Operating Rf Channel
    DATA_RATE = '250ksps'                   # Transfer speed
    PAYLOAD_SIZE = 0x05                     # Static payload size up to 32b

Configure chip to transmit/receive data
---------------------------------------
Simplest mode to transmit data it is when transmitter send data into the air and do not care whether it was received. Typical configuration is:

TX Part configuration is the same as for previouse example. But additional tuning required

.. code-block:: python
    :linenos:

    # Reset AA for all pipes
    controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge()

    # Enable AA on TX part is mandatory, otherwise TX will be unable to receive ACK packet
    # PIPE_ADDR must be the same as target RX pipe 
    controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)
    controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)
    controller.config_ctrl.pipe_ctrl.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)
    controller.config_ctrl.pipe_ctrl.enable_pipe_auto_acknowledge(PIPE_NO)


On RX part pipe AA must be enabled:

.. code-block:: python
    :linenos:

    # Configure PIPE
    controller.config_ctrl.pipe_ctrl.enable_pipe(PIPE_NO)
    controller.config_ctrl.pipe_ctrl.set_rx_pipe_address(PIPE_NO, PIPE_ADDR)
    controller.config_ctrl.pipe_ctrl.set_rx_pipe_payload_width(PIPE_NO, PAYLOAD_SIZE)
    controller.config_ctrl.pipe_ctrl.disable_auto_acknowledge() # Reset AA for all pipes if any were enabled
    controller.config_ctrl.pipe_ctrl.enable_pipe_auto_acknowledge(PIPE_NO) # Enable AA for PIPE_NO 

After this normal start routine and receive loop can be started
