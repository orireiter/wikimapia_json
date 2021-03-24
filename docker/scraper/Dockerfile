# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
ADD ./requirements.txt .
RUN python -m pip install -r requirements.txt

COPY ./sleeper.sh .

WORKDIR /app
ADD ./source_code/main.py /app/
COPY ./source_code/utilities /app/utilities


# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser
CMD [ "/sleeper.sh" ]