#!/usr/bin/bash
uv build --offline && uv pip install --offline dist/cveforge-*.tar.gz && uv deploy && rm -r dist/*
