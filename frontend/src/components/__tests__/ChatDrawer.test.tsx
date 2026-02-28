import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import ChatDrawer from '../ChatDrawer';

vi.mock('@clerk/clerk-react', () => ({
  useClerk: () => ({
    session: {
      getToken: vi.fn().mockResolvedValue('mock-token'),
    },
  }),
}));

global.fetch = vi.fn(() =>
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({ messages: [] }),
  })
) as any;

describe('ChatDrawer', () => {
  it('renders correct header for user role', () => {
    const { getByText } = render(
      <ChatDrawer 
        userId="test-user" 
        userRole="user" 
        onClose={() => {}} 
      />
    );
    expect(getByText('Chat with Admin')).toBeInTheDocument();
  });

  it('renders user list for admin role', async () => {
    const mockUsers = [{ id: 'user1', name: 'Test User 1', username: 'testuser1' }];
    (global.fetch as any).mockImplementationOnce(() => Promise.resolve({
      ok: true,
      json: () => Promise.resolve({ users: mockUsers }),
    }));

    const { findByText } = render(
      <ChatDrawer 
        userId="test-admin" 
        userRole="admin" 
        onClose={() => {}} 
      />
    );
    
    expect(await findByText('Test User 1')).toBeInTheDocument();
  });
});
