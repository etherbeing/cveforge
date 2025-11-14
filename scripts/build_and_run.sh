#!/usr/bin/bash
uv build --offline && uv pip install --offline dist/cveforge-0.1.0.tar.gz && uv run cveforge