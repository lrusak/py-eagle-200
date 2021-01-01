# SPDX-License-Identifier: GPL-2.0-only

from flask import Flask, abort, jsonify, request
from flask_httpauth import HTTPBasicAuth
from lxml import etree


class Eagle200Sim(object):

    auth = {"0077dd": "6e61a3a94882eef9"}

    def process_request(self, data):
        xml = etree.fromstring(data)
        command_name = xml.findtext("Name")

        if command_name == "device_list":
            return self._device_list()

        elif command_name == "device_details":
            details = xml.find("DeviceDetails")
            address = details.findtext("HardwareAddress")

            return self._device_details(address)

        elif command_name == "device_query":
            details = xml.find("DeviceDetails")
            address = details.findtext("HardwareAddress")
            components = xml.find("Components")

            all = components.find("All")
            if all is not None:
                if all.text ==  "Y":
                    return self._device_query(address)
            else:
                component = components.find("Component")
                name = component.findtext("Name")
                variables = component.find("Variables")
                variable = variables.find("Variable")
                value = variable.findtext("Name")

                return self._device_query(address, name, value)

        abort(400, "Fuction not implemented")

    def _device_list(self):
        """
        Returns the device list

        Example return:
        <DeviceList>
          <Device>
            <HardwareAddress>0x000781000081fd0b</HardwareAddress>
            <Manufacturer>generic</Manufacturer>
            <ModelId>electric_meter</ModelId>
            <Protocol>Zigbee</Protocol>
            <LastContact>0x5989f8f5</LastContact>
            <ConnectionStatus>Connected</ConnectionStatus>
            <NetworkAddress>0x0000</NetworkAddress>
          </Device>
        </DeviceList>
        """

        map = {
            "HardwareAddress": "0x000781000081fd0b",
            "Manufacturer": "generic",
            "ModelId": "electric_meter",
            "Protocol": "Zigbee",
            "LastContact": "0x5989f8f5",
            "ConnectionStatus": "Connected",
            "NetworkAddress": "0x0000",
        }

        root = etree.Element("DeviceList")
        device = etree.SubElement(root, "Device")

        for key in map:
            etree.SubElement(device, key).text = map[key]

        # print(etree.tostring(root, pretty_print=True).decode())

        return etree.tostring(root)

    def _device_details(self, address):
        """
        Returns the device details for a given hardware address

        address:str the hardware address of the device

        Example return:
        <Device>
          <DeviceDetails>
            <Name>Power Meter</Name>
            <HardwareAddress>0x000781000081fd0b</HardwareAddress>
            <Protocol>Zigbee</Protocol>
            <Manufacturer>Generic</Manufacturer>
            <ModelId>electric_meter</ModelId>
          </DeviceDetails>
          <Components>
            <Component>
              <Name>Main</Name>
              <FixedId>0</FixedId>
              <Variables>
                <Variable>zigbee:InstantaneousDemand</Variable>
                <Variable>zigbee:Multiplier</Variable>
                <Variable>zigbee:Divisor</Variable>
                <Variable>zigbee:CurrentSummationDelivered</Variable>
                <Variable>zigbee:Price</Variable>
                <Variable>zigbee:RateLabel</Variable>
                <Variable>zigbee:Message</Variable>
              </Variables>
            </Component>
          </Components>
        </Device>
        """

        details_map = {
            "Name": "Power Meter",
            "HardwareAddress": address,
            "Protocol": "Zigbee",
            "Manufacturer": "Generic",
            "ModelId": "electric_meter",
        }

        root = etree.Element("Device")
        device_details = etree.SubElement(root, "DeviceDetails")

        for key in details_map:
            etree.SubElement(device_details, key).text = details_map[key]

        components = etree.SubElement(root, "Components")
        component = etree.SubElement(components, "Component")

        component_map = {"Name": "Main", "FixedId": "0"}

        for key in component_map:
            etree.SubElement(component, key).text = component_map[key]

        variables = etree.SubElement(component, "Variables")

        variable_list = [
            "zigbee:InstantaneousDemand",
            "zigbee:Multiplier",
            "zigbee:Divisor",
            "zigbee:CurrentSummationDelivered",
            "zigbee:Price",
            "zigbee:RateLabel",
            "zigbee:Message",
        ]

        for item in variable_list:
            etree.SubElement(variables, "Variable").text = item

        # print(etree.tostring(root, pretty_print=True).decode())

        return etree.tostring(root)

    def _device_query(self, address, name=None, value=None):
        """
        Returns the device query for a given hardware address, name, and variable

        address:str the hardware address of the device to query
        name:str the name of the component to query
        value:str the variable to query

        Example return:
        <Device>
          <DeviceDetails>
            <Name>Power Meter</Name>
            <HardwareAddress>0x000781000081fd0b</HardwareAddress>
            <Protocol>Zigbee</Protocol>
            <Manufacturer>Generic</Manufacturer>
            <ModelId>electric_meter</ModelId>
            <LastContact>0x59a0b67c</LastContact>
            <ConnectionStatus>Connected</ConnectionStatus>
          </DeviceDetails>
          <Components>
            <Component>
              <Name>Main</Name>
              <FixedId>0</FixedId>
              <Variables>
                <Variable>
                  <Name>zigbee:InstantaneousDemand</Name>
                  <Value>21.499 kW</Value>
                </Variable>
              </Variables>
            </Component>
          </Components>
        </Device>
        """

        details_map = {
            "Name": "Power Meter",
            "HardwareAddress": address,
            "Protocol": "Zigbee",
            "Manufacturer": "Generic",
            "ModelId": "electric_meter",
            "LastContact": "0x59a0b67c",
            "ConnectionStatus": "Connected",
        }

        root = etree.Element("Device")
        device_details = etree.SubElement(root, "DeviceDetails")

        for key in details_map:
            etree.SubElement(device_details, key).text = details_map[key]

        components = etree.SubElement(root, "Components")
        component = etree.SubElement(components, "Component")

        component_map = {"Name": "Main", "FixedId": "0"}

        if name is not None and name != component_map["Name"]:
            abort(400, "name '%s' doesn't exist" % name)

        for key in component_map:
            etree.SubElement(component, key).text = component_map[key]

        variables = etree.SubElement(component, "Variables")

        variable_map = {
            "zigbee:InstantaneousDemand": "21.499 kW",
            "zigbee:Multiplier": "",
            "zigbee:Divisor": "",
            "zigbee:CurrentSummationDelivered": "1000 kWh",
            "zigbee:Price": "0.1 CAD",
            "zigbee:RateLabel": "CAD",
            "zigbee:Message": "Hello, World!",
        }

        if value is not None and value not in variable_map:
            abort(400, "Variable '%s' doesn't exist" % value)

        if value is None:
            for key in variable_map:
                variable = etree.Element("Variable")
                etree.SubElement(variable, "Name").text = key
                etree.SubElement(variable, "Value").text = variable_map[key]
                variables.append(variable)
        else:
            variable = etree.SubElement(variables, "Variable")
            etree.SubElement(variable, "Name").text = value
            etree.SubElement(variable, "Value").text = variable_map[value]

        # print(etree.tostring(root, pretty_print=True).decode())

        return etree.tostring(root)


app = Flask(__name__)
auth = HTTPBasicAuth()

eagle = Eagle200Sim()


@auth.get_password
def get_password(username):
    return eagle.auth[username]


@app.route("/cgi-bin/post_manager", methods=["POST"])
@auth.login_required
def process_request():
    if request.content_type != "text/xml":
        abort(415, "Content-type must be 'text/xml'")

    return eagle.process_request(request.data)


def create_app():
    return app


if __name__ == "__main__":
    app.run(debug=True)
