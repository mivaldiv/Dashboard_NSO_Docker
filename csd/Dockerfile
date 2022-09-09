
FROM ubuntu:latest

WORKDIR /home/csd

ADD requirements.txt .
ADD service_priority.csv .
ADD app.py .
ADD script_modules /home/csd/script_modules
#Here we added the python file that we want to run in docker and define its location.

RUN apt-get update -y
RUN apt-get install python3 -y
RUN apt-get install pip -y
RUN pip install -r requirements.txt
#Here we installed the dependencies, we are using the pygame library in our main.py file so we have to use the pip command for installing the library
#CMD [ "python", "script_modules/main.py" ]
CMD [ "python3", "app.py" ]
#lastly we specified the entry command this line is simply running python ./main.py in our container terminal