# Setup PostgreSQL Local Database for User Accounts

1. Connect to port 5433 on PostgreSQL using `psql -h localhost -p 5433 -U postgres`
2. Once connected run these commands:

```
CREATE DATABASE basketify;
CREATE USER basketify_user WITH PASSWORD 'your_password';
GRANT ALL ON SCHEMA public TO basketify_user;
GRANT ALL ON DATABASE basketify TO basketify_user;
ALTER USER basketify_user WITH SUPERUSER;
GRANT ALL PRIVILEGES ON DATABASE basketify TO basketify_user;
\q
```

3. Create an .env file with the following:

```
   DB_NAME=basketify
   DB_USER=basketify_user
   DB_PWD=your_password
   DB_HOST=localhost
   DB_PORT=5433
```
