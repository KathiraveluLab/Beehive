import React from 'react';

interface Props {
  page: number;
  totalPages: number;
  onPageChange: (page: number) => void;
}

const Pagination: React.FC<Props> = ({ page, totalPages, onPageChange }) => {
  const prev = () => onPageChange(Math.max(1, page - 1));
  const next = () => onPageChange(Math.min(totalPages, page + 1));

  const renderPageButtons = () => {
    const buttons = [];
    const pageButtonCount = 5;
    let start = Math.max(1, page - Math.floor(pageButtonCount / 2));
    let end = start + pageButtonCount - 1;

    if (end > totalPages) {
      end = totalPages;
      start = Math.max(1, end - pageButtonCount + 1);
    }

    for (let p = start; p <= end; p++) {
      buttons.push(
        <button
          key={p}
          type="button"
          onClick={() => onPageChange(p)}
          className={`px-3 py-1 rounded-md mx-1 ${p === page ? 'bg-yellow-400 text-black' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200'}`}
        >
          {p}
        </button>
      );
    }
    return buttons;
  };

  if (totalPages <= 1) return null;

  return (
    <div className="flex items-center justify-center space-x-2 mt-4">
      <button
        type="button"
        onClick={prev}
        disabled={page <= 1}
        className="px-3 py-1 rounded-md bg-gray-100 dark:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Prev
      </button>
      {renderPageButtons()}
      <button
        type="button"
        onClick={next}
        disabled={page >= totalPages}
        className="px-3 py-1 rounded-md bg-gray-100 dark:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        Next
      </button>
    </div>
  );
};

export default Pagination;
