FROM node:17-alpine as builder
WORKDIR /app
COPY package.json .
COPY yarn.lock .
RUN yarn install
COPY . .
RUN yarn build

FROM nginx:1.19.0
WORKDIR /usr/share/nginx/html
ENV NODE_ENV production
COPY --from=builder /app/dist .
COPY nginx.conf /etc/nginx/conf.d/default/conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]