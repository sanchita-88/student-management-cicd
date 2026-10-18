# Student Management System with CI/CD

A small CRUD web application for managing student records. Flask serves the interface, PostgreSQL stores the records, Docker packages the app, and GitHub Actions builds the image and triggers a Render deployment.

## Features

- Add, list, edit, and remove student records
- Validate required fields, study year, and duplicate email addresses
- Responsive interface
- PostgreSQL in Docker Compose for local development
- GitHub Actions workflow for container build and deployment trigger
- Render deployment configuration

## Run it locally

You need Docker Desktop with Docker Compose. From this folder, run:

```sh
docker compose up --build
```

Open [http://localhost:8000](http://localhost:8000). Add a student, edit the record, and remove it to see the CRUD flow. Stop the app with `Ctrl+C`. Data stays in the `postgres_data` Docker volume; remove it with `docker compose down -v` only if you want to erase your local records.

To change local secrets, copy `.env.example` to `.env` and set `POSTGRES_PASSWORD` and `SECRET_KEY` to your own values. Keep `.env` private and never commit it.

## Deploy with GitHub Actions and Render

1. Create a GitHub repository and push this project to its `main` branch.
2. In Render, create a PostgreSQL database. Copy its **internal connection string** for a web service in the same region (or the external string if the database is hosted elsewhere).
3. In Render, create a Web Service from the GitHub repository. Select Docker as the runtime and turn off automatic deploys. Set `DATABASE_URL` to the PostgreSQL connection string and set `SECRET_KEY` to a long random value.
4. In the Render service settings, create a deploy hook and copy its URL.
5. In the GitHub repository, open **Settings → Secrets and variables → Actions** and add a repository secret named `RENDER_DEPLOY_HOOK` with that URL.
6. Push a commit to `main`, or run **Actions → Build and deploy → Run workflow**. The workflow builds the container image first, then triggers Render to build and deploy the commit. The first deployment may take a few minutes.

The Render database is a separate service. Its plan, storage, and retention depend on the current choices in your Render account. Check those settings before using real student data. The checked-in `render.yaml` is a starting point; you can also create the service in the Render dashboard and set the same environment variables there.

## How the pipeline works

`.github/workflows/deploy.yml` runs on pushes to `main` and manual dispatches. The `build` job checks out the source and builds the Docker image. Only after that succeeds, the `deploy` job calls the Render deploy hook. GitHub secrets keep the hook URL out of the repository.

## Project structure

```text
app.py                         Flask routes, form validation, and database model
templates/                     HTML pages
static/style.css               Responsive styling
Dockerfile                     Production container image
compose.yaml                   Local web app and PostgreSQL services
render.yaml                    Render service starting point
.github/workflows/deploy.yml   Build and deploy workflow
```
