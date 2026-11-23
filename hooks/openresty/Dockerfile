FROM openresty/openresty:alpine-fat

ENV TZ=UTC

RUN luarocks install lua-resty-http
RUN luarocks install lua-resty-openssl

COPY nginx.conf /usr/local/openresty/nginx/conf/
COPY lua /usr/local/openresty/lualib/ipxa

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/ || exit 1

CMD ["openresty", "-g", "daemon off;"] # nosemgrep: dockerfile.security.missing-user.missing-user