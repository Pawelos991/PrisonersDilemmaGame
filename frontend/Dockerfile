FROM node:17-alpine
WORKDIR /app
COPY package.json .
COPY yarn.lock .
RUN yarn install
COPY . .
RUN yarn build
CMD [ "npx", "serve", "./dist" ]