drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  timestamp integer NOT NULL,
  value integer NOT NULL
);
