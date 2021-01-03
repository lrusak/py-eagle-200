# py-eagle-200

This python library is used to wrap calls to a [Rainforest Automation EAGLE-200 device](https://rainforestautomation.com/rfa-z114-eagle-200-2/).

The library was designed around the API documentation available [here](https://rainforestautomation.com/wp-content/uploads/2017/02/EAGLE-200-Local-API-Manual-v1.0.pdf).

The API uses an awkward xml format with POST request. This library does it's best to wrap this and provide a more python friendly JSON output.

## Simulator

A simulator is also provided as I didn't have the device at the time I started this library. I needed a way to test the library to make sure the API calls were correct. Any changes should be validated via tests which may require changes to the simulator as well.

The simulator uses [flask](https://flask.palletsprojects.com/en/1.1.x/) to handle POST requests. The simulator hands out xml data from the examples in the developer API manual.

See [simulator](tests/simulator/eagle200sim.py)

## Usage

See [tests](tests/test_eagle200.py)

See [eagle-200-mqtt](https://github.com/lrusak/eagle-200-mqtt)

## Future

 Make the output more _pythonic_. The output should look similar to what is output by the device but wrapped in a python friendly JSON interface. Currently the output uses an inconsitent and mixed dict/list object.
