# Use Python 3.12 as the base image
FROM python:3.12-bookworm

# Define build-time arguments
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create user and group
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

# Set environment variables
ENV PYTHONUSERBASE=/home/$USERNAME/.local
ENV PATH=$PYTHONUSERBASE/bin:$PATH

# Switch to the user
USER $USERNAME

# Set working directory
WORKDIR /workspace

# Install necessary packages
RUN pip install --user --upgrade pip setuptools poetry

# Copy source code
COPY --chown=$USERNAME:$USERNAME . /workspace

# Install dependencies
RUN poetry config virtualenvs.create true \
    && poetry install --no-dev --no-interaction --no-ansi

# Run the application
CMD ["poetry", "run", "chainlit", "run", "src/main.py"]
