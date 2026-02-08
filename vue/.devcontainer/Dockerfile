FROM node:24-bullseye

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends sudo \
 && rm -rf /var/lib/apt/lists/* \
 && echo "node ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/node \
 && chmod 0440 /etc/sudoers.d/node

RUN corepack enable

# 以降は普段通り node ユーザで開発
USER node

EXPOSE 3000
