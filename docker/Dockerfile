FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN python3 -m pip install --no-cache-dir --upgrade pip \
&& python3 -m pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . .
RUN apt-get update && apt-get install -y sudo \
    && curl -o napcat.sh https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.sh \
    && sudo bash napcat.sh \
    && nb bs -y --no-venv -a nonebot.adapters.onebot.v11 nailong \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /code/nailong
RUN nb plugin install nonebot-plugin-nailongremove
COPY ../../.env.prod /.env.prod
COPY ../..//onebot11.json /opt/QQ/resources/app/app_launcher/napcat/config/onebot11_3990547445.json
RUN xvfb-run -a qq --no-sandbox & nb run