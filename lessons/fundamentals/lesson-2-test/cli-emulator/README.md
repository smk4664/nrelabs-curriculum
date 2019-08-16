A simple CLI emulator to use when playing with Blue Planet. It has many of the CRUDL functions used on a generic router and a "show device" type function.




```
currand@M_C02N72W0G3QK_fake$ help

Documented commands (type help <topic>):
========================================
create_interface  delete_xconnect  show_interface
create_xconnect   help             show_interfaces
delete_interface  show_device      update_interface

Undocumented commands:
======================
exit  show_xconnects


currand@M_C02N72W0G3QK_fake$ show_interfaces
interface ge-1/0/2
  Description: CKT ETH/12345/A
  Logical interface: 10, protocol address 192.168.2.1/24
    Description: Bob's Taco Shack Site 1 - CKT VC/123
    Type: Gigabit Ethernet
    VLAN ID: 10
    Bandwidth: 5000M
    Protocol state (interface/protocol): up/up

  Logical interface: 11, protocol address 192.168.3.1/24
    Description: Bob's Taco Shack Site 2 - CKT VC/124
    Type: Gigabit Ethernet
    VLAN ID: 11
    Bandwidth: 5000M
    Protocol state (interface/protocol): up/up

interface ge-1/0/1
  Description: CKT ETH/45678/QZ
  Logical interface: 10, protocol address 192.168.1.1/24
    Description: Bob's Taco Shack Host - CKT VC/125
    Type: Gigabit Ethernet
    VLAN ID: 10
    Bandwidth: 10000M
    Protocol state (interface/protocol): down/down

interface ge-2/0/0
  Description: Uplink CKT GE/1212345/QZDW
  Protocol address 192.168.4.1/24
  Type: Ten-Gigabit Ethernet
  VLAN ID: 1000
  Bandwidth: 100000M
  Protocol state (interface/protocol): up/up

interface loopback0
  Description: BGP Peer Interface
  Protocol address 192.168.5.1/32
  Type: Loopback
  VLAN ID: 0
  Bandwidth: 100000M
  Protocol state (interface/protocol): up/up


currand@M_C02N72W0G3QK_fake$ show_xconnects
Name	Source	Destination	Type
----	------	------------	-----
vpn1	ge-1/0/1.10	ge-1/0/2.10	vlan
vpn2	ge-1/0/1.11	ge-1/0/2.10	vlan
offnet-vpn	10.1.1.1	ge-1/0/2.10	mpls

currand@M_C02N72W0G3QK_fake$ create_interface ge-3/0/0.10

currand@M_C02N72W0G3QK_fake$ show interface ge-3/0/0.10
*** Unknown syntax: show interface ge-3/0/0.10

currand@M_C02N72W0G3QK_fake$ show_interface ge-3/0/0.10
interface ge-3/0/0.10
  Description:
  Logical interface: 10, protocol address
    Description:
    Type:
    VLAN ID: 0
    Bandwidth: 1000M
    Protocol state (interface/protocol): down/down


currand@M_C02N72W0G3QK_fake$ update_interface ip_address 192.168.3.1/24
update_interface <command> <data> where <command> is one of:
            description <description>
            type <type>
            bandwidth <bandwidth>
            ip_address <ip_address>
            vlan <vlan>
            proto_state <up/down>
            int_state <up/down>

currand@M_C02N72W0G3QK_fake$ update_interface ge-3/0/0.10 ip_address 192.168.3.1/24

currand@M_C02N72W0G3QK_fake$ show_interface ge-3/0/0.10
interface ge-3/0/0.10
  Description:
  Logical interface: 10, protocol address 192.168.3.1/24
    Description:
    Type:
    VLAN ID: 0
    Bandwidth: 1000M
    Protocol state (interface/protocol): down/down
'''
