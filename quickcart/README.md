# QuickCart
Small Flask + Jinja2 shopping app with receipt previews.

## Run
`docker build -t quickcart .`
`docker run --rm -p 8000:8000 quickcart`
Open `http://localhost:8000`.

Application code lives in `code/app_code/`.
Configuration uses environment variables; no secrets are stored in the repository.
