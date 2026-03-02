import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AdminRoute, UserRoute } from '../ProtectedRoutes';

vi.mock('@clerk/clerk-react', () => ({
  SignedIn: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

vi.mock('../../hooks/useAuth', () => ({
  useAuth: () => ({
    isAdmin: () => false,
    isUser: () => true,
    user: { id: 'test-user' },
  }),
}));

describe('ProtectedRoutes', () => {
  it('redirects non-admin users', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route path="/" element={<AdminRoute />} />
          <Route path="/no-access" element={<div>No Access Page</div>} />
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('No Access Page')).toBeInTheDocument();
  });

  it('renders children for authenticated user', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <Routes>
          <Route element={<UserRoute />}>
            <Route path="/" element={<div>User Content</div>} />
          </Route>
        </Routes>
      </MemoryRouter>
    );
    expect(screen.getByText('User Content')).toBeInTheDocument();
  });
});
