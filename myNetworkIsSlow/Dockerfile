FROM python:3

WORKDIR /app
COPY requirements.txt /app/requirements.txt
# Install any needed packages specified in requirements.txt
# RUN pip install --trusted-host pypi.python.org -r requirements.txt

# COPY db/network.db /app/db/network.db

# Copy the current directory contents into the container at /app
COPY . /app


ENTRYPOINT ["/bin/bash"]
CMD ["start.sh"]
