# flink_processor/Dockerfile

# FROM apache/flink:latest

# RUN mkdir -p /opt/flink/job
# COPY requirements.txt /opt/flink/job/
# RUN pip install --upgrade pip
# RUN pip install -r /opt/flink/job/requirements.txt
# COPY flink_processor.py /opt/flink/job/

# ENTRYPOINT ["flink", "run", "-d", "-c", "flink_processor.FlinkJob", "/opt/flink/job/flink_processor.py"]






# Use the official Apache Flink image
FROM flink:1.13.2-scala_2.12

# Add Kafka connector jar
ADD flink-sql-connector-kafka-3.1.0-1.18-sources.jar /opt/flink/lib/

# Set environment variables for Flink
ENV FLINK_HOME /opt/flink
ENV PATH $FLINK_HOME/bin:$PATH

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install Python dependencies
COPY requirements.txt /opt/flink/job/
RUN pip3 install --upgrade pip
RUN pip3 install -r /opt/flink/job/requirements.txt

# Copy the Flink processor script
COPY flink_processor.py /opt/flink/job/

# Expose ports for JobManager and TaskManager
EXPOSE 8081 8082 6123 6124

ENTRYPOINT ["flink", "run", "-d", "-c", "flink_processor.FlinkJob", "/opt/flink/job/flink_processor.py"]



