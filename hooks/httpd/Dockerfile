FROM rockylinux:9-minimal

ENV TZ=UTC

RUN microdnf install -y \
    ca-certificates epel-release \
    && microdnf install -y httpd mod_lua lua-socket \
    && microdnf clean all

COPY lua/ /etc/httpd/lua/
COPY conf.d/ /etc/httpd/conf.d/

EXPOSE 80

CMD ["/usr/sbin/httpd", "-D", "FOREGROUND"]