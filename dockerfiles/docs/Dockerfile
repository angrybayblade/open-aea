FROM ubuntu:22.04 as base
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y python3-pip git

RUN mkdir /build
WORKDIR /build
COPY docs/ /build/docs
COPY config/ /build/config

RUN python3 -m pip install "tomte[docs]==0.2.13"
RUN python3 -m pip install git+https://github.com/pugong/mkdocs-mermaid-plugin.git
RUN mkdocs build --config-file config/mkdocs.yml

WORKDIR /build/site
CMD ["python3", "-m", "http.server"]
