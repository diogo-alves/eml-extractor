# EML Extractor

EML Extractor is a CLI tool to extract attachments from .eml files (email messages saved as files).


## Features

* Find .eml files (recursively or not) in a selected folder;
* Select individuals .eml files to extraction;
* Save all attachments in a single main folder;
* Organize the attachments by email subject subfolder.


## Requirements

Python 3.6+


## Usage

By default, the current working directory is used as the source for .eml files as well as destination for extracted attachments. You can set different optional arguments to change this behavior:

```console
usage: eml-extractor [OPTIONS]

Extracts attachments from .eml files

optional arguments:
  -h, --help            show this help message and exit
  -s PATH, --source PATH
                        the directory containing the .eml files to extract
                        attachments (default: current working directory)
  -r, --recursive       allow recursive search for .eml files under SOURCE
                        directory
  -f FILE [FILE ...], --files FILE [FILE ...]
                        specify an .eml file or a list of .eml files to extract
                        attachments
```
The destination directory of extracted attachments is the location of the .eml itself. It is made for a large number of files being resided in multiple folders and future processing with index tools and for faster searching later on.

## Examples

### 1. Find all .eml files in current working dir, extract the attachments and save them in the same dir:
```console
$ eml-extractor
```

The command above is equivalent to:
```console
$ eml-extractor --source . --destination .
```

### 2. Set another path for searching .eml files:
```console
$ eml-extractor --source /path/to/eml/files/
```

### 3. Allow recursive searching:
```console
$ eml-extractor --source /path/to/eml/files/ --recursive
```

### 4. Define manually from which files the attachments will be extracted:
```console
$ eml-extractor --files /path/to/file1.eml /path/to/file2.eml
```

### 5. Change the path where to save the extracted attachments:
```console
$ eml-extractor --destination /path/to/extracted/attachments/
```


## License

This project is licensed under the terms of the [MIT License](https://github.com/diogo-alves/eml-extractor/blob/main/LICENSE).
