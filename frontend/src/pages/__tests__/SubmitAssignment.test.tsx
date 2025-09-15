import { render, screen, fireEvent } from '@testing-library/react';
import SubmitAssignment from '../SubmitAssignment';
import React from 'react';

describe('SubmitAssignment', () => {
  it('shows error if no assignment or file selected', () => {
    render(<SubmitAssignment />);
    fireEvent.click(screen.getByText('Submit'));
    expect(screen.getByText(/please select assignment/i)).toBeInTheDocument();
  });
});
