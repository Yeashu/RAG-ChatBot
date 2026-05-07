# RAG Chatbot

A Retrieval-Augmented Generation (RAG) application consisting of a FastAPI backend and a Next.js frontend.

## Structure

- `/backend` - The FastAPI server connecting to Pinecone and OpenAI.
- `/frontend` - The Next.js web application built with React and Tailwind CSS

## Getting Started

### Backend
1. Go to the `backend` directory.
2. Ensure you have the Python environment set up this project uses uv and pyproject.toml. To install dependencies run `uv sync`.
3. Copy `.example.env` to `.env` and fill in your API keys.
4. Run the server. `uv run fastapi dev`

### Frontend
1. Go to the `frontend` directory.
2. Install dependencies: `npm install`.
3. Start the development server: `npm run dev`.
