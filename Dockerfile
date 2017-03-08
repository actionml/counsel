FROM stackfeed/alpine

LABEL vendor=stackfeed

RUN cd /tmp && \
    apk add --no-cache \
          build-base \
          python3 \
          python3-dev \
    && \
    ln -s /usr/bin/python3 /usr/bin/python && \
    ln -s /usr/bin/python3-config /usr/bin/python-config && \
    ln -s /usr/bin/pydoc3 /usr/bin/pydoc && \
    curl -sSL https://bootstrap.pypa.io/get-pip.py | python
