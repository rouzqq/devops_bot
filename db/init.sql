CREATE USER repl_user WITH REPLICATION ENCRYPTED PASSWORD '1111';
SELECT 'CREATE DATABASE bd_emails_and_numphones'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'bd_emails_and_numphones');
CREATE TABLE emails(
id SERIAL PRIMARY KEY,
email VARCHAR(255)
);
CREATE TABLE numbersphone(
id SERIAL PRIMARY KEY,
number VARCHAR(255)
);

INSERT INTO emails(email) VALUES ('avatar@mail.ru');
INSERT INTO numbersphone(number) VALUES ('89008007766');

SELECT pg_create_physical_replication_slot('replication_slot');
CREATE TABLE hba ( lines text );
COPY hba FROM '/var/lib/postgresql/data/pg_hba.conf';
INSERT INTO hba (lines) VALUES ('host replication all 0.0.0.0/0 md5');
COPY hba TO '/var/lib/postgresql/data/pg_hba.conf';
SELECT pg_reload_conf();