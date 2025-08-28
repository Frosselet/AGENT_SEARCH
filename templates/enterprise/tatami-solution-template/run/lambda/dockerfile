FROM docker.binrepo.cglcloud.in/tatami-image-lambda-python-daf:1-stable

ARG HTTPS_PROXY

ENV HTTP_PROXY=${HTTPS_PROXY:+${HTTPS_PROXY}}
ENV HTTPS_PROXY=${HTTPS_PROXY:+${HTTPS_PROXY}}

COPY ./requirements.txt ./requirements.txt
RUN python3 -m pip install --ignore-installed --no-cache-dir -r requirements.txt
COPY ./ ./

# Reset proxy

ENV AWS_CA_BUNDLE="${HTTPS_PROXY:+${AWS_CA_BUNDLE}}"
ENV REQUESTS_CA_BUNDLE="${HTTPS_PROXY:+${REQUESTS_CA_BUNDLE}}"
ENV HTTP_PROXY="${HTTPS_PROXY:+${HTTP_PROXY}}"
ENV HTTPS_PROXY="${HTTPS_PROXY:+${HTTPS_PROXY}}"
