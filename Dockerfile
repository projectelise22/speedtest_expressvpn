# Create debian container with speedtest-cli and expressvpn installed
# --platform added since host is running at arm64 and expressvpn only supports amd64 installers
FROM --platform=linux/amd64 debian:bullseye

# Set environment variables
ENV ACTIVATION_CODE Code
ENV LOCATION smart
ENV PREFERRED_PROTOCOL auto
ENV LIGHTWAY_CIPHER auto

ARG APP=expressvpn_3.82.0.2-1_amd64.deb

# Install speedtest dependencies
RUN apt-get update && apt-get install -y curl jq gnupg1 apt-transport-https dirmngr \
    libterm-readkey-perl ca-certificates iputils-ping net-tools iproute2 wget expect \
    python3 python3-pip

# Download and install ExpressVPN
RUN wget "https://www.expressvpn.works/clients/linux/${APP}" -O /tmp/${APP} \
    && dpkg -i /tmp/${APP} \
    && rm -rf /tmp/*.deb \
    && apt-get purge -y --auto-remove wget

# Download and install speedtest-cli
RUN apt-get update && apt-get install -y speedtest-cli

# Install pytest
RUN pip3 install --no-cache-dir pytest

# Copy script files to the container
COPY /util/. /util/.
COPY entrypoint.sh /tmp/entrypoint.sh
COPY expressvpnActivate.sh /tmp/expressvpnActivate.sh

WORKDIR /util

# Run entrypoint script
ENTRYPOINT ["/bin/bash", "/tmp/entrypoint.sh"]
