FROM nginx:1.27-alpine

# 初始化資料（會被 docker-compose 的匿名 volume 掛載覆寫）
COPY data/ /usr/share/nginx/html/data/

# nginx 設定
COPY docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost/health || exit 1