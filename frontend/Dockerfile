# 1. 建置環境 (Build Stage)
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# 開發模式直接啟動 Vite (支援熱更新)
# 如果是正式環境通常會 build 成靜態檔再用 Nginx 跑，但開發用這個最快
CMD ["npm", "run", "dev", "--", "--host"]