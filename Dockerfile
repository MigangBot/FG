FROM python:3.8-slim-bullseye

# 设置语言
ENV LANG=zh_CN.UTF-8 LC_ALL=zh_CN.UTF-8

COPY . /app

WORKDIR /app

# 安装依赖
RUN apt-get update \
  && apt-get -y upgrade \
  && apt-get install -y --no-install-recommends curl locales fontconfig fonts-noto-cjk fonts-noto-color-emoji build-essential \
  && localedef -i zh_CN -c -f UTF-8 -A /usr/share/locale/locale.alias zh_CN.UTF-8 \
  && fc-cache -fv \
  && pip install --no-cache-dir --upgrade -r requirements.txt \
  && apt-get purge -y --auto-remove \
  && rm -rf /var/lib/apt/lists/* \
  && rm /app/requirements.txt

CMD python bot.py