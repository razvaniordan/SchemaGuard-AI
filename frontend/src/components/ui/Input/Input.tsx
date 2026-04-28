import type { InputHTMLAttributes } from 'react';
import { cn } from '../../../utils/cn';
import './Input.css';

export type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label?: string;
  error?: string;
};

export function Input({ id, label, error, className, ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <div className="ui-input-field">
      {label ? (
        <label className="ui-input-label" htmlFor={inputId}>
          {label}
        </label>
      ) : null}

      <input
        id={inputId}
        className={cn('ui-input', error && 'ui-input--error', className)}
        aria-invalid={Boolean(error)}
        aria-describedby={error ? `${inputId}-error` : undefined}
        {...props}
      />

      {error ? (
        <p id={`${inputId}-error`} className="ui-input-error">
          {error}
        </p>
      ) : null}
    </div>
  );
}