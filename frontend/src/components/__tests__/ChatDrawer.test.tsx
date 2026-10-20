import { beforeEach, describe, it, expect, vi } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import ChatDrawer from '../ChatDrawer';

const jsonResponse = (body: unknown) =>
  new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'Content-Type': 'application/json' },
  });

describe('ChatDrawer', () => {
  beforeEach(() => {
    localStorage.setItem('access_token', 'mock-token');
    vi.stubGlobal(
      'fetch',
      vi.fn(async (url: string) => {
        if (url.includes('/api/admin/users/only-users')) {
          return jsonResponse({
            users: [{ id: 'user1', name: 'Test User 1', username: 'testuser1' }],
          });
        }
        return jsonResponse({ messages: [] });
      })
    );
  });

  it('shows the support header for a user', async () => {
    render(<ChatDrawer userId="test-user" userRole="user" onClose={() => {}} />);

    expect(await screen.findByText('Support')).toBeInTheDocument();
    expect(await screen.findByText('No messages yet.')).toBeInTheDocument();
  });

  it('lists the users for an admin', async () => {
    render(<ChatDrawer userId="test-admin" userRole="admin" onClose={() => {}} />);

    expect(await screen.findByText('Users')).toBeInTheDocument();
    expect(await screen.findByText('Test User 1')).toBeInTheDocument();
  });

  it('does not nest a button inside a button', async () => {
    const { container } = render(
      <ChatDrawer userId="test-user" userRole="user" onClose={() => {}} />
    );
    await screen.findByText('Support');

    expect(container.querySelectorAll('button button')).toHaveLength(0);
  });

  it('closes without minimising when the close button is clicked', async () => {
    const onClose = vi.fn();
    render(<ChatDrawer userId="test-user" userRole="user" onClose={onClose} />);
    await screen.findByText('No messages yet.');

    fireEvent.click(screen.getByRole('button', { name: 'Close chat' }));

    expect(onClose).toHaveBeenCalledTimes(1);
    expect(screen.getByText('No messages yet.')).toBeInTheDocument();
  });

  it('minimises and expands when the header is clicked', async () => {
    render(<ChatDrawer userId="test-user" userRole="user" onClose={() => {}} />);
    await screen.findByText('No messages yet.');

    fireEvent.click(screen.getByRole('button', { name: /Support/ }));
    expect(screen.queryByText('No messages yet.')).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole('button', { name: /Support/ }));
    expect(screen.getByText('No messages yet.')).toBeInTheDocument();
  });
});
