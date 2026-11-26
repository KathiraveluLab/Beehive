import { afterEach, beforeEach, describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import SignInPage from '../SignIn';

vi.mock('@react-oauth/google', () => ({
  GoogleLogin: () => <div data-testid="google-login" />,
}));

const tokenWithRole = (role: 'admin' | 'user') =>
  `header.${btoa(JSON.stringify({ sub: 'test-user', role }))}.signature`;

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

const renderSignIn = () =>
  render(
    <MemoryRouter initialEntries={['/sign-in']}>
      <Routes>
        <Route path="/sign-in" element={<SignInPage />} />
        <Route path="/dashboard" element={<div>User Dashboard</div>} />
        <Route path="/admin" element={<div>Admin Dashboard</div>} />
      </Routes>
    </MemoryRouter>
  );

const submit = (username: string, password: string) => {
  fireEvent.change(screen.getByPlaceholderText('Enter your username'), {
    target: { value: username },
  });
  fireEvent.change(screen.getByPlaceholderText('••••••••'), {
    target: { value: password },
  });
  fireEvent.click(screen.getByRole('button', { name: 'Sign In' }));
};

describe('SignInPage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('renders the sign-in form and the Google button', () => {
    renderSignIn();

    expect(screen.getByRole('heading', { name: 'Sign In' })).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your username')).toBeInTheDocument();
    expect(screen.getByTestId('google-login')).toBeInTheDocument();
  });

  it('signs a user in, stores the token and opens the dashboard', async () => {
    const token = tokenWithRole('user');
    const fetchMock = vi.fn(async () => jsonResponse({ access_token: token }));
    vi.stubGlobal('fetch', fetchMock);
    renderSignIn();

    submit('alice', 'correct-horse');

    expect(await screen.findByText('User Dashboard')).toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBe(token);
    const [url, options] = fetchMock.mock.calls[0] as unknown as [string, RequestInit];
    expect(url).toContain('/api/auth/login');
    expect(JSON.parse(options.body as string)).toEqual({
      username: 'alice',
      password: 'correct-horse',
    });
  });

  it('opens the admin page for an admin', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => jsonResponse({ access_token: tokenWithRole('admin') }))
    );
    renderSignIn();

    submit('admin', 'correct-horse');

    expect(await screen.findByText('Admin Dashboard')).toBeInTheDocument();
  });

  it('shows the server message for wrong credentials', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => jsonResponse({ error: 'Invalid credentials' }, 401))
    );
    renderSignIn();

    submit('alice', 'wrong');

    expect(await screen.findByText('Invalid credentials')).toBeInTheDocument();
    expect(localStorage.getItem('access_token')).toBeNull();
  });

  it('shows a locked-account notice when the server answers 429', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn(async () => jsonResponse({ error: 'Account locked. Try again in 14m 59s.' }, 429))
    );
    renderSignIn();

    submit('alice', 'wrong');

    expect(await screen.findByText('Account Locked')).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByText(/Try again in 14m 59s/)).toBeInTheDocument()
    );
  });
});
