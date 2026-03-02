import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import SignInPage from '../SignIn';

vi.mock('@clerk/clerk-react', () => ({
  SignIn: ({ appearance }: { appearance: unknown }) => (
    <div data-testid="clerk-signin">Sign In Component</div>
  ),
}));

describe('SignInPage', () => {
  it('renders Clerk SignIn component', () => {
    const { getByTestId } = render(
      <MemoryRouter>
        <SignInPage />
      </MemoryRouter>
    );
    
    expect(getByTestId('clerk-signin')).toBeInTheDocument();
  });
});
