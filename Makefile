.DEFAULT_GOAL := help

# Setup
SHELL := /bin/zsh
MMAKE := /usr/local/bin/mmake
WORKSPACE ?= ${PWD}
PROJECT_NAME := caffeine

# Maya
MAYA_VERSION = 2019
MAYA = /Applications/Autodesk/maya${MAYA_VERSION}/Maya.app/Contents/bin/maya
MAYAPY = /Applications/Autodesk/maya${MAYA_VERSION}/Maya.app/Contents/bin/mayapy


# Push the variables to the env.
export MAYA_VERSION WORKSPACE PROJECT_NAME

# Enable conda environment
.PHONY: conda-on
conda-on:
	conda activate caffeine-dev

# Remove all files related to build Python packages.
.PHONY: clean
clean:
	rm -rf ${WORKSPACE}/dist
	find . -name "*.pyc" -exec rm -f {} \;

# Build into a useable Maya module in the dist directory at the project root.
.PHONY: build
build:
	mkdir -p ${WORKSPACE}/dist

.PHONY: test
test:
	export PYTHONPATH=${CONDA_PREFIX}/lib/python2.7/site-packages:${PYTHONPATH} && \
	${MAYAPY} ./scripts/run_maya_tests.py


.PHONY: develop
develop:
	export PYTHONPATH=${CONDA_PREFIX}/lib/python2.7/site-packages:$(WORKSPACE)/src:${PYTHONPATH} && \
	${MAYA} &

.PHONY : help
help: ${MMAKE}
	${MMAKE} help