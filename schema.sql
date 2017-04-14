drop table if exists contents;
create table contents (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);