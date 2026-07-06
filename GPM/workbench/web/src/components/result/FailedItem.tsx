interface FailedItemProps {
  label: string;
  message: string;
}

export function FailedItem({ label, message }: FailedItemProps) {
  return (
    <div className="gpm-failed-item">
      <span className="gpm-failed-item__label">{label}</span>
      <span className="gpm-failed-item__message">{message}</span>
    </div>
  );
}
