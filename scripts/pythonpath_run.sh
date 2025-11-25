UV_COMMAND_PATH=$1
shift
PYTHONPATH=src $UV_COMMAND_PATH run ./src/cveforge $@