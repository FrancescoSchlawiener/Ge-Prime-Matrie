interface BadgeProps {
  active: boolean;
  children: string;
}

export function Badge({ active, children }: BadgeProps) {
  return <span className={`gpm-badge${active ? " gpm-badge--ok" : " gpm-badge--no"}`}>{children}</span>;
}
