# Quiz App

A Flask-based quiz application for creating and taking quizzes with flashcards.

## Features

- Create folders to organize quizzes
- Add quizzes with terms and definitions
- Take multiple-choice quizzes
- View results with incorrect answers highlighted

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `python app.py`

The app will open in your browser at http://127.0.0.1:5000/

## Deployment

This app is configured for Vercel deployment using `vercel.json` and the Python runtime.

To deploy:

1. Install the Vercel CLI: `npm install -g vercel`
2. Run `vercel login`
3. Run `vercel` from the project folder

## Usage

- Create folders for different subjects
- In each folder, create quizzes
- Add terms and definitions to quizzes
- Take quizzes to test your knowledge