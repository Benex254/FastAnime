FROM ubuntu 
RUN apt-get update
RUN apt-get -y install python3
RUN apt-get update
RUN apt-get -y install pipx
RUN pipx ensurepath
COPY . /fastanime
WORKDIR /fastanime
RUN pipx install .
CMD ["bash"]
