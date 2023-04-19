FROM python:3.7-alpine


#RUN apk update
#RUN apk add git
RUN mkdir app
#RUN git clone https://github.com/yaylinda/delete-tweets.git app
COPY pyviera/ app
WORKDIR app
RUN pip install -r requirements.txt
ENTRYPOINT ["python3", "viera.py"]