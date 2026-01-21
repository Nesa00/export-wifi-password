
# Wi-Fi Password Exporter

This script retrieves WiFi profiles and passwords stored on your Windows system and allows you to export them to a file or print them in the terminal.

## Requirements
Python 3

## Usage

Run the script using:

```
python main.py [options]
```

### Options

- `-h`, `--help`           Show this help message and exit
- `-p`, `--path [FILE]`    Export to a file. If used without a value, defaults to `export.json`. If a value is provided, uses that as the export path. Supports `.json`, `.xml`.
- `-t`, `--terminal`       Print output to terminal instead of exporting to a file

## Examples

Export to the default file (export.json):
```
python main.py -p
```

Export to a specific file:
```
python main.py -p wifi_data.xml
```

Print output to the terminal:
```
python main.py -t
```

Export to a file and print to terminal:
```
python main.py -p wifi_data.json -t
```
