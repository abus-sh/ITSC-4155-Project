FROM node:20.14

RUN ["npm", "install", "-g", "typescript"]
RUN ["npm", "install", "-g", "@angular/cli"]

WORKDIR "/app"

# Copy files for building
COPY "./tsconfig.json" "."
COPY "./package.json" "."
COPY "./package-lock.json" "."
COPY "./tsconfig.app.json" "."
COPY "./tsconfig.spec.json" "."
COPY "./angular.json" "."

RUN ["npm", "install", "--save-prod"]

RUN --mount=type=bind,source="./src",target="/app/src" ["ng", "build"]

FROM nginx:1.27

COPY --from=0 --chown=nginx:nginx "/app/dist/frontend/browser" "/app"
COPY "./nginx/nginx.conf" "/etc/nginx/nginx.conf"
COPY "./nginx/default.conf" "/etc/nginx/conf.d/default.conf"
