# 2. Containers

## The problem

"It works on my machine." Your laptop has one version of Python, certain
packages, certain files. The server has different ones. The app breaks there
for reasons you cannot see.

This project hit exactly that. The dashboard needed a database file that only
existed on the developer's laptop. Read the story in the
[postmortem](../runbooks/postmortem-fresh-deploy-crash.md).

## The idea

A **container** is a sealed box holding the app plus everything it needs to run:
the right Python, the right packages, the right files. The box runs the same
on your laptop, a teammate's laptop, and a cloud server.

Two words you must keep straight:

- **Image:** the blueprint. A frozen, saved copy of the box. You build it once.
- **Container:** a running box made from an image. You can start many from one
  image.

Same as a cake recipe (image) and an actual cake (container).

**Container vs virtual machine:** a virtual machine pretends to be a whole
computer, operating system included, so it is heavy and slow to start. A
container shares the host's operating system and only packs the app, so it is
small and starts in seconds.

## The Dockerfile, line by line

The recipe for the image is [`Dockerfile`](../../Dockerfile). Here is what each
part does.

| Line | What it does | Why |
|---|---|---|
| `FROM python:3.11-slim` | Start from a small ready-made image with Python 3.11 | You do not build an operating system from nothing |
| `WORKDIR /app` | Work inside the folder `/app` | A tidy known location |
| `COPY requirements.txt .` then `RUN pip install ...` | Install packages before copying your code | See "layers" below |
| `COPY . .` | Copy the rest of the project in | |
| `RUN python -m scripts.export_raw_sources ...` | Build the data and train the model while making the image | The container starts fast and never hits the fresh-deploy bug |
| `useradd ... USER app` | Run as a normal user, not the all-powerful root user | If the app is hacked, the attacker is not an admin. Least privilege. |
| `HEALTHCHECK ...` | Every 30 seconds, ask the app "are you alive?" | Docker can then mark it `unhealthy` |
| `CMD ["streamlit", "run", ...]` | The command that starts the app | |

### Layers and caching

Each line of a Dockerfile makes a **layer**. Docker saves each one and reuses it
if nothing above it changed. Packages change rarely and your code changes
constantly, so packages are installed first. Edit a code file and Docker skips
the slow `pip install`. Put them the other way round and every tiny edit
reinstalls everything.

### Files that stay out

[`.dockerignore`](../../.dockerignore) lists what must not be copied into the
image: `.git`, `.env` (secrets), `data/`, and so on. Same idea as `.gitignore`.

## docker-compose

Typing long `docker run` commands is painful.
[`docker-compose.yml`](../../docker-compose.yml) writes the settings down once:
which image, which port, which environment variables, that the filesystem is
read-only. `docker compose up` then does it all.

## Try it

You need Docker Desktop open with the engine running.

```bash
docker build -t ai-data-analyst:local .     # build the image (a few minutes the first time)
docker images                                # you should see ai-data-analyst listed
docker compose up                            # start the dashboard, open http://localhost:8501
```

In a second terminal while it runs:

```bash
docker ps                                    # a running container, look for (healthy)
docker logs <container name>                 # what the app printed
docker exec -it <container name> sh          # step inside the box, type "whoami" (answer: app, not root), then "exit"
docker compose run --rm healthcheck          # run the project's health check inside a fresh container
docker compose down                          # stop and remove it
```

**Break it on purpose.** In the Dockerfile, move `COPY . .` above
`RUN pip install`. Build twice, editing a README line between builds. Watch the
second build reinstall every package. Undo the change.

## Check yourself

- Image or container: which one is running?
- Why is `pip install` before `COPY . .`?
- Why run as a non-root user?
- What bug did baking the data into the image prevent?
