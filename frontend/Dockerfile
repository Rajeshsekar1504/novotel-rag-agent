# Stage 1 — Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm ci

COPY . .

RUN npm run build


# Stage 2 — Production runtime (lightweight)
FROM node:18-alpine

WORKDIR /app

# install lightweight static server
RUN npm install -g serve

# copy built frontend from builder
COPY --from=builder /app/dist /app/dist

EXPOSE 5173

CMD ["serve", "-s", "dist", "-l", "5173"]