.DEFAULT_GOAL := help

# Setup
SHELL := /bin/zsh
MMAKE := /usr/local/bin/mmake
WORKSPACE ?= ${PWD}
PROJECT_NAME := caffeine

# Python
VIRTUAL_ENV_DIR = venv

# Maya
DEFAULT_MAYA_VERSION = 2019
MAYAPY = /Applications/Autodesk/maya${MAYA_VERSION}/Maya.app/Contents/bin/mayapy
MAYA_VERSION = 2019
MAYA_MODULE_PATH = ${WORKSPACE}/dist

# Push the variables to the env.
export DEFAULT_MAYA_VERSION MAYA_VERSION WORKSPACE MAYA_MODULE_PATH PROJECT_NAME

toggleEnv:
	conda activate caffeine-dev

# Remove all files related to build Python packages.
.PHONY : clean
clean:
	rm -Rf build dist src/*.egg-info .eggs *.egg
	find . -name "*.pyc" -exec rm -f {} \;

# Build into a useable Maya module in the dist directory at the project root.
.PHONY : build
build:
	mkdir -p ${WORKSPACE}/dist/${PROJECT_NAME}/scripts/${PROJECT_NAME}
	cp -r ${WORKSPACE}/src/${PROJECT_NAME} ${WORKSPACE}/dist/${PROJECT_NAME}/scripts
	cp ${WORKSPACE}/src/${PROJECT_NAME}.mod ${WORKSPACE}/dist/${PROJECT_NAME}.mod
	cp ${WORKSPACE}/src/userSetup.py ${WORKSPACE}/dist/${PROJECT_NAME}/scripts/userSetup.py

# Install with symlinks to this folder for faster development.
.PHONY : develop
develop:
	virtualenv -p python2.7 --clear ${VIRTUAL_ENV_DIR}
	source ./venv/bin/activate && pip install -r ./requirements.txt
	rm -rf ${WORKSPACE}/dist
	mkdir -p ${WORKSPACE}/dist/${PROJECT_NAME}/scripts
	ln -sf ${WORKSPACE}/src/${PROJECT_NAME} ${WORKSPACE}/dist/${PROJECT_NAME}/scripts
	ln -sf ${WORKSPACE}/src/${PROJECT_NAME}.mod ${WORKSPACE}/dist/${PROJECT_NAME}.mod
	ln -sf ${WORKSPACE}/src/userSetup.py ${WORKSPACE}/dist/${PROJECT_NAME}/scripts/userSetup.py

.PHONY : test
test:
	export PYTHONPATH=${CONDA_PREFIX}/lib/python2.7/site-packages:$PYTHONPATH && \
	${MAYAPY} ./scripts/run_maya_tests.py


.PHONY : help
help: ${MMAKE}
	${MMAKE} help