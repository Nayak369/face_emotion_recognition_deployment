# Face Emotion Recognition - Deployment Instructions

## Project Overview

This is a complete face emotion recognition system that uses a pre-trained deep learning model to detect human emotions from facial expressions. The system can identify 7 different emotions: Angry, Disgust, Fear, Happy, Neutral, Sad, and Surprise.

## Deployment Options

### 1. Local Deployment (Recommended for Testing)

#### Prerequisites
- Python 3.7 or higher
- pip package manager

#### Installation Steps
1. Create a virtual environment (recommended):
   ```bash
   python -m venv emotion_env
   source emotion_env/bin/activate  # On Windows: emotion_env\Scripts\activate
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Access the application at `http://localhost:5000`

### 2. Docker Deployment (Recommended for Production)

#### Prerequisites
- Docker installed on your system

#### Steps
1. Create a Dockerfile in the project root:
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["python", "app.py"]
   ```

2. Create a .dockerignore file:
   ```
   __pycache__
   *.pyc
   *.pyo
   *.pyd
   .Python
   env/
   venv/
   .env
   .venv
   ```

3. Build the Docker image:
   ```bash
   docker build -t face-emotion-recognition .
   ```

4. Run the container:
   ```bash
   docker run -p 5000:5000 face-emotion-recognition
   ```

5. Access the application at `http://localhost:5000`

### 3. Cloud Deployment (Heroku)

#### Prerequisites
- Heroku CLI installed
- Heroku account

#### Steps
1. Create a Procfile in the project root:
   ```
   web: python app.py
   ```

2. Create a runtime.txt file to specify Python version:
   ```
   python-3.9.16
   ```

3. Login to Heroku:
   ```bash
   heroku login
   ```

4. Create a new Heroku app:
   ```bash
   heroku create your-app-name
   ```

5. Deploy the application:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   heroku git:remote -a your-app-name
   git push heroku master
   ```

6. Access your deployed application using the URL provided by Heroku

### 4. Cloud Deployment (AWS EC2)

#### Steps
1. Launch an EC2 instance with Ubuntu Server
2. SSH into your instance:
   ```bash
   ssh -i your-key.pem ubuntu@your-instance-public-ip
   ```

3. Update the system:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

4. Install Python and pip:
   ```bash
   sudo apt install python3 python3-pip -y
   ```

5. Install required packages:
   ```bash
   pip3 install -r requirements.txt
   ```

6. Run the application:
   ```bash
   python3 app.py
   ```

7. Configure security groups to allow inbound traffic on port 5000

### 5. Cloud Deployment (Google Cloud Platform)

#### Steps
1. Create a Google Cloud Platform account
2. Create a new project
3. Enable the Compute Engine API
4. Create a new Compute Engine instance
5. SSH into your instance
6. Install dependencies and run the application as shown in the AWS EC2 steps

## Project Structure

```
face emotion/
├── EM.h5                           # Pre-trained emotion recognition model
├── app.py                          # Flask web application for real-time emotion detection
├── emotion_recognition.py          # Standalone Python script for real-time emotion detection
├── requirements.txt                # List of required Python packages
├── README.md                       # Project documentation and usage instructions
├── run_app.bat                     # Batch file to run web application
├── run_standalone.bat              # Batch file to run standalone application
└── templates/
    └── ultimate.html               # Web interface for the Flask application
```

## Environment Variables

The application uses the following environment variables (with defaults):

- `PORT`: Port to run the application on (default: 5000)
- `DEBUG`: Enable debug mode (default: False)

To set environment variables:

Linux/Mac:
```bash
export PORT=8080
export DEBUG=False
```

Windows:
```cmd
set PORT=8080
set DEBUG=False
```

## Performance Considerations

### System Requirements
- Modern CPU with at least 4 cores recommended
- At least 4GB RAM (8GB recommended)
- Webcam for real-time detection (for local use)

### Optimization Tips
1. For production deployment, consider using a production WSGI server like Gunicorn:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. For better performance, consider using a reverse proxy like Nginx

3. For handling multiple concurrent users, consider using a load balancer

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in app.py or use a different port
2. **Memory errors**: Ensure sufficient RAM is available
3. **Camera not working**: Ensure camera permissions are granted to the application
4. **Package import errors**: Reinstall required packages using `pip install -r requirements.txt`

### Model Loading Issues
If you encounter issues with model loading:
1. Verify that `EM.h5` file is in the project directory
2. Check file permissions
3. Ensure sufficient disk space

## Security Considerations

1. For production deployment, disable debug mode
2. Use HTTPS in production
3. Implement proper input validation
4. Consider rate limiting for API endpoints
5. Regularly update dependencies

## Scaling Considerations

For handling high traffic:
1. Use a load balancer
2. Implement caching for static assets
3. Consider using a CDN
4. Use a database for storing results if needed
5. Implement proper logging and monitoring

## Maintenance

1. Regularly update dependencies
2. Monitor application performance
3. Backup the model file
4. Monitor logs for errors

## Support

For issues with the application, please check:
1. All dependencies are properly installed
2. The model file (EM.h5) is present
3. Sufficient system resources are available

Made by Satyajit