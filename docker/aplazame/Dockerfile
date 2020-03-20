# Get the last python image version and update all the repositories
FROM python
RUN apt-get update && apt-get install -y wget && apt-get clean

# Install dockerize to avoid startup problems (waiting for DB to start)
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz -O - | tar -C /usr/local/bin -xzv

# Set the external path for the docker container
ARG PROJECT_EXTERNAL_PATH=src/

# Prepare work directory
RUN mkdir aplazame_mgc
WORKDIR aplazame_mgc

# Install all the requirements
ADD ${PROJECT_EXTERNAL_PATH}/requirements.txt /aplazame_mgc/
RUN pip install --upgrade pip && pip install -r requirements.txt

##Load source code from the repository or local to the container
COPY ${PROJECT_EXTERNAL_PATH}/ /aplazame_mgc/

# Load executors
COPY docker/aplazame/post_deploy.sh \
     docker/aplazame/pre_deploy.sh \
     docker/celery/run_celery.sh docker/celery/run_worker.sh \
     docker/celery/docker_entrypoint.sh \
     /aplazame_mgc/

