CREATE TABLE IF NOT EXISTS rtrs (
  rtr_id INTEGER PRIMARY KEY AUTOINCREMENT,
  rtr_name varchar(60) UNIQUE NOT NULL,
  ip varchar(60) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS seps (
  sep_id INTEGER PRIMARY KEY AUTOINCREMENT,
  name varchar(60) NOT NULL,
  rtr_name varchar(60) NOT NULL,
  port varchar(60) NOT NULL,
  FOREIGN KEY (rtr_name)
    REFERENCES rtrs(rtr_name)
      ON DELETE CASCADE
      ON UPDATE NO ACTION
);