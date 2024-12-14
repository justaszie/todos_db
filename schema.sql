CREATE TABLE lists(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL UNIQUE
);

CREATE TABLE todos(
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    completed boolean NOT NULL DEFAULT false,
    list_id INT NOT NULL
                REFERENCES lists(id)
                ON DELETE CASCADE
);