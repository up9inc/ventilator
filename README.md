# Ventilator

<p align="center">
    <a href="https://github.com/up9inc/mockintosh/blob/master/LICENSE">
        <img alt="GitHub License" src="https://img.shields.io/github/license/up9inc/mockintosh?logo=GitHub&style=flat-square">
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
