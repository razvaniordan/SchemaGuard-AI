import type { HTMLAttributes, ReactNode } from 'react';
import { cn } from '../../../utils/cn';
import './Card.css';

export type CardProps = HTMLAttributes<HTMLDivElement> & {
  title?: string;
  description?: string;
  footer?: ReactNode;
};

export function Card({ title, description, footer, children, className, ...props }: CardProps) {
  return (
    <section className={cn('ui-card', className)} {...props}>
      {(title || description) && (
        <header className="ui-card-header">
          {title ? <h3 className="ui-card-title">{title}</h3> : null}
          {description ? <p className="ui-card-description">{description}</p> : null}
        </header>
      )}

      <div className="ui-card-content">{children}</div>

      {footer ? <footer className="ui-card-footer">{footer}</footer> : null}
    </section>
  );
}