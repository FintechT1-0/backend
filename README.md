# Server README

## Overview

This repository contains a FastAPI-based server application. Follow the instructions below to set up and run the server locally.

## Requirements

* Python 3.8 or higher
* pip (Python package manager)

## Setup Instructions

1. **Download the repository**
   Clone or download the repository to your local machine.

   ```bash
   git clone <repository_url>
   ```

   or download the ZIP file and extract it.

2. **Install dependencies**
   Navigate to the project folder and install all required libraries listed in `requirements.txt`.

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**
   Open the command prompt (cmd) or terminal, navigate to the folder containing the repository, and execute the following command:

   ```bash
   uvicorn app.main:app
   ```

   By default, the server will start at:

   ```
   http://127.0.0.1:8000
   ```

4. **Access the documentation**
   Once the server is running, you can view the automatically generated API documentation at:

   ```
   http://127.0.0.1:8000/docs
   ```

## Notes

* Ensure all dependencies are installed before running the server.
* To stop the server, press `CTRL + C` in the terminal.

---
