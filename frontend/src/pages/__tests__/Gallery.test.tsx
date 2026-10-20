import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import Gallery from '../Gallery';

const IMAGE = {
  id: 'img1',
  filename: 'img1_photo.png',
  title: 'My photo',
  description: 'A description',
  created_at: '2026-01-01T10:00:00',
  sentiment: 'neutral',
};

const jsonResponse = (body: unknown, status = 200) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });

describe('Gallery delete flow', () => {
  let fetchMock: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    fetchMock = vi.fn(async (url: string, options?: RequestInit) => {
      if (options?.method === 'DELETE') {
        return jsonResponse({ message: 'Image deleted successfully!' });
      }
      if (url.includes('/api/user/user_uploads')) {
        return jsonResponse({ images: [IMAGE], total: 1, hasMore: false });
      }
      return new Response(new Blob(['x']), { status: 200 });
    });
    vi.stubGlobal('fetch', fetchMock);
    URL.createObjectURL = vi.fn(() => 'blob:mock');
    URL.revokeObjectURL = vi.fn();
  });

  const openDeleteModal = async () => {
    render(
      <MemoryRouter>
        <Gallery />
      </MemoryRouter>
    );
    fireEvent.click(await screen.findByTitle('Delete'));
    await screen.findByText('Delete Image');
  };

  it('opens the delete confirmation modal', async () => {
    await openDeleteModal();

    expect(screen.getByText('Delete Permanently')).not.toBeDisabled();
  });

  it('deletes the image on the server once the undo window has passed', async () => {
    await openDeleteModal();
    vi.useFakeTimers({ shouldAdvanceTime: true });

    try {
      fireEvent.click(screen.getByText('Delete Permanently'));
      // Nothing is sent while the undo toast is still showing.
      expect(fetchMock.mock.calls.some(([, o]) => o?.method === 'DELETE')).toBe(false);

      await act(async () => {
        await vi.advanceTimersByTimeAsync(5000);
      });

      await waitFor(() => {
        const deleteCall = fetchMock.mock.calls.find(([, o]) => o?.method === 'DELETE');
        expect(deleteCall?.[0]).toContain('/delete/img1');
      });
    } finally {
      vi.useRealTimers();
    }
  });
});
