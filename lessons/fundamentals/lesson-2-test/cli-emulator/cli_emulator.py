#!/usr/bin/python
from __future__ import print_function
import cmd
import sys
import getpass
import socket
import platform
import pickle
import re
import os.path
from jinja2 import Environment, PackageLoader, select_autoescape

jinja_env = Environment(
    loader=PackageLoader('cli_emulator', 'templates'),
    autoescape=select_autoescape(['html', 'xml'])
    )

version = "0.9"

ipadd_pattern = re.compile('\b(?:\d{1,3}\.){3}\d{1,3}\b')

interfaces = {
    "ge-1/0/1": {
        "description": "CKT ETH/12345/A",
        "sub_interfaces": {
            "10": {
                "description": "Bob's Taco Shack Site 1 - CKT VC/123",
                "ip_address": "192.168.2.1/24",
                "type": "Gigabit Ethernet",
                "vlan": 10,
                "proto_state": "up",
                "int_state": "up",
                "bandwidth": "5000M"
            },
            "11": {
                "description": "Bob's Taco Shack Site 2 - CKT VC/124",
                "ip_address": "192.168.3.1/24",
                "type": "Gigabit Ethernet",
                "vlan": 11,
                "proto_state": "up",
                "int_state": "up",
                "bandwidth": "5000M"
            }
        }
    },
    "ge-1/0/2": {
        "description": "CKT ETH/45678/QZ",
        "sub_interfaces": {
            "10": {
                "description": "Bob's Taco Shack Host - CKT VC/125",
                "ip_address": "192.168.1.1/24",
                "type": "Gigabit Ethernet",
                "vlan": 10,
                "proto_state": "down",
                "int_state": "down",
                "bandwidth": "10000M"
            }
        }
    },
    "ge-2/0/0": {
        "description": "Uplink CKT GE/1212345/QZDW",
        "ip_address": "192.168.4.1/24",
        "type": "Ten-Gigabit Ethernet",
        "vlan": 1000,
        "proto_state": "up",
        "int_state": "up",
        "bandwidth": "100000M"
    },
    "loopback0": {
        "description": "BGP Peer Interface",
        "ip_address": "192.168.5.1/32",
        "type": "Loopback",
        "vlan": 0,
        "proto_state": "up",
        "int_state": "up",
        "bandwidth": "100000M"
    }
}

xconnects = {
    "vpn1": {
        "source-int": "ge-1/0/1.10",
        "dest-int": "ge-1/0/2.10",
        "type": "vlan",
    },
    "vpn2": {
        "source-int": "ge-1/0/1.11",
        "dest-int": "ge-1/0/2.10",
        "type": "vlan",
    }
}

xconnect_hash = {}


