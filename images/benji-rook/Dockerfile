FROM rook/toolbox:v0.7.1 AS build

# For the Git checkout
ARG CEPH_VERSION="12.2.7"

# If you change VENV_PATH you also need to change the paths in 
# images/common/benji-wrapper and images/common/bashrc
ENV VENV_PATH /benji

RUN apt-get update && \
	apt-get upgrade -y -q && \
	apt-get install -y -q --force-yes --no-install-recommends software-properties-common python-software-properties && \
	add-apt-repository -y ppa:deadsnakes/ppa && \
	apt-get update && \
	apt-get install  -y -q --force-yes --no-install-recommends python3.6 python3.6-venv python3.6-dev git gcc && \
	apt-get install -y -q --force-yes --no-install-recommends librados2 librbd1 librados-dev librbd-dev

RUN python3.6 -m venv $VENV_PATH && \
	ln -s /usr/bin/python3.6-config $VENV_PATH/bin/python-config && \
	. $VENV_PATH/bin/activate && \
	pip install --upgrade 'pip==10.0.*' && \
	sed -i "s|self.run_command(\['clone', '-q', url, dest\])|self.run_command(['clone', '--depth=1', '--branch', rev if rev else 'master', '-q', url, dest])|" $(python -c 'import site; print(site.getsitepackages()[0])')/pip/_internal/vcs/git.py

RUN . $VENV_PATH/bin/activate && \
	pip install cython && \
	pip install "git+https://github.com/ceph/ceph@v$CEPH_VERSION#subdirectory=src/pybind/rados" && \
	pip install "git+https://github.com/ceph/ceph@v$CEPH_VERSION#subdirectory=src/pybind/rbd"

ADD . /benji-source/
RUN . $VENV_PATH/bin/activate && \
	pip install --process-dependency-links '/benji-source/[encryption,compression,s3,readcache,b2]'

FROM rook/toolbox:v0.7.1 AS runtime

ARG VCS_REF
ARG VCS_URL
ARG VERSION 
ARG BUILD_DATE

LABEL org.label-schema.schema-version="1.0" \
      org.label-schema.vcs-ref="$VCS_REF" \
      org.label-schema.vcs-url="$VCS_URL" \
      org.label-schema.build-date="$BUILD_DATE" \
      org.label-schema.version="$VERSION" \
      org.label-schema.url="https://benji-backup.me/"

ARG GO_CRON_VERSION="0.0.7"

ENV SCRIPTS_PATH /scripts

RUN apt-get update && \
	apt-get upgrade -y -q && \
	apt-get install -y -q --force-yes --no-install-recommends software-properties-common python-software-properties && \
	add-apt-repository -y ppa:deadsnakes/ppa && \
	apt-get update && \
	apt-get install -y -q --force-yes --no-install-recommends python3.6 python3.6-dev && \
	apt-get install -y -q --force-yes --no-install-recommends librados2 librbd1 && \
	apt-get install -y -q --force-yes --no-install-recommends bash-completion joe && \
	rm -rf /var/lib/apt/lists/*

COPY --from=build $VENV_PATH/ $VENV_PATH/
COPY scripts/ $SCRIPTS_PATH/
COPY images/benji-rook/scripts/backup.sh $SCRIPTS_PATH/backup.sh
COPY images/benji-rook/docker-entrypoint.sh /docker-entrypoint.sh
COPY etc/benji-minimal.yaml /etc/benji/benji.yaml
COPY images/common/benji-wrapper /usr/bin/benji
COPY images/common/bashrc /root/.bashrc

RUN curl -sSL -o /go-cron-linux.gz https://github.com/odise/go-cron/releases/download/v$GO_CRON_VERSION/go-cron-linux.gz && \
	ls -al go-cron-linux.gz && \
	gunzip /go-cron-linux.gz && \
	curl -o /usr/bin/kubectl -sSL https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl && \
	chmod a+x $SCRIPTS_PATH/backup.sh /docker-entrypoint.sh /go-cron-linux /usr/bin/kubectl /usr/bin/benji

ENTRYPOINT ["/docker-entrypoint.sh"]
