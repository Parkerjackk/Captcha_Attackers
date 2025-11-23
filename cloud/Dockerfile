FROM ubuntu:22.04

# Install base tools
RUN apt-get update && \
    apt-get install -y wget curl unzip gnupg python3 python3-pip && \
    apt-get install -y libxss1 libappindicator3-1 libindicator7 libgbm1 \
                       libasound2 libnss3 libgtk-3-0 libxrandr2 libxdamage1 \
                       libxcomposite1 libxcursor1 libx11-xcb1 libxext6 \
                       libxi6 libxtst6 libxinerama1 libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

# ---- NEW: Download Chrome for Testing (CFT) + matching driver ----
RUN CFT_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json | \
    python3 -c "import sys,json; print(json.load(sys.stdin)['channels']['Stable']['version'])") && \
    echo Using Chrome version: $CFT_VERSION && \
    wget -O chrome.zip https://storage.googleapis.com/chrome-for-testing-public/$CFT_VERSION/linux64/chrome-linux64.zip && \
    wget -O chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/$CFT_VERSION/linux64/chromedriver-linux64.zip && \
    unzip chrome.zip && unzip chromedriver.zip && \
    mv chrome-linux64 /opt/chrome && \
    mv chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf chrome.zip chromedriver.zip chromedriver-linux64

# Add Chrome to PATH
ENV PATH="/opt/chrome:$PATH"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "tls_server:app", "--host", "0.0.0.0", "--port", "8000"]
