FROM jenkins/jenkins:lts

USER root

RUN apt-get update
RUN apt-get install -y unzip curl python3-pip
RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip awscliv2.zip
RUN ./aws/install
#RUN aws --version
RUN rm -rf awscliv2.zip aws
RUN pip3 install boto3 --break-system-packages
#RUN pip3 install awscli --break-system-packages
RUN curl -fsSL https://get.pulumi.com | sh
RUN ln -s /root/.pulumi/bin/pulumi /usr/local/bin/pulumi && chmod +x /usr/local/bin/pulumi && pulumi version

ENV PATH="usr/local/bin:/root/.pulumi/bin:${PATH}"

USER jenkins
