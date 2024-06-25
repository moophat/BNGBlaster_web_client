FROM python:3.10.12-slim

RUN apt-get update -y \
    && apt-get install -y --no-install-recommends libc6-dev make dpkg-dev git openssh-client iputils-ping vim sqlite3 net-tools\
    && apt-get clean all \
    && rm -rf /var/cache/apt/archives /var/lib/apt/lists/*

#########git clone#########

# # Clone the conf files into the docker container
RUN /usr/bin/git clone --branch main https://github.com/moophat/BNGBlaster_web_client.git

########done git clone#########

WORKDIR /BNGBlaster_web_client
COPY default_variable.yml /root/default_variable.yml 
ENV STREAMLIT_CONFIG="/root/default_variable.yml"
COPY entrypoint.sh /root/entrypoint.sh
RUN ["chmod", "+x", "/root/entrypoint.sh"]

COPY ./requirements.txt /tmp/requirements.txt

RUN pip install -r /tmp/requirements.txt --no-cache-dir

# RUN rm -rf /BNGBlaster_web_client
EXPOSE 8505
ENTRYPOINT [ "/root/entrypoint.sh" ]
CMD ["/bin/bash"]
