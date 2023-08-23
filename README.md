# FashionPlace
  FashionPlace Ecommerce API is a comprehensive solution for managing an online fashion store. It offers user authentication and profile management, seamless shopping cart handling, efficient order processing, and detailed product management. This API ensures secure authentication with JWT tokens and provides endpoints for essential e-commerce operations.

# Introduction
  Welcome to the FashionPlace Ecommerce API! This API is designed to provide a seamless experience for managing your online fashion store. Below are some key features and information about this API:

 * Swagger UI: Explore and interact with the API using Swagger UI. The API documentation is available at http://localhost:8000/swagger/ when running the development server.

 * JWT Authentication: To access protected endpoints, you need to obtain an access token. You can do this by logging in or signing up as a user. The access token should be included in the request headers for authentication.

# Getting Started
* Prerequisites
   Before getting started, make sure you have the following installed:

     Python
     Django
     Django REST framework
     Other dependencies (specified in requirements.txt)

# Installation
* Clone the repository:
   git clone https://github.com/Dolapur/fashionplace_ecommerce_api.git

* Navigate to the project directory:
   
   cd fashionplace_ecommerce_api

* Create and activate a virtual environment:

   python3 -m venv env
   
   source env/bin/activate  (Linux/macOS)
   
   env\Scripts\activate  (Windows)

* Install the project dependencies:
  
   pip install -r requirements.txt

* Apply database migrations:

   python3 manage.py migrate

* Create a superuser for administrative access:
   python3 manage.py createsuperuser

* Start the development server:

   python3 manage.py runserver


# Endpoints
  Access the website at http://localhost:8000/swagger


# Error Handling
  The API returns standard HTTP response codes for success and error cases. In case of an error, a JSON response will include an error field with a description of the problem.

# License
  The FashionPlace_Ecommerce_api is licensed under the MIT License - see the LICENSE file for details.

# Deployments
   The FashionPlace_Ecommerce_api is developed on vercel and the endpoints are stated below

   * API Root:
     https://fashionplace-ecommerce-api-git-main-dolapur.vercel.app/

   * Swagger Ui:
      https://fashionplace-ecommerce-api-git-main-dolapur.vercel.app/swagger

# THANKS FOR VISITING



