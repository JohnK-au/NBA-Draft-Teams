interface Props {
  wins: number;
  losses: number;
  winPct?: number;
  size?: "sm" | "lg";
}

export function RecordBadge({ wins, losses, winPct, size = "sm" }: Props) {
  const pct =
    winPct !== undefined
      ? winPct.toFixed(3).replace(/^0/, "")
      : null;

  return (
    <span className={`record-badge record-badge--${size}`}>
      {wins}–{losses}
      {pct && <span className="record-badge__pct"> ({pct})</span>}
    </span>
  );
}
