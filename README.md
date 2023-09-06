# Lumacryte

## Introduction

This software is a game developed during the [Open Source AI Game Jam](https://itch.io/jam/open-source-ai-game-jam) from Hugging Face between the 7th and the 9th of July 2023.

## Installation

### For users

Just download our zip folder, unzip it and start the .exe file.

### For developers

#### Cloning the repository

To clone the github repository, you have to search the clone button on the main page of the project. Then click on it and select `https` or `ssh` depending on your favorite mode of connexion. Copy the given id and then open a terminal on your computer, go to the folder where you want to install the project and use the following command:

```bash
git clone <your copied content>
```

#### Creation of a virtual environment

You might want to use a virtual environment to execute the code. To do so, use the following command:

```bash
python -m virtualenv venv
```

To start it, use the command on *Windows*:

```bash
venv/Scripts/Activate.ps1
```

Or for *MacOS* and *Linux*:

```bash
venv/Scripts/activate
```

#### Installation of the necessary librairies

To execute this software, you need several *Python* librairies, specified in the `requirements.txt` file. To install them, use the following command:

```bash
pip install -r requirements.txt
```

## Utilisation

Start and play :wink:.

## Development

### Architecture of the project

The project is divided into several folders:

- `data`
- `resources`
- `tools`, divided into several modules:
  - `tools_`
  - `tools_`

It also contains the following files:

- `.gitignore`
- `main.py`
- `requirements.txt`, list of packages required to run the app.
- `pyproject.toml`, configuration file for *Pylint* and *Pytest*.

### Build for Windows

`pyinstaller lumacryte_onefile.spec`

### Build for Android

To create a debug unsigned apk, use the following command : `buildozer android debug`

To launch it on a device connected with a USB cable, use the following command : `buildozer -v android deploy run logcat | grep python`

To create a release version of the application : `buildozer android release`

```bash
keytool -genkey -v -keystore ~/keystores/Lumacryte.keystore -alias Lumacryte -keyalg RSA -keysize 2048 -validity 10000
keytool -importkeystore -srckeystore ~/keystores/Lumacryte.keystore -destkeystore ~/keystores/Lumacryte.keystore -deststoretype pkcs12

export P4A_RELEASE_KEYSTORE=~/keystores/Lumacryte.keystore
export P4A_RELEASE_KEYSTORE_PASSWD=
export P4A_RELEASE_KEYALIAS_PASSWD=
export P4A_RELEASE_KEYALIAS="Lumacryte"
```

## Credits

This software has been developed by Paul and Agathe.

## License

This program is licensed under the `Apache License version 2.0`.

