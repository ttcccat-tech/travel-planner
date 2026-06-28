FROM nginx:1.27-alpine

# 前端靜態檔
COPY web/ /usr/share/nginx/html/

# 確保前端靜態檔可被 nginx 讀取（COPY 會保留原始權限）
RUN find /usr/share/nginx/html -type f -exec chmod 644 {} \; && \
    find /usr/share/nginx/html -type d -exec chmod 755 {} \;

# 預設資料（會被 docker-compose 的匿名 volume 掛載覆寫）
COPY data/ /usr/share/nginx/html/data/

# 確保資料檔可讀
RUN find /usr/share/nginx/html/data -type f -exec chmod 644 {} \; && \
    find /usr/share/nginx/html/data -type d -exec chmod 755 {} \;

# nginx 設定
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health || exit 1