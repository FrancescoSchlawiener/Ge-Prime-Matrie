interface EmptyStateProps {
  title: string;
  hint?: string;
}

export function EmptyState({ title, hint }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <p>{title}</p>
      {hint ? <p style={{ fontSize: "0.9rem" }}>{hint}</p> : null}
    </div>
  );
}
