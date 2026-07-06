export function LoadingSkeleton({ rows = 3 }: { rows?: number }) {
  return (
    <div>
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="skeleton" style={{ marginBottom: 8, height: 48 }} />
      ))}
    </div>
  );
}
