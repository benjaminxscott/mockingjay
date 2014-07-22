drop table if exists breaches;
create table breaches (
  id integer primary key autoincrement,
  submitter text not null
 -- confidence text not null
  --timestamp text not null,
  --sensitive Boolean not null, 
  --organization text not null,
  --description text not null,
  --asset text not null
);
