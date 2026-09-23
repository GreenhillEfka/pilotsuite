FROM ghcr.io/home-assistant/base-python:3.14-alpine3.24-2026.06.1

ARG BUILD_VERSION="0.1.0-alpha.10"
ARG BUILD_ARCH="unknown"

LABEL \
    io.hass.version="${BUILD_VERSION}" \
    io.hass.type="app" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.name="PilotSuite" \
    io.hass.description="Explainable, policy-governed Habitus intelligence for Home Assistant" \
    io.hass.url="https://github.com/GreenhillEfka/pilotsuite" \
    org.opencontainers.image.title="PilotSuite" \
    org.opencontainers.image.description="PilotSuite v21 for Home Assistant" \
    org.opencontainers.image.source="https://github.com/GreenhillEfka/pilotsuite" \
    org.opencontainers.image.version="${BUILD_VERSION}"

WORKDIR /opt/pilotsuite

COPY requirements.txt ./requirements.txt
RUN apk add --no-cache tzdata
RUN python -c "from zoneinfo import ZoneInfo; ZoneInfo('Europe/Berlin')"
RUN pip install --no-cache-dir --requirement requirements.txt

COPY pilotsuite ./pilotsuite
COPY run.sh /run.sh
RUN chmod 0755 /run.sh

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PILOTSUITE_DATA_DIR=/data \
    PILOTSUITE_OPTIONS=/data/options.json

EXPOSE 8099

CMD ["/run.sh"]
