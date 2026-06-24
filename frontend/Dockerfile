FROM node:22-alpine AS build

WORKDIR /app

COPY frontend/package.json ./
RUN npm install

COPY frontend/ .

ARG VITE_API_BASE_URL=/api
ARG VITE_WS_BASE_URL=
ARG VITE_ENABLE_WEBSOCKETS=true

ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL
ENV VITE_ENABLE_WEBSOCKETS=$VITE_ENABLE_WEBSOCKETS

RUN npm run build

FROM nginx:1.27-alpine

COPY --from=build /app/dist /usr/share/nginx/html
COPY docker/nginx/frontend.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
