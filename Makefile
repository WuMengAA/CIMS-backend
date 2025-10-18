.PHONY: build ruff black test grpc clean

build: grpc
	pip install --no-cache-dir .

ruff:
	ruff check .
	ruff format .

black:
	black --check .

test:
	pytest

grpc: clean
	python -m grpc_tools.protoc -I./src/cims --python_out=./src/cims --grpc_python_out=./src/cims $(shell find ./src/cims/Protobuf -name "*.proto")
	python fix_imports.py

clean:
	find src/cims/Protobuf -name "*_pb2*.py" -delete
