# SHELL=/bin/bash

TARGET_VERSION ?= latest

all: docker

docker:
	docker build -t antidotelabs/netbox:$(TARGET_VERSION) .
	docker push antidotelabs/netbox:$(TARGET_VERSION)
