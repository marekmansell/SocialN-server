DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS posts;

CREATE TABLE users (
    id              SERIAL PRIMARY KEY NOT NULL,
    username        varchar(20) UNIQUE NOT NULL,
    formatted_name  varchar(20) NOT NULL,
    password        varchar(50) NOT NULL,
    bio             varchar(500),
    photo           varchar(20),
    web             varchar(50),
    mail            varchar(50) NOT NULL,
    date_of_birth   date NOT NULL
);

CREATE TABLE posts (
    id              SERIAL PRIMARY KEY NOT NULL,
    user_id         INT references users(id) NOT NULL,
    publish_time    timestamp NOT NULL,
    photo           varchar(20),
    content         varchar(150) NOT NULL,
    last_edit_time  timestamp
);