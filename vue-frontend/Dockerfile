FROM node:18-alpine

WORKDIR /app

COPY package.json .
# If you use pnpm or yarn, copy their lock files as well
# COPY pnpm-lock.yaml .

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
