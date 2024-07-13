CREATE TABLE actors (
    nconst TEXT PRIMARY KEY,
    primaryname TEXT,
    birthyear INTEGER,
    deathyear INTEGER,
    primaryprofession TEXT,
    knownfortitles TEXT
);

COPY actors FROM '/docker-entrypoint-initdb.d/actors.csv' CSV HEADER;