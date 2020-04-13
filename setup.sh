# Setupscript to pull, build and deploy a Dockerized app straight from github
# Requires GIT and Docker to be installed on the host-system
# By Jan Macenka (2019-07-19)

# Specify your project-parameters
PROJECT_GIT=jmacenka/dash-covid-19-visualization # Specify the github-path to the project e.g. user/project will lead to https://github.com/user/project.git
FOLDER_NAME=app

# Check if app folder already exists, if so just rebuild and redeploy the container
if [ -e ./.git ]; then
    echo "Now: Repository already locally cloned, rebuilding all all containers."
else
    echo "Now: Pulling project from github"
    git clone https://github.com/$PROJECT_GIT.git $FOLDER_NAME && cd $FOLDER_NAME
fi
source .env
echo "Now: Building the docker images and starting the containers for $APPLICATION_NAME"
docker-compose up -d --build
echo "All Done, Containers are up and running. Visite http://$(hostname -I | cut -d' ' -f1):$PUBLISHED_PORT"