# ビルド環境
FROM node:24-bullseye as build-stage
WORKDIR /app
COPY package*.json ./

RUN corepack enable

RUN pnpm install
COPY . .
RUN pnpm run build

# 本番環境
FROM nginx:stable-alpine as production-stage
COPY nginx.conf /etc/nginx/nginx.conf
COPY --from=build-stage /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]