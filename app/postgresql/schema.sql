DROP TABLE IF EXISTS posts;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id              SERIAL PRIMARY KEY NOT NULL,
    username        varchar(20) UNIQUE NOT NULL,
    formatted_name  varchar(20) NOT NULL,
    password        varchar(50) NOT NULL,
    token           varchar(50),
    bio             varchar(500),
    photo           text,
    web             varchar(50),
    mail            varchar(50) NOT NULL,
    date_of_birth   date NOT NULL
);

CREATE TABLE posts (
    id              SERIAL PRIMARY KEY NOT NULL,
    user_id         INT references users(id) NOT NULL,
    publish_time    timestamp NOT NULL,
    photo           text,
    content         varchar(150) NOT NULL,
    last_edit_time  timestamp
);