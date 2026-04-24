FROM openresty/openresty:alpine-fat

RUN luarocks install lua-resty-http
RUN luarocks install lua-resty-openssl

COPY nginx.conf /usr/local/openresty/nginx/conf/
COPY lua /usr/local/openresty/lualib/ipxa

EXPOSE 80

CMD ["openresty", "-g", "daemon off;"]