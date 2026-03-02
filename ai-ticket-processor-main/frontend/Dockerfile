FROM node:18-alpine

WORKDIR /app

COPY package.json /app/package.json
# Copiar package-lock si existe; si no, continuar sin error
COPY package-lock.json* /app/
RUN npm install

COPY . /app

EXPOSE 5200

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5200"]
