# AIZEN: A Full-Stack Generative AI Platform

AIZEN is an innovative full-stack web application leveraging generative AI technologies to offer a suite of functionalities, including text-to-image generation, text summarization, and more. This platform is designed to demonstrate the capabilities of advanced AI models in real-world applications, providing users with intuitive and powerful tools.

## Features

### Home Page
AIZEN's home page presents a clean and responsive interface, enhanced with a user-friendly navigation bar. The "Tools" dropdown menu provides quick access to key features, including Text-to-Image and Text Summarization tools. The footer contains links to social media, contact information, and additional resources, creating a comprehensive and professional homepage.

### Text-to-Image
This feature allows users to generate images from textual prompts using state-of-the-art models like Stable Diffusion. The integration with Hugging Face's inference API ensures real-time image generation, providing users with immediate visual representations of their textual inputs.

### Text Summarization
AIZEN leverages advanced, fine-tuned models for efficient text summarization. By accessing these models through an API, the platform handles large model sizes and API limits, ensuring robust and scalable summarization capabilities for users.

### Authentication System
AIZEN provides a secure authentication system that includes user registration, login, and email verification via OTP. Passwords are securely hashed using bcrypt, and user sessions are maintained across different pages to ensure a secure and seamless experience.

### Data Handling with SQL
The platform integrates with MySQL for robust database management, securely storing user data and application states. By using prepared statements, AIZEN prevents SQL injection attacks, maintaining data integrity and security.

## Getting Started

### Clone the Repository
```sh
git clone https://github.com/yourusername/aizen.git
```

### Install Dependencies:
```sh
pip install -r requirements.txt
```

###Set Up Environment Variables: 
Configure your .env file with necessary environment variables.

###Run the Application:
```sh
flask run
```
