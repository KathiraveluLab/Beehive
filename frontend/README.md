# Beehive

Beehive is a platform where users can upload images and voice notes, while admins can view, analyze, and manage media content via an admin portal.

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

## Getting Started

1. Clone the repository:
```bash
git clone https://github.com/yourusername/beehive.git
cd beehive
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file in the root directory and add your Clerk publishable key:
```
VITE_CLERK_PUBLISHABLE_KEY=your_clerk_publishable_key_here
```

4. Start the development server:
```bash
npm run dev
```

5. Open [http://localhost:5173](http://localhost:5173) to view the app in your browser.

## Environment Setup

1. Sign up for a Clerk account at [https://clerk.dev](https://clerk.dev)
2. Create a new application in Clerk
3. Copy your publishable key from the Clerk dashboard
4. Add the key to your `.env` file

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

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
