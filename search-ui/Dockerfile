FROM node:18 AS build

WORKDIR /app

# copy all pkg files and install dependencies
COPY app-search-reference-ui-react-master/package*.json ./
COPY app-search-reference-ui-react-master/ ./

RUN npm install

#COPY app-search-reference-ui-react-master/ /app

RUN npm run build

FROM nginx:stable-alpine
COPY --from=build /app/build /usr/share/nginx/html

# default nginx port
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
