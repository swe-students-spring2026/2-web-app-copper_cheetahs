# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

We developed an application that allows developers and stakeholders to easily identify the completion of tasks in a project.

## User stories

See user stories [here](https://github.com/swe-students-spring2026/2-web-app-copper_cheetahs/issues).

## Steps necessary to run the software

### Run with Docker

#### 1 Configure environment variables

- Create a `.env` file in the project root (same folder as
`docker-compose.yml`).

- Copy the contents under 'optional docker' from the example file.

#### 2 Start services

- Type `docker compose up --build` in terminal.

#### 3 Open the app

- Go to: http://localhost:5001
- (`docker-compose.yml` maps host port **5001** to container port **5000**.)

#### 4 Stop services

- Use ctrl c to stop services.

## Task boards

See task board [here](https://github.com/orgs/swe-students-spring2026/projects/26/views/2).
