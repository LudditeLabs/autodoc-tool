# Dockerfile to build autodoc-tool linux package.
#
# This image provides cx-Freeze and uses python 3.6 (built with pyenv)
#
# How to use
# ----------
#
# Build docker image:
#
#     $ docker build -t autodoc-tool-build .
#
# To override arguments you may use '--build-arg':
#
#     $ docker build -t autodoc-tool-build --build-arg pyversion=2.7.11 .
#
# Run build script:
#
#     $ docker run --rm -v /path/to/src:/project autodoc-tool-build
#
# By default result will have permissions 1000:1000, you may change that by
# passing env var UID:
#
#     $ docker run --rm -v /path/to/src:/project -e UID=1234 autodoc-tool-build
#
FROM debian:jessie-slim

ARG pyversion="3.6.6"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYENV_ROOT=/opt/pyenv
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}" \
    LANG=C.UTF-8 LC_ALL=C.UTF-8

RUN echo deb http://deb.debian.org/debian jessie-backports main contrib >> /etc/apt/sources.list

RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo git ssh-client ca-certificates curl build-essential make \
    libjpeg-dev libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libxml2-dev libxslt1-dev libyaml-dev \
    unzip flex bison && \
    # To have c11 support in cmake.
    apt-get -t jessie-backports install --no-install-recommends -y cmake

# Print a trace of simple commands.
# See https://www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html
RUN set -x

# Build su-exec (see build.sh)
RUN git clone https://github.com/ncopa/su-exec.git
RUN cd su-exec && make && cp su-exec /usr/bin && cd / && rm -rf su-exec

# Install pyenv and build python specified in 'pyversion' arg.
RUN curl -L https://raw.githubusercontent.com/yyuu/pyenv-installer/master/bin/pyenv-installer | /bin/bash
RUN PYTHON_CONFIGURE_OPTS="--enable-shared" pyenv install ${pyversion} && pyenv global ${pyversion}

### Prepare build env.

# NOTE: Install common python packages to speedup building on later steps.
RUN pip install click==6.7 docutils==0.14 PyYAML==3.13 pytest==3.7.1
RUN pip install cx_freeze==6.0b1

# Cleanup.
RUN rm -rf /root/.cache && \
    apt-get autoremove -y && sudo apt-get clean all && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get purge $(apt-cache pkgnames | grep -e "-doc")

CMD cd /project && chmod +x build.sh && ./build.sh
