#!/usr/bin/bash

cd {ABSOLUTE_PATH}
PYTHONPATH=src ~/.local/bin/uv run ./src/cveforge $@