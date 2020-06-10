drop table if exists Post;
drop table if exists Author;

create table Author (
    id int auto_increment,
    blogger_id int,
    gender varchar(32),
    age int,
    industry varchar(64),
    astro_sign varchar(32),
    constraint pk_Author primary key (id)
);

create table Post (
    id int auto_increment,
    author_id int not null,
    publish_date date,
    bucket_path varchar(128),
    sentiment_score Float,
    sentiment_magnitude Float,
    constraint pk_Post primary key (id),
    constraint fk_Post_Author foreign key (author_id) references Author(id)
);