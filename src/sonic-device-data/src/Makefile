.ONESHELL:
SHELL = /bin/bash
.SHELLFLAGS += -e

test:
	# Execute Broadcom config file test
	pushd ../tests/
	for f in $$(find ../../../device -name "*.config.bcm"); do
		./config_checker $$f
	done
	for f in $$(find ../../../device -name media_settings.json); do
	    ./media_checker $$f
	done
	popd
