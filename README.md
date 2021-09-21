# Satellite labelling tool

## About this app

A tool for manual labelling of storm top features such as overshooting tops, above-anvil plumes, cold U/Vs, rings etc. 

## How to run this app locally

(The following instructions are for unix-like shells)

### Using pip

Install the package from its git repository using `pip install` and run
`slt` for production version or `slt --develop` for develop version. 

Port of the application (8050 by default) can be changed with `-p` switch

### Using docker

After manually building docker image from the included `Dockerfile` run

```shell
docker run -p 8050:8050 satellite-labelling-tool-dev:latest
```

### Using git clone

Clone this repository and navigate to the directory containing this `README` in
a terminal.

Create and activate a virtual environment (recommended):

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

Install the requirements

```bash
pip install -r requirements.txt
```

Run the app. An IP address where you can view the app in your browser will be
displayed in the terminal.

```bash
python slt/app.py
```

## Options

### Path prefix

When routing traffic to the app through reverse proxy such as nging or traefic, you will need to pass the routing prefix 
to the application. This may be done by setting environment variable `SLT_PREFIX`, e.g. `SLT_PREFIX=/slt/` or by `--prefix` argument of the run script 
```shell
slt --prefix /slt/
```

## Screenshot

![Screenshot of app](/slt/assets/screenshot.png)

