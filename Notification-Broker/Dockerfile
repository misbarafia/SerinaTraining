FROM openjdk:8-jre-alpine
RUN wget -O activemq.tar.gz http://archive.apache.org/dist/activemq/5.15.6/apache-activemq-5.15.6-bin.tar.gz 
RUN tar -xzf activemq.tar.gz
COPY mysql-connector-java-8.0.27.jar apache-activemq-5.15.6/lib/lib/optional
COPY activemqauthenticate.jar apache-activemq-5.15.6/lib
COPY activemq.xml apache-activemq-5.15.6/conf
CMD ["apache-activemq-5.15.6/bin/activemq", "console"]