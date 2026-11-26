import { afterEach, describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { AdminRoute, UserRoute } from '../ProtectedRoutes';

// The app only reads the payload of the token, so the signature part can be anything.
const tokenWithRole = (role: 'admin' | 'user') =>
  `header.${btoa(JSON.stringify({ sub: 'test-user', role }))}.signature`;

const renderRoutes = (guard: 'admin' | 'user') =>
  render(
    <MemoryRouter initialEntries={['/']}>
      <Routes>
        <Route element={guard === 'admin' ? <AdminRoute /> : <UserRoute />}>
          <Route path="/" element={<div>Protected Content</div>} />
        </Route>
        <Route path="/sign-in" element={<div>Sign In Page</div>} />
        <Route path="/no-access" element={<div>No Access Page</div>} />
      </Routes>
    </MemoryRouter>
  );

describe('ProtectedRoutes', () => {
  afterEach(() => {
    localStorage.clear();
  });

  it('sends a visitor without a token to sign in', () => {
    renderRoutes('admin');

    expect(screen.getByText('Sign In Page')).toBeInTheDocument();
  });

  it('sends a signed-out visitor to sign in on user routes', () => {
    renderRoutes('user');

    expect(screen.getByText('Sign In Page')).toBeInTheDocument();
  });

  it('redirects non-admin users away from admin routes', () => {
    localStorage.setItem('access_token', tokenWithRole('user'));

    renderRoutes('admin');

    expect(screen.getByText('No Access Page')).toBeInTheDocument();
  });

  it('renders admin routes for an admin', () => {
    localStorage.setItem('access_token', tokenWithRole('admin'));

    renderRoutes('admin');

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('renders user routes for an authenticated user', () => {
    localStorage.setItem('access_token', tokenWithRole('user'));

    renderRoutes('user');

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });
});
