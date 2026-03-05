# Web Application Exercise

A little exercise to build a web application following an agile development process. See the [instructions](instructions.md) for more detail.

## Product vision statement

We developed an application that allows developers and stakeholders to easily identify the completion of tasks in a project.

## User stories

See user stories [here](https://github.com/swe-students-spring2026/2-web-app-copper_cheetahs/issues).

## Steps Necessary to Run the Software

### Run with Docker

#### 0. Prerequisites
Before running the application, make sure you have the following installed:

- **Git**
- **Docker Desktop**

Download Docker here: https://www.docker.com/get-started/

Make sure Docker Desktop is running before you continue.

#### 1. Clone the Repository (Using VS Code)

1. Open **Visual Studio Code**.
2. Click **Source Control** in the left sidebar or press `Ctrl + Shift + G`.
3. Click **Clone Repository**.
4. Paste the repository URL:

```
https://github.com/swe-students-spring2026/2-web-app-copper_cheetahs.git
```

5. Choose a folder on your computer where the project will be saved.
6. Once cloning finishes, click **Open** to open the project in VS Code.

After opening the project, open a terminal in VS Code:

Make sure you are inside the project folder:

```bash
cd 2-web-app-copper_cheetahs
```

#### 2. Configure Environment Variables

Create a `.env` file in the **project root directory** (the same folder that contains `docker-compose.yml`).

Copy the contents under `optional docker` from the `env.example` file.

#### 3. Start the Application

Make sure **Docker Desktop is running**, then run in terminal:

```bash
docker compose up --build
```

#### 4. Open the Application

Once the containers are running, open a browser and go to:

```
http://localhost:5001
```

Because the `docker-compose.yml` file maps Host port 5001 to Container port 5000

#### If you encounter a port conflict

If you see an error indicating that port **5001 is already in use**, you can change the host port in the `docker-compose.yml` file.

Find the following line in the `flask-app` service:

```yaml
ports:
  - "5001:5000"
```

Change the first number (the host port) to another available port, for example:

```yaml
ports:
  - "10000:5000"
```

Then restart the containers:

```bash
docker compose down
docker compose up --build
```

You would then access the application at:

```
http://localhost:10000
```

#### 5. Stop the Application

To stop the running containers:

```
Ctrl + C
```

Then optionally run:

```bash
docker compose down
```

to fully stop and remove the containers.

#### 6. Restart the Application

If the containers were stopped previously, restart them with:

```bash
docker compose up
```

Use `--build` again if you modified dependencies or Dockerfiles.

## Task boards

See task board sprint 1 [here](https://github.com/orgs/swe-students-spring2026/projects/26/views/2).
See task board sprint 2 [here](https://github.com/orgs/swe-students-spring2026/projects/79/views/2)
