-- Read local credentials from the container environment without storing them in source control.
\getenv banking_db_user BANKING_DB_USER
\getenv banking_db_password BANKING_DB_PASSWORD

-- Keep the application identity separate from the image's PostgreSQL bootstrap superuser.
CREATE ROLE :"banking_db_user"
    LOGIN
    PASSWORD :'banking_db_password'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION;

ALTER DATABASE simulated_banking_dev OWNER TO :"banking_db_user";
CREATE DATABASE simulated_banking_test OWNER :"banking_db_user";
