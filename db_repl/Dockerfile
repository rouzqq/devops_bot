FROM postgres:14

RUN echo "#!/bin/bash" > /usr/local/bin/init.sh && \
    echo "rm -rf /var/lib/postgresql/data/*" >> /usr/local/bin/init.sh && \
    echo "until pg_basebackup -h db -R --slot=replication_slot --pgdata /var/lib/postgresql/data ; do" >> /usr/local/bin/init.sh && \
    echo "  echo 'Replica not ready, trying again...'" >> /usr/local/bin/init.sh && \
    echo "  sleep 1" >> /usr/local/bin/init.sh && \
    echo "done" >> /usr/local/bin/init.sh && \
    echo "chown -R postgres:postgres /var/lib/postgresql/data" >> /usr/local/bin/init.sh && \
    echo "chmod 700 /var/lib/postgresql/data" >> /usr/local/bin/init.sh && \
    echo "su - postgres -c 'exec /usr/lib/postgresql/14/bin/postgres -D /var/lib/postgresql/data'" >> /usr/local/bin/init.sh

RUN chmod +x /usr/local/bin/init.sh

CMD ["/usr/local/bin/init.sh"]