class Shell(cmd.Cmd, object):
    intro = "\n\nTest shell " + version +\
        """\n  by: David Curran (david.curran@ftr.com)\n\
  Type 'help' to see a list of commands\n"""

    prompt = getpass.getuser() + "@" + socket.gethostname() + "_fake$ "
    completekey = 'tab'

    def __init__(self):
        super(Shell, self).__init__()
        self.configfile = None

    def check_for_int(self, interface):
        if interface in interfaces.keys():
            return True

        try:
            interface, sub_int = interface.split('.')
            if sub_int in interfaces[interface]['sub_interfaces'].keys():
                return True
            else:
                return False
        except (ValueError, KeyError):
            return False

    def save_config(self):
        'save the current config to a file'
        if self.configfile is None:
            print("No configfile set")
            return False

        with open(self.configfile, 'wb') as fh:
            pickle.dump((interfaces, xconnects, xconnect_hash), fh)

    def read_config(self):
        'read a config from a file'
        global interfaces
        global xconnects
        global xconnect_hash

        if self.configfile is not None:
            with open(self.configfile, 'rb') as fh:
                input_data = pickle.load(fh)

            interfaces = input_data[0]
            xconnects = input_data[1]
            xconnect_hash = input_data[2]

    def do_set_configfile(self, args):
        'create an output file <filename>'

        if os.path.isfile(args):
            self.configfile = args
            self.read_config()
        else:
            self.configfile = args

    def do_create_xconnect(self, args):
        'create_xconnect <source> <dest> <xc_type> <name>'
        try:
            source, dest, xc_type, name = args.split(None)
        except ValueError:
            print('create_xconnect <source> <dest> <xc_type> <name>')
            return False

        if not self.check_for_int(source) or not self.check_for_int(dest):
            if not ipadd_pattern.match(source) or not ipadd_pattern.match(dest):
                print('source/destination must be valid interface or IP Address')
                return False

        if xc_type not in ['mpls', 'vlan']:
            print('xc_type must be one of [vlan, mpls]')
            return False

        xconnects[name] = {
            "source-int": source,
            "dest-int": dest,
            "type": xc_type
        }

        return True

    def do_show_xconnects(self, args):
        template = jinja_env.get_template('show-xconnects.tmpl')
        print(template.render(xconnects=xconnects))

        return True

    def do_show_xconnect(self, args):
        'show_xconnect <name>'

        data = {}

        if args in xconnects.keys():
            data[args] = xconnects[args]
            template = jinja_env.get_template('show-xconnects.tmpl')
            print(template.render(xconnects=data))

            return True
        else:
            print("Xconnect does not exist")
            return False

    def do_delete_xconnect(self,args):
        'delete_xconnect <xconnect>'
        if args in xconnects.keys():
            xconnects.pop(args)
        else:
            print("xconnect does not exist")
            return False

    def do_show_interface(self, args):
        'do_show_interface <interface>.[sub-interface]'

        sub_int = False
        try:
            interface, sub_int = args.split('.')
            if sub_int not in interfaces[interface]["sub_interfaces"].keys():
                print("Interface {}.{} not found".format(interface, sub_int))
                return False
        except (ValueError, KeyError):
            interface = args
            if interface not in interfaces.keys():
                print("Interface {} not found".format(interface))
                return False

        template = jinja_env.get_template('show_interface.tmpl')
        print(template.render(interface=interface, sub_int=sub_int, interfaces=interfaces))
        return True

    def do_show_interfaces(self, args):
        'Show all interfaces'
        template = jinja_env.get_template('show_interface.tmpl')

        for interface in interfaces:
            print(template.render(interface=interface, sub_int=False,
                                  interfaces=interfaces))

        return True

    def do_create_interface(self, args):
        'create_interface <interface>.[sub-interface]'

        if len(args) < 1:
            print('create_interface <interface>.[sub-interface]')
            return False

        try:
            interface, sub_int = args.split('.')
            if self.check_for_int(args):
                print("Interface already exists")
                return False

            interfaces[interface] = {
                "description": "",
                "sub_interfaces": {
                    sub_int: {
                        "description": "",
                        "ip_address": "",
                        "type": "",
                        "vlan": 0,
                        "proto_state": "down",
                        "int_state": "down",
                        "bandwidth": "1000M"
                    }
                }
            }
        except UnboundLocalError:
            print("create_interface <interface>.[sub-interface]")
            return False

        except ValueError:
            if self.check_for_int(args):
                print("Interface already exists")
                return False

            interfaces[args] = {
                "description": "",
                "ip_address": "",
                "type": "",
                "vlan": 0,
                "proto_state": "down",
                "int_state": "down",
                "bandwidth": "1000M"
            }

    def do_update_interface(self, args):
        """update_interface <command> <data> where <command> is one of:
        description <description>
        type <type>
        bandwidth <bandwidth>
        ip_address <ip_address>
        vlan <vlan>
        proto_state <up/down>
        int_state <up/down>"""

        commands = [
            'description',
            'type',
            'bandwidth',
            'ip_address',
            'vlan',
            'proto_state',
            'int_state'
        ]

        try:
            interface, command, data = args.split(None, 2)
            if not self.check_for_int(interface):
                print("Interface does not exist")
                return False
            elif command not in commands:
                print("Command does not exist")
                return False
        except ValueError:
            print("""update_interface <command> <data> where <command> is one of:
            description <description>
            type <type>
            bandwidth <bandwidth>
            ip_address <ip_address>
            vlan <vlan>
            proto_state <up/down>
            int_state <up/down>""")
            return False

        try:
            interface, sub_int = interface.split('.')
            interfaces[interface]['sub_interfaces'][sub_int][command] = data
            return True
        except ValueError:
            interfaces[interface][command] = data

    def do_delete_interface(self, args):
        'delete_interface <interface>.[sub_interface]'
        if not self.check_for_int(args):
            print("Interface does not exist")
            return False

        for xconnect in xconnects:
            for key, value in xconnects[xconnect].items():
                if args in value:
                    print("Interface is part of an xconnect")
                    return False

        try:
            interface, sub_int = args.split('.')
            interfaces[interface]['sub_interfaces'].pop(sub_int)
        except ValueError:
            interface = args
            interfaces.pop(interface)

        


    def do_show_device(self, args):
        "Show system info"
        print("Hostname: " + socket.gethostname())
        print("OS: " + platform.system())
        print("Release: " + platform.release())
        print("Version: " + str(platform.platform()))
        print("Machine: " + platform.machine())
        print("Processor: " + platform.processor())

    def do_exit(self, arg):
        self.save_config()
        print("Goodbye...")
        sys.exit()

    def precmd(self, line):
        return line

    def postcmd(self, stop, line):
        self.save_config()
        print()


if __name__ == '__main__':
    try:
        Shell().cmdloop()
    except KeyboardInterrupt:
        print("\nGoodbye...")
        sys.exit()
