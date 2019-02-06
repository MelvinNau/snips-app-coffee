# Snips App Coffee Hack

Snips action code for your Hacked Coffee Machine.
[Here](https://medium.com/snips-ai/your-personal-home-barista-comes-to-life-with-this-voice-enabled-coffee-machine-5fc333326f31) the instructions to make this hack.

```
turn on and off the coffee machine.
brew one or two coffee
brew one or two long coffee
brew a strong coffee
```

## Getting Started

Please follow the step [here](https://medium.com/snips-ai/your-personal-home-barista-comes-to-life-with-this-voice-enabled-coffee-machine-5fc333326f31)
### Prerequisites

Snips platform should be runing with the coffee assistant on the device.
have done the hardware preparation indicate in the tutorial

have [sam](https://www.npmjs.com/package/snips-sam) installed on your computer
have a coffee assistant with coffee bundle

### Installing

A step by step series of examples that tell you how to get a development env running

```
sam install assistant
```
Select your assistant

## Running the tests

No test for the moment

### And coding style tests

no test for the moment

## Deployment

```
sam install actions -g https://github.com/snipsco/snips-app-coffee
ssh <username>@<hostname> sudo usermod -a -G dialout _snips-skills
```

## Built With

* [python](https://www.python.org)
* [sam](https://www.npmjs.com/package/snips-sam) - snips assistant manager

## Contributing

Please see the [Contribution Guidelines](https://github.com/snipsco/snips-app-coffee/blob/master/CONTRIBUTING.md).
## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Kamwa watanabe Bjay** - *Initial work* - [akaisuisei](https://github.com/akaisuisei)

## Copyright

This action code is provided by [Snips](https://www.snips.ai) as Open Source
software. See [LICENSE](https://github.com/snipsco/snips-app-coffee/blob/master/LICENSE.txt) for more
information.

## Acknowledgments


## Others

## TODO
add other Language configuration\
add test program

