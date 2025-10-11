# Beehive Frontend

This folder contains the frontend for the Beehive platform where users can upload images and voice notes, while admins can view, analyze, and manage media content via an admin portal.

## Features

- User Authentication with Clerk
- Image and Voice Note Upload
- Media Gallery with Edit and Delete Functionality
- Admin Dashboard with Analytics
- User Management
- Dark/Light Mode Support
- Responsive Design

## Tech Stack

- React with TypeScript
- Vite for Build Tool
- Clerk for Authentication
- Tailwind CSS for Styling
- React Router for Navigation
- React Icons and Heroicons


## Project Structure

```
src/
├── components/     # Reusable UI components
├── context/       # React context providers
├── hooks/         # Custom React hooks
├── layouts/       # Page layout components
├── pages/         # Page components
│   ├── admin/     # Admin-specific pages
│   └── auth/      # Authentication pages
├── types/         # TypeScript type definitions
└── utils/         # Utility functions
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build locally
