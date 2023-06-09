import uuid


def mac_address(default_value=None):
    mac_addr = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                         for ele in range(0, 8*6, 8)][::-1])
    return "<div class='mb-2'><b>MAC Address:</b> " + mac_addr + "</div>"
