# Ventilator

<p align="center">
    <a href="https://github.com/up9inc/ventilator/blob/master/LICENSE">
        <img alt="GitHub License" src="https://img.shields.io/github/license/up9inc/mockintosh?logo=GitHub&style=flat-square">
    </a>
<a href="https://travis-ci.com/github/up9inc/ventilator/builds/">
        <img alt="Travis" src="https://img.shields.io/travis/up9inc/ventilator?logo=Travis&style=flat-square">
    </a>
<a href="https://codecov.io/gh/up9inc/ventilator">
        <img alt="Code Coverage (Codecov)" src="https://img.shields.io/codecov/c/github/up9inc/ventilator?logo=Codecov&style=flat-square">
    </a>
</p>                                                             

## Usage
```bash
 ❯ ventilator -h                                                    
usage: ventilator [-h] [-c CONFIGURATOR] [-f CONFIGURATOR_FILE] -i INPUT [-o OUTPUT] [-v]

optional arguments:
  -h, --help            show this help message and exit
  -c CONFIGURATOR, --configurator CONFIGURATOR
                        web / cli / file. Default: CLI
  -f CONFIGURATOR_FILE, --configurator_file CONFIGURATOR_FILE
                        The path of the configurator file.
  -i INPUT, --input INPUT
                        docker-compose / kubernetes file.
  -o OUTPUT, --output OUTPUT
                        Ventilator Output Path. Default: current directory
  -v, --verbose         Logging in DEBUG level
```
