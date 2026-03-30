# NBA Team Draft Tracker

A lightweight web app for tracking a friend-group NBA team draft across a full season. Each participant drafts a set of NBA teams at the start of the season. This app shows live standings, records, and comparisons so you can see who's winning the draft.

## Features

- Live W-L record, home/away split, last-10, and conference standing for every drafted team
- Aggregate combined record per participant, sorted by win percentage
- Historical seasons stored as static JSON files — no database required
- Admin endpoint to update rosters after the draft (protected by API key)
- Fully free and open-source: Python + FastAPI backend, React + Vite frontend, deployed on Render.com free tier