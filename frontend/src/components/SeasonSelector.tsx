import { useEffect, useState } from "react";
import { fetchSeasons } from "../api/client";
import type { SeasonsResponse } from "../types";

interface Props {
  selected: string;
  onChange: (season: string) => void;
}

export function SeasonSelector({ selected, onChange }: Props) {
  const [seasons, setSeasons] = useState<SeasonsResponse | null>(null);

  useEffect(() => {
    fetchSeasons().then(setSeasons).catch(() => null);
  }, []);

  if (!seasons) return null;

  const allSeasons = [seasons.current, ...seasons.historical];

  return (
    <div className="season-selector">
      <label htmlFor="season-select">Season:</label>
      <select
        id="season-select"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
      >
        {allSeasons.map((s) => (
          <option key={s} value={s}>
            {s === seasons.current ? `${s} (live)` : s}
          </option>
        ))}
      </select>
    </div>
  );
}